"""Shared helpers for building the node tree returned by a binding callable into
a real bpy node group of a given context, so bindings can be asserted per-context."""

import procfunc as pf
from procfunc.nodes.bpy_node_info import NodeGroupType


def realize(fn, group: NodeGroupType):
    """Build the node tree returned by a binding callable (or @node_function)
    into a real bpy node group of the given context, for per-context assertions."""
    graph = pf.nodes.function_to_compute_graph(fn)
    return pf.nodes.as_nodegroup(graph, group)


def node_operations(ng, bl_idname: str) -> list[str]:
    """Sorted `.operation` values of every node of the given bl_idname in `ng`."""
    return sorted(n.operation for n in ng.nodes if n.bl_idname == bl_idname)
