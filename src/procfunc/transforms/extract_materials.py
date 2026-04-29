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
) -> dict[int, tuple[cg.ComputeGraph, cg.SubgraphCallNode]]:
    parent_map = {}
    for call_node, graph in cg.traverse_nested_graphs(top_graph, yield_call_nodes=True):
        for node in cg.traverse_depth_first(graph):
            if isinstance(node, cg.SubgraphCallNode):
                parent_map[id(node.subgraph)] = (graph, node)
    return parent_map


def _replace_node_in_graph(
    graph: cg.ComputeGraph,
    old_node: cg.Node,
    new_node: cg.Node,
) -> None:
    for node in cg.traverse_depth_first(graph):
        new_args = tuple(new_node if arg is old_node else arg for arg in node.args)
        if new_args != node.args:
            node.args = new_args

        for key, val in list(node.kwargs.items()):
            if val is old_node:
                node.kwargs[key] = new_node


def extract_materials_from_graph(
    top_graph: cg.ComputeGraph,
) -> dict[str, cg.SubgraphCallNode]:
    parent_map = _build_parent_map(top_graph)
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

            current_graph = graph
            while id(current_graph) in parent_map:
                parent_graph, call_node = parent_map[id(current_graph)]

                if not parent_graph.metadata.get("is_node_function", False):
                    item_node = cg.MethodCallNode(mat_call, "item", args=(), kwargs={})
                    call_node.kwargs[input_name] = item_node
                    break

                if input_name not in call_node.kwargs:
                    parent_inp = _add_input(parent_graph, input_name)
                    call_node.kwargs[input_name] = parent_inp
                current_graph = parent_graph

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
