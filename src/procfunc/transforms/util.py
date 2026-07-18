import functools
from typing import Callable

from procfunc import compute_graph as cg


def map_graph_list(
    func: Callable[[cg.ComputeGraph], cg.ComputeGraph],
) -> Callable[[list[cg.ComputeGraph]], list[cg.ComputeGraph]]:
    @functools.wraps(func)
    def wrapper(graphs):
        return [func(g) for g in graphs]

    return wrapper


def map_subgraphs(
    func: Callable[[cg.Node, cg.ComputeGraph], cg.ComputeGraph],
) -> Callable[[list[cg.ComputeGraph]], list[cg.ComputeGraph]]:
    @functools.wraps(func)
    def wrapper(graphs: list[cg.ComputeGraph]) -> list[cg.ComputeGraph]:
        def rewrite(graph: cg.ComputeGraph) -> cg.ComputeGraph:
            replacements = {}
            for node in cg.traverse_depth_first(graph):
                if not isinstance(node, cg.SubgraphCallNode):
                    continue
                res = func(node, node.subgraph)
                if not isinstance(res, cg.ComputeGraph):
                    raise ValueError(
                        f"Transform {func.__name__} produced {res=} for {graph=}"
                    )
                replacements[id(node)] = node._replace(subgraph=rewrite(res))
            updated = cg.replace_in_graph(graph, replacements)
            graph.inputs, graph.outputs = updated.inputs, updated.outputs
            return graph

        for graph in graphs:
            rewrite(graph)
        return graphs

    return wrapper
