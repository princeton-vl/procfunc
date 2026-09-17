import ast
import inspect

import bpy
import pytest
import shader_eval

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.util.bpy_node_info import NodeGroupType
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo

texture = pf.nodes.texture
pytestmark = pytest.mark.render


def test_checker_fac() -> None:
    vector = shader_eval.constant_vector(0.1, 0.1, 0.1)
    value = shader_eval.render(texture.checker(vector, scale=1.0).fac)
    shader_eval.assert_value(value, 0.0)


def test_checker_color() -> None:
    vector = shader_eval.constant_vector(0.1, 0.1, 0.1)
    node = texture.checker(
        vector, color1=pf.Color((1, 0, 0)), color2=pf.Color((0, 1, 0)), scale=1.0
    )
    shader_eval.assert_value(shader_eval.render(node.color), (0.0, 1.0, 0.0))


def test_gradient_fac() -> None:
    vector = shader_eval.constant_vector(0.25, 0.5, 0.75)
    value = shader_eval.render(texture.gradient(vector).fac)
    shader_eval.assert_value(value, 0.25)


def test_gradient_color() -> None:
    vector = shader_eval.constant_vector(0.25, 0.5, 0.75)
    value = shader_eval.render(texture.gradient(vector).color)
    shader_eval.assert_value(value, 0.25)


def test_noise_3d_origin() -> None:
    vector = shader_eval.constant_vector(0, 0, 0)
    value = shader_eval.render(texture.noise(vector, scale=1.0, detail=0.0).fac)
    shader_eval.assert_value(value, 0.5)


def test_noise_1d_origin() -> None:
    node = texture.noise(None, scale=1.0, detail=0.0, noise_dimensions="1D", w=0.0)
    shader_eval.assert_value(shader_eval.render(node.fac), 0.5)


def test_wave_origin() -> None:
    vector = shader_eval.constant_vector(0, 0, 0)
    value = shader_eval.render(texture.wave(vector, scale=1.0, detail=0.0).fac)
    shader_eval.assert_value(value, 0.0)


def test_voronoi_1d_returns_feature_w() -> None:
    result = texture.voronoi(
        None, scale=1.0, randomness=0.0, voronoi_dimensions="1D", w=0.75
    )
    assert result.position is None
    assert result.w is not None
    shader_eval.assert_value(shader_eval.render(result.w), 1.0)


def test_voronoi_smooth_1d_returns_feature_w() -> None:
    result = texture.voronoi_smooth_f1(
        None, scale=1.0, smoothness=0.0, randomness=0.0, voronoi_dimensions="1D", w=0.75
    )
    assert result.position is None
    assert result.w is not None
    shader_eval.assert_value(shader_eval.render(result.w), 1.0)


def test_image_returns_real_color_and_alpha() -> None:
    raw = bpy.data.images.new("shader_eval", 1, 1, alpha=True, float_buffer=True)
    raw.colorspace_settings.name = "Non-Color"
    raw.pixels.foreach_set((0.25, 0.5, 0.75, 0.4))
    raw.update()
    image = pf.Image(raw)

    result = texture.image((0.5, 0.5, 0), image)
    shader_eval.assert_value(shader_eval.render(result.color), (0.25, 0.5, 0.75))
    shader_eval.assert_value(shader_eval.render(result.fac), 0.4)


_SKY_FUNCTIONS = {
    "PREETHAM": "sky_texture_preetham",
    "HOSEK_WILKIE": "sky_texture_hosek_wilkie",
    "NISHITA": "sky_texture_nishita",
}

_SKY_PARAMETERS = {
    "sky_texture_preetham": ["vector", "sun_direction", "turbidity"],
    "sky_texture_hosek_wilkie": [
        "vector",
        "ground_albedo",
        "sun_direction",
        "turbidity",
    ],
    "sky_texture_nishita": [
        "vector",
        "air_density",
        "altitude",
        "dust_density",
        "ozone_density",
        "sun_disc",
        "sun_elevation",
        "sun_intensity",
        "sun_rotation",
        "sun_size",
    ],
}
_NISHITA_SUN_PARAMETERS = (
    "sun_elevation",
    "sun_intensity",
    "sun_rotation",
    "sun_size",
)
_NISHITA_SUN_DEFAULTS = {
    "sun_elevation": 0.261799,
    "sun_intensity": 1.0,
    "sun_rotation": 0.0,
    "sun_size": 0.009512,
}


def _native_sky_tree(sky_type: str, sun_disc: bool) -> bpy.types.NodeTree:
    tree = bpy.data.node_groups.new("_native_sky", "ShaderNodeTree")
    tree.interface.new_socket("Vector", in_out="INPUT", socket_type="NodeSocketVector")
    tree.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    group_input = tree.nodes.new("NodeGroupInput")
    group_output = tree.nodes.new("NodeGroupOutput")
    sky = tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = sky_type
    sky.sun_disc = sun_disc
    sky.sun_direction = (0.1, 0.2, 0.9)
    sky.turbidity = 3.5
    sky.ground_albedo = 0.6
    sky.air_density = 1.1
    sky.altitude = 0.5
    sky.dust_density = 1.2
    sky.ozone_density = 1.3
    sky.sun_elevation = 0.4
    sky.sun_intensity = 1.4
    sky.sun_rotation = 0.3
    sky.sun_size = 0.02
    vector = sky.inputs.get("Vector")
    if vector is not None and vector.enabled:
        tree.links.new(group_input.outputs["Vector"], vector)
    tree.links.new(sky.outputs["Color"], group_output.inputs["Color"])
    return tree


def _transpile_sky(tree: bpy.types.NodeTree) -> str:
    graph, _ = parse_node_tree(tree, ParseMemo())
    source = to_python(graph, toplevel_as_maincall=False)
    ast.parse(source)
    return source


def _sky_call(source: str) -> ast.Call:
    calls = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr.startswith("sky_texture_")
    ]
    assert len(calls) == 1
    return calls[0]


def _rebuild_sky(source: str) -> bpy.types.Node:
    namespace: dict = {}
    exec(source, namespace)  # noqa: S102
    functions = [
        value
        for value in namespace.values()
        if callable(value) and hasattr(value, "__wrapped__")
    ]
    assert len(functions) == 1
    graph = pf.nodes.function_to_compute_graph(functions[0])
    tree = as_nodegroup(graph, NodeGroupType.SHADER)
    nodes = [node for node in tree.nodes if node.bl_idname == "ShaderNodeTexSky"]
    assert len(nodes) == 1
    return nodes[0]


@pytest.mark.parametrize(
    ("sky_type", "sun_disc"),
    [
        ("PREETHAM", False),
        ("HOSEK_WILKIE", False),
        ("NISHITA", True),
        ("NISHITA", False),
    ],
)
def test_sky_texture_modes_round_trip(sky_type: str, sun_disc: bool) -> None:
    source = _transpile_sky(_native_sky_tree(sky_type, sun_disc))
    call = _sky_call(source)
    function_name = _SKY_FUNCTIONS[sky_type]
    assert call.func.attr == function_name
    assert "sky_type=" not in source

    expected_parameters = set(_SKY_PARAMETERS[function_name])
    if sky_type == "NISHITA" and sun_disc:
        expected_parameters.remove("vector")
        expected_parameters.remove("sun_disc")
    if sky_type == "NISHITA" and not sun_disc:
        expected_parameters.difference_update(("sun_intensity", "sun_size"))
    assert {keyword.arg for keyword in call.keywords} == expected_parameters

    rebuilt = _rebuild_sky(source)
    assert rebuilt.sky_type == sky_type
    vector = rebuilt.inputs.get("Vector")
    assert (vector is not None and bool(vector.links)) is not (
        sky_type == "NISHITA" and sun_disc
    )
    if sky_type == "NISHITA":
        assert rebuilt.sun_disc is sun_disc
        assert rebuilt.air_density == pytest.approx(1.1)
        assert rebuilt.ground_albedo == pytest.approx(0.3)
        expected_sun = {
            "sun_elevation": 0.4,
            "sun_intensity": 1.4,
            "sun_rotation": 0.3,
            "sun_size": 0.02,
        }
        if not sun_disc:
            expected_sun.update(sun_intensity=1.0, sun_size=0.009512)
        for name, value in expected_sun.items():
            assert getattr(rebuilt, name) == pytest.approx(value)
        return
    assert rebuilt.sun_disc is True
    assert tuple(rebuilt.sun_direction) == pytest.approx((0.1, 0.2, 0.9))
    assert rebuilt.turbidity == pytest.approx(3.5)
    assert rebuilt.air_density == pytest.approx(1.0)
    if sky_type == "HOSEK_WILKIE":
        assert rebuilt.ground_albedo == pytest.approx(0.6)


@pytest.mark.parametrize(("function_name", "parameters"), _SKY_PARAMETERS.items())
def test_sky_texture_mode_signatures(function_name: str, parameters: list[str]) -> None:
    signature = inspect.signature(getattr(texture, function_name))
    assert list(signature.parameters) == parameters
    assert signature.parameters["vector"].default is None
    assert "sky_type" not in signature.parameters


def test_sky_texture_nishita_sun_parameters_default_to_none() -> None:
    signature = inspect.signature(texture.sky_texture_nishita)
    for parameter in _NISHITA_SUN_PARAMETERS:
        assert signature.parameters[parameter].default is None


@pytest.mark.parametrize("sun_disc", [True, False])
def test_sky_texture_nishita_fills_sun_defaults(sun_disc: bool) -> None:
    attrs = texture.sky_texture_nishita(sun_disc=sun_disc).item().attrs
    actual = {name: attrs[name] for name in _NISHITA_SUN_PARAMETERS}
    assert actual == _NISHITA_SUN_DEFAULTS


@pytest.mark.parametrize("parameter", ["sun_intensity", "sun_size"])
def test_sky_texture_nishita_rejects_sun_parameters_without_disc(
    parameter: str,
) -> None:
    with pytest.raises(ValueError, match=parameter):
        texture.sky_texture_nishita(sun_disc=False, **{parameter: 1.0})


def test_sky_texture_nishita_preserves_sun_position_without_disc() -> None:
    sky = texture.sky_texture_nishita(
        sun_disc=False, sun_elevation=0.4, sun_rotation=0.3
    )
    attrs = sky.item().attrs
    assert attrs["sun_disc"] is False
    assert attrs["sun_elevation"] == pytest.approx(0.4)
    assert attrs["sun_rotation"] == pytest.approx(0.3)


def test_sky_texture_replaces_combined_sky_function() -> None:
    assert not hasattr(texture, "sky")


def test_sky_texture_nishita_rejects_vector_with_sun_disc() -> None:
    with pytest.raises(ValueError, match="sun_disc=False"):
        texture.sky_texture_nishita((0.0, 0.0, 1.0))
