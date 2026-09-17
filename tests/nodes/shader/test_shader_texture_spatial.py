from pathlib import Path

import bpy
import numpy as np
import pytest
import shader_eval

import procfunc as pf

texture = pf.nodes.texture
shader = pf.nodes.shader
pytestmark = pytest.mark.render
UV = shader.coord().uv

IES_PROFILE = """IESNA:LM-63-1995
TILT=NONE
1 1000 1.0 3 1 1 2 0.0 0.0 0.0
1.0 1.0 0.0
0 45 90
0
1000.0 500.0 100.0
"""


@pytest.mark.parametrize(
    "source,node_type,inputs,properties,output",
    [
        (
            texture.brick(
                UV,
                color1=pf.Color((0.7, 0.1, 0.2)),
                color2=pf.Color((0.3, 0.8, 0.4)),
                mortar=pf.Color((0.05, 0.15, 0.9)),
                scale=4.0,
                mortar_size=0.07,
                bias=0.3,
                brick_width=0.4,
                offset=0.25,
                squash=0.6,
            ).color,
            "ShaderNodeTexBrick",
            {
                "Color1": (0.7, 0.1, 0.2, 1),
                "Color2": (0.3, 0.8, 0.4, 1),
                "Mortar": (0.05, 0.15, 0.9, 1),
                "Scale": 4.0,
                "Mortar Size": 0.07,
                "Bias": 0.3,
                "Brick Width": 0.4,
            },
            {"offset": 0.25, "squash": 0.6},
            "Color",
        ),
        (
            texture.magic(UV, scale=4.0, distortion=1.5, turbulence_depth=3).fac,
            "ShaderNodeTexMagic",
            {"Scale": 4.0, "Distortion": 1.5},
            {"turbulence_depth": 3},
            "Fac",
        ),
        (
            texture.white_noise(UV, noise_dimensions="4D", w=0.7).fac,
            "ShaderNodeTexWhiteNoise",
            {"W": 0.7},
            {"noise_dimensions": "4D"},
            "Value",
        ),
        (
            texture.voronoi_distance(
                UV, scale=4.0, randomness=0.6, detail=3.0, roughness=0.8
            ),
            "ShaderNodeTexVoronoi",
            {"Scale": 4.0, "Randomness": 0.6, "Detail": 3.0, "Roughness": 0.8},
            {"feature": "DISTANCE_TO_EDGE", "voronoi_dimensions": "3D"},
            "Distance",
        ),
        (
            texture.voronoi_n_spheres_distance(UV, scale=4.0, randomness=0.6),
            "ShaderNodeTexVoronoi",
            {"Scale": 4.0, "Randomness": 0.6},
            {"feature": "N_SPHERE_RADIUS", "voronoi_dimensions": "3D"},
            "Radius",
        ),
        (
            texture.noise(
                UV,
                scale=4.0,
                detail=3.0,
                roughness=0.7,
                lacunarity=2.5,
                distortion=0.2,
                noise_type="MULTIFRACTAL",
            ).fac,
            "ShaderNodeTexNoise",
            {
                "Scale": 4.0,
                "Detail": 3.0,
                "Roughness": 0.7,
                "Lacunarity": 2.5,
                "Distortion": 0.2,
            },
            {"noise_type": "MULTIFRACTAL"},
            "Fac",
        ),
        (
            texture.wave(
                UV,
                scale=4.0,
                distortion=1.5,
                detail=3.0,
                phase_offset=0.4,
                wave_profile="SAW",
                wave_type="RINGS",
            ).fac,
            "ShaderNodeTexWave",
            {"Scale": 4.0, "Distortion": 1.5, "Detail": 3.0, "Phase Offset": 0.4},
            {"wave_profile": "SAW", "wave_type": "RINGS"},
            "Fac",
        ),
    ],
    ids=[
        "brick",
        "magic",
        "white_noise",
        "voronoi_distance",
        "voronoi_radius",
        "noise",
        "wave",
    ],
)
def test_texture_matches_native(
    source: pf.ProcNode, node_type: str, inputs: dict, properties: dict, output: str
) -> None:
    tree = shader_eval._nodegroup(source)
    bound = next(node for node in tree.nodes if node.bl_idname == node_type)
    output_link = tree.nodes["Group Output"].inputs[0].links[0]
    assert output_link.from_socket == bound.outputs[output]
    for name, value in properties.items():
        expected = pytest.approx(value) if isinstance(value, float) else value
        assert getattr(bound, name) == expected
    for name, value in inputs.items():
        np.testing.assert_allclose(bound.inputs[name].default_value, value)

    def native(tree: bpy.types.NodeTree) -> bpy.types.NodeSocket:
        coord = tree.nodes.new("ShaderNodeTexCoord")
        node = tree.nodes.new(node_type)
        for name, value in properties.items():
            setattr(node, name, value)
        for name, value in inputs.items():
            node.inputs[name].default_value = value
        tree.links.new(coord.outputs["UV"], node.inputs["Vector"])
        return node.outputs[output]

    shader_eval.assert_image(shader_eval.render(source), shader_eval.render(native))


def test_brick_swapping_the_two_colours_swaps_the_render() -> None:
    forwards = shader_eval.render(
        texture.brick(
            UV, color1=pf.Color((1, 0, 0)), color2=pf.Color((0, 1, 0)), scale=4.0
        ).color
    )
    backwards = shader_eval.render(
        texture.brick(
            UV, color1=pf.Color((0, 1, 0)), color2=pf.Color((1, 0, 0)), scale=4.0
        ).color
    )
    shader_eval.assert_image(forwards[..., [1, 0, 2]], backwards)


@pytest.mark.parametrize("detail,changes", [(0.0, False), (6.0, True)])
def test_noise_roughness_weights_later_octaves(detail: float, changes: bool) -> None:
    low = shader_eval.render(
        texture.noise(UV, scale=4.0, detail=detail, roughness=0.1).fac
    )
    high = shader_eval.render(
        texture.noise(UV, scale=4.0, detail=detail, roughness=0.9).fac
    )
    if changes:
        shader_eval.assert_differs(low, high)
    else:
        shader_eval.assert_image(low, high)


@pytest.mark.parametrize("engine", [shader_eval.CYCLES, shader_eval.EEVEE])
def test_gradient_linear_is_the_u_coordinate(engine: str) -> None:
    frame = shader_eval.render(
        texture.gradient(UV, gradient_type="LINEAR").fac, engine=engine
    )
    expected = np.repeat(shader_eval.uv_grid()[..., :1], 3, axis=-1)
    interior = shader_eval.INTERIOR
    shader_eval.assert_image(frame[interior], expected[interior], atol=5e-3)


def test_checker_fac_is_binary() -> None:
    frame = shader_eval.render(texture.checker(UV, scale=4.0).fac)
    assert set(np.unique(np.round(frame[shader_eval.INTERIOR], 3)).tolist()) == {
        0.0,
        1.0,
    }


def _ramp_image(size: int = 8) -> pf.Image:
    raw = bpy.data.images.new("shader_eval_ramp", size, size, float_buffer=True)
    raw.colorspace_settings.name = "Non-Color"
    row, col = np.mgrid[:size, :size] / (size - 1)
    pixels = np.stack((col, row, np.full_like(row, 0.5), np.ones_like(row)), axis=-1)
    raw.pixels.foreach_set(pixels.astype(np.float32).ravel())
    raw.update()
    return pf.Image(raw)


def test_environment_reads_the_image() -> None:
    frame = shader_eval.render(texture.environment(UV, _ramp_image()))
    np.testing.assert_allclose(frame[..., 2], 0.5, atol=1e-6)
    shader_eval.assert_varies(frame)


def test_environment_projection_changes_the_lookup() -> None:
    image = _ramp_image()
    equirectangular = shader_eval.render(
        texture.environment(UV, image, projection="EQUIRECTANGULAR")
    )
    mirror_ball = shader_eval.render(
        texture.environment(UV, image, projection="MIRROR_BALL")
    )
    shader_eval.assert_varies(equirectangular)
    shader_eval.assert_differs(equirectangular, mirror_ball, threshold=0.1)


@pytest.mark.parametrize("strength,expected", [(1.0, 100.0), (2.5, 250.0)])
def test_ies_reads_and_scales_external_profile(
    tmp_path: Path, strength: float, expected: float
) -> None:
    path = tmp_path / "profile.ies"
    path.write_text(IES_PROFILE)
    node = texture.ies(
        shader.geometry().position,
        strength=strength,
        filepath=str(path),
        mode="EXTERNAL",
    )
    shader_eval.assert_value(
        shader_eval.render(node, engine=shader_eval.CYCLES), expected
    )


def test_image_interpolation_changes_the_lookup() -> None:
    image = _ramp_image(4)
    closest = shader_eval.render(
        texture.image(UV, image, interpolation="Closest").color
    )
    linear = shader_eval.render(texture.image(UV, image, interpolation="Linear").color)
    shader_eval.assert_varies(closest)
    shader_eval.assert_differs(closest, linear)
