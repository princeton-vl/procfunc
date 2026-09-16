import bpy
import shader_eval

import procfunc as pf

texture = pf.nodes.texture


def test_checker_fac() -> None:
    vector = pf.nodes.math.combine_xyz(0.1, 0.1, 0.1)
    value = shader_eval.render(texture.checker(vector, scale=1.0).fac)
    shader_eval.assert_value(value, 0.0)


def test_checker_color() -> None:
    vector = pf.nodes.math.combine_xyz(0.1, 0.1, 0.1)
    node = texture.checker(
        vector, color1=pf.Color((1, 0, 0)), color2=pf.Color((0, 1, 0)), scale=1.0
    )
    shader_eval.assert_value(shader_eval.render(node.color), (0.0, 1.0, 0.0))


def test_gradient_fac() -> None:
    vector = pf.nodes.math.combine_xyz(0.25, 0.5, 0.75)
    value = shader_eval.render(texture.gradient(vector).fac)
    shader_eval.assert_value(value, 0.25)


def test_gradient_color() -> None:
    vector = pf.nodes.math.combine_xyz(0.25, 0.5, 0.75)
    value = shader_eval.render(texture.gradient(vector).color)
    shader_eval.assert_value(value, 0.25)


def test_noise_3d_origin() -> None:
    vector = pf.nodes.math.combine_xyz(0, 0, 0)
    value = shader_eval.render(texture.noise(vector, scale=1.0, detail=0.0).fac)
    shader_eval.assert_value(value, 0.5)


def test_noise_1d_origin() -> None:
    node = texture.noise(None, scale=1.0, detail=0.0, noise_dimensions="1D", w=0.0)
    shader_eval.assert_value(shader_eval.render(node.fac), 0.5)


def test_wave_origin() -> None:
    vector = pf.nodes.math.combine_xyz(0, 0, 0)
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
