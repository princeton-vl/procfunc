"""
Transform to extract material SubgraphCallNodes from geometry node functions,
making them pure by moving material calls to the caller.
"""

import logging

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes import types as nt
from procfunc.util import pytree

logger = logging.getLogger(__name__)


def _is_material_subgraph(subgraph: cg.ComputeGraph) -> bool:
    return subgraph.outputs.toplevel_type() is pf.Material


def _sanitize_name(name: str) -> str:
    return f"material_{name.replace('.', '_').replace(' ', '_').lower()}"


def _add_input(graph: cg.ComputeGraph, name: str) -> cg.InputPlaceholderNode:
    inp = cg.InputPlaceholderNode(
        name=name,
        default_value=None,
        metadata={"known_value_type": nt.ProcNode[pf.Material], "varname": name},
    )
    inputs = graph.inputs.obj()
    inputs[name] = inp
    graph.inputs = pytree.PyTree(inputs)
    return inp


def _build_parent_map(
    top_graph: cg.ComputeGraph,
) -> dict[int, list[tuple[cg.ComputeGraph, cg.SubgraphCallNode]]]:
    parent_map = {}
    for _call_node, graph in cg.traverse_nested_graphs(
        top_graph, yield_call_nodes=True
    ):
        for node in cg.traverse_depth_first(graph):
            if isinstance(node, cg.SubgraphCallNode):
                parent_map.setdefault(id(node.subgraph), []).append((graph, node))
    return parent_map


def _plumb_material_to_callers(
    graph: cg.ComputeGraph,
    mat_call: cg.SubgraphCallNode,
    input_name: str,
    parent_map: dict[int, list[tuple[cg.ComputeGraph, cg.SubgraphCallNode]]],
) -> None:
    added_inputs: dict[int, cg.InputPlaceholderNode] = {}
    visited = {id(graph)}
    worklist = [graph]

    while worklist:
        current_graph = worklist.pop()
        for parent_graph, call_node in parent_map.get(id(current_graph), []):
            if not parent_graph.metadata.get("is_node_function", False):
                if input_name not in call_node.kwargs:
                    item_node = cg.MethodCallNode(mat_call, "item", args=(), kwargs={})
                    _replace_call_kwargs(parent_graph, call_node, input_name, item_node)
                continue

            parent_inp = added_inputs.get(id(parent_graph))
            if parent_inp is None:
                parent_inp = _add_input(parent_graph, input_name)
                added_inputs[id(parent_graph)] = parent_inp

            if input_name not in call_node.kwargs:
                _replace_call_kwargs(parent_graph, call_node, input_name, parent_inp)

            if id(parent_graph) not in visited:
                visited.add(id(parent_graph))
                worklist.append(parent_graph)


def _replace_node_in_graph(
    graph: cg.ComputeGraph,
    old_node: cg.Node,
    new_node: cg.Node,
) -> None:
    updated = cg.replace_in_graph(graph, {id(old_node): new_node})
    graph.inputs, graph.outputs = updated.inputs, updated.outputs


def _replace_call_kwargs(
    graph: cg.ComputeGraph,
    call_node: cg.SubgraphCallNode,
    input_name: str,
    value: cg.Node,
) -> None:
    replacement = call_node._replace(
        kwargs={**call_node.kwargs, input_name: value}
    )
    updated = cg.replace_in_graph(graph, {id(call_node): replacement})
    graph.inputs, graph.outputs = updated.inputs, updated.outputs


def extract_materials_from_graph(
    top_graph: cg.ComputeGraph,
) -> dict[str, cg.SubgraphCallNode]:
    extracted_materials = {}

    for graph in cg.traverse_nested_graphs(top_graph):
        if not graph.metadata.get("is_node_function", False):
            continue

        material_calls = []
        for node in cg.traverse_depth_first(graph):
            if isinstance(node, cg.SubgraphCallNode) and _is_material_subgraph(
                node.subgraph
            ):
                material_calls.append(node)

        for mat_call in material_calls:
            input_name = _sanitize_name(mat_call.subgraph.name)

            inp = _add_input(graph, input_name)
            _replace_node_in_graph(graph, mat_call, inp)

            parent_map = _build_parent_map(top_graph)
            _plumb_material_to_callers(graph, mat_call, input_name, parent_map)

            extracted_materials[input_name] = mat_call
            logger.debug(
                f"Extracted material '{mat_call.subgraph.name}' from {graph.name}"
            )

    return extracted_materials


def extract_materials_from_graphs(
    graphs: list[cg.ComputeGraph],
) -> list[cg.ComputeGraph]:
    for graph in graphs:
        materials = extract_materials_from_graph(graph)
        if materials:
            logger.info(
                f"Extracted materials from {graph.name}: {list(materials.keys())}"
            )
    return graphs
