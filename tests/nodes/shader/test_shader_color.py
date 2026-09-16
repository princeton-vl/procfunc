import shader_eval

import procfunc as pf

color = pf.nodes.color


def test_mix_rgb() -> None:
    node = color.mix_rgb(0.25, pf.Color((1, 0, 0)), pf.Color((0, 1, 0)))
    shader_eval.assert_value(shader_eval.render(node), (0.75, 0.25, 0.0))


def test_rgb_curve_identity() -> None:
    node = color.rgb_curve(1.0, pf.Color((0.25, 0.5, 0.75)))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_combine_rgb() -> None:
    value = shader_eval.render(color.combine_rgb(0.25, 0.5, 0.75))
    shader_eval.assert_value(value, (0.25, 0.5, 0.75))


def test_combine_hsv() -> None:
    value = shader_eval.render(color.combine_hsv(0.0, 1.0, 1.0))
    shader_eval.assert_value(value, (1.0, 0.0, 0.0))


def test_combine_hsl() -> None:
    value = shader_eval.render(color.combine_hsl(0.0, 1.0, 0.5))
    shader_eval.assert_value(value, (1.0, 0.0, 0.0))


def test_color_ramp_color() -> None:
    value = shader_eval.render(color.color_ramp(0.25).color)
    shader_eval.assert_value(value, 0.25)


def test_color_ramp_alpha() -> None:
    value = shader_eval.render(color.color_ramp(0.25).alpha)
    shader_eval.assert_value(value, 1.0)


def test_bright_contrast() -> None:
    node = color.bright_contrast(pf.Color((0.5, 0.5, 0.5)), bright=0.25)
    shader_eval.assert_value(shader_eval.render(node), 0.75)


def test_gamma() -> None:
    node = color.gamma(pf.Color((0.25, 0.5, 0.75)), 2.0)
    shader_eval.assert_value(shader_eval.render(node), (0.0625, 0.25, 0.5625))


def test_hue_saturation() -> None:
    node = color.hue_saturation(pf.Color((1, 0, 0)), fac=1.0, value=0.5)
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.0, 0.0))


def test_rgb_to_bw() -> None:
    value = shader_eval.render(color.rgb_to_bw(pf.Color((1, 0, 0))))
    shader_eval.assert_value(value, 0.2126)


def test_separate_rgb_returns_real_channels() -> None:
    result = color.separate_rgb(pf.Color((0.25, 0.5, 0.75)))
    assert result._fields == ("red", "green", "blue", "alpha")
    node = color.combine_rgb(result.red, result.green, result.blue)
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_separate_hsv_returns_hue_saturation_value() -> None:
    result = color.separate_hsv(pf.Color((1, 0, 0)))
    assert result._fields == ("hue", "saturation", "value", "alpha")
    node = pf.nodes.math.combine_xyz(result.hue, result.saturation, result.value)
    shader_eval.assert_value(shader_eval.render(node), (0.0, 1.0, 1.0))


def test_separate_hsl_returns_hue_saturation_lightness() -> None:
    result = color.separate_hsl(pf.Color((1, 0, 0)))
    assert result._fields == ("hue", "saturation", "lightness", "alpha")
    node = pf.nodes.math.combine_xyz(result.hue, result.saturation, result.lightness)
    shader_eval.assert_value(shader_eval.render(node), (0.0, 1.0, 0.5))


def test_blackbody_has_warm_daylight_channels() -> None:
    value = shader_eval.render(color.blackbody(6500.0))
    assert 0.95 <= value[0] <= 1.05
    assert 0.9 <= value[1] <= 1.0
    assert 0.9 <= value[2] <= 1.05
