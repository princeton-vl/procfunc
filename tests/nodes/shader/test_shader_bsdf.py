from collections.abc import Callable

import bpy
import numpy as np
import pytest
import shader_eval

import procfunc as pf

shader = pf.nodes.shader
ALBEDO = pf.Color((0.8, 0.2, 0.1))
LAMBERT = tuple(c / np.pi for c in (0.8, 0.2, 0.1))


@pytest.mark.parametrize(
    "source,expected,world",
    [
        (shader.diffuse_bsdf(color=ALBEDO), LAMBERT, (0, 0, 0)),
        (
            shader.emission(pf.Color((0.5, 0.25, 0.125)), 2.0),
            (1.0, 0.5, 0.25),
            (0, 0, 0),
        ),
        (shader.background(pf.Color((0.2, 0.4, 0.6)), 2.0), (0.4, 0.8, 1.2), (0, 0, 0)),
        (
            shader.transparent_bsdf(color=pf.Color((1.0, 0.0, 0.5))),
            (0.3, 0.0, 0.25),
            (0.3, 0.4, 0.5),
        ),
        (shader.holdout(), (0.0, 0.0, 0.0), (0.3, 0.4, 0.5)),
        (
            shader.glass_bsdf(color=ALBEDO, roughness=0.0),
            (0.24, 0.08, 0.05),
            (0.3, 0.4, 0.5),
        ),
        (
            shader.refraction_bsdf(color=ALBEDO, roughness=0.0),
            (0.24, 0.08, 0.05),
            (0.3, 0.4, 0.5),
        ),
        (shader.ray_portal_bsdf(color=ALBEDO), (0.24, 0.08, 0.05), (0.3, 0.4, 0.5)),
    ],
    ids=[
        "diffuse",
        "emission",
        "background",
        "transparent",
        "holdout",
        "glass",
        "refraction",
        "ray_portal",
    ],
)
def test_surface_light_transport(
    source: pf.ProcNode, expected: tuple, world: tuple
) -> None:
    shader_eval.assert_value(shader_eval.render_shader(source, world=world), expected)


def test_add_shader_sums_its_inputs() -> None:
    node = shader.add_shader(
        shader.emission(pf.Color((0.1, 0.2, 0.3)), 1.0),
        shader.emission(pf.Color((0.4, 0.1, 0.2)), 1.0),
    )
    shader_eval.assert_value(shader_eval.render_shader(node), (0.5, 0.3, 0.5))


@pytest.mark.parametrize("factor,expected", [(0.0, 0.4), (0.25, 0.5), (1.0, 0.8)])
def test_mix_shader_interpolates_towards_b(factor: float, expected: float) -> None:
    dim = shader.emission(pf.Color((0.4, 0.4, 0.4)), 1.0)
    bright = shader.emission(pf.Color((0.8, 0.8, 0.8)), 1.0)
    node = shader.mix_shader(factor, dim, bright)
    shader_eval.assert_value(shader_eval.render_shader(node), expected)


@pytest.mark.parametrize(
    "source,node_type,inputs,properties,render",
    [
        (
            shader.glass_bsdf(color=ALBEDO, roughness=0.2, ior=1.7, distribution="GGX"),
            "ShaderNodeBsdfGlass",
            {"Color": (0.8, 0.2, 0.1, 1), "Roughness": 0.2, "IOR": 1.7},
            {"distribution": "GGX"},
            shader_eval.render_cube,
        ),
        (
            shader.refraction_bsdf(
                color=ALBEDO, roughness=0.8, ior=1.7, distribution="GGX"
            ),
            "ShaderNodeBsdfRefraction",
            {"Color": (0.8, 0.2, 0.1, 1), "Roughness": 0.8, "IOR": 1.7},
            {"distribution": "GGX"},
            shader_eval.render_cube,
        ),
        (
            shader.toon_bsdf(color=ALBEDO, size=0.4, smooth=0.2, component="GLOSSY"),
            "ShaderNodeBsdfToon",
            {"Color": (0.8, 0.2, 0.1, 1), "Size": 0.4, "Smooth": 0.2},
            {"component": "GLOSSY"},
            shader_eval.render_cube,
        ),
        (
            shader.sheen_bsdf(color=ALBEDO, roughness=0.3, distribution="ASHIKHMIN"),
            "ShaderNodeBsdfSheen",
            {"Color": (0.8, 0.2, 0.1, 1), "Roughness": 0.3},
            {"distribution": "ASHIKHMIN"},
            shader_eval.render_cube,
        ),
        (
            shader.anisotropic_bsdf(
                color=ALBEDO,
                roughness=0.35,
                anisotropy=0.6,
                rotation=0.2,
                distribution="GGX",
            ),
            "ShaderNodeBsdfAnisotropic",
            {
                "Color": (0.8, 0.2, 0.1, 1),
                "Roughness": 0.35,
                "Anisotropy": 0.6,
                "Rotation": 0.2,
            },
            {"distribution": "GGX"},
            shader_eval.render_cube,
        ),
        (
            shader.principled_bsdf(
                base_color=ALBEDO,
                metallic=0.3,
                roughness=0.4,
                ior=1.6,
                emission_color=pf.Color((0.5, 0.25, 0.125)),
                emission_strength=2.0,
            ),
            "ShaderNodeBsdfPrincipled",
            {
                "Base Color": (0.8, 0.2, 0.1, 1),
                "Metallic": 0.3,
                "Roughness": 0.4,
                "IOR": 1.6,
                "Emission Color": (0.5, 0.25, 0.125, 1),
                "Emission Strength": 2.0,
            },
            {},
            shader_eval.render_cube,
        ),
        (
            shader.subsurface_scattering_burley(color=ALBEDO, scale=0.2),
            "ShaderNodeSubsurfaceScattering",
            {"Color": (0.8, 0.2, 0.1, 1), "Scale": 0.2},
            {"falloff": "BURLEY"},
            shader_eval.render_shader,
        ),
        (
            shader.subsurface_scattering_random_walk(
                color=ALBEDO, scale=0.2, ior=1.3, roughness=0.5, anisotropy=0.4
            ),
            "ShaderNodeSubsurfaceScattering",
            {
                "Color": (0.8, 0.2, 0.1, 1),
                "Scale": 0.2,
                "IOR": 1.3,
                "Roughness": 0.5,
                "Anisotropy": 0.4,
            },
            {"falloff": "RANDOM_WALK"},
            shader_eval.render_shader,
        ),
        (
            shader.subsurface_scattering_random_walk_skin(
                color=ALBEDO, scale=0.2, ior=1.3, anisotropy=0.4
            ),
            "ShaderNodeSubsurfaceScattering",
            {"Color": (0.8, 0.2, 0.1, 1), "Scale": 0.2, "IOR": 1.3, "Anisotropy": 0.4},
            {"falloff": "RANDOM_WALK_SKIN"},
            shader_eval.render_shader,
        ),
        (
            shader.hair_bsdf(
                color=ALBEDO,
                offset=0.05,
                roughness_u=0.2,
                roughness_v=0.6,
                component="Transmission",
            ),
            "ShaderNodeBsdfHair",
            {
                "Color": (0.8, 0.2, 0.1, 1),
                "Offset": 0.05,
                "RoughnessU": 0.2,
                "RoughnessV": 0.6,
            },
            {"component": "Transmission"},
            shader_eval.render_hair,
        ),
        (
            shader.principled_hair_bsdf_chiang(
                color=ALBEDO, roughness=0.25, radial_roughness=0.4, coat=0.3, ior=1.6
            ),
            "ShaderNodeBsdfHairPrincipled",
            {
                "Color": (0.8, 0.2, 0.1, 1),
                "Roughness": 0.25,
                "Radial Roughness": 0.4,
                "Coat": 0.3,
                "IOR": 1.6,
            },
            {"model": "CHIANG", "parametrization": "COLOR"},
            shader_eval.render_hair,
        ),
        (
            shader.principled_hair_bsdf_huang(
                color=ALBEDO, roughness=0.25, aspect_ratio=0.7, ior=1.6
            ),
            "ShaderNodeBsdfHairPrincipled",
            {
                "Color": (0.8, 0.2, 0.1, 1),
                "Roughness": 0.25,
                "Aspect Ratio": 0.7,
                "IOR": 1.6,
            },
            {"model": "HUANG", "parametrization": "COLOR"},
            shader_eval.render_hair,
        ),
        (
            shader.volume_scatter(color=ALBEDO, density=1.5, anisotropy=0.4),
            "ShaderNodeVolumeScatter",
            {"Color": (0.8, 0.2, 0.1, 1), "Density": 1.5, "Anisotropy": 0.4},
            {},
            shader_eval.render_volume,
        ),
        (
            shader.volume_principled(color=ALBEDO, density=1.2, anisotropy=0.3),
            "ShaderNodeVolumePrincipled",
            {"Color": (0.8, 0.2, 0.1, 1), "Density": 1.2, "Anisotropy": 0.3},
            {},
            shader_eval.render_volume,
        ),
    ],
    ids=[
        "glass",
        "refraction",
        "toon",
        "sheen",
        "anisotropic",
        "principled",
        "burley",
        "random_walk",
        "random_walk_skin",
        "hair",
        "chiang",
        "huang",
        "volume_scatter",
        "volume_principled",
    ],
)
def test_shader_matches_native(
    source: pf.ProcNode,
    node_type: str,
    inputs: dict,
    properties: dict,
    render: Callable,
) -> None:
    tree = shader_eval._nodegroup(source)
    bound = next(node for node in tree.nodes if node.bl_idname == node_type)
    for name, value in properties.items():
        assert getattr(bound, name) == value
    for name, value in inputs.items():
        np.testing.assert_allclose(bound.inputs[name].default_value, value)

    def native(tree: bpy.types.NodeTree) -> bpy.types.NodeSocket:
        node = tree.nodes.new(node_type)
        for name, value in properties.items():
            setattr(node, name, value)
        for name, value in inputs.items():
            node.inputs[name].default_value = value
        return node.outputs[0]

    shader_eval.assert_image(render(source), render(native), atol=1e-4)


def test_eevee_specular_matches_native() -> None:
    source = shader.eevee_specular(
        base_color=ALBEDO,
        roughness=0.3,
        emissive_color=pf.Color((0.2, 0.1, 0.05)),
        specular=pf.Color((0.1, 0.15, 0.05)),
    )

    def native(tree: bpy.types.NodeTree) -> bpy.types.NodeSocket:
        node = tree.nodes.new("ShaderNodeEeveeSpecular")
        node.inputs["Base Color"].default_value = (0.8, 0.2, 0.1, 1)
        node.inputs["Specular"].default_value = (0.1, 0.15, 0.05, 1)
        node.inputs["Roughness"].default_value = 0.3
        node.inputs["Emissive Color"].default_value = (0.2, 0.1, 0.05, 1)
        return node.outputs[0]

    actual = shader_eval.render_shader(source, engine=shader_eval.EEVEE)
    expected = shader_eval.render_shader(native, engine=shader_eval.EEVEE)
    shader_eval.assert_image(actual, expected)


def test_translucent_bsdf_transmits_light_from_behind() -> None:
    shader_eval.assert_value(
        shader_eval.render_backlit(shader.translucent_bsdf(color=ALBEDO)), LAMBERT
    )


def test_hair_bsdf_keeps_the_colour_ratio_on_strands() -> None:
    lit = shader_eval.probe(shader_eval.render_hair(shader.hair_bsdf(color=ALBEDO)))
    assert lit[0] > 0.05
    np.testing.assert_allclose(lit[1:] / lit[0], [0.25, 0.125], rtol=1e-2)


def test_volume_scatter_lights_the_cube_interior() -> None:
    frame = shader_eval.render_volume(shader.volume_scatter(color=ALBEDO, density=1.0))
    lit = shader_eval.probe(frame)
    assert lit[0] > lit[1] > lit[2] > 0.0


def test_volume_absorption_follows_beer_lambert() -> None:
    color = np.array([0.9, 0.5, 0.2])
    frame = shader_eval.render_volume(
        shader.volume_absorption(color=pf.Color(tuple(color)), density=1.0),
        world=(0.5, 0.5, 0.5),
    )
    thickness = shader_eval.CUBE_VERTS[6][2] - shader_eval.CUBE_VERTS[0][2]
    np.testing.assert_allclose(
        shader_eval.probe(frame), 0.5 * np.exp(-(1.0 - color) * thickness), rtol=2e-3
    )


def test_volume_principled_emission_integrates_over_the_path() -> None:
    node = shader.volume_principled(
        density=0.0, emission_strength=1.0, emission_color=pf.Color((0.25, 0.5, 0.75))
    )
    thickness = shader_eval.CUBE_VERTS[6][2] - shader_eval.CUBE_VERTS[0][2]
    expected = np.array([0.25, 0.5, 0.75]) * thickness
    np.testing.assert_allclose(
        shader_eval.probe(shader_eval.render_volume(node)), expected, rtol=2e-3
    )


@pytest.mark.parametrize(
    "flat,raised",
    [
        (
            shader.displacement(height=0.0, midlevel=0.0, scale=1.0),
            shader.displacement(height=0.5, midlevel=0.0, scale=1.0),
        ),
        (
            shader.vector_displacement(vector=pf.Vector((0.0, 0.0, 0.0))),
            shader.vector_displacement(vector=pf.Vector((0.0, 0.0, 0.5))),
        ),
    ],
    ids=["scalar", "vector"],
)
def test_displacement_moves_the_silhouette(
    flat: pf.ProcNode, raised: pf.ProcNode
) -> None:
    shader_eval.assert_differs(
        shader_eval.render_displacement(flat),
        shader_eval.render_displacement(raised),
        threshold=0.5,
    )
