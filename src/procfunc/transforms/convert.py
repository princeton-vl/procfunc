import procfunc as pf
from procfunc import compute_graph as cg


def colors_to_hsv_definition(graph: cg.ComputeGraph) -> cg.ComputeGraph:
    def as_hsv_call(color: pf.Color) -> cg.FunctionCallNode:
        hsv = tuple(round(x, 4) for x in color.hsv)
        return cg.FunctionCallNode(pf.color.hsv_to_rgba, args=(), kwargs={"hsv": hsv})

    for node in cg.traverse_depth_first(graph):
        if any(isinstance(arg, pf.Color) for arg in node.args):
            node.args = tuple(
                as_hsv_call(arg) if isinstance(arg, pf.Color) else arg
                for arg in node.args
            )
        for key, arg in node.kwargs.items():
            if isinstance(arg, pf.Color):
                node.kwargs[key] = as_hsv_call(arg)

    return graph
