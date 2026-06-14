"""Multi-input link order round-trip: joining three distinguishable geometries
must preserve order through transpile + re-execute. Pins the contract that
connect_multisocket_input's connect-time reversal matches bpy's (undocumented,
descending) multi_input_sort_id link ordering."""

import bpy
import numpy as np

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.bpy_node_info import NodeGroupType
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo

_SIZES = [1.0, 2.0, 3.0]


def _build_native(sizes: list[float]):
    ng = bpy.data.node_groups.new("_native_join_order", "GeometryNodeTree")
    ng.interface.new_socket(
        "Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )
    gout = ng.nodes.new("NodeGroupOutput")
    join = ng.nodes.new("GeometryNodeJoinGeometry")

    for size in sizes:
        cube = ng.nodes.new("GeometryNodeMeshCube")
        cube.inputs["Size"].default_value = (size, size, size)
        ng.links.new(cube.outputs["Mesh"], join.inputs["Geometry"])

    ng.links.new(join.outputs["Geometry"], gout.inputs["Geometry"])
    return ng


def _transpile_reexecute(native_ng):
    graph, _ = parse_node_tree(native_ng, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    ns: dict = {}
    exec(src, ns)  # noqa: S102
    fns = [v for v in ns.values() if callable(v) and hasattr(v, "__wrapped__")]
    assert len(fns) == 1, f"expected one generated function, got {len(fns)}"
    subgraph = pf.nodes.function_to_compute_graph(fns[0])
    return as_nodegroup(subgraph, NodeGroupType.GEOMETRY)


def _eval_verts(node_group) -> np.ndarray:
    obj = pf.ops.primitives.mesh.mesh_plane()
    pf.ops.modifier.modify(obj, "NODES", node_group=node_group)
    return pf.ops.attr.vertex_positions(obj)


def _join_link_sizes(ng) -> list[float]:
    """Cube sizes feeding the join node's multi-input socket, in bpy's
    evaluation order (descending multi_input_sort_id)."""
    join = next(n for n in ng.nodes if n.bl_idname == "GeometryNodeJoinGeometry")
    links = [link for link in ng.links if link.to_socket == join.inputs["Geometry"]]
    links.sort(key=lambda link: -link.multi_input_sort_id)
    return [link.from_node.inputs["Size"].default_value[0] for link in links]


def test_multiinput_join_order_roundtrips():
    native_ng = _build_native(_SIZES)
    native_verts = _eval_verts(native_ng)

    # sensitivity: the same cubes joined in reverse order concatenate their
    # vertices differently, so an order swap cannot pass the allclose below.
    reversed_ng = _build_native(list(reversed(_SIZES)))
    reversed_verts = _eval_verts(reversed_ng)
    assert native_verts.shape == reversed_verts.shape
    assert not np.allclose(native_verts, reversed_verts, atol=1e-5)

    reexec_ng = _transpile_reexecute(native_ng)
    reexec_verts = _eval_verts(reexec_ng)

    assert _join_link_sizes(reexec_ng) == _join_link_sizes(native_ng)
    assert np.allclose(native_verts, reexec_verts, atol=1e-5)
