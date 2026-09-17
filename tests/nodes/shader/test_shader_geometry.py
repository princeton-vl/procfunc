"""Rendered coverage for the bindings whose value only exists in a shading
context: attributes, coordinates, curves, points and particles."""

import math

import bpy
import numpy as np
import pytest
import shader_eval

import procfunc as pf

shader = pf.nodes.shader
pytestmark = pytest.mark.render

UV = shader.coord().uv


def test_uv_map_matches_the_plane_uvs() -> None:
    frame = shader_eval.render(shader.uv_map(uv_map=shader_eval.UV_LAYER))
    interior = shader_eval.INTERIOR
    shader_eval.assert_image(
        frame[interior], shader_eval.uv_grid()[interior], atol=5e-3
    )


def test_coord_uv_matches_the_plane_uvs() -> None:
    frame = shader_eval.render(UV)
    interior = shader_eval.INTERIOR
    shader_eval.assert_image(
        frame[interior], shader_eval.uv_grid()[interior], atol=5e-3
    )


def test_coord_object_is_the_plane_in_object_space() -> None:
    frame = shader_eval.render(shader.coord().object)
    interior = shader_eval.INTERIOR
    expected = shader_eval.uv_grid() * 2.0 - np.array([1.0, 1.0, 0.0], dtype=np.float32)
    shader_eval.assert_image(frame[interior], expected[interior], atol=1e-2)


def test_coord_generated_sits_at_the_midpoint_in_z() -> None:
    frame = shader_eval.render(shader.coord().generated)
    shader_eval.assert_value(frame, (0.3125, 0.6875, 0.5))


def test_coord_window_tracks_the_frame() -> None:
    shader_eval.assert_varies(shader_eval.render(shader.coord().window))


def test_coord_normal_is_the_plane_normal() -> None:
    shader_eval.assert_value(shader_eval.render(shader.coord().normal), (0, 0, 1))


def test_attribute_reads_the_float_layer() -> None:
    frame = shader_eval.render(
        shader.attribute(attribute_name=shader_eval.FLOAT_LAYER).fac
    )
    shader_eval.assert_varies(frame)
    corners = [frame[0, 0, 0], frame[0, -1, 0], frame[-1, -1, 0], frame[-1, 0, 0]]
    np.testing.assert_allclose(corners, [0.0, 0.25, 0.5, 1.0], atol=0.07)


def test_attribute_reads_the_color_layer() -> None:
    frame = shader_eval.render(
        shader.attribute(attribute_name=shader_eval.COLOR_LAYER).color
    )
    np.testing.assert_allclose(frame[0, 0], (1, 0, 0), atol=0.07)
    np.testing.assert_allclose(frame[0, -1], (0, 1, 0), atol=0.07)
    np.testing.assert_allclose(frame[-1, -1], (0, 0, 1), atol=0.07)
    np.testing.assert_allclose(frame[-1, 0], (1, 1, 0), atol=0.07)


def test_vertex_color_reads_the_named_layer() -> None:
    frame = shader_eval.render(
        shader.vertex_color(layer_name=shader_eval.COLOR_LAYER).color
    )
    np.testing.assert_allclose(frame[0, 0], (1, 0, 0), atol=0.07)
    np.testing.assert_allclose(frame[-1, -1], (0, 0, 1), atol=0.07)


def test_tangent_from_uv_points_along_u() -> None:
    node = shader.tangent(direction_type="UV_MAP", uv_map=shader_eval.UV_LAYER)
    shader_eval.assert_value(shader_eval.render(node), (1, 0, 0))


def test_tangent_radial_sweeps_around_the_axis() -> None:
    # radial tangents about X or Y are degenerate on a plane lying in XY and
    # render NaN under Cycles, in the native node as much as through the binding
    frame = shader_eval.render(
        shader.tangent(axis="Z", direction_type="RADIAL"), engine=shader_eval.CYCLES
    )
    shader_eval.assert_varies(frame)
    assert not np.isnan(frame).any()
    assert np.isnan(
        shader_eval.render(
            shader.tangent(axis="X", direction_type="RADIAL"),
            engine=shader_eval.CYCLES,
        )
    ).any()


def test_bevel_rounds_a_cube_edge() -> None:
    grey = pf.Color((0.8, 0.8, 0.8))
    flat = shader_eval.render_cube(shader.diffuse_bsdf(color=grey))
    rounded = shader_eval.render_cube(
        shader.diffuse_bsdf(color=grey, normal=shader.bevel(radius=0.4, samples=16))
    )
    shader_eval.assert_differs(flat, rounded, threshold=0.01)


def test_bevel_radius_changes_how_far_the_rounding_reaches() -> None:
    grey = pf.Color((0.8, 0.8, 0.8))
    hairline = shader_eval.render_cube(
        shader.diffuse_bsdf(color=grey, normal=shader.bevel(radius=0.02, samples=16))
    )
    wide = shader_eval.render_cube(
        shader.diffuse_bsdf(color=grey, normal=shader.bevel(radius=0.4, samples=16))
    )
    shader_eval.assert_differs(hairline, wide, threshold=0.01)


def test_bump_tilts_the_shading_normal() -> None:
    # the AOV pass carries no surface differentials, so bump only moves once it
    # drives a real BSDF normal
    height = pf.nodes.texture.noise(UV, scale=6.0, detail=2.0).fac
    flat = shader_eval.render_shader(
        shader.diffuse_bsdf(color=pf.Color((0.8, 0.8, 0.8)))
    )
    bumped = shader_eval.render_shader(
        shader.diffuse_bsdf(
            color=pf.Color((0.8, 0.8, 0.8)),
            normal=shader.bump(strength=1.0, distance=1.0, height=height),
        )
    )
    shader_eval.assert_differs(flat, bumped, threshold=0.01)


def test_bump_strength_scales_the_tilt() -> None:
    height = pf.nodes.texture.noise(UV, scale=6.0, detail=2.0).fac
    weak = shader_eval.render_emission(shader.bump(strength=0.1, height=height))
    strong = shader_eval.render_emission(shader.bump(strength=1.0, height=height))
    shader_eval.assert_differs(weak, strong, threshold=0.01)


def test_bump_invert_flips_the_tilt() -> None:
    height = pf.nodes.texture.noise(UV, scale=6.0, detail=2.0).fac
    up = shader_eval.render_emission(shader.bump(height=height, invert=False))
    down = shader_eval.render_emission(shader.bump(height=height, invert=True))
    shader_eval.assert_differs(up, down, threshold=0.01)


def test_ambient_occlusion_color_is_the_colour_times_the_visibility() -> None:
    frame = shader_eval.render(
        shader.ambient_occlusion(color=pf.Color((0.5, 0.25, 0.125))).color,
        engine=shader_eval.CYCLES,
    )
    shader_eval.assert_value(frame, (0.5, 0.25, 0.125))


def test_ambient_occlusion_darkens_under_an_occluder() -> None:
    scene = shader_eval._scene(shader_eval.CYCLES)
    shader_eval._configure_aov(scene)
    plane = shader_eval.probe_plane(scene)
    plane.data.materials.append(
        shader_eval._aov_material(shader.ambient_occlusion(distance=2.0).ao)
    )

    mesh = bpy.data.meshes.new("occluder")
    mesh.from_pydata(shader_eval.CUBE_VERTS, [], shader_eval.CUBE_FACES)
    mesh.update()
    occluder = bpy.data.objects.new("occluder", mesh)
    occluder.location = (0.6, 0.6, 0.5)
    scene.collection.objects.link(occluder)

    frame = shader_eval.render_scene(scene)
    shader_eval.assert_varies(frame)
    assert frame[shader_eval.INTERIOR].min() < 0.5


def test_camera_data_view_z_depth_is_the_camera_height() -> None:
    frame = shader_eval.render(shader.camera_data().view_z_depth)
    shader_eval.assert_value(frame, 4.0)


def test_camera_data_view_vector_points_away_from_the_camera() -> None:
    frame = shader_eval.render(shader.camera_data().view_vector)
    assert frame[shader_eval.PROBE][..., 2].min() > 0.9
    shader_eval.assert_varies(frame)


def test_light_falloff_quadratic_passes_the_strength_through() -> None:
    frame = shader_eval.render(shader.light_falloff(strength=100.0).quadratic)
    shader_eval.assert_value(frame, 100.0)


def test_light_falloff_modes_are_powers_of_the_ray_length() -> None:
    strength = 100.0
    quadratic = shader_eval.probe(
        shader_eval.render(shader.light_falloff(strength=strength).quadratic)
    )[0]
    linear = shader_eval.probe(
        shader_eval.render(shader.light_falloff(strength=strength).linear)
    )[0]
    constant = shader_eval.probe(
        shader_eval.render(shader.light_falloff(strength=strength).constant)
    )[0]
    ray_length = linear / quadratic
    np.testing.assert_allclose(constant / quadratic, ray_length**2, rtol=1e-3)


def test_hair_info_marks_the_strands() -> None:
    frame = shader_eval.render_hair(shader.emission(shader.hair_info().is_strand, 1.0))
    assert frame.max() == 1.0
    assert frame.min() == 0.0


def test_hair_info_thickness_is_the_curve_diameter() -> None:
    frame = shader_eval.render_hair(shader.emission(shader.hair_info().thickness, 1.0))
    np.testing.assert_allclose(frame.max(), 2 * shader_eval.HAIR_RADIUS, atol=1e-3)


def test_hair_info_length_is_the_strand_length() -> None:
    frame = shader_eval.render_hair(shader.emission(shader.hair_info().length, 1.0))
    np.testing.assert_allclose(frame.max(), 1.2, atol=1e-3)


def test_hair_info_intercept_runs_from_root_to_tip() -> None:
    frame = shader_eval.render_hair(shader.emission(shader.hair_info().intercept, 1.0))
    shader_eval.assert_varies(frame)
    top = frame[shader_eval.RESOLUTION // 2 :].max()
    bottom = frame[: shader_eval.RESOLUTION // 2].max()
    assert top > bottom


def test_hair_info_random_differs_between_strands() -> None:
    frame = shader_eval.render_hair(shader.emission(shader.hair_info().random, 1.0))
    strand_values = {round(float(v), 4) for v in frame[..., 0].ravel() if v > 0}
    assert len(strand_values) >= len(shader_eval.HAIR_ROOTS)


def test_hair_info_tangent_normal_follows_the_strand() -> None:
    frame = shader_eval.render_hair(
        shader.emission(shader.hair_info().tangent_normal, 1.0)
    )
    shader_eval.assert_varies(frame)


def test_point_info_radius_is_the_point_radius() -> None:
    frame = shader_eval.render_points(shader.point_info().radius)
    np.testing.assert_allclose(frame.max(), shader_eval.POINT_RADIUS, atol=1e-4)


def test_point_info_position_spans_the_point_cloud() -> None:
    frame = shader_eval.render_points(shader.point_info().position)
    np.testing.assert_allclose(frame[..., 0].max(), 0.35, atol=1e-3)
    np.testing.assert_allclose(frame[..., 0].min(), -0.35, atol=1e-3)


def test_point_info_random_differs_between_points() -> None:
    frame = shader_eval.render_points(shader.point_info().random)
    values = {round(float(v), 4) for v in frame[..., 0].ravel() if v > 0}
    assert len(values) >= len(shader_eval.POINT_POSITIONS)


def test_particle_info_index_counts_the_particles() -> None:
    frame = shader_eval.render_particles(shader.particle_info().index)
    np.testing.assert_allclose(frame.max(), shader_eval.PARTICLE_COUNT - 1, atol=1e-4)


def test_particle_info_lifetime_is_the_configured_lifetime() -> None:
    frame = shader_eval.render_particles(shader.particle_info().lifetime)
    np.testing.assert_allclose(frame.max(), shader_eval.PARTICLE_LIFETIME, rtol=1e-4)


def test_particle_info_age_advances_since_emission() -> None:
    frame = shader_eval.render_particles(shader.particle_info().age, frame=11)
    np.testing.assert_allclose(frame.max(), 10.0, atol=1e-4)


def test_particle_info_size_is_the_scaled_instance_radius() -> None:
    frame = shader_eval.render_particles(shader.particle_info().size)
    bounding_radius = 0.75 * math.sqrt(3)
    np.testing.assert_allclose(
        frame.max(), shader_eval.PARTICLE_SIZE * bounding_radius, rtol=0.02
    )


def test_particle_info_random_and_location_vary_per_particle() -> None:
    shader_eval.assert_varies(
        shader_eval.render_particles(shader.particle_info().random)
    )
    shader_eval.assert_varies(
        shader_eval.render_particles(shader.particle_info().location)
    )


def test_shader_to_rgb_flattens_a_diffuse_bsdf() -> None:
    # ShaderNodeShaderToRGB is an EEVEE node; Cycles compiles it away to black
    node = shader.shader_to_rgb(shader.diffuse_bsdf(color=pf.Color((0.8, 0.2, 0.1))))
    frame = shader_eval.render(node.color, engine=shader_eval.EEVEE)
    shader_eval.assert_value(frame, (0.25465, 0.06366, 0.03183))


def test_shader_to_rgb_flattens_an_emission() -> None:
    node = shader.shader_to_rgb(shader.emission(pf.Color((0.5, 0.25, 0.125)), 2.0))
    frame = shader_eval.render(node.color, engine=shader_eval.EEVEE)
    shader_eval.assert_value(frame, (1.0, 0.5, 0.25))
