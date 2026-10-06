import functools
from typing import Callable

from procfunc import compute_graph as cg

SubgraphTransform = Callable[[cg.Node, cg.ComputeGraph], cg.ComputeGraph]


def map_graph_list(
    func: Callable[[cg.ComputeGraph], cg.ComputeGraph],
) -> Callable[[list[cg.ComputeGraph]], list[cg.ComputeGraph]]:
    @functools.wraps(func)
    def wrapper(graphs):
        return [func(g) for g in graphs]

    return wrapper


GraphMemo = dict[int, tuple[cg.ComputeGraph, cg.ComputeGraph]]


def _transform_subgraphs(
    func: SubgraphTransform, graphs: list[cg.ComputeGraph]
) -> GraphMemo:
    # reapplied once per top-level graph, with its first breadth-first call site
    visits = [
        (node, subgraph)
        for graph in graphs
        for node, subgraph in cg.traverse_nested_graphs(graph, yield_call_nodes=True)
        if node is not None
    ]
    transformed: GraphMemo = {}
    for node, subgraph in visits:
        latest = transformed.get(id(subgraph), (subgraph, subgraph))[1]
        res = func(node, latest)
        if not isinstance(res, cg.ComputeGraph):
            raise ValueError(f"Transform {func.__name__} produced {res=} for {node=}")
        transformed[id(subgraph)] = (subgraph, res)
    return transformed


def _rebuild_with_subgraphs(
    graph: cg.ComputeGraph,
    transformed: GraphMemo,
    rebuilt: GraphMemo,
) -> cg.ComputeGraph:
    if id(graph) in rebuilt:
        return rebuilt[id(graph)][1]

    calls = [
        node
        for node in cg.traverse_depth_first(graph)
        if isinstance(node, cg.SubgraphCallNode)
    ]
    replacements = {}
    for node in calls:
        latest = transformed.get(id(node.subgraph), (node.subgraph, node.subgraph))[1]
        res = _rebuild_with_subgraphs(latest, transformed, rebuilt)
        if res is not node.subgraph:
            replacements[id(node)] = node._replace(subgraph=res)

    result = cg.replace_in_graph(graph, replacements)
    rebuilt[id(graph)] = (graph, result)
    return result


def map_subgraphs(
    func: SubgraphTransform,
) -> Callable[[list[cg.ComputeGraph]], list[cg.ComputeGraph]]:
    @functools.wraps(func)
    def wrapper(graphs: list[cg.ComputeGraph]) -> list[cg.ComputeGraph]:
        transformed = _transform_subgraphs(func, graphs)
        rebuilt = {}
        return [_rebuild_with_subgraphs(g, transformed, rebuilt) for g in graphs]

    return wrapper
