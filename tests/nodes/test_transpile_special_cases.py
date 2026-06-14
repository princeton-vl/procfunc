import ast
import uuid

import bpy

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.bpy_node_info import NodeGroupType
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo


def _shader_tree_with_hsv_ramp():
    tree = bpy.data.node_groups.new(f"ramp_{uuid.uuid4().hex[:8]}", "ShaderNodeTree")
    inp = tree.nodes.new("NodeGroupInput")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Fac", in_out="INPUT", socket_type="NodeSocketFloat")
    tree.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")

    ramp = tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.color_mode = "HSV"
    ramp.color_ramp.interpolation = "B_SPLINE"
    ramp.color_ramp.hue_interpolation = "CW"
    tree.links.new(inp.outputs["Fac"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], out.inputs["Color"])
    return tree


def test_transpile_color_ramp_preserves_color_mode():
    """A ColorRamp in HSV mode must transpile to color_ramp(..., mode="HSV"),
    not silently fall back to RGB interpolation on re-execution."""
    tree = _shader_tree_with_hsv_ramp()
    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    assert "mode='HSV'" in src
    assert "interpolation='B_SPLINE'" in src
    assert "hue_interpolation='CW'" in src


@pf.nodes.node_function
def _hsv_cw_ramp():
    return pf.nodes.color.color_ramp(
        fac=0.5,
        points=[(0.0, (1.0, 0.0, 0.0, 1.0)), (1.0, (0.0, 0.0, 1.0, 1.0))],
        mode="HSV",
        hue_interpolation="CW",
    ).color


def test_color_ramp_hue_interpolation_round_trips():
    graph = pf.nodes.function_to_compute_graph(_hsv_cw_ramp)
    ng = as_nodegroup(graph, NodeGroupType.SHADER)
    ramp = next(n for n in ng.nodes if n.bl_idname == "ShaderNodeValToRGB")
    assert ramp.color_ramp.color_mode == "HSV"
    assert ramp.color_ramp.hue_interpolation == "CW"


def test_transpile_color_ramp_default_mode_omitted():
    tree = bpy.data.node_groups.new(f"ramp_{uuid.uuid4().hex[:8]}", "ShaderNodeTree")
    inp = tree.nodes.new("NodeGroupInput")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Fac", in_out="INPUT", socket_type="NodeSocketFloat")
    tree.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    ramp = tree.nodes.new("ShaderNodeValToRGB")
    tree.links.new(inp.outputs["Fac"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], out.inputs["Color"])

    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    assert "mode=" not in src


def test_transpile_keyword_socket_name_emits_valid_python():
    """A socket named after a python keyword must be renamed, not emitted as
    a SyntaxError like `def f(lambda: ...)`."""
    tree = bpy.data.node_groups.new(f"kw_{uuid.uuid4().hex[:8]}", "GeometryNodeTree")
    inp = tree.nodes.new("NodeGroupInput")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Lambda", in_out="INPUT", socket_type="NodeSocketFloat")
    tree.interface.new_socket("Value", in_out="OUTPUT", socket_type="NodeSocketFloat")

    add = tree.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    tree.links.new(inp.outputs["Lambda"], add.inputs[0])
    tree.links.new(add.outputs[0], out.inputs["Value"])

    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    ast.parse(src)
    assert "lambda_" in src
