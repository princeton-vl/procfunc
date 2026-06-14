"""Matrix socket round-trips: a GeometryNodeTransform in MATRIX mode (fed by
CombineMatrix constants or by a NodeSocketMatrix group input) must transpile to
parseable source and re-execute to numerically identical geometry. Guards the
NodeSocketMatrix/NodeSocketImage rows in SOCKET_CLASS_TO_DATATYPE."""

import ast

import bpy
import numpy as np

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes import bpy_node_info as bni
from procfunc.nodes.bpy_node_info import NodeGroupType
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo

_TRANSLATION = (0.1, 2.0, 3.0)


def _new_transform_tree(name: str):
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket(
        "Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    ng.interface.new_socket(
        "Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )
    gin = ng.nodes.new("NodeGroupInput")
    gout = ng.nodes.new("NodeGroupOutput")
    transform = ng.nodes.new("GeometryNodeTransform")
    transform.mode = "MATRIX"
    ng.links.new(gin.outputs["Geometry"], transform.inputs["Geometry"])
    ng.links.new(transform.outputs["Geometry"], gout.inputs["Geometry"])
    return ng, gin, transform


def _transpile_source(native_ng) -> str:
    graph, _ = parse_node_tree(native_ng, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    ast.parse(src)
    return src


def _reexecute(src: str):
    ns: dict = {}
    exec(src, ns)  # noqa: S102
    fns = [v for v in ns.values() if callable(v) and hasattr(v, "__wrapped__")]
    assert len(fns) == 1, f"expected one generated function, got {len(fns)}"
    subgraph = pf.nodes.function_to_compute_graph(fns[0])
    return as_nodegroup(subgraph, NodeGroupType.GEOMETRY)


def _eval_verts(node_group) -> np.ndarray:
    obj = pf.ops.primitives.mesh.mesh_monkey()
    pf.ops.modifier.modify(obj, "NODES", node_group=node_group)
    return pf.ops.attr.vertex_positions(obj)


def test_matrix_value_transpile_roundtrip():
    """Constant matrix (CombineMatrix -> Transform) survives transpile +
    re-execute, and the matrix values land numerically on the geometry."""
    ng, _, transform = _new_transform_tree("_native_matrix_const")
    combine = ng.nodes.new("FunctionNodeCombineMatrix")
    for i, val in enumerate(_TRANSLATION):
        combine.inputs[f"Column 4 Row {i + 1}"].default_value = val
    ng.links.new(combine.outputs["Matrix"], transform.inputs["Transform"])

    native_verts = _eval_verts(ng)
    monkey_verts = pf.ops.attr.vertex_positions(pf.ops.primitives.mesh.mesh_monkey())

    # the matrix translation must land exactly on the native geometry
    assert np.allclose(native_verts, monkey_verts + np.array(_TRANSLATION), atol=1e-5)

    reexec_ng = _reexecute(_transpile_source(ng))
    reexec_verts = _eval_verts(reexec_ng)
    assert np.allclose(native_verts, reexec_verts, atol=1e-5)


def test_matrix_interface_input_roundtrip():
    """A NodeSocketMatrix group input transpiles to a pf.Matrix-typed parameter
    (previously KeyError: 'NodeSocketMatrix') and re-executes to a MATRIX
    interface socket."""
    ng, gin, transform = _new_transform_tree("_native_matrix_input")
    ng.interface.new_socket("Transform", in_out="INPUT", socket_type="NodeSocketMatrix")
    ng.links.new(gin.outputs["Transform"], transform.inputs["Transform"])

    src = _transpile_source(ng)
    assert "t.SocketOrVal[pf.Matrix]" in src

    reexec_ng = _reexecute(src)
    socket_types = {
        s.name: s.socket_type
        for s in reexec_ng.interface.items_tree
        if s.in_out == "INPUT"
    }
    assert socket_types["transform"] == "NodeSocketMatrix"


@pf.nodes.node_function
def _switch_between_matrices(geo: pf.ProcNode[pf.MeshObject]) -> pf.ProcNode:
    identity = pf.nodes.func.combine_matrix()
    translated = pf.nodes.func.combine_matrix(
        column_4_row_1=_TRANSLATION[0],
        column_4_row_2=_TRANSLATION[1],
        column_4_row_3=_TRANSLATION[2],
    )
    chosen = pf.nodes.func.switch(switch=True, a=identity, b=translated)
    return pf.nodes.geo.transform_by_matrix(geo, matrix=chosen)


def test_switch_matrix_data_type_inference():
    """Runtime data-type inference on matrix operands resolves Switch to MATRIX
    (previously bare KeyError: 'NodeSocketMatrix')."""
    graph = pf.nodes.function_to_compute_graph(_switch_between_matrices)
    ng = as_nodegroup(graph, NodeGroupType.GEOMETRY)
    switches = [n for n in ng.nodes if n.bl_idname == "GeometryNodeSwitch"]
    assert [n.input_type for n in switches] == ["MATRIX"]


@pf.nodes.node_function
def _transform_by_constant_ndarray(geo: pf.ProcNode[pf.MeshObject]) -> pf.ProcNode:
    matrix = np.eye(4)
    matrix[:3, 3] = _TRANSLATION
    return pf.nodes.geo.transform_by_matrix(geo, matrix=matrix)


def test_constant_matrix_lowers_to_combine_matrix():
    """A constant 4x4 ndarray fed to a MATRIX socket (which has no
    default_value in bpy 4.2) lowers to a column-major CombineMatrix node and
    transforms geometry exactly."""
    graph = pf.nodes.function_to_compute_graph(_transform_by_constant_ndarray)
    ng = as_nodegroup(graph, NodeGroupType.GEOMETRY)

    combine = next(n for n in ng.nodes if n.bl_idname == "FunctionNodeCombineMatrix")
    for i, val in enumerate(_TRANSLATION):
        socket_val = combine.inputs[f"Column 4 Row {i + 1}"].default_value
        assert abs(socket_val - val) < 1e-6
    assert combine.outputs["Matrix"].is_linked

    verts = _eval_verts(ng)
    monkey_verts = pf.ops.attr.vertex_positions(pf.ops.primitives.mesh.mesh_monkey())
    assert np.allclose(verts, monkey_verts + np.array(_TRANSLATION), atol=1e-5)


def test_constant_matrix_transpile_roundtrip():
    """The lowered constant-matrix group transpiles and re-executes to
    numerically identical geometry."""
    graph = pf.nodes.function_to_compute_graph(_transform_by_constant_ndarray)
    ng = as_nodegroup(graph, NodeGroupType.GEOMETRY)

    reexec_ng = _reexecute(_transpile_source(ng))
    assert np.allclose(_eval_verts(ng), _eval_verts(reexec_ng), atol=1e-5)


def test_socket_class_datatype_rows():
    assert (
        bni.SOCKET_CLASS_TO_DATATYPE["NodeSocketMatrix"]
        is bni.NodeDataType.FLOAT_MATRIX
    )
    assert bni.SOCKET_CLASS_TO_DATATYPE["NodeSocketImage"] is bni.NodeDataType.IMAGE
