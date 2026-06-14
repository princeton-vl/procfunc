"""VectorRotate transpile round-trip: a native ShaderNodeVectorRotate, applied to
a non-symmetric mesh, must produce geometry identical to its transpiled+re-executed
form for every rotation_type. Guards the per-axis CombineXYZ folding and the
AXIS_ANGLE/EULER_XYZ socket-passthrough special cases."""

import bpy
import numpy as np
import pytest

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.bpy_node_info import NodeGroupType
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo

# non-trivial, non-axis-aligned params so a dropped/wrong rotation moves vertices
_ANGLE = 0.7
_AXIS = (0.3, 0.5, 0.8)
_EULER = (0.4, 0.6, 0.8)


def _build_native(rotation_type: str):
    ng = bpy.data.node_groups.new(f"_native_{rotation_type}", "GeometryNodeTree")
    ng.interface.new_socket(
        "Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    ng.interface.new_socket(
        "Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )

    gin = ng.nodes.new("NodeGroupInput")
    gout = ng.nodes.new("NodeGroupOutput")
    pos = ng.nodes.new("GeometryNodeInputPosition")
    rot = ng.nodes.new("ShaderNodeVectorRotate")
    set_pos = ng.nodes.new("GeometryNodeSetPosition")

    rot.rotation_type = rotation_type
    if rotation_type in ("X_AXIS", "Y_AXIS", "Z_AXIS"):
        rot.inputs["Angle"].default_value = _ANGLE
    elif rotation_type == "AXIS_ANGLE":
        rot.inputs["Axis"].default_value = _AXIS
        rot.inputs["Angle"].default_value = _ANGLE
    else:  # EULER_XYZ
        rot.inputs["Rotation"].default_value = _EULER

    ng.links.new(pos.outputs["Position"], rot.inputs["Vector"])
    ng.links.new(gin.outputs["Geometry"], set_pos.inputs["Geometry"])
    ng.links.new(rot.outputs["Vector"], set_pos.inputs["Position"])
    ng.links.new(set_pos.outputs["Geometry"], gout.inputs["Geometry"])
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
    obj = pf.ops.primitives.mesh.mesh_monkey()
    # apply the geonode group so vertex_positions reads the realized mesh
    pf.ops.modifier.modify(obj, "NODES", node_group=node_group)
    return pf.ops.attr.vertex_positions(obj)


def _monkey_verts() -> np.ndarray:
    return pf.ops.attr.vertex_positions(pf.ops.primitives.mesh.mesh_monkey())


@pytest.mark.parametrize(
    "rotation_type", ["X_AXIS", "Y_AXIS", "Z_AXIS", "EULER_XYZ", "AXIS_ANGLE"]
)
def test_vector_rotate_transpile_roundtrip(rotation_type):
    native_ng = _build_native(rotation_type)
    native_verts = _eval_verts(native_ng)

    reexec_ng = _transpile_reexecute(native_ng)
    reexec_verts = _eval_verts(reexec_ng)

    # sensitivity: the rotate must actually move vertices off the input mesh,
    # otherwise allclose would pass trivially on two unrotated monkeys.
    assert not np.allclose(native_verts, _monkey_verts(), atol=1e-5)

    assert np.allclose(native_verts, reexec_verts, atol=1e-5)
