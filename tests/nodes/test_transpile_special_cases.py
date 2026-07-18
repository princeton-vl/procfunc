import ast
import inspect
import uuid

import bpy

import procfunc as pf
from procfunc import types as pt
from procfunc.codegen import to_python
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.util.bpy_node_info import NodeGroupType
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo, parse_material
from procfunc.transpiler.main import transpile_targets


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


def test_transpile_1d_noise_supplies_vector_none():
    """A 1D texture node disables its Vector input socket. The binding still
    requires `vector`, so codegen must emit vector=None - omitting it produces
    a call missing a required positional argument."""
    tree = bpy.data.node_groups.new(f"noise1d_{uuid.uuid4().hex[:8]}", "ShaderNodeTree")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Fac", in_out="OUTPUT", socket_type="NodeSocketFloat")

    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "1D"
    tree.links.new(noise.outputs["Fac"], out.inputs["Fac"])

    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    assert "noise_dimensions='1D'" in src
    assert "vector=None" in src
    exec(compile(src, "<noise1d>", "exec"), {})  # noqa: S102


def test_transpile_1d_white_noise_round_trips():
    tree = bpy.data.node_groups.new(f"white1d_{uuid.uuid4().hex[:8]}", "ShaderNodeTree")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Fac", in_out="OUTPUT", socket_type="NodeSocketFloat")

    white = tree.nodes.new("ShaderNodeTexWhiteNoise")
    white.noise_dimensions = "1D"
    tree.links.new(white.outputs["Value"], out.inputs["Fac"])

    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    assert "noise_dimensions='1D'" in src
    exec(compile(src, "<white1d>", "exec"), {})  # noqa: S102


def test_transpile_dangling_reroute_resolves_to_default():
    """A reroute whose input is unconnected but whose output is wired downstream
    must resolve to its input socket's default (how blender evaluates it), not
    raise."""
    tree = bpy.data.node_groups.new(f"reroute_{uuid.uuid4().hex[:8]}", "ShaderNodeTree")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Value", in_out="OUTPUT", socket_type="NodeSocketFloat")

    reroute = tree.nodes.new("NodeReroute")
    tree.links.new(reroute.outputs[0], out.inputs["Value"])
    reroute.inputs[0].default_value = 0.25

    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    assert "0.25" in src
    exec(compile(src, "<reroute>", "exec"), {})  # noqa: S102


def test_transpile_multi_output_selects_named_socket():
    """A node whose procfunc function returns a namedtuple of outputs (e.g.
    attribute_domain_size) must select the wired output by name, even when the
    source node's component/mode disables all but one output socket - so the
    active-socket count is 1. Dropping the selection would emit
    `attribute_domain_size.astype(...)` on the whole result instead of
    `attribute_domain_size.point_count.astype(...)`."""
    tree = bpy.data.node_groups.new(f"dsz_{uuid.uuid4().hex[:8]}", "GeometryNodeTree")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Value", in_out="OUTPUT", socket_type="NodeSocketFloat")

    dsz = tree.nodes.new("GeometryNodeAttributeDomainSize")
    dsz.component = "POINTCLOUD"  # gates every output socket off except Point Count
    math = tree.nodes.new("ShaderNodeMath")
    math.operation = "ADD"
    point_count = next(s for s in dsz.outputs if s.name == "Point Count")
    tree.links.new(point_count, math.inputs[0])
    tree.links.new(math.outputs[0], out.inputs["Value"])

    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    ast.parse(src)
    assert "attribute_domain_size.point_count" in src
    exec(compile(src, "<domain_size>", "exec"), {})  # noqa: S102


def test_transpile_geometry_input_socket_defaults_to_none():
    """An interface input socket with no synthesizable scalar default (geometry,
    left unconnected in v1) must become an optional param (= None), not a
    required one - else the transpiled function raises TypeError when called
    without it."""
    tree = bpy.data.node_groups.new(f"grp_{uuid.uuid4().hex[:8]}", "GeometryNodeTree")
    inp = tree.nodes.new("NodeGroupInput")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Geo", in_out="INPUT", socket_type="NodeSocketGeometry")
    tree.interface.new_socket(
        "Strecher Instance", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    tree.interface.new_socket("Geo", in_out="OUTPUT", socket_type="NodeSocketGeometry")

    # Wire only the first geometry input; leave Strecher Instance unconnected.
    join = tree.nodes.new("GeometryNodeJoinGeometry")
    tree.links.new(inp.outputs["Geo"], join.inputs[0])
    tree.links.new(join.outputs[0], out.inputs["Geo"])

    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    ast.parse(src)
    assert "strecher_instance: pf.ProcNode = None" in src

    ns: dict = {}
    exec(compile(src, "<geo_default>", "exec"), ns)  # noqa: S102
    fn = next(v for v in ns.values() if callable(v) and hasattr(v, "__wrapped__"))

    params = inspect.signature(fn.__wrapped__).parameters
    assert params["strecher_instance"].default is None


def test_transpile_material_unlinked_displacement_is_zero_procnode():
    """Unconnected Displacement transpiles to a zero-vector ProcNode, not None
    and not a raw tuple."""
    mat = bpy.data.materials.new(f"mat_{uuid.uuid4().hex[:8]}")
    mat.use_nodes = True
    graph = parse_material(mat, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    assert "displacement=None" not in src
    assert "displacement=(0.0, 0.0, 0.0)" not in src
    assert "pf.nodes.math.constant((0.0, 0.0, 0.0))" in src

    mat2 = bpy.data.materials.new(f"mat_{uuid.uuid4().hex[:8]}")
    mat2.use_nodes = True
    assert pt.is_zero_displacement(
        parse_material(mat2, ParseMemo()).outputs.obj().displacement
    )


def test_transpile_modulo_emits_named_call_not_percent():
    """Blender MODULO is truncated (fmod); Python % is floored. The transpiler
    must keep the named call so constant-folded negative operands don't flip sign."""

    tree = bpy.data.node_groups.new(f"mod_{uuid.uuid4().hex[:8]}", "GeometryNodeTree")
    inp = tree.nodes.new("NodeGroupInput")
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("A", in_out="INPUT", socket_type="NodeSocketFloat")
    tree.interface.new_socket("Value", in_out="OUTPUT", socket_type="NodeSocketFloat")

    mod = tree.nodes.new("ShaderNodeMath")
    mod.operation = "MODULO"
    mod.inputs[1].default_value = 3.0
    tree.links.new(inp.outputs["A"], mod.inputs[0])
    tree.links.new(mod.outputs[0], out.inputs["Value"])

    src = transpile_targets([tree], transforms=[])
    assert "math.modulo(" in src
    assert " % " not in src
