import math

import shader_eval

import procfunc as pf

node_math = pf.nodes.math


def test_clamp() -> None:
    value = shader_eval.render(node_math.clamp(1.5, min=0.25, max=0.75))
    shader_eval.assert_value(value, 0.75)


def test_add() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.add(0.25, 0.5)), 0.75)


def test_subtract() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.subtract(0.75, 0.25)), 0.5)


def test_multiply() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.multiply(0.5, 0.5)), 0.25)


def test_multiply_add() -> None:
    value = shader_eval.render(node_math.multiply_add(0.25, 0.5, 0.25))
    shader_eval.assert_value(value, 0.375)


def test_divide() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.divide(0.25, 0.5)), 0.5)


def test_power() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.power(0.5, 2.0)), 0.25)


def test_logarithm() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.logarithm(0.5, 0.25)), 0.5)


def test_sqrt() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.sqrt(0.25)), 0.5)


def test_inverse_sqrt() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.inverse_sqrt(4.0)), 0.5)


def test_absolute() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.absolute(-0.25)), 0.25)


def test_exponent() -> None:
    value = shader_eval.render(node_math.exponent(-math.log(2.0)))
    shader_eval.assert_value(value, 0.5)


def test_minimum() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.minimum(0.25, 0.75)), 0.25)


def test_maximum() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.maximum(0.25, 0.75)), 0.75)


def test_less_than() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.less_than(0.25, 0.75)), 1.0)


def test_greater_than() -> None:
    value = shader_eval.render(node_math.greater_than(0.25, 0.75))
    shader_eval.assert_value(value, 0.0)


def test_sign() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.sign(0.25)), 1.0)


def test_compare() -> None:
    value = shader_eval.render(node_math.compare(0.5, 0.5005, 0.001))
    shader_eval.assert_value(value, 1.0)


def test_smooth_minimum() -> None:
    value = shader_eval.render(node_math.smooth_minimum(0.25, 0.75))
    shader_eval.assert_value(value, 0.25)


def test_smooth_maximum() -> None:
    value = shader_eval.render(node_math.smooth_maximum(0.25, 0.75))
    shader_eval.assert_value(value, 0.75)


def test_round() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.round(0.6)), 1.0)


def test_floor() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.floor(1.75)), 1.0)


def test_ceil() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.ceil(0.25)), 1.0)


def test_truncate() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.truncate(1.75)), 1.0)


def test_fraction() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.fraction(1.25)), 0.25)


def test_modulo() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.modulo(1.25, 0.5)), 0.25)


def test_floor_mod() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.floor_mod(-0.25, 0.5)), 0.25)


def test_wrap() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.wrap(1.25)), 0.25)


def test_snap() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.snap(0.74, 0.25)), 0.5)


def test_pingpong() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.pingpong(1.25)), 0.75)


def test_sin() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.sin(math.pi / 6)), 0.5)


def test_cos() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.cos(math.pi / 3)), 0.5)


def test_tan() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.tan(math.atan(0.5))), 0.5)


def test_asin() -> None:
    value = shader_eval.render(node_math.asin(0.5))
    shader_eval.assert_value(value, math.asin(0.5))


def test_acos() -> None:
    value = shader_eval.render(node_math.acos(0.75))
    shader_eval.assert_value(value, math.acos(0.75))


def test_atan() -> None:
    value = shader_eval.render(node_math.atan(0.5))
    shader_eval.assert_value(value, math.atan(0.5))


def test_atan2() -> None:
    value = shader_eval.render(node_math.atan2(0.5, 1.0))
    shader_eval.assert_value(value, math.atan2(0.5, 1.0))


def test_sinh() -> None:
    value = shader_eval.render(node_math.sinh(0.25))
    shader_eval.assert_value(value, math.sinh(0.25))


def test_cosh() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.cosh(0.0)), 1.0)


def test_tanh() -> None:
    value = shader_eval.render(node_math.tanh(0.5))
    shader_eval.assert_value(value, math.tanh(0.5))


def test_deg_to_rad() -> None:
    value = shader_eval.render(node_math.deg_to_rad(30.0))
    shader_eval.assert_value(value, math.pi / 6)


def test_rad_to_deg() -> None:
    value = shader_eval.render(node_math.rad_to_deg(0.01))
    shader_eval.assert_value(value, math.degrees(0.01))


def test_mix() -> None:
    shader_eval.assert_value(shader_eval.render(node_math.mix(0.25, 0.75, 0.5)), 0.5)


def test_float_curve_identity() -> None:
    value = shader_eval.render(node_math.float_curve(1.0, 0.25))
    shader_eval.assert_value(value, 0.25)


def test_map_range() -> None:
    value = shader_eval.render(node_math.map_range(0.25, to_min=0.2, to_max=0.6))
    shader_eval.assert_value(value, 0.3)


def test_map_range_stepped() -> None:
    value = shader_eval.render(node_math.map_range(0.3, interpolation_type="STEPPED"))
    shader_eval.assert_value(value, 0.25)


def test_map_range_stepped_steps() -> None:
    node = node_math.map_range(0.3, interpolation_type="STEPPED", steps=1.0)
    shader_eval.assert_value(shader_eval.render(node), 0.0)


def test_vector_add() -> None:
    node = node_math.vector_add((0.1, 0.2, 0.3), (0.2, 0.3, 0.4))
    shader_eval.assert_value(shader_eval.render(node), (0.3, 0.5, 0.7))


def test_vector_subtract() -> None:
    node = node_math.vector_subtract((0.7, 0.6, 0.5), (0.2, 0.1, 0.1))
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.5, 0.4))


def test_vector_multiply() -> None:
    node = node_math.vector_multiply((0.5, 0.5, 0.5), (0.5, 0.25, 0.75))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.125, 0.375))


def test_vector_multiply_add() -> None:
    node = node_math.vector_multiply_add(
        (0.25, 0.5, 0.75), (0.5, 0.5, 0.5), (0.25, 0.25, 0.25)
    )
    shader_eval.assert_value(shader_eval.render(node), (0.375, 0.5, 0.625))


def test_vector_divide() -> None:
    node = node_math.vector_divide((0.25, 0.5, 0.75), (0.5, 1.0, 1.0))
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.5, 0.75))


def test_vector_cross_product() -> None:
    node = node_math.vector_cross_product((1, 0, 0), (0, 1, 0))
    shader_eval.assert_value(shader_eval.render(node), (0.0, 0.0, 1.0))


def test_vector_project() -> None:
    node = node_math.vector_project((0.5, 0.5, 0), (1, 0, 0))
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.0, 0.0))


def test_vector_reflect() -> None:
    node = node_math.vector_reflect((0.25, -0.25, 0), (0, 1, 0))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.25, 0.0))


def test_vector_refract() -> None:
    node = node_math.vector_refract((0, 0, -1), (0, 0, 1))
    shader_eval.assert_value(shader_eval.render(node), (0.0, 0.0, -1.0))


def test_vector_faceforward() -> None:
    node = node_math.vector_faceforward((0.25, 0.5, 0.75), (0, 0, -1), (0, 0, 1))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_vector_dot_product() -> None:
    node = node_math.vector_dot_product((0.5, 0.5, 0), (0.5, 0.5, 0))
    shader_eval.assert_value(shader_eval.render(node), 0.5)


def test_vector_distance() -> None:
    node = node_math.vector_distance((0, 0, 0), (0.3, 0.4, 0))
    shader_eval.assert_value(shader_eval.render(node), 0.5)


def test_vector_length() -> None:
    node = node_math.vector_length((0.3, 0.4, 0))
    shader_eval.assert_value(shader_eval.render(node), 0.5)


def test_vector_scale() -> None:
    node = node_math.vector_scale((0.1, 0.2, 0.3), 2.0)
    shader_eval.assert_value(shader_eval.render(node), (0.2, 0.4, 0.6))


def test_vector_normalize() -> None:
    node = node_math.vector_normalize((0.3, 0.4, 0))
    shader_eval.assert_value(shader_eval.render(node), (0.6, 0.8, 0.0))


def test_vector_wrap() -> None:
    node = node_math.vector_wrap((1.25, 1.5, 1.75), (1, 1, 1), (0, 0, 0))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_vector_snap() -> None:
    node = node_math.vector_snap((0.74, 0.49, 0.26), (0.25, 0.25, 0.25))
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.25, 0.25))


def test_vector_floor() -> None:
    node = node_math.vector_floor((1.2, 0.9, 0.1))
    shader_eval.assert_value(shader_eval.render(node), (1.0, 0.0, 0.0))


def test_vector_ceil() -> None:
    node = node_math.vector_ceil((0.1, 0.0, 0.8))
    shader_eval.assert_value(shader_eval.render(node), (1.0, 0.0, 1.0))


def test_vector_modulo() -> None:
    node = node_math.vector_modulo((1.25, 1.5, 1.75), (1, 1, 1))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_vector_fraction() -> None:
    node = node_math.vector_fraction((1.25, 1.5, 1.75))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_vector_absolute() -> None:
    node = node_math.vector_absolute((-0.25, -0.5, 0.75))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_vector_minimum() -> None:
    node = node_math.vector_minimum((0.25, 0.75, 0.5), (0.5, 0.5, 0.75))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.5))


def test_vector_maximum() -> None:
    node = node_math.vector_maximum((0.25, 0.75, 0.5), (0.5, 0.5, 0.75))
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.75, 0.75))


def test_vector_sine() -> None:
    node = node_math.vector_sine((math.pi / 6, 0, math.pi / 2))
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.0, 1.0))


def test_vector_cosine() -> None:
    node = node_math.vector_cosine((math.pi / 3, math.pi / 2, 0))
    shader_eval.assert_value(shader_eval.render(node), (0.5, 0.0, 1.0))


def test_vector_tangent() -> None:
    node = node_math.vector_tangent((math.atan(0.25), math.atan(0.5), math.atan(0.75)))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_vector_rotate_axis_angle() -> None:
    node = node_math.vector_rotate_axis_angle(
        (0.5, 0, 0), axis=(0, 0, 1), angle=math.pi / 2
    )
    shader_eval.assert_value(shader_eval.render(node), (0.0, 0.5, 0.0))


def test_vector_rotate_euler() -> None:
    node = node_math.vector_rotate_euler((0.5, 0, 0), rotation=(0, 0, math.pi / 2))
    shader_eval.assert_value(shader_eval.render(node), (0.0, 0.5, 0.0))


def test_vector_transform() -> None:
    node = node_math.vector_transform(
        (0.25, 0.5, 0.75), convert_from="OBJECT", convert_to="WORLD"
    )
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_mix_vector() -> None:
    node = node_math.mix((0, 0.25, 0.5), (0.5, 0.75, 1), 0.5)
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_vector_curve_identity() -> None:
    node = node_math.vector_curve((0.25, 0.5, 0.75))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_combine_xyz() -> None:
    node = node_math.combine_xyz(0.25, 0.5, 0.75)
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))


def test_separate_xyz_roundtrip() -> None:
    node = node_math.combine_xyz(*node_math.separate_xyz((0.25, 0.5, 0.75)))
    shader_eval.assert_value(shader_eval.render(node), (0.25, 0.5, 0.75))
