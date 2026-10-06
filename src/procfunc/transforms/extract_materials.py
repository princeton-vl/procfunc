"""
Transform to extract material SubgraphCallNodes from geometry node functions,
making them pure by moving material calls to the caller.
"""

import dataclasses
import logging

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes import types as nt
from procfunc.util import pytree

logger = logging.getLogger(__name__)

# input name -> the material call that a caller must bind to that input
MaterialNeeds = dict[str, cg.SubgraphCallNode]
ExtractMemo = dict[int, tuple[cg.ComputeGraph, cg.ComputeGraph, MaterialNeeds]]


def _is_material_subgraph(subgraph: cg.ComputeGraph) -> bool:
    return subgraph.outputs.toplevel_type() is pf.Material


def _is_node_function(graph: cg.ComputeGraph) -> bool:
    return graph.metadata.get("is_node_function", False)


def _sanitize_name(name: str) -> str:
    return f"material_{name.replace('.', '_').replace(' ', '_').lower()}"


def _material_input(name: str) -> cg.InputPlaceholderNode:
    return cg.InputPlaceholderNode(
        input_name=name,
        args=(),
        default_value=None,
        metadata={"known_value_type": nt.ProcNode[pf.Material], "varname": name},
    )


def _material_arg(
    name: str,
    mat_call: cg.SubgraphCallNode,
    placeholders: dict[str, cg.InputPlaceholderNode],
) -> cg.Node:
    if name in placeholders:
        return placeholders[name]
    return cg.MethodCallNode(mat_call, "item", args=(), kwargs={})


def _bound_call(
    call: cg.SubgraphCallNode,
    subgraph: cg.ComputeGraph,
    needs: MaterialNeeds,
    placeholders: dict[str, cg.InputPlaceholderNode],
) -> cg.SubgraphCallNode:
    missing = {k: v for k, v in needs.items() if k not in call.kwargs}
    if subgraph is call.subgraph and not missing:
        return call
    bound = {k: _material_arg(k, v, placeholders) for k, v in missing.items()}
    return call._replace(subgraph=subgraph, kwargs={**call.kwargs, **bound})


def _with_inputs(
    graph: cg.ComputeGraph, placeholders: dict[str, cg.InputPlaceholderNode]
) -> cg.ComputeGraph:
    if not placeholders:
        return graph
    inputs = pytree.PyTree({**graph.inputs.obj(), **placeholders})
    return dataclasses.replace(graph, inputs=inputs)


def _extract(
    graph: cg.ComputeGraph,
    memo: ExtractMemo,
    extracted: MaterialNeeds,
) -> tuple[cg.ComputeGraph, MaterialNeeds]:
    if id(graph) in memo:
        return memo[id(graph)][1:]

    is_node_function = _is_node_function(graph)
    calls = [
        node
        for node in cg.traverse_depth_first(graph)
        if isinstance(node, cg.SubgraphCallNode)
    ]
    own = [c for c in calls if is_node_function and _is_material_subgraph(c.subgraph)]
    own_ids = {id(c) for c in own}
    children = [c for c in calls if id(c) not in own_ids]
    rebuilt = {id(c): _extract(c.subgraph, memo, extracted) for c in children}

    needs: MaterialNeeds = {}
    if is_node_function:
        needs.update({_sanitize_name(c.subgraph.name): c for c in own})
        for _subgraph, child_needs in rebuilt.values():
            needs.update(child_needs)
    placeholders = {name: _material_input(name) for name in needs}

    replacements = {id(c): placeholders[_sanitize_name(c.subgraph.name)] for c in own}
    for c in children:
        new_call = _bound_call(c, *rebuilt[id(c)], placeholders)
        if new_call is not c:
            replacements[id(c)] = new_call

    result = cg.replace_in_graph(_with_inputs(graph, placeholders), replacements)
    for c in own:
        logger.debug(f"Extracted material '{c.subgraph.name}' from {graph.name}")
        extracted[_sanitize_name(c.subgraph.name)] = c

    memo[id(graph)] = (graph, result, needs)
    return result, needs


def extract_materials_from_graph(
    top_graph: cg.ComputeGraph,
) -> tuple[cg.ComputeGraph, MaterialNeeds]:
    extracted: MaterialNeeds = {}
    result, _needs = _extract(top_graph, {}, extracted)
    return result, extracted


def extract_materials_from_graphs(
    graphs: list[cg.ComputeGraph],
) -> list[cg.ComputeGraph]:
    memo: ExtractMemo = {}
    results = []
    for graph in graphs:
        extracted: MaterialNeeds = {}
        result, _needs = _extract(graph, memo, extracted)
        results.append(result)
        if extracted:
            logger.info(f"Extracted materials from {graph.name}: {list(extracted)}")
    return results
