import dataclasses
import logging
from collections import defaultdict
from typing import Any, Callable

from procfunc import compute_graph as cg
from procfunc import types as t
from procfunc.nodes import types as nt
from procfunc.nodes.shader import coord, geometry
from procfunc.transforms.util import map_subgraphs
from procfunc.util import pytree

logger = logging.getLogger(__name__)


def remove_v1_name_from_graph(
    _call_node: cg.Node, graph: cg.ComputeGraph
) -> cg.ComputeGraph:
    name = graph.name.removeprefix("nodegroup_").removeprefix("shader_")
    if name == graph.name:
        return graph
    return dataclasses.replace(graph, name=name)


def _nested_subgraphs(
    graphs: list[cg.ComputeGraph], reverse: bool
) -> list[cg.ComputeGraph]:
    unique = {}
    for topgraph in graphs:
        nested = list(cg.traverse_nested_graphs(topgraph))
        unique.update({id(g): g for g in (reversed(nested) if reverse else nested)})
    return list(unique.values())


def _group_equal_subgraphs(
    graphs: list[cg.ComputeGraph],
) -> list[list[cg.ComputeGraph]]:
    groups: list[list[cg.ComputeGraph]] = []
    for subgraph in _nested_subgraphs(graphs, reverse=True):
        match = next((m for m in groups if cg.graph_nodes_equal(subgraph, m[0])), None)
        if match is None:
            groups.append([subgraph])
        else:
            match.append(subgraph)
    return groups


def _apply_subgraph_replacements(
    graphs: list[cg.ComputeGraph],
    replacements: dict[int, cg.ComputeGraph],
    top_replacements: dict[int, cg.ComputeGraph],
) -> list[cg.ComputeGraph]:
    def replace_subgraph(_node: cg.Node, subgraph: cg.ComputeGraph) -> cg.ComputeGraph:
        return replacements.get(id(subgraph), subgraph)

    graphs = [top_replacements.get(id(graph), graph) for graph in graphs]
    return map_subgraphs(replace_subgraph)(graphs)


def eliminate_duplicate_subgraphs(
    graphs: list[cg.ComputeGraph],
) -> list[cg.ComputeGraph]:
    replacements: dict[int, cg.ComputeGraph] = {}
    renamed: dict[int, cg.ComputeGraph] = {}
    removed: list[cg.ComputeGraph] = []
    for members in _group_equal_subgraphs(graphs):
        shortest = min((g.name for g in members), key=len)
        canonical = members[0]
        if shortest != canonical.name:
            canonical = dataclasses.replace(canonical, name=shortest)
        replacements.update({id(g): canonical for g in members})
        renamed[id(members[0])] = canonical
        removed.extend(members[1:])

    logger.debug(f"Eliminated duplicated subgraphs {[g.name for g in removed]}")

    return _apply_subgraph_replacements(graphs, replacements, renamed)


def _with_result_type(graph: cg.ComputeGraph, result_type: type) -> cg.ComputeGraph:
    spec = dataclasses.replace(graph.outputs.spec, container=result_type)
    outputs = pytree.PyTree.from_children_spec(graph.outputs.children, spec)
    return dataclasses.replace(graph, outputs=outputs)


def _matching_result_type(result_type: type, known: list[type]) -> type:
    fields = list(result_type._fields)
    return next((rt for rt in known if list(rt._fields) == fields), result_type)


def eliminate_duplicate_result_types(
    graphs: list[cg.ComputeGraph],
    uses_threshold: int = 1,
) -> list[cg.ComputeGraph]:
    rettype_uses: dict[type, list[cg.ComputeGraph]] = defaultdict(list)

    # counted once per top-level graph that reaches it, so shared subgraphs weigh more
    nested = [g for graph in graphs for g in cg.traverse_nested_graphs(graph)]
    for subgraph in nested:
        result_type = subgraph.outputs.toplevel_type()
        if result_type is None or not pytree.is_type_namedtuple(result_type):
            continue
        result_type = _matching_result_type(result_type, list(rettype_uses))
        rettype_uses[result_type].append(subgraph)

    replacements: dict[int, cg.ComputeGraph] = {}
    for uses in rettype_uses.values():
        if len(uses) <= uses_threshold:
            continue
        first_rettype = uses[0].outputs.toplevel_type()
        for subgraph in uses[1:]:
            if subgraph.outputs.toplevel_type() is first_rettype:
                continue
            replacements[id(subgraph)] = _with_result_type(subgraph, first_rettype)

    return _apply_subgraph_replacements(graphs, replacements, replacements)


def fill_graph_defaults_with_call_node(
    call_node: cg.SubgraphCallNode,
    graph: cg.ComputeGraph,
) -> cg.ComputeGraph:
    if call_node is None:
        return graph

    if any(
        isinstance(arg.default_value, float) and arg.default_value != 0.0
        for arg in graph.inputs.values()
    ):
        logger.debug(
            f"Skipping {graph.name} because it has nondefault existing default args"
        )
        return graph

    replacements = {}
    for name, inpnode in graph.inputs.items():
        fillval = call_node.kwargs.get(name, None)
        if fillval is not None and not isinstance(fillval, cg.Node):
            replacements[id(inpnode)] = inpnode._replace(
                kwargs={**inpnode.kwargs, "default_value": fillval}
            )

    return cg.replace_in_graph(graph, replacements)


def coerce_shaders_to_materialresult(
    _call_node: cg.Node, subgraph: cg.ComputeGraph
) -> cg.ComputeGraph:
    if subgraph.outputs.toplevel_type() is t.Material:
        return subgraph
    outputs = subgraph.outputs.dict()
    surface = outputs.get("surface") or outputs.get("bsdf")
    if surface is None:
        return subgraph
    # a missing displacement output is left as None ("no displacement")
    shader_outputs = {
        "surface": surface,
        "displacement": outputs.get("displacement"),
        "volume": outputs.get("volume"),
    }
    if len(outputs) > len(shader_outputs):
        logger.warning(
            f"{coerce_shaders_to_materialresult.__name__} skipping due to extra outputs: {outputs.keys()}"
        )
        return subgraph
    logger.debug(
        f"{coerce_shaders_to_materialresult.__name__} converted {subgraph.name} output"
    )
    return dataclasses.replace(
        subgraph, outputs=pytree.PyTree(t.Material(**shader_outputs))
    )


def replace_ids(
    graph: cg.ComputeGraph,
    ids: set[int],
    val: Any,
):
    """
    Pull out hardcoded arguments to be inputs to the graph instead

    Args:
        graph: The graph to extract constants from
        extract_mask: A mask of which args to extract. The key is a tuple of the parent node id and the arg name.
    """

    assert isinstance(graph, cg.ComputeGraph)

    return cg.replace_in_graph(graph, {node_id: val for node_id in ids})


def extract_as_input(
    graph: cg.ComputeGraph,
    nodes: set[int],
    name: str,
    arg_type: type,
):
    inp = cg.InputPlaceholderNode(
        input_name=name,
        args=(),
        default_value=None,
        metadata={"known_value_type": arg_type, "varname": name},
    )

    inputs = graph.inputs.obj()
    assert isinstance(inputs, dict), inputs
    graph = dataclasses.replace(graph, inputs=pytree.PyTree({**inputs, name: inp}))

    return replace_ids(graph, nodes, inp)


def extract_shader_vectors_as_inputs(
    graph: cg.ComputeGraph,
    extract_funcs: list[Callable[..., Any]] | None = None,
):
    """
    Pull out shader vectors as inputs to the graph instead
    """

    if extract_funcs is None:
        extract_funcs = [coord, geometry]

    def _is_vector_target(node: cg.FunctionCallNode) -> bool:
        return isinstance(node, cg.FunctionCallNode) and node.func in extract_funcs

    vector_nodes = set(
        id(node)
        for node in cg.traverse_depth_first(graph)
        if _is_vector_target(node)
        or (isinstance(node, cg.GetAttributeNode) and _is_vector_target(node.args[0]))
    )

    if len(vector_nodes) == 0:
        return graph

    return extract_as_input(graph, vector_nodes, "vector", nt.ProcNode[t.Vector])
