import logging
from collections import defaultdict
from typing import Any, Callable

from procfunc import compute_graph as cg
from procfunc import types as t
from procfunc.nodes import types as nt
from procfunc.nodes.shader import coord, geometry
from procfunc.util import pytree

logger = logging.getLogger(__name__)


def remove_v1_name_from_graph(
    _call_node: cg.Node, graph: cg.ComputeGraph
) -> cg.ComputeGraph:
    if graph.name.startswith("nodegroup_"):
        graph.name = graph.name.replace("nodegroup_", "")
    if graph.name.startswith("shader_"):
        graph.name = graph.name.replace("shader_", "")
    return graph


def eliminate_duplicate_subgraphs(
    graphs: list[cg.ComputeGraph],
) -> list[cg.ComputeGraph]:
    unique: list[cg.ComputeGraph] = []
    removed: list[cg.ComputeGraph] = []
    # maps id(duplicate_subgraph) -> canonical subgraph to replace it with
    replacements: dict[int, cg.ComputeGraph] = {}

    for topgraph in graphs:
        subgraphs = reversed(
            list(cg.traverse_nested_graphs(topgraph, yield_call_nodes=True))
        )
        for _call_node, subgraph in subgraphs:
            match = next((g for g in unique if cg.graph_nodes_equal(subgraph, g)), None)
            if match is not None:
                if len(subgraph.name) < len(match.name):
                    match.name = subgraph.name
                replacements[id(subgraph)] = match
                removed.append(subgraph)
            else:
                unique.append(subgraph)

    # second pass: update ALL call nodes (in all nested subgraphs) that reference a replaced subgraph
    for topgraph in graphs:
        for subgraph in cg.traverse_nested_graphs(topgraph):
            for node in cg.traverse_depth_first(subgraph):
                if (
                    isinstance(node, cg.SubgraphCallNode)
                    and id(node.subgraph) in replacements
                ):
                    node.subgraph = replacements[id(node.subgraph)]

    logger.debug(f"Eliminated duplicated subgraphs {[g.name for g in removed]}")

    return graphs


def eliminate_duplicate_result_types(
    graphs: list[cg.ComputeGraph],
    uses_threshold: int = 1,
) -> list[cg.ComputeGraph]:
    rettype_uses: dict[type, list[cg.ComputeGraph]] = defaultdict(list)

    for graph in graphs:
        for subgraph in cg.traverse_nested_graphs(graph):
            result_type = subgraph.outputs.toplevel_type()
            if result_type is None or not pytree.is_type_namedtuple(result_type):
                continue

            for rt in rettype_uses.keys():
                if list(rt._fields) == list(result_type._fields):
                    result_type = rt
                    break

            rettype_uses[result_type].append(subgraph)

    for rettype, uses in rettype_uses.items():
        if len(uses) <= uses_threshold:
            continue
        first_rettype = uses[0].outputs.toplevel_type()
        for subgraph in uses[1:]:
            subgraph.outputs.spec.container = first_rettype

    return graphs


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

    for name, inpnode in graph.inputs.items():
        fillval = call_node.kwargs.get(name, None)
        if fillval is not None and not isinstance(fillval, cg.Node):
            inpnode.kwargs["default_value"] = fillval

    return graph


def coerce_shaders_to_materialresult(
    _call_node: cg.Node, subgraph: cg.ComputeGraph
) -> cg.ComputeGraph:
    if subgraph.outputs.toplevel_type() is t.Material:
        return subgraph
    outputs = subgraph.outputs.dict()
    surface = outputs.get("surface") or outputs.get("bsdf")
    if surface is None:
        return subgraph
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
    subgraph.outputs = pytree.PyTree(t.Material(**shader_outputs))

    return subgraph


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

    for name, parent, child in cg.traverse_depth_first(
        graph, yield_consts=True, yield_name=True, yield_parent=True
    ):
        if id(child) not in ids:
            continue
        if isinstance(name, int):
            args = list(parent.args)
            args[name] = val
            parent.args = tuple(args)
        else:
            parent.kwargs[name] = val

    return graph


def extract_as_input(
    graph: cg.ComputeGraph,
    nodes: set[int],
    name: str,
    arg_type: type,
):
    inp = cg.InputPlaceholderNode(
        default_value=None, metadata={"known_value_type": arg_type, "varname": name}
    )

    inputs = graph.inputs.obj()
    assert isinstance(inputs, dict), inputs
    inputs[name] = inp
    graph.inputs = pytree.PyTree(inputs)

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

    extract_as_input(graph, vector_nodes, "vector", nt.ProcNode[t.Vector])
    return graph
