import ast

import bpy
import pytest

import procfunc as pf
from conftest import realize as _realize
from procfunc.codegen import to_python
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.util.bpy_node_info import NodeGroupType
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo


def _single_node(tree, bl_idname):
    nodes = [node for node in tree.nodes if node.bl_idname == bl_idname]
    assert len(nodes) == 1
    return nodes[0]


def _transpile_node(bl_idname, attr_name, attr_value, input_name, input_value):
    tree = bpy.data.node_groups.new(f"_native_{bl_idname}", "GeometryNodeTree")
    tree.interface.new_socket(
        "Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )
    output = tree.nodes.new("NodeGroupOutput")
    node = tree.nodes.new(bl_idname)
    setattr(node, attr_name, attr_value)
    node.inputs[input_name].default_value = input_value
    tree.links.new(node.outputs[0], output.inputs[0])

    graph, _ = parse_node_tree(tree, ParseMemo())
    source = to_python(graph, toplevel_as_maincall=False)
    ast.parse(source)
    namespace = {}
    exec(source, namespace)  # noqa: S102
    functions = [
        value
        for value in namespace.values()
        if callable(value) and hasattr(value, "__wrapped__")
    ]
    assert len(functions) == 1
    subgraph = pf.nodes.function_to_compute_graph(functions[0])
    realized = as_nodegroup(subgraph, NodeGroupType.GEOMETRY)
    return source, _single_node(realized, bl_idname)


@pytest.mark.parametrize(
    ("kwargs", "mode", "socket_name", "socket_value"),
    [
        ({}, "GRID", None, None),
        ({"voxel_amount": 24.0}, "VOXEL_AMOUNT", "Voxel Amount", 24.0),
        ({"voxel_size": 0.25}, "VOXEL_SIZE", "Voxel Size", 0.25),
    ],
)
def test_volume_to_mesh_derives_resolution_mode(
    kwargs, mode, socket_name, socket_value
):
    tree = _realize(
        lambda: pf.nodes.geo.volume_to_mesh(None, **kwargs), NodeGroupType.GEOMETRY
    )
    node = _single_node(tree, "GeometryNodeVolumeToMesh")
    assert node.resolution_mode == mode
    if socket_name is not None:
        assert node.inputs[socket_name].default_value == pytest.approx(socket_value)


def test_volume_to_mesh_rejects_both_resolution_inputs():
    with pytest.raises(ValueError, match="both voxel_amount and voxel_size"):
        pf.nodes.geo.volume_to_mesh(None, voxel_amount=24.0, voxel_size=0.25)


@pytest.mark.parametrize("overflow", ["SCALE_TO_FIT", "TRUNCATE"])
def test_string_to_curves_accepts_text_box_height(overflow):
    tree = _realize(
        lambda: (
            pf.nodes.geo.string_to_curves(
                "hello", overflow=overflow, text_box_height=2.5
            ).curve_instances
        ),
        NodeGroupType.GEOMETRY,
    )
    node = _single_node(tree, "GeometryNodeStringToCurves")
    assert node.overflow == overflow
    assert node.inputs["Text Box Height"].default_value == pytest.approx(2.5)


def test_string_to_curves_rejects_height_for_overflow():
    with pytest.raises(ValueError, match="text_box_height"):
        pf.nodes.geo.string_to_curves("hello", text_box_height=2.5)


def test_volume_to_mesh_resolution_mode_round_trips():
    source, node = _transpile_node(
        "GeometryNodeVolumeToMesh",
        "resolution_mode",
        "VOXEL_AMOUNT",
        "Voxel Amount",
        24.0,
    )
    assert "resolution_mode" not in source
    assert "voxel_amount=24.0" in source
    assert node.resolution_mode == "VOXEL_AMOUNT"


def test_string_to_curves_text_box_height_round_trips():
    source, node = _transpile_node(
        "GeometryNodeStringToCurves",
        "overflow",
        "SCALE_TO_FIT",
        "Text Box Height",
        2.5,
    )
    assert "text_box_height=2.5" in source
    assert node.overflow == "SCALE_TO_FIT"
    assert node.inputs["Text Box Height"].default_value == pytest.approx(2.5)
