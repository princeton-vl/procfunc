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
        for g in graphs:
            for node, g in cg.traverse_nested_graphs(g, yield_call_nodes=True):
                if node is None:
                    continue
                assert isinstance(node, cg.SubgraphCallNode)
                res = func(node, g)
                if not isinstance(res, cg.ComputeGraph):
                    raise ValueError(
                        f"Transform {func.__name__} produced {res=} for {g=}"
                    )
                node.subgraph = res
        return graphs

    return wrapper
