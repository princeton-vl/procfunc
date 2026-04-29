import procfunc as pf
from procfunc import compute_graph as cg


def colors_to_hsv_definition(graph: cg.ComputeGraph) -> cg.ComputeGraph:
    for node in cg.traverse_depth_first(graph):
        for i, arg in enumerate(node.args):
            if isinstance(arg, pf.Color):
                hsv = tuple(round(x, 4) for x in arg.hsv)
                node.args[i] = cg.FunctionCallNode(
                    pf.color.hsv_to_rgba, args=(), kwargs={"hsv": hsv}
                )
        for key, arg in node.kwargs.items():
            if isinstance(arg, pf.Color):
                hsv = tuple(round(x, 4) for x in arg.hsv)
                node.kwargs[key] = cg.FunctionCallNode(
                    pf.color.hsv_to_rgba, args=(), kwargs={"hsv": hsv}
                )

    return graph
