import pytest
import shader_eval

import procfunc as pf

shader = pf.nodes.shader


def test_render_color_passthrough() -> None:
    value = shader_eval.render(pf.nodes.math.constant(pf.Color((0.25, 0.5, 0.75))))
    shader_eval.assert_value(value, (0.25, 0.5, 0.75))


def test_render_float_passthrough() -> None:
    value = shader_eval.render(pf.nodes.math.constant(-0.5))
    shader_eval.assert_value(value, -0.5)


@pytest.mark.parametrize("engine", [shader_eval.CYCLES, shader_eval.EEVEE])
def test_render_vector_passthrough(engine: str) -> None:
    value = shader_eval.render(
        pf.nodes.math.constant(pf.Vector((-1.25, 0.5, 2.5))), engine=engine
    )
    shader_eval.assert_value(value, (-1.25, 0.5, 2.5))


def test_render_sequential_calls_are_independent() -> None:
    red = shader_eval.render(pf.nodes.math.constant(pf.Color((1.0, 0.0, 0.0))))
    green = shader_eval.render(pf.nodes.math.constant(pf.Color((0.0, 1.0, 0.0))))
    blue = shader_eval.render(pf.nodes.math.constant(pf.Color((0.0, 0.0, 1.0))))
    shader_eval.assert_value(red, (1.0, 0.0, 0.0))
    shader_eval.assert_value(green, (0.0, 1.0, 0.0))
    shader_eval.assert_value(blue, (0.0, 0.0, 1.0))


def test_invert() -> None:
    value = shader_eval.render(
        shader.invert(fac=1.0, color=pf.Color((0.25, 0.5, 0.75)))
    )
    shader_eval.assert_value(value, (0.75, 0.5, 0.25))


def test_fresnel() -> None:
    value = shader_eval.render(shader.fresnel(ior=1.5, normal=(0, 0, 1)))
    shader_eval.assert_value(value, 0.04)


def test_layer_weight_facing() -> None:
    value = shader_eval.render(shader.layer_weight(blend=0.5, normal=(0, 0, 1)).facing)
    shader_eval.assert_value(value, 0.0)


def test_light_path_is_camera_ray() -> None:
    value = shader_eval.render(shader.light_path().is_camera_ray)
    shader_eval.assert_value(value, 1.0)


def test_normal_output() -> None:
    value = shader_eval.render(shader.normal((0.6, 0.8, 0)).normal)
    shader_eval.assert_value(value, (0.0, 0.0, 1.0))


def test_normal_dot() -> None:
    value = shader_eval.render(shader.normal((0.6, 0.8, 0)).dot)
    shader_eval.assert_value(value, 0.0)


def test_normal_map() -> None:
    node = shader.normal_map(
        strength=1.0, color=pf.Color((0.5, 0.5, 1.0)), space="OBJECT"
    )
    shader_eval.assert_value(shader_eval.render(node), (0.0, 0.0, 1.0))


def test_squeeze() -> None:
    value = shader_eval.render(
        shader.squeeze(value=0.0, width=1.0, center=0.0), engine=shader_eval.EEVEE
    )
    shader_eval.assert_value(value, 0.5)


def test_displacement() -> None:
    node = shader.displacement(height=0.75, midlevel=0.25, scale=0.5, normal=(0, 0, 1))
    shader_eval.assert_value(shader_eval.render(node), (0.0, 0.0, 0.25))


def test_vector_displacement() -> None:
    node = shader.vector_displacement(
        vector=pf.Color((0.75, 0.5, 0.25)), midlevel=0.5, scale=2.0, space="OBJECT"
    )
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.0, -0.5))


def test_geometry_normal() -> None:
    value = shader_eval.render(shader.geometry().normal)
    shader_eval.assert_value(value, (0.0, 0.0, 1.0))


def test_object_info_location() -> None:
    value = shader_eval.render(shader.object_info().location)
    shader_eval.assert_value(value, (0.0, 0.0, 0.0))


def test_wireframe_face_interior() -> None:
    value = shader_eval.render(shader.wireframe(size=0.01))
    shader_eval.assert_value(value, 0.0)


def test_mapping_point_applies_location() -> None:
    node = shader.mapping((0.1, 0.2, 0.3), location=(0.2, 0.3, 0.4), scale=(2, 2, 2))
    shader_eval.assert_value(shader_eval.render(node), (0.4, 0.7, 1.0))


def test_mapping_texture_inverts_transform() -> None:
    node = shader.mapping_texture(
        (0.4, 0.7, 1.0), location=(0.2, 0.3, 0.4), scale=(2, 2, 2)
    )
    shader_eval.assert_value(shader_eval.render(node), (0.1, 0.2, 0.3))


def test_mapping_vector_scales_without_location() -> None:
    node = shader.mapping_vector((0.1, 0.2, 0.3), scale=(2, 2, 2))
    shader_eval.assert_value(shader_eval.render(node), (0.2, 0.4, 0.6))


def test_mapping_normal_renormalizes() -> None:
    node = shader.mapping_normal((0.25, 0.5, 0.75))
    shader_eval.assert_value(shader_eval.render(node), (0.267261, 0.534522, 0.801784))


def test_wavelength_500nm_is_green_cyan() -> None:
    value = shader_eval.probe(shader_eval.render(shader.wavelength(500.0)))
    assert value[1] > value[0]
    assert value[1] > value[2]
    assert value[1] > 0.2
