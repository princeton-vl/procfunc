import procfunc as pf
from procfunc import compute_graph as cg


def colors_to_hsv_definition(graph: cg.ComputeGraph) -> cg.ComputeGraph:
    def as_hsv_call(color: pf.Color) -> cg.FunctionCallNode:
        hsv = tuple(round(x, 4) for x in color.hsv)
        return cg.FunctionCallNode(pf.color.hsv_to_rgba, args=(), kwargs={"hsv": hsv})

    replacements = {}
    for node in cg.traverse_depth_first(graph):
        args = tuple(
            as_hsv_call(arg) if isinstance(arg, pf.Color) else arg for arg in node.args
        )
        kwargs = {
            key: as_hsv_call(arg) if isinstance(arg, pf.Color) else arg
            for key, arg in node.kwargs.items()
        }
        if args != node.args or any(kwargs[k] is not node.kwargs[k] for k in kwargs):
            replacements[id(node)] = node._replace(args=args, kwargs=kwargs)

    updated = cg.replace_in_graph(graph, replacements)
    graph.inputs, graph.outputs = updated.inputs, updated.outputs
    return graph
