from procfunc import compute_graph as cg

from .distribution import as_distribution


def extract_parameter_distributions(
    compute_graph: cg.ComputeGraph,
) -> list[cg.Node]:
    return [
        child
        for _, _, child in cg.traverse_depth_first(
            compute_graph, yield_consts=True, yield_name=True, yield_parent=True
        )
        if isinstance(child, cg.Node) and as_distribution(child) is not None
    ]
