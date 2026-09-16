import typing
from pathlib import Path

import bpy
import numpy as np
import pytest
from compositor_eval import (
    assert_uniform,
    build_compositor,
    composite_render,
    composite_source,
    halves,
    image_node,
    movie_clip_datablock,
    ramp,
    realized_node,
    render_scene,
    solid,
)

import procfunc as pf
from procfunc.transpiler import bpy_to_computegraph

comp = pf.nodes.compositor

N = 8
COLOR = solid(N, N, (0.25, 0.5, 0.75, 1.0))
GREY = solid(N, N, (0.5, 0.5, 0.5, 1.0))
WHITE = solid(N, N, (1.0, 1.0, 1.0, 1.0))
BLACK = solid(N, N, (0.0, 0.0, 0.0, 1.0))
RED = solid(N, N, (1.0, 0.0, 0.0, 1.0))
GREEN = solid(N, N, (0.0, 1.0, 0.0, 1.0))
SEMI = solid(N, N, (0.25, 0.5, 0.75, 0.5))
STEP_X = halves(N, N, (0, 0, 0, 1), (1, 1, 1, 1), "x")
STEP_Y = halves(N, N, (0, 0, 0, 1), (1, 1, 1, 1), "y")
RAMP = ramp(N, N, 0.0, 1.0)
NARROW_RAMP = ramp(N, N, 0.25, 0.5)

CORNER = np.zeros((N, N, 4), dtype=np.float32)
CORNER[..., 3] = 1.0
CORNER[: N // 2, : N // 2, :3] = 1.0

ASYMMETRIC = np.empty((N, N, 4), dtype=np.float32)
ASYMMETRIC[..., :3] = np.arange(N * N, dtype=np.float32).reshape(N, N, 1)
ASYMMETRIC[..., 3] = 1.0


# ---------------------------------------------------------------- harness ----


def test_image_node_round_trips_its_pixels_exactly():
    out = composite_render(image_node("src", COLOR).image)
    assert out.shape == (N, N, 4)
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_image_node_alpha_output_carries_the_alpha_channel():
    out = composite_render(image_node("src", SEMI).alpha)
    assert_uniform(out, (0.5, 0.5, 0.5, 1.0))


def test_composite_constant_alpha_input_replaces_the_alpha_channel():
    src = image_node("src", COLOR)
    out = composite_render(src.image, alpha=0.25)
    assert_uniform(out, (0.25, 0.5, 0.75, 0.25))


def test_composite_linked_alpha_input_replaces_the_alpha_channel():
    src = image_node("src", SEMI)
    out = composite_render(src.image, alpha=src.alpha)
    assert_uniform(out, (0.25, 0.5, 0.75, 0.5))


@pytest.mark.parametrize(
    "use_alpha,alpha,expected_alpha",
    [(True, None, 0.5), (False, None, 1.0), (False, 0.25, 1.0), (True, 0.0, 0.0)],
)
def test_composite_preserves_or_discards_image_alpha(
    use_alpha: bool, alpha: float | None, expected_alpha: float
) -> None:
    src = image_node("src", SEMI)
    result = comp.composite(image=src.image, alpha=alpha, use_alpha=use_alpha)

    out = render_scene(build_compositor(result))

    assert_uniform(out, (0.25, 0.5, 0.75, expected_alpha))


@pytest.mark.parametrize("use_alpha", [True, False])
def test_composite_transpile_preserves_native_alpha(use_alpha: bool) -> None:
    scene = bpy.data.scenes.new("native_composite_alpha")
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    node = tree.nodes.new("CompositorNodeComposite")
    node.use_alpha = use_alpha
    node.inputs["Image"].default_value = (0.25, 0.5, 0.75, 0.5)
    node.inputs["Alpha"].default_value = 0.25
    expected = render_scene(scene)

    parsed = bpy_to_computegraph.parse_standard_node(
        tree, node, bpy_to_computegraph.ParseMemo()
    )
    rebuilt = parsed.func(**parsed.kwargs)
    actual = render_scene(build_compositor(rebuilt))

    np.testing.assert_allclose(actual, expected, atol=1e-4)


def test_image_node_preserves_row_order_top_down():
    out = composite_render(image_node("src", STEP_Y).image)
    assert out[0, 0, 0] == pytest.approx(0.0)
    assert out[N - 1, 0, 0] == pytest.approx(1.0)


def test_composite_render_leaves_the_context_scene_unchanged() -> None:
    scene = bpy.data.scenes.new("sentinel")
    scene.use_nodes = True
    node = scene.node_tree.nodes.new("CompositorNodeRGB")
    scene.render.resolution_x = 1234
    scene.render.filepath = "/tmp/untouched"
    with bpy.context.temp_override(scene=scene):
        composite_render(image_node("src", COLOR).image)
        assert bpy.context.scene == scene
    assert node in scene.node_tree.nodes.values()
    assert scene.camera is None
    assert scene.render.resolution_x == 1234
    assert scene.render.filepath == "/tmp/untouched"


def test_render_layers_reaches_the_composite_output():
    out = composite_render(comp.render_layers().image)
    assert out.shape == (N, N, 4)


# -------------------------------------------------------- native contracts ----


def test_rgb_curve_maps_all_four_curve_point_sets():
    curves = np.asarray(
        [
            [[0.0, 0.1], [1.0, 0.9]],
            [[0.0, 0.2], [1.0, 0.8]],
            [[0.0, 0.3], [1.0, 0.7]],
            [[0.0, 0.4], [1.0, 0.6]],
        ]
    )
    node = realized_node(
        comp.rgb_curve(fac=1.0, image=(0.1, 0.2, 0.3, 1.0), curves=curves),
        "CompositorNodeCurveRGB",
    )
    for curve, expected in zip(node.mapping.curves, curves, strict=True):
        assert [tuple(point.location) for point in curve.points] == pytest.approx(
            expected
        )


def test_time_maps_distinct_frame_bounds():
    node = realized_node(comp.time(frame_start=7, frame_end=23), "CompositorNodeTime")
    assert node.frame_start == 7
    assert node.frame_end == 23


@pytest.mark.parametrize(
    ("binding", "space", "kwargs"),
    [
        (comp.scale_absolute, "ABSOLUTE", {"x": 320, "y": 180}),
        (comp.scale_relative, "RELATIVE", {"x": 2.0, "y": 3.0}),
        (comp.scale_render, "RENDER_SIZE", {}),
        (comp.scale_scene, "SCENE_SIZE", {}),
    ],
    ids=["absolute", "relative", "render", "scene"],
)
def test_scale_selects_its_size_space(
    binding: typing.Callable, space: str, kwargs: dict
) -> None:
    node = realized_node(binding(**kwargs), "CompositorNodeScale")
    assert node.space == space
    assert [socket.enabled for socket in node.inputs] == [
        True,
        bool(kwargs),
        bool(kwargs),
    ]
    if kwargs:
        assert node.inputs["X"].default_value == kwargs["x"]
        assert node.inputs["Y"].default_value == kwargs["y"]


@pytest.mark.parametrize(
    ("method", "active"),
    [
        ("LIFT_GAMMA_GAIN", ("lift", "gamma", "gain")),
        ("OFFSET_POWER_SLOPE", ("offset", "offset_basis", "power", "slope")),
    ],
    ids=["lift_gamma_gain", "offset_power_slope"],
)
def test_color_balance_preserves_active_controls(
    method: str, active: tuple[str, ...]
) -> None:
    controls = {
        "lift": (0.7, 0.8, 0.9),
        "gamma": (1.1, 1.2, 1.3),
        "gain": (1.4, 1.5, 1.6),
        "offset": (0.2, 0.3, 0.4),
        "offset_basis": 0.15,
        "power": (0.6, 0.7, 0.8),
        "slope": (1.7, 1.8, 1.9),
    }
    binding = (
        comp.color_balance
        if method == "LIFT_GAMMA_GAIN"
        else comp.color_balance_slope_offset_power
    )
    node = realized_node(
        binding(**{name: controls[name] for name in active}),
        "CompositorNodeColorBalance",
    )
    assert node.correction_method == method
    for name in active:
        np.testing.assert_allclose(getattr(node, name), controls[name], err_msg=name)


def test_map_uv_preserves_image_uv_and_filter_controls() -> None:
    node = realized_node(
        comp.map_uv(
            image=(0.1, 0.2, 0.3, 1.0),
            uv=(0.4, 0.5, 0.6),
            alpha=7,
            filter_type="NEAREST",
        ),
        "CompositorNodeMapUV",
    )
    assert tuple(node.inputs["Image"].default_value) == pytest.approx(
        (0.1, 0.2, 0.3, 1.0)
    )
    assert tuple(node.inputs["UV"].default_value) == pytest.approx((0.4, 0.5, 0.6))
    assert node.alpha == 7
    assert node.filter_type == "NEAREST"


def test_sun_beams_preserves_ray_origin_and_length() -> None:
    node = realized_node(
        comp.sun_beams(image=(0.1, 0.2, 0.3, 1.0), ray_length=0.3, source=(0.2, 0.7)),
        "CompositorNodeSunBeams",
    )
    assert tuple(node.inputs["Image"].default_value) == pytest.approx(
        (0.1, 0.2, 0.3, 1.0)
    )
    assert tuple(node.source) == pytest.approx((0.2, 0.7))
    assert node.ray_length == pytest.approx(0.3)


def test_tonemap_selects_simple_photographic_controls() -> None:
    node = realized_node(
        comp.tonemap(
            image=(0.1, 0.2, 0.3, 1.0),
            tonemap_type="RH_SIMPLE",
            key=0.3,
            offset=1.7,
            gamma=2.1,
        ),
        "CompositorNodeTonemap",
    )
    assert tuple(node.inputs["Image"].default_value) == pytest.approx(
        (0.1, 0.2, 0.3, 1.0)
    )
    assert node.tonemap_type == "RH_SIMPLE"
    assert (node.key, node.offset, node.gamma) == pytest.approx((0.3, 1.7, 2.1))


def test_image_maps_resource_and_playback_properties():
    image = bpy.data.images.new("property_test", 2, 2)
    result = comp.image(
        image=image,
        frame_duration=7,
        frame_offset=2,
        frame_start=3,
        use_auto_refresh=False,
        use_cyclic=True,
        use_straight_alpha_output=True,
    )
    node = realized_node(result.image, "CompositorNodeImage")
    assert node.image == image
    assert node.frame_duration == 7
    assert node.frame_offset == 2
    assert node.frame_start == 3
    assert not node.use_auto_refresh
    assert node.use_cyclic
    assert node.use_straight_alpha_output


def test_texture_maps_resource_and_vector_inputs():
    texture = bpy.data.textures.new("property_test", type="IMAGE")
    result = comp.texture(
        texture=texture,
        node_output=2,
        offset=(1, 2, 3),
        scale=(4, 5, 6),
    )
    node = realized_node(result.color, "CompositorNodeTexture")
    assert node.texture == texture
    assert node.node_output == 2
    assert tuple(node.inputs["Offset"].default_value) == pytest.approx((1, 2, 3))
    assert tuple(node.inputs["Scale"].default_value) == pytest.approx((4, 5, 6))


@pytest.mark.parametrize(
    ("binding", "bl_idname", "output", "properties"),
    [
        (comp.movie_clip, "CompositorNodeMovieClip", "image", {}),
        (
            comp.stabilize,
            "CompositorNodeStabilize",
            None,
            {"filter_type": "BICUBIC", "invert": True},
        ),
        (
            comp.keying_screen,
            "CompositorNodeKeyingScreen",
            None,
            {"tracking_object": "Camera", "smoothness": 0.4},
        ),
        (
            comp.track_pos,
            "CompositorNodeTrackPos",
            "x",
            {
                "frame_relative": 7,
                "position": "RELATIVE_FRAME",
                "track_name": "feature",
                "tracking_object": "Camera",
            },
        ),
        (
            comp.plane_track_deform,
            "CompositorNodePlaneTrackDeform",
            "image",
            {
                "motion_blur_samples": 8,
                "motion_blur_shutter": 0.25,
                "plane_track_name": "plane",
                "tracking_object": "Camera",
                "use_motion_blur": True,
            },
        ),
        (
            comp.movie_distortion,
            "CompositorNodeMovieDistortion",
            None,
            {"distortion_type": "UNDISTORT"},
        ),
    ],
    ids=[
        "movie_clip",
        "stabilize",
        "keying_screen",
        "track_pos",
        "plane_track_deform",
        "movie_distortion",
    ],
)
def test_movie_bindings_preserve_clip_and_properties(
    tmp_path: Path,
    binding: typing.Callable,
    bl_idname: str,
    output: str | None,
    properties: dict,
) -> None:
    clip = movie_clip_datablock(tmp_path / "clip.png")
    image = {}
    if binding in (comp.stabilize, comp.plane_track_deform, comp.movie_distortion):
        image = {"image": (0.1, 0.2, 0.3, 1.0)}
    result = binding(clip=clip, **properties, **image)
    node = realized_node(getattr(result, output) if output else result, bl_idname)
    assert node.clip == clip
    for name, expected in properties.items():
        assert getattr(node, name) == pytest.approx(expected), name
    if image:
        assert tuple(node.inputs["Image"].default_value) == pytest.approx(
            image["image"]
        )


def test_mask_maps_datablock_size_feather_and_motion_blur():
    mask = bpy.data.masks.new("property_test")
    node = realized_node(
        comp.mask(
            mask=mask,
            motion_blur_samples=8,
            motion_blur_shutter=0.25,
            size_source="FIXED",
            size_x=320,
            size_y=180,
            use_feather=False,
            use_motion_blur=True,
        ),
        "CompositorNodeMask",
    )
    assert node.mask == mask
    assert node.motion_blur_samples == 8
    assert node.motion_blur_shutter == pytest.approx(0.25)
    assert node.size_source == "FIXED"
    assert (node.size_x, node.size_y) == (320, 180)
    assert not node.use_feather
    assert node.use_motion_blur


def test_cryptomatte_maps_id_and_each_image_input():
    pixels = [
        (0.1, 0.2, 0.3, 1.0),
        (0.4, 0.5, 0.6, 1.0),
        (0.7, 0.8, 0.9, 1.0),
        (0.2, 0.4, 0.6, 1.0),
    ]
    result = comp.cryptomatte(
        image=pixels[0],
        crypto_00=pixels[1],
        crypto_01=pixels[2],
        crypto_02=pixels[3],
        matte_id="asset",
    )
    node = realized_node(result.image, "CompositorNodeCryptomatte")
    assert node.matte_id == "asset"
    for socket, expected in zip(
        ("Image", "Crypto 00", "Crypto 01", "Crypto 02"), pixels, strict=True
    ):
        assert tuple(node.inputs[socket].default_value) == pytest.approx(expected)


def test_output_file_maps_path_format_slot_and_input():
    node = realized_node(
        comp.output_file(
            active_input_index=0,
            base_path="/tmp/sentinel",
            slot_paths={"Image": "beauty"},
            format={"file_format": "PNG"},
            Image=(0.1, 0.2, 0.3, 1.0),
        ),
        "CompositorNodeOutputFile",
    )
    assert node.active_input_index == 0
    assert node.base_path == "/tmp/sentinel"
    assert node.format.file_format == "PNG"
    assert node.file_slots[0].path == "beauty"
    assert tuple(node.inputs["Image"].default_value) == pytest.approx(
        (0.1, 0.2, 0.3, 1.0)
    )


def test_viewer_maps_inputs_and_alpha_option():
    node = realized_node(
        comp.viewer(image=(0.1, 0.2, 0.3, 1.0), alpha=0.4, use_alpha=False),
        "CompositorNodeViewer",
    )
    assert tuple(node.inputs["Image"].default_value) == pytest.approx(
        (0.1, 0.2, 0.3, 1.0)
    )
    assert node.inputs["Alpha"].default_value == pytest.approx(0.4)
    assert not node.use_alpha


@pytest.mark.parametrize(
    ("binding", "bl_idname", "outputs"),
    [
        (
            comp.movie_clip,
            "CompositorNodeMovieClip",
            {
                "image": "Image",
                "alpha": "Alpha",
                "offset_x": "Offset X",
                "offset_y": "Offset Y",
                "scale": "Scale",
                "angle": "Angle",
            },
        ),
        (comp.texture, "CompositorNodeTexture", {"value": "Value", "color": "Color"}),
        (
            comp.track_pos,
            "CompositorNodeTrackPos",
            {"x": "X", "y": "Y", "speed": "Speed"},
        ),
        (
            comp.cryptomatte,
            "CompositorNodeCryptomatte",
            {"image": "Image", "matte": "Matte", "pick": "Pick"},
        ),
        (
            comp.plane_track_deform,
            "CompositorNodePlaneTrackDeform",
            {"image": "Image", "plane": "Plane"},
        ),
        (
            comp.corner_pin,
            "CompositorNodeCornerPin",
            {"image": "Image", "plane": "Plane"},
        ),
        (
            comp.keying,
            "CompositorNodeKeying",
            {"image": "Image", "matte": "Matte", "edges": "Edges"},
        ),
        (comp.levels, "CompositorNodeLevels", {"mean": "Mean", "std_dev": "Std Dev"}),
        (
            comp.separate_ycc,
            "CompositorNodeSeparateColor",
            {"y": "Red", "cb": "Green", "cr": "Blue", "alpha": "Alpha"},
        ),
        (
            comp.separate_yuv,
            "CompositorNodeSeparateColor",
            {"y": "Red", "u": "Green", "v": "Blue", "alpha": "Alpha"},
        ),
    ],
    ids=[
        "movie_clip",
        "texture",
        "track_pos",
        "cryptomatte",
        "plane_track_deform",
        "corner_pin",
        "keying",
        "levels",
        "separate_ycc",
        "separate_yuv",
    ],
)
def test_result_fields_select_the_named_native_socket(
    binding: typing.Callable, bl_idname: str, outputs: dict[str, str]
) -> None:
    kwargs = {}
    if binding in (comp.separate_ycc, comp.separate_yuv):
        kwargs = {"color": (0.1, 0.2, 0.3, 1.0)}
    result = binding(**kwargs)
    for field, socket in outputs.items():
        assert composite_source(getattr(result, field)) == (bl_idname, socket)


# ------------------------------------------------------------------ color ----


def test_invert_flips_every_rgb_channel():
    out = composite_render(comp.invert(fac=1.0, color=image_node("src", COLOR).image))
    assert_uniform(out, (0.75, 0.5, 0.25, 1.0))


def test_invert_fac_half_lands_midway():
    out = composite_render(comp.invert(fac=0.5, color=image_node("src", COLOR).image))
    assert_uniform(out, (0.5, 0.5, 0.5, 1.0))


def test_invert_fac_zero_is_a_passthrough():
    out = composite_render(comp.invert(fac=0.0, color=image_node("src", COLOR).image))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_invert_alpha_only_leaves_rgb_alone():
    out = composite_render(
        comp.invert(
            fac=1.0,
            color=image_node("src", SEMI).image,
            invert_alpha=True,
            invert_rgb=False,
        )
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 0.5))


def test_invert_both_flips_rgb_and_alpha():
    out = composite_render(
        comp.invert(
            fac=1.0,
            color=image_node("src", SEMI).image,
            invert_alpha=True,
            invert_rgb=True,
        )
    )
    assert_uniform(out, (0.75, 0.5, 0.25, 0.5))


def test_gamma_two_squares_each_channel():
    out = composite_render(comp.gamma(image=image_node("src", COLOR).image, gamma=2.0))
    assert_uniform(out, (0.0625, 0.25, 0.5625, 1.0))


def test_gamma_one_is_a_passthrough():
    out = composite_render(comp.gamma(image=image_node("src", COLOR).image, gamma=1.0))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_gamma_half_takes_the_square_root():
    out = composite_render(comp.gamma(image=image_node("src", GREY).image, gamma=0.5))
    assert_uniform(out, (0.70710, 0.70710, 0.70710, 1.0))


def test_exposure_one_doubles_the_image():
    out = composite_render(
        comp.exposure(image=image_node("src", COLOR).image, exposure=1.0)
    )
    assert_uniform(out, (0.5, 1.0, 1.5, 1.0))


def test_exposure_zero_is_a_passthrough():
    out = composite_render(
        comp.exposure(image=image_node("src", COLOR).image, exposure=0.0)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_exposure_minus_one_halves_the_image():
    out = composite_render(
        comp.exposure(image=image_node("src", COLOR).image, exposure=-1.0)
    )
    assert_uniform(out, (0.125, 0.25, 0.375, 1.0))


def test_bright_contrast_bright_adds_a_scaled_offset():
    out = composite_render(
        comp.bright_contrast(image=image_node("src", GREY).image, bright=0.25)
    )
    assert_uniform(out, (0.5025, 0.5025, 0.5025, 1.0))


def test_bright_contrast_contrast_pushes_away_from_mid_grey():
    out = composite_render(
        comp.bright_contrast(image=image_node("src", COLOR).image, contrast=1.0)
    )
    assert_uniform(out, (0.2475, 0.5, 0.7525, 1.0))


def test_bright_contrast_defaults_leave_the_image_alone():
    out = composite_render(
        comp.bright_contrast(
            image=image_node("src", COLOR).image, bright=0.0, contrast=0.0
        )
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_rgb_to_bw_uses_rec709_luma_weights():
    out = composite_render(comp.rgb_to_bw(image=image_node("src", COLOR).image))
    expected = 0.2126 * 0.25 + 0.7152 * 0.5 + 0.0722 * 0.75
    assert_uniform(out, (expected, expected, expected, 1.0))


def test_rgb_to_bw_of_pure_red_is_the_red_luma_weight():
    out = composite_render(comp.rgb_to_bw(image=image_node("src", RED).image))
    assert_uniform(out, (0.2126, 0.2126, 0.2126, 1.0))


def test_mix_rgb_fac_half_averages_the_two_inputs():
    out = composite_render(
        comp.mix_rgb(
            a=image_node("a", BLACK).image, b=image_node("b", WHITE).image, fac=0.5
        )
    )
    assert_uniform(out, (0.5, 0.5, 0.5, 1.0))


def test_mix_rgb_fac_zero_returns_the_first_input():
    out = composite_render(
        comp.mix_rgb(
            a=image_node("a", BLACK).image, b=image_node("b", WHITE).image, fac=0.0
        )
    )
    assert_uniform(out, (0.0, 0.0, 0.0, 1.0))


def test_mix_rgb_add_sums_the_two_inputs():
    out = composite_render(
        comp.mix_rgb(
            a=image_node("a", COLOR).image,
            b=image_node("b", GREY).image,
            fac=1.0,
            blend_type="ADD",
        )
    )
    assert_uniform(out, (0.75, 1.0, 1.25, 1.0))


def test_mix_rgb_multiply_multiplies_the_two_inputs():
    out = composite_render(
        comp.mix_rgb(
            a=image_node("a", COLOR).image,
            b=image_node("b", GREY).image,
            fac=1.0,
            blend_type="MULTIPLY",
        )
    )
    assert_uniform(out, (0.125, 0.25, 0.375, 1.0))


def test_mix_rgb_subtract_subtracts_the_second_input():
    out = composite_render(
        comp.mix_rgb(
            a=image_node("a", COLOR).image,
            b=image_node("b", GREY).image,
            fac=1.0,
            blend_type="SUBTRACT",
        )
    )
    assert_uniform(out, (-0.25, 0.0, 0.25, 1.0))


def test_mix_rgb_difference_takes_the_absolute_difference():
    out = composite_render(
        comp.mix_rgb(
            a=image_node("a", COLOR).image,
            b=image_node("b", GREY).image,
            fac=1.0,
            blend_type="DIFFERENCE",
        )
    )
    assert_uniform(out, (0.25, 0.0, 0.25, 1.0))


def test_mix_rgb_clamp_result_caps_an_overflowing_add():
    out = composite_render(
        comp.mix_rgb(
            a=image_node("a", WHITE).image,
            b=image_node("b", GREY).image,
            fac=1.0,
            blend_type="ADD",
            clamp_result=True,
        )
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


def test_mix_rgb_without_clamp_lets_the_add_overflow():
    out = composite_render(
        comp.mix_rgb(
            a=image_node("a", WHITE).image,
            b=image_node("b", GREY).image,
            fac=1.0,
            blend_type="ADD",
            clamp_result=False,
        )
    )
    assert_uniform(out, (1.5, 1.5, 1.5, 1.0))


def test_alpha_over_opaque_foreground_hides_the_background():
    out = composite_render(
        comp.alpha_over(
            a=image_node("a", RED).image, b=image_node("b", GREEN).image, fac=1.0
        )
    )
    assert_uniform(out, (0.0, 1.0, 0.0, 1.0))


def test_alpha_over_fac_zero_keeps_the_background():
    out = composite_render(
        comp.alpha_over(
            a=image_node("a", RED).image, b=image_node("b", GREEN).image, fac=0.0
        )
    )
    assert_uniform(out, (1.0, 0.0, 0.0, 1.0))


def test_alpha_over_semi_transparent_foreground_blends_premultiplied():
    fg = solid(N, N, (0.0, 1.0, 0.0, 0.5))
    out = composite_render(
        comp.alpha_over(
            a=image_node("a", RED).image, b=image_node("b", fg).image, fac=1.0
        )
    )
    assert_uniform(out, (0.5, 1.0, 0.0, 1.0))


def test_set_alpha_replace_overwrites_the_alpha_channel():
    out = composite_render(
        comp.set_alpha(
            image=image_node("src", COLOR).image, alpha=0.5, mode="REPLACE_ALPHA"
        )
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 0.5))


def test_set_alpha_apply_multiplies_rgb_by_the_alpha():
    out = composite_render(
        comp.set_alpha(image=image_node("src", COLOR).image, alpha=0.5, mode="APPLY")
    )
    assert_uniform(out, (0.125, 0.25, 0.375, 0.5))


def test_premultiply_key_straight_to_premul_scales_rgb_down():
    out = composite_render(
        comp.premultiply_key(
            image=image_node("src", SEMI).image, mapping="STRAIGHT_TO_PREMUL"
        )
    )
    assert_uniform(out, (0.125, 0.25, 0.375, 0.5))


def test_premultiply_key_premul_to_straight_scales_rgb_up():
    out = composite_render(
        comp.premultiply_key(
            image=image_node("src", SEMI).image, mapping="PREMUL_TO_STRAIGHT"
        )
    )
    assert_uniform(out, (0.5, 1.0, 1.5, 0.5))


def test_posterize_two_steps_quantises_a_ramp_to_black_grey_white():
    out = composite_render(comp.posterize(image=image_node("src", RAMP).image, steps=2))
    assert set(np.unique(out[..., 0].round(4)).tolist()) <= {0.0, 0.5, 1.0}


def test_posterize_four_steps_quantises_a_ramp_to_quarters():
    out = composite_render(comp.posterize(image=image_node("src", RAMP).image, steps=4))
    assert out[0, :, 0] == pytest.approx([0.0, 0.0, 0.25, 0.25, 0.5, 0.5, 0.75, 1.0])


def test_hue_correct_with_flat_curves_is_a_passthrough():
    out = composite_render(
        comp.hue_correct(image=image_node("src", COLOR).image, fac=1.0)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_rgb_curve_with_default_curves_is_a_passthrough():
    out = composite_render(
        comp.rgb_curve(fac=1.0, image=image_node("src", COLOR).image)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_rgb_curve_fac_zero_is_a_passthrough():
    out = composite_render(
        comp.rgb_curve(fac=0.0, image=image_node("src", COLOR).image)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_rgb_curve_black_level_at_the_input_value_maps_to_black():
    out = composite_render(
        comp.rgb_curve(
            fac=1.0,
            image=image_node("src", GREY).image,
            black_level=(0.5, 0.5, 0.5, 1.0),
        )
    )
    assert_uniform(out, (0.0, 0.0, 0.0, 1.0))


def test_color_correction_defaults_leave_the_image_alone():
    out = composite_render(comp.color_correction(image=image_node("src", COLOR).image))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_color_correction_zero_saturation_collapses_to_luma():
    out = composite_render(
        comp.color_correction(
            image=image_node("src", COLOR).image, master_saturation=0.0
        )
    )
    expected = 0.2126 * 0.25 + 0.7152 * 0.5 + 0.0722 * 0.75
    assert_uniform(out, (expected, expected, expected, 1.0))


def test_color_balance_fac_zero_leaves_the_image_alone():
    out = composite_render(
        comp.color_balance(image=image_node("src", COLOR).image, fac=0.0)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_convert_color_space_between_identical_spaces_is_a_passthrough():
    out = composite_render(
        comp.convert_color_space(
            image=image_node("src", COLOR).image,
            from_color_space="Non-Color",
            to_color_space="Non-Color",
        )
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_z_combine_keeps_the_nearer_of_the_two_images():
    out = composite_render(
        comp.z_combine(
            image_a=image_node("a", RED).image,
            z_a=0.0,
            image_b=image_node("b", GREEN).image,
            z_b=1.0,
        ).image
    )
    assert_uniform(out, (1.0, 0.0, 0.0, 1.0))


def test_z_combine_swaps_when_the_second_image_is_nearer():
    out = composite_render(
        comp.z_combine(
            image_a=image_node("a", RED).image,
            z_a=1.0,
            image_b=image_node("b", GREEN).image,
            z_b=0.0,
        ).image
    )
    assert_uniform(out, (0.0, 1.0, 0.0, 1.0))


def test_z_combine_z_output_is_the_nearer_depth():
    out = composite_render(
        comp.z_combine(
            image_a=image_node("a", RED).image,
            z_a=0.25,
            image_b=image_node("b", GREEN).image,
            z_b=1.0,
        ).z
    )
    assert_uniform(out, (0.25, 0.25, 0.25, 1.0))


# -------------------------------------------------------------- converter ----


def test_separate_yuv_y_matches_the_rec709_luma():
    out = composite_render(comp.separate_yuv(color=image_node("src", COLOR).image).y)
    expected = 0.2126 * 0.25 + 0.7152 * 0.5 + 0.0722 * 0.75
    assert_uniform(out, (expected, expected, expected, 1.0))


def test_separate_yuv_u_is_the_blue_difference():
    out = composite_render(comp.separate_yuv(color=image_node("src", COLOR).image).u)
    assert_uniform(out, (0.13397, 0.13397, 0.13397, 1.0))


def test_separate_ycc_defaults_to_the_itubt709_luma():
    out = composite_render(comp.separate_ycc(color=image_node("src", COLOR).image).y)
    assert_uniform(out, (0.46197, 0.46197, 0.46197, 1.0))


def test_separate_ycc_jfif_mode_uses_different_weights():
    out = composite_render(
        comp.separate_ycc(color=image_node("src", COLOR).image, ycc_mode="JFIF").y
    )
    assert_uniform(out, (0.45383, 0.45383, 0.45383, 1.0))


def test_combine_yuv_of_zero_is_black():
    assert_uniform(composite_render(comp.combine_yuv()), (0.0, 0.0, 0.0, 1.0))


def test_combine_yuv_luma_only_is_neutral_grey():
    out = composite_render(comp.combine_yuv(y=0.5, u=0.0, v=0.0))
    assert_uniform(out, (0.5, 0.5, 0.5, 1.0))


def test_separate_then_combine_yuv_round_trips_the_color():
    src = comp.separate_yuv(color=image_node("src", COLOR).image)
    out = composite_render(comp.combine_yuv(y=src.y, u=src.u, v=src.v))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_separate_then_combine_ycc_jfif_round_trips_the_color():
    src = comp.separate_ycc(
        color=image_node("src", COLOR).image,
        ycc_mode="JFIF",
    )
    out = composite_render(
        comp.combine_ycc(
            y=src.y,
            cb=src.cb,
            cr=src.cr,
            alpha=src.alpha,
            ycc_mode="JFIF",
        )
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_switch_check_true_selects_the_on_input():
    out = composite_render(
        comp.switch(
            check=True, off=image_node("a", RED).image, on=image_node("b", GREEN).image
        )
    )
    assert_uniform(out, (0.0, 1.0, 0.0, 1.0))


def test_switch_check_false_selects_the_off_input():
    out = composite_render(
        comp.switch(
            check=False, off=image_node("a", RED).image, on=image_node("b", GREEN).image
        )
    )
    assert_uniform(out, (1.0, 0.0, 0.0, 1.0))


def test_id_mask_without_a_matching_index_is_uniform():
    out = composite_render(
        comp.id_mask(id_value=image_node("src", BLACK).alpha, index=1)
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


def test_normal_dot_of_an_opposing_vector_is_minus_one():
    out = composite_render(comp.normal(normal=(0, 0, 1)).dot)
    assert_uniform(out, (-1.0, -1.0, -1.0, 1.0))


def test_normal_passes_its_vector_through():
    out = composite_render(comp.normal(normal=(0, 0, 1)).normal)
    assert_uniform(out, (0.0, 0.0, 1.0, 1.0))


def test_normalize_rescales_a_narrow_ramp_to_the_unit_range():
    out = composite_render(comp.normalize(value=image_node("src", NARROW_RAMP).image))
    assert out[..., 0].min() == pytest.approx(0.0)
    assert out[..., 0].max() == pytest.approx(1.0)


def test_map_value_size_scales_the_input():
    out = composite_render(
        comp.map_value(value=image_node("src", SEMI).alpha, size=(2.0,))
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


def test_map_value_offset_is_added_before_the_scale():
    out = composite_render(
        comp.map_value(value=image_node("src", SEMI).alpha, offset=(0.25,))
    )
    assert_uniform(out, (0.75, 0.75, 0.75, 1.0))


def test_map_value_use_max_clamps_the_result():
    out = composite_render(
        comp.map_value(
            value=image_node("src", SEMI).alpha, size=(4.0,), max=(1.0,), use_max=True
        )
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


# ----------------------------------------------------------------- filter ----


def test_blur_leaves_a_uniform_image_unchanged():
    out = composite_render(comp.blur(image=image_node("src", COLOR).image, size=3.0))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_blur_size_zero_leaves_a_step_edge_sharp():
    out = composite_render(comp.blur(image=image_node("src", STEP_X).image, size=0.0))
    assert set(np.unique(out[..., 0].round(4)).tolist()) == {0.0, 1.0}


def test_blur_explicit_zero_radii_leave_a_step_edge_sharp():
    out = composite_render(
        comp.blur(
            image=image_node("src", STEP_X).image,
            size=3.0,
            size_x=0,
            size_y=0,
        )
    )
    assert set(np.unique(out[..., 0].round(4)).tolist()) == {0.0, 1.0}


def test_blur_smooths_a_step_edge_into_intermediate_values():
    out = composite_render(comp.blur(image=image_node("src", STEP_X).image, size=3.0))
    row = out[0, :, 0]
    assert np.all(np.diff(row) >= -1e-6)
    assert ((row > 0.01) & (row < 0.99)).sum() >= 2


def test_filter_soften_smooths_a_step_edge():
    out = composite_render(
        comp.filter(image=image_node("src", STEP_X).image, filter_type="SOFTEN")
    )
    row = out[0, :, 0]
    assert ((row > 0.01) & (row < 0.99)).sum() >= 2


def test_filter_fac_zero_leaves_the_image_untouched():
    out = composite_render(
        comp.filter(image=image_node("src", STEP_X).image, filter_type="SOBEL", fac=0.0)
    )
    assert set(np.unique(out[..., 0].round(4)).tolist()) == {0.0, 1.0}


def test_filter_sharpen_leaves_a_uniform_image_unchanged():
    out = composite_render(
        comp.filter(image=image_node("src", COLOR).image, filter_type="SHARPEN")
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_bilateral_blur_leaves_a_uniform_image_unchanged():
    out = composite_render(comp.bilateral_blur(image=image_node("src", COLOR).image))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_bokeh_blur_leaves_a_uniform_image_unchanged():
    out = composite_render(
        comp.bokeh_blur(image=image_node("src", COLOR).image, size=2.0)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_defocus_leaves_a_uniform_image_unchanged():
    out = composite_render(comp.defocus(image=image_node("src", COLOR).image))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_despeckle_leaves_a_uniform_image_unchanged():
    out = composite_render(comp.despeckle(image=image_node("src", COLOR).image))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_inpaint_leaves_an_opaque_image_unchanged():
    out = composite_render(
        comp.inpaint(image=image_node("src", COLOR).image, distance=1)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_pixelate_leaves_a_uniform_image_unchanged():
    out = composite_render(comp.pixelate(color=image_node("src", COLOR).image))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_pixelate_averages_a_ramp_into_blocks():
    out = composite_render(
        comp.pixelate(color=image_node("src", RAMP).image, pixel_size=4)
    )
    assert out[0, :, 0] == pytest.approx([0.21428] * 4 + [0.78571] * 4, abs=1e-4)


def test_directional_blur_with_zero_distance_is_a_passthrough():
    out = composite_render(
        comp.directional_blur(image=image_node("src", COLOR).image, distance=0.0)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_anti_aliasing_leaves_a_uniform_image_unchanged():
    out = composite_render(comp.anti_aliasing(image=image_node("src", COLOR).image))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_denoise_of_a_uniform_image_keeps_each_channel_mean():
    out = composite_render(comp.denoise(image=image_node("src", COLOR).image))
    assert out[..., :3].mean(axis=(0, 1)) == pytest.approx([0.25, 0.5, 0.75], abs=0.1)


def test_kuwahara_leaves_a_uniform_image_unchanged():
    out = composite_render(comp.kuwahara(image=image_node("src", COLOR).image, size=2))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_dilate_erode_positive_distance_grows_the_bright_region():
    out = composite_render(
        comp.dilate_erode(mask=image_node("src", STEP_X).image, distance=2)
    )
    assert (out[0, :, 0] > 0.5).sum() > (STEP_X[0, :, 0] > 0.5).sum()


def test_dilate_erode_negative_distance_shrinks_the_bright_region():
    out = composite_render(
        comp.dilate_erode(mask=image_node("src", STEP_X).image, distance=-2)
    )
    assert (out[0, :, 0] > 0.5).sum() < (STEP_X[0, :, 0] > 0.5).sum()


def test_glare_fully_mixed_to_the_original_is_a_passthrough():
    out = composite_render(
        comp.glare_streaks(image=image_node("src", COLOR).image, mix=-1.0)
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_vector_blur_with_an_explicit_zero_speed_is_a_passthrough():
    out = composite_render(
        comp.vector_blur(
            image=image_node("src", COLOR).image, speed=(0, 0, 0), factor=0.0
        )
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


# ------------------------------------------------------------------ matte ----


def test_luma_matte_scales_the_image_by_the_matte():
    out = composite_render(
        comp.luma_matte(
            image=image_node("src", COLOR).image, limit_min=0.0, limit_max=0.5
        ).image
    )
    matte = (0.2126 * 0.25 + 0.7152 * 0.5 + 0.0722 * 0.75) / 0.5
    assert_uniform(out, (0.25 * matte, 0.5 * matte, 0.75 * matte, matte))


def test_luma_matte_matte_is_the_luma_rescaled_by_the_limits():
    out = composite_render(
        comp.luma_matte(
            image=image_node("src", COLOR).image, limit_min=0.0, limit_max=0.5
        ).matte
    )
    luma = 0.2126 * 0.25 + 0.7152 * 0.5 + 0.0722 * 0.75
    assert_uniform(out, (luma / 0.5, luma / 0.5, luma / 0.5, 1.0))


def test_diff_matte_of_identical_images_is_fully_keyed_out():
    out = composite_render(
        comp.diff_matte(
            a=image_node("a", RED).image, b=image_node("b", RED).image, tolerance=0.1
        ).matte
    )
    assert_uniform(out, (0.0, 0.0, 0.0, 1.0))


def test_diff_matte_of_different_images_is_fully_kept():
    out = composite_render(
        comp.diff_matte(
            a=image_node("a", RED).image, b=image_node("b", GREEN).image, tolerance=0.1
        ).matte
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


def test_color_matte_on_an_exact_key_removes_everything():
    out = composite_render(
        comp.color_matte(
            image=image_node("src", RED).image, key_color=(1, 0, 0, 1)
        ).matte
    )
    assert_uniform(out, (0.0, 0.0, 0.0, 1.0))


def test_distance_matte_on_an_exact_key_removes_everything():
    out = composite_render(
        comp.distance_matte(
            image=image_node("src", RED).image, key_color=(1, 0, 0, 1)
        ).matte
    )
    assert_uniform(out, (0.0, 0.0, 0.0, 1.0))


def test_channel_matte_defaults_keep_an_opaque_image():
    out = composite_render(
        comp.channel_matte(image=image_node("src", COLOR).image).matte
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


def test_channel_matte_limits_rescale_the_matte():
    out = composite_render(
        comp.channel_matte(
            image=image_node("src", COLOR).image,
            matte_channel="B",
            limit_channel="R",
            limit_method="SINGLE",
            limit_min=0.2,
            limit_max=1.0,
        ).matte
    )
    matte = (1.0 - (0.75 - 0.25) - 0.2) / (1.0 - 0.2)
    assert_uniform(out, (matte, matte, matte, 1.0))


def test_chroma_matte_defaults_keep_an_opaque_image():
    out = composite_render(
        comp.chroma_matte(image=image_node("src", COLOR).image).matte
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


def test_color_spill_removes_the_selected_channel():
    out = composite_render(
        comp.color_spill(image=image_node("src", GREEN).image, channel="G", ratio=1.0)
    )
    assert_uniform(out, (0.0, 0.0, 0.0, 1.0))


def test_keying_on_an_exact_key_color_produces_an_empty_matte():
    out = composite_render(
        comp.keying(image=image_node("src", GREEN).image, key_color=(0, 1, 0, 1)).matte
    )
    assert_uniform(out, (0.0, 0.0, 0.0, 1.0))


def test_box_mask_with_zero_size_leaves_the_mask_input_untouched():
    out = composite_render(
        comp.box_mask(mask_width=0.0, mask_height=0.0, mask=0.0, value=1.0)
    )
    assert_uniform(out, (0.0, 0.0, 0.0, 1.0))


def test_box_mask_covering_the_frame_fills_the_whole_image():
    out = composite_render(
        comp.box_mask(mask_width=2.0, mask_height=2.0, mask=0.0, value=1.0)
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


def test_double_edge_mask_marks_the_region_between_the_two_masks():
    inner = np.zeros((N, N, 4), dtype=np.float32)
    inner[..., 3] = 1.0
    inner[3:5, 3:5, :3] = 1.0
    outer = np.zeros((N, N, 4), dtype=np.float32)
    outer[..., 3] = 1.0
    outer[2:6, 2:6, :3] = 1.0
    out = composite_render(
        comp.double_edge_mask(
            inner_mask=image_node("inner", inner).image,
            outer_mask=image_node("outer", outer).image,
        )
    )
    assert out[3, :, 0] == pytest.approx([0, 0, 0, 1, 1, 0, 0, 0])


def test_ellipse_mask_covering_the_frame_fills_the_whole_image():
    out = composite_render(
        comp.ellipse_mask(mask_width=2.0, mask_height=2.0, mask=0.0, value=1.0)
    )
    assert_uniform(out, (1.0, 1.0, 1.0, 1.0))


def test_mask_without_a_datablock_is_black():
    assert_uniform(composite_render(comp.mask()), (0.0, 0.0, 0.0, 1.0))


# ---------------------------------------------------------------- distort ----


def test_flip_x_mirrors_a_horizontal_step_edge():
    out = composite_render(comp.flip(image=image_node("src", STEP_X).image, axis="X"))
    assert out[0, :, 0] == pytest.approx(STEP_X[0, ::-1, 0])


def test_flip_y_mirrors_a_vertical_step_edge():
    out = composite_render(comp.flip(image=image_node("src", STEP_Y).image, axis="Y"))
    assert out[:, 0, 0] == pytest.approx(STEP_Y[::-1, 0, 0])


def test_flip_xy_mirrors_both_axes():
    out = composite_render(
        comp.flip(image=image_node("src", ASYMMETRIC).image, axis="XY")
    )
    assert out == pytest.approx(ASYMMETRIC[::-1, ::-1])


def test_scale_identity_leaves_a_step_edge_in_place():
    out = composite_render(
        comp.scale_relative(image=image_node("src", STEP_X).image, x=1.0, y=1.0)
    )
    assert out[0, :, 0] == pytest.approx(STEP_X[0, :, 0])


def test_scale_relative_double_enlarges_the_image_about_its_center():
    out = composite_render(
        comp.scale_relative(image=image_node("src", ASYMMETRIC).image, x=2.0, y=2.0)
    )
    expected = 14 + 4 * np.arange(N)[:, None] + 0.5 * np.arange(N)[None, :]
    assert out[..., 0] == pytest.approx(expected)


def test_rotate_by_zero_leaves_the_image_in_place():
    out = composite_render(comp.rotate(image=image_node("src", STEP_X).image, degr=0.0))
    assert out[0, :, 0] == pytest.approx(STEP_X[0, :, 0])


def test_rotate_by_a_quarter_turn_moves_the_bright_quadrant_down():
    out = composite_render(
        comp.rotate(
            image=image_node("src", CORNER).image,
            degr=np.pi / 2,
            filter_type="NEAREST",
        )
    )
    assert out[5:, 1:4, 0] == pytest.approx(1.0)
    assert out[:3, 1:4, 0] == pytest.approx(0.0)


@pytest.mark.xfail(
    strict=True,
    reason="bpy 4.2 rotates about a half-pixel-offset centre, shifting the result one row",
)
def test_rotate_by_pi_mirrors_the_image():
    out = composite_render(
        comp.rotate(image=image_node("src", STEP_X).image, degr=np.pi)
    )
    assert out[0, :, 0] == pytest.approx(STEP_X[0, ::-1, 0])


def test_transform_identity_leaves_the_image_in_place():
    out = composite_render(
        comp.transform(image=image_node("src", STEP_X).image, scale=1.0)
    )
    assert out[0, :, 0] == pytest.approx(STEP_X[0, :, 0])


def test_transform_x_shifts_the_step_edge_right():
    out = composite_render(
        comp.transform(image=image_node("src", STEP_X).image, x=2.0, scale=1.0)
    )
    assert out[0, :, 0] == pytest.approx([0, 0, 0, 0, 0, 0, 1, 1])


def test_translate_by_zero_leaves_the_image_in_place():
    out = composite_render(
        comp.translate(image=image_node("src", STEP_X).image, x=0.0, y=0.0)
    )
    assert out[0, :, 0] == pytest.approx(STEP_X[0, :, 0])


def test_translate_shifts_the_step_edge_along_x():
    out = composite_render(
        comp.translate(image=image_node("src", STEP_X).image, x=2.0, y=0.0)
    )
    assert out[0, :, 0] == pytest.approx([0, 0, 0, 0, 0, 0, 1, 1])


def test_translate_with_x_wrapping_brings_the_edge_around():
    out = composite_render(
        comp.translate(
            image=image_node("src", STEP_X).image, x=4.0, y=0.0, wrap_axis="XAXIS"
        )
    )
    assert out[0, :, 0] == pytest.approx([1, 1, 1, 1, 0, 0, 0, 0])


@pytest.mark.xfail(
    strict=True,
    reason="bpy 4.2 crop blanks the kept region too, leaving an entirely black image",
)
def test_crop_keeps_the_region_and_blanks_everything_outside_it():
    out = composite_render(
        comp.crop(
            image=image_node("src", WHITE).image, min_x=2, max_x=6, min_y=2, max_y=6
        )
    )
    assert out[0, :, 0] == pytest.approx(np.zeros(N))
    assert out[N // 2, :, 0] == pytest.approx([0, 0, 1, 1, 1, 1, 0, 0])


def test_lens_distortion_with_zero_distortion_is_a_passthrough():
    out = composite_render(
        comp.lens_distortion(
            image=image_node("src", COLOR).image, distortion=0.0, dispersion=0.0
        )
    )
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_movie_distortion_without_a_clip_is_a_passthrough():
    out = composite_render(comp.movie_distortion(image=image_node("src", COLOR).image))
    assert_uniform(out, (0.25, 0.5, 0.75, 1.0))


def test_displace_with_an_explicit_zero_vector_is_a_passthrough():
    out = composite_render(
        comp.displace(
            image=image_node("src", STEP_X).image,
            vector=(0, 0, 0),
            x_scale=0.0,
            y_scale=0.0,
        )
    )
    assert out[0, :, 0] == pytest.approx(STEP_X[0, :, 0])


def test_corner_pin_with_the_frame_corners_is_a_passthrough():
    corners = {
        "upper_left": (0, 1, 0),
        "upper_right": (1, 1, 0),
        "lower_left": (0, 0, 0),
        "lower_right": (1, 0, 0),
    }
    out = composite_render(
        comp.corner_pin(image=image_node("src", STEP_X).image, **corners).image
    )
    assert out[0, :, 0] == pytest.approx(STEP_X[0, :, 0])


def test_split_factor_fifty_puts_the_second_image_on_the_left_half():
    out = composite_render(
        comp.split(
            a=image_node("a", RED).image,
            b=image_node("b", GREEN).image,
            factor=50,
            axis="X",
        )
    )
    expected_a = [0] * 4 + [1] * (N - 4)
    assert out[0, :, 0] == pytest.approx(expected_a)
    assert out[0, :, 1] == pytest.approx([1 - v for v in expected_a])


def test_split_factor_zero_shows_only_the_first_image():
    out = composite_render(
        comp.split(
            a=image_node("a", RED).image,
            b=image_node("b", GREEN).image,
            factor=0,
            axis="X",
        )
    )
    assert_uniform(out, (1.0, 0.0, 0.0, 1.0))


def test_split_factor_one_hundred_shows_only_the_second_image():
    out = composite_render(
        comp.split(
            a=image_node("a", RED).image,
            b=image_node("b", GREEN).image,
            factor=100,
            axis="X",
        )
    )
    assert_uniform(out, (0.0, 1.0, 0.0, 1.0))


def test_split_axis_y_puts_the_first_image_on_the_top_half():
    out = composite_render(
        comp.split(
            a=image_node("a", RED).image,
            b=image_node("b", GREEN).image,
            factor=50,
            axis="Y",
        )
    )
    assert out[:, 0, 0] == pytest.approx([1, 1, 1, 1, 0, 0, 0, 0])


# --------------------------------------------------- every binding's defaults ----


@pytest.mark.parametrize(
    ("binding_name", "expected", "tolerance"),
    [
        pytest.param(name, (1.0, 1.0, 1.0, 1.0), 1e-4, id=name)
        for name in (
            "alpha_over",
            "anti_aliasing",
            "bilateral_blur",
            "blur",
            "bokeh_image",
            "bright_contrast",
            "color_correction",
            "color_spill",
            "defocus",
            "despeckle",
            "directional_blur",
            "exposure",
            "filter",
            "gamma",
            "glare_bloom",
            "glare_fog_glow",
            "glare_ghosts",
            "glare_simple_star",
            "glare_streaks",
            "hue_correct",
            "inpaint",
            "kuwahara",
            "map_value",
            "mix_rgb",
            "posterize",
            "premultiply_key",
        )
    ]
    + [
        pytest.param(name, (0.8, 0.8, 0.8, 1.0), 1e-4, id=name)
        for name in (
            "bokeh_blur",
            "pixelate",
            "rgb_to_bw",
            "switch",
        )
    ]
    + [
        pytest.param(name, (0.0, 0.0, 0.0, 1.0), 1e-4, id=name)
        for name in (
            "box_mask",
            "combine_yuv",
            "dilate_erode",
            "ellipse_mask",
            "id_mask",
            "switch_view",
            "time",
        )
    ]
    + [pytest.param("color_balance", (1.0, 1.0, 1.0, 1.0), 1e-3, id="color_balance")],
)
def test_binding_defaults_render_expected_uniform_pixels(
    binding_name: str, expected: tuple[float, float, float, float], tolerance: float
) -> None:
    result = getattr(comp, binding_name)()
    assert_uniform(composite_render(result), expected, tol=tolerance)


def test_invert_defaults_invert_the_white_default_to_black():
    assert_uniform(composite_render(comp.invert()), (0.0, 0.0, 0.0, 1.0))


def test_normal_defaults_build_and_render():
    assert_uniform(composite_render(comp.normal().normal), (0.0, 0.0, 1.0, 1.0))


def test_levels_defaults_build_and_render():
    assert_uniform(composite_render(comp.levels().mean), (0.0, 0.0, 0.0, 1.0))


def test_scene_time_defaults_report_the_first_frame_time():
    out = composite_render(comp.scene_time().seconds)
    assert_uniform(out, (1 / 24, 1 / 24, 1 / 24, 1.0))


def test_scene_time_frame_output_is_the_current_frame():
    assert_uniform(composite_render(comp.scene_time().frame), (1.0, 1.0, 1.0, 1.0))


def test_channel_matte_defaults_build_and_render():
    assert_uniform(composite_render(comp.channel_matte().image), (1.0, 1.0, 1.0, 1.0))


def test_separate_yuv_defaults_build_and_render():
    out = composite_render(comp.separate_yuv(color=(0.25, 0.5, 0.75, 1.0)).y)
    expected = 0.2126 * 0.25 + 0.7152 * 0.5 + 0.0722 * 0.75
    assert_uniform(out, (expected, expected, expected, 1.0))


def test_z_combine_defaults_build_and_render():
    assert_uniform(composite_render(comp.z_combine().image), (1.0, 1.0, 1.0, 1.0))


def test_diff_matte_defaults_build_and_render():
    assert composite_render(comp.diff_matte().image)[..., :3] == pytest.approx(0.0)


def test_distance_matte_defaults_build_and_render():
    assert composite_render(comp.distance_matte().image)[..., :3] == pytest.approx(0.0)


def test_color_matte_defaults_build_and_render():
    assert composite_render(comp.color_matte().image)[..., :3] == pytest.approx(0.0)


def test_chroma_matte_defaults_build_and_render():
    assert composite_render(comp.chroma_matte().image)[..., :3] == pytest.approx(0.0)
