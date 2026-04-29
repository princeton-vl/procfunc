"""
Auto-generated Shader Node bindings for Blender
"""

import logging
from typing import Any, Literal, NamedTuple

import procfunc as pf
from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import (
    raise_error_or_warn,
    raise_explicit_noise_vector_error,
    raise_io_error,
    raise_shader_normal_error,
)

TBlendType = Literal[
    "MIX",
    "DARKEN",
    "MULTIPLY",
    "BURN",
    "LIGHTEN",
    "SCREEN",
    "DODGE",
    "ADD",
    "OVERLAY",
    "SOFT_LIGHT",
    "LINEAR_LIGHT",
    "DIFFERENCE",
    "EXCLUSION",
    "SUBTRACT",
    "DIVIDE",
    "HUE",
    "SATURATION",
    "COLOR",
    "VALUE",
]
TRenderTarget = Literal["ALL", "EEVEE", "CYCLES"]

logger = logging.getLogger(__name__)


def add_shader(
    shader_0: nt.ProcNode[nt.Shader] | None = None,
    shader_1: nt.ProcNode[nt.Shader] | None = None,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a AddShader Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/add.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeAddShader",
        inputs={("Shader", 0): shader_0, ("Shader", 1): shader_1},
        attrs={},
    )


class AmbientOcclusionResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    ao: nt.ProcNode[float]


def ambient_occlusion(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    distance: nt.SocketOrVal[float] = 1.0,
    normal: nt.SocketOrVal[pt.Vector] = None,
    inside: bool = False,
    only_local: bool = False,
    samples: int = 16,
) -> AmbientOcclusionResult:
    """
    Uses a AmbientOcclusion Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/ao.html
    """
    if normal is not None:
        raise_shader_normal_error("ambient_occlusion", logger=logger)

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeAmbientOcclusion",
        inputs={"Color": color, "Distance": distance, "Normal": normal},
        attrs={"inside": inside, "only_local": only_local, "samples": samples},
    )
    return AmbientOcclusionResult(
        color=res._output_socket("color"), ao=res._output_socket("ao")
    )


class AttributeResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    vector: nt.ProcNode[pt.Vector]
    fac: nt.ProcNode[float]
    alpha: nt.ProcNode[float]


def attribute(
    attribute_name: str = "",
    attribute_type: Literal[
        "GEOMETRY", "OBJECT", "INSTANCER", "VIEW_LAYER"
    ] = "GEOMETRY",
) -> AttributeResult:
    """
    Uses a Attribute Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/attribute.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeAttribute",
        inputs={},
        attrs={"attribute_name": attribute_name, "attribute_type": attribute_type},
    )
    return AttributeResult(
        color=res._output_socket("color"),
        vector=res._output_socket("vector"),
        fac=res._output_socket("fac"),
        alpha=res._output_socket("alpha"),
    )


def background(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    strength: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a Background Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/background.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBackground",
        inputs={"Color": color, "Strength": strength},
        attrs={},
    )


def bevel(
    radius: nt.SocketOrVal[float] = 0.05,
    normal: nt.SocketOrVal[pt.Vector] = None,
    samples: int = 4,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a Bevel Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/bevel.html
    """
    if normal is not None:
        raise_shader_normal_error("bevel", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBevel",
        inputs={"Radius": radius, "Normal": normal},
        attrs={"samples": samples},
    )


def blackbody(temperature: nt.SocketOrVal[float] = 1500.0) -> nt.ProcNode[pt.Color]:
    """
    Uses a Blackbody Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/blackbody.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBlackbody",
        inputs={"Temperature": temperature},
        attrs={},
    )


def bright_contrast(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    bright: nt.SocketOrVal[float] = 0.0,
    contrast: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a BrightContrast Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/bright_contrast.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBrightContrast",
        inputs={"Color": color, "Bright": bright, "Contrast": contrast},
        attrs={},
    )


def anisotropic_bsdf(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    roughness: nt.SocketOrVal[float] = 0.5,
    anisotropy: nt.SocketOrVal[float] = 0.0,
    rotation: nt.SocketOrVal[float] = 0.0,
    normal: nt.SocketOrVal[pt.Vector] = None,
    tangent: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    distribution: Literal[
        "BECKMANN", "GGX", "ASHIKHMIN_SHIRLEY", "MULTI_GGX"
    ] = "MULTI_GGX",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfAnisotropic Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/principled.html
    """

    if normal is not None:
        raise_shader_normal_error("anisotropic_bsdf", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfAnisotropic",
        inputs={
            "Color": color,
            "Roughness": roughness,
            "Anisotropy": anisotropy,
            "Rotation": rotation,
            "Normal": normal,
            "Tangent": tangent,
        },
        attrs={"distribution": distribution},
    )


def diffuse_bsdf(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    roughness: nt.SocketOrVal[float] = 0.0,
    normal: nt.SocketOrVal[pt.Vector] = None,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfDiffuse Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/diffuse.html
    """

    if normal is not None:
        raise_shader_normal_error("diffuse_bsdf", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfDiffuse",
        inputs={"Color": color, "Roughness": roughness, "Normal": normal},
        attrs={},
    )


def glass_bsdf(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    roughness: nt.SocketOrVal[float] = 0.0,
    ior: nt.SocketOrVal[float] = 1.5,
    normal: nt.SocketOrVal[pt.Vector] = None,
    distribution: Literal["BECKMANN", "GGX", "MULTI_GGX"] = "MULTI_GGX",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfGlass Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/glass.html
    """

    if normal is not None:
        raise_shader_normal_error("glass_bsdf", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfGlass",
        inputs={"Color": color, "Roughness": roughness, "IOR": ior, "Normal": normal},
        attrs={"distribution": distribution},
    )


def hair_bsdf(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    offset: nt.SocketOrVal[float] = 0.0,
    roughness_u: nt.SocketOrVal[float] = 0.1,
    roughness_v: nt.SocketOrVal[float] = 1.0,
    tangent: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    component: Literal["Reflection", "Transmission"] = "Reflection",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfHair Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/hair.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfHair",
        inputs={
            "Color": color,
            "Offset": offset,
            "RoughnessU": roughness_u,
            "RoughnessV": roughness_v,
            "Tangent": tangent,
        },
        attrs={"component": component},
    )


def principled_hair_bsdf(
    color: nt.SocketOrVal[pt.Color] = (0.017513, 0.005763, 0.002059, 1),
    roughness: nt.SocketOrVal[float] = 0.3,
    radial_roughness: nt.SocketOrVal[float] = 0.3,
    coat: nt.SocketOrVal[float] = 0.0,
    ior: nt.SocketOrVal[float] = 1.55,
    offset: nt.SocketOrVal[float] = 0.034907,
    random_roughness: nt.SocketOrVal[float] = 0.0,
    random: nt.SocketOrVal[float] = 0.0,
    model: Literal["CHIANG", "HUANG"] = "CHIANG",
    parametrization: Literal["ABSORPTION", "MELANIN", "COLOR"] = "COLOR",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfHairPrincipled Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/hair_principled.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfHairPrincipled",
        inputs={
            "Color": color,
            "Roughness": roughness,
            "Radial Roughness": radial_roughness,
            "Coat": coat,
            "IOR": ior,
            "Offset": offset,
            "Random Roughness": random_roughness,
            "Random": random,
        },
        attrs={"model": model, "parametrization": parametrization},
    )


TSubsurfaceMethod = Literal["BURLEY", "RANDOM_WALK", "RANDOM_WALK_SKIN"]


def principled_bsdf(
    base_color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    metallic: nt.SocketOrVal[float] = 0.0,
    roughness: nt.SocketOrVal[float] = 0.5,
    ior: nt.SocketOrVal[float] = 1.5,
    alpha: nt.SocketOrVal[float] = 1.0,
    normal: nt.SocketOrVal[pt.Vector] = (0.0, 0.0, 0.0),
    # subsurface scattering
    subsurface_method: TSubsurfaceMethod = "RANDOM_WALK",
    subsurface_weight: nt.SocketOrVal[float] = 0.0,
    subsurface_radius: nt.SocketOrVal[pt.Vector] = (1, 0.2, 0.1),
    subsurface_scale: nt.SocketOrVal[float] = 0.05,
    subsurface_ior: nt.SocketOrVal[float] | None = None,
    subsurface_anisotropy: nt.SocketOrVal[float] | None = None,
    # specular
    distribution: Literal["GGX", "MULTI_GGX"] = "MULTI_GGX",
    specular_ior_level: nt.SocketOrVal[float] = 0.5,
    specular_tint: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    anisotropic: nt.SocketOrVal[float] = 0.0,
    anisotropic_rotation: nt.SocketOrVal[float] = 0.0,
    tangent: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    transmission_weight: nt.SocketOrVal[float] = 0.0,
    coat_weight: nt.SocketOrVal[float] = 0.0,
    coat_roughness: nt.SocketOrVal[float] = 0.03,
    coat_ior: nt.SocketOrVal[float] = 1.5,
    coat_tint: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    coat_normal: nt.SocketOrVal[pt.Vector] = (0.0, 0.0, 0.0),
    sheen_weight: nt.SocketOrVal[float] = 0.0,
    sheen_roughness: nt.SocketOrVal[float] = 0.5,
    sheen_tint: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    emission_color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    emission_strength: nt.SocketOrVal[float] = 0.0,
    thin_film_thickness: nt.SocketOrVal[float] = 0.0,
    thin_film_ior: nt.SocketOrVal[float] = 1.33,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfPrincipled Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.
        subsurface_ior: Only supported if subsurface_method is RANDOM_WALK_SKIN.
        distribution: configurs specular shading

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/principled.html
    """

    if normal is not None:
        raise_shader_normal_error("principled_bsdf", logger=logger)

    inputs = {
        "Base Color": base_color,
        "Metallic": metallic,
        "Roughness": roughness,
        "IOR": ior,
        "Alpha": alpha,
        "Normal": normal,
        "Subsurface Weight": subsurface_weight,
        "Subsurface Radius": subsurface_radius,
        "Subsurface Scale": subsurface_scale,
        "Subsurface Anisotropy": subsurface_anisotropy,
        "Specular IOR Level": specular_ior_level,
        "Specular Tint": specular_tint,
        "Anisotropic": anisotropic,
        "Anisotropic Rotation": anisotropic_rotation,
        "Tangent": tangent,
        "Transmission Weight": transmission_weight,
        "Coat Weight": coat_weight,
        "Coat Roughness": coat_roughness,
        "Coat IOR": coat_ior,
        "Coat Tint": coat_tint,
        "Coat Normal": coat_normal,
        "Sheen Weight": sheen_weight,
        "Sheen Roughness": sheen_roughness,
        "Sheen Tint": sheen_tint,
        "Emission Color": emission_color,
        "Emission Strength": emission_strength,
        "Thin Film Thickness": thin_film_thickness,
        "Thin Film IOR": thin_film_ior,
    }

    if subsurface_ior is not None:
        assert subsurface_method == "RANDOM_WALK_SKIN"
        inputs["Subsurface IOR"] = subsurface_ior
    if subsurface_anisotropy is not None:
        assert subsurface_method in ["RANDOM_WALK", "RANDOM_WALK_SKIN"]
        inputs["Subsurface Anisotropy"] = subsurface_anisotropy

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfPrincipled",
        inputs=inputs,
        attrs={"distribution": distribution, "subsurface_method": subsurface_method},
    )


def ray_portal_bsdf(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    position: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    direction: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfRayPortal Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/ray_portal.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfRayPortal",
        inputs={"Color": color, "Position": position, "Direction": direction},
        attrs={},
    )


def refraction_bsdf(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    roughness: nt.SocketOrVal[float] = 0.0,
    ior: nt.SocketOrVal[float] = 1.45,
    normal: nt.SocketOrVal[pt.Vector] = None,
    distribution: Literal["BECKMANN", "GGX"] = "BECKMANN",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfRefraction Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/refraction.html
    """

    if normal is not None:
        raise_shader_normal_error("refraction_bsdf", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfRefraction",
        inputs={"Color": color, "Roughness": roughness, "IOR": ior, "Normal": normal},
        attrs={"distribution": distribution},
    )


def sheen_bsdf(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    roughness: nt.SocketOrVal[float] = 0.5,
    normal: nt.SocketOrVal[pt.Vector] = None,
    distribution: Literal["ASHIKHMIN", "MICROFIBER"] = "MICROFIBER",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfSheen Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/sheen.html
    """

    if normal is not None:
        raise_shader_normal_error("sheen_bsdf", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfSheen",
        inputs={"Color": color, "Roughness": roughness, "Normal": normal},
        attrs={"distribution": distribution},
    )


def toon_bsdf(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    size: nt.SocketOrVal[float] = 0.5,
    smooth: nt.SocketOrVal[float] = 0.0,
    normal: nt.SocketOrVal[pt.Vector] = None,
    component: Literal["DIFFUSE", "GLOSSY"] = "DIFFUSE",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfToon Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/toon.html
    """

    if normal is not None:
        raise_shader_normal_error("toon_bsdf", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfToon",
        inputs={"Color": color, "Size": size, "Smooth": smooth, "Normal": normal},
        attrs={"component": component},
    )


def translucent_bsdf(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    normal: nt.SocketOrVal[pt.Vector] = None,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfTranslucent Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/translucent.html
    """

    if normal is not None:
        raise_shader_normal_error("translucent_bsdf", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfTranslucent",
        inputs={"Color": color, "Normal": normal},
        attrs={},
    )


def transparent_bsdf(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a BsdfTransparent Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/transparent.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfTransparent",
        inputs={"Color": color},
        attrs={},
    )


def bump(
    strength: nt.SocketOrVal[float] = 1.0,
    distance: nt.SocketOrVal[float] = 1.0,
    height: nt.SocketOrVal[float] = 1.0,
    normal: nt.SocketOrVal[pt.Vector] = None,
    invert: bool = False,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a Bump Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/bump.html
    """

    msg = (
        "Using the Bump shader node! We recommend using the shader's Displacement output instead"
        ", as it has more capabilities e.g. mesh-based displacement "
        "To suppress this warning, set pf.context.globals.warn_mode_avoid_normal_bump = 'ignore'"
    )
    raise_error_or_warn(msg, pf.context.globals.warn_mode_avoid_normal_bump, logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBump",
        inputs={
            "Strength": strength,
            "Distance": distance,
            "Height": height,
            "Normal": normal,
        },
        attrs={"invert": invert},
    )


class CameraDataResult(NamedTuple):
    view_vector: nt.ProcNode[pt.Vector]
    view_z_depth: nt.ProcNode[float]
    view_distance: nt.ProcNode[float]


def camera_data() -> CameraDataResult:
    """
    Uses a CameraData Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/camera_data.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeCameraData",
        inputs={},
        attrs={},
    )

    return CameraDataResult(
        view_vector=res._output_socket("view_vector"),
        view_z_depth=res._output_socket("view_z_depth"),
        view_distance=res._output_socket("view_distance"),
    )


def displacement(
    height: nt.SocketOrVal[float] = 0.0,
    midlevel: nt.SocketOrVal[float] = 0.5,
    scale: nt.SocketOrVal[float] = 1.0,
    normal: nt.SocketOrVal[pt.Vector] = None,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a Displacement Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/displacement.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeDisplacement",
        inputs={
            "Height": height,
            "Midlevel": midlevel,
            "Scale": scale,
            "Normal": normal,
        },
        attrs={"space": space},
    )


def eevee_specular(
    base_color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    specular: nt.SocketOrVal[pt.Color] = (0.03, 0.03, 0.03, 1),
    roughness: nt.SocketOrVal[float] = 0.2,
    emissive_color: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    transparency: nt.SocketOrVal[float] = 0.0,
    normal: nt.SocketOrVal[pt.Vector] = None,
    clear_coat: nt.SocketOrVal[float] = 0.0,
    clear_coat_roughness: nt.SocketOrVal[float] = 0.0,
    clear_coat_normal: nt.SocketOrVal[pt.Vector] = None,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a EeveeSpecular Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/specular_bsdf.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeEeveeSpecular",
        inputs={
            "Base Color": base_color,
            "Specular": specular,
            "Roughness": roughness,
            "Emissive Color": emissive_color,
            "Transparency": transparency,
            "Normal": normal,
            "Clear Coat": clear_coat,
            "Clear Coat Roughness": clear_coat_roughness,
            "Clear Coat Normal": clear_coat_normal,
        },
        attrs={},
    )


def emission(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    strength: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a Emission Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/emission.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeEmission",
        inputs={"Color": color, "Strength": strength},
        attrs={},
    )


def fresnel(
    ior: nt.SocketOrVal[float] = 1.5, normal: nt.SocketOrVal[pt.Vector] = None
) -> nt.ProcNode[float]:
    """
    Uses a Fresnel Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/fresnel.html
    """
    if normal is not None:
        raise_shader_normal_error("fresnel", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeFresnel",
        inputs={"IOR": ior, "Normal": normal},
        attrs={},
    )


def gamma(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1), gamma: nt.SocketOrVal[float] = 1.0
) -> nt.ProcNode[pt.Color]:
    """
    Uses a Gamma Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/gamma.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeGamma",
        inputs={"Color": color, "Gamma": gamma},
        attrs={},
    )


class HairInfoResult(NamedTuple):
    is_strand: nt.ProcNode[float]
    intercept: nt.ProcNode[float]
    length: nt.ProcNode[float]
    thickness: nt.ProcNode[float]
    tangent_normal: nt.ProcNode[pt.Vector]
    random: nt.ProcNode[float]


def hair_info() -> HairInfoResult:
    """
    Uses a HairInfo Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/hair_info.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeHairInfo",
        inputs={},
        attrs={},
    )

    return HairInfoResult(
        is_strand=res._output_socket("is_strand"),
        intercept=res._output_socket("intercept"),
        length=res._output_socket("length"),
        thickness=res._output_socket("thickness"),
        tangent_normal=res._output_socket("tangent_normal"),
        random=res._output_socket("random"),
    )


def holdout() -> nt.ProcNode[nt.Shader]:
    """
    Uses a Holdout Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/holdout.html
    """
    return nt.ProcNode.from_nodetype(node_type="ShaderNodeHoldout", inputs={}, attrs={})


def hue_saturation(
    hue: nt.SocketOrVal[float] = 0.5,
    saturation: nt.SocketOrVal[float] = 1.0,
    value: nt.SocketOrVal[float] = 1.0,
    fac: nt.SocketOrVal[float] = 1.0,
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
) -> nt.ProcNode[pt.Color]:
    """
    Uses a HueSaturation Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/hue_saturation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeHueSaturation",
        inputs={
            "Hue": hue,
            "Saturation": saturation,
            "Value": value,
            "Fac": fac,
            "Color": color,
        },
        attrs={},
    )


def invert(
    fac: nt.SocketOrVal[float] = 1.0, color: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1)
) -> nt.ProcNode[pt.Color]:
    """
    Uses a Invert Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/invert_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeInvert",
        inputs={"Fac": fac, "Color": color},
        attrs={},
    )


class LayerWeightResult(NamedTuple):
    fresnel: nt.ProcNode[float]
    facing: nt.ProcNode[float]


def layer_weight(
    blend: nt.SocketOrVal[float] = 0.5,
    normal: nt.SocketOrVal[pt.Vector] = (0.0, 0.0, 0.0),
) -> LayerWeightResult:
    """
    Uses a LayerWeight Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/layer_weight.html
    """
    if normal != (0.0, 0.0, 0.0):
        raise_shader_normal_error("layer_weight", logger=logger)

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeLayerWeight",
        inputs={"Blend": blend, "Normal": normal},
        attrs={},
    )
    return LayerWeightResult(
        fresnel=res._output_socket("fresnel"),
        facing=res._output_socket("facing"),
    )


class LightFalloffResult(NamedTuple):
    quadratic: nt.ProcNode[float]
    linear: nt.ProcNode[float]
    constant: nt.ProcNode[float]


def light_falloff(
    strength: nt.SocketOrVal[float] = 100.0, smooth: nt.SocketOrVal[float] = 0.0
) -> LightFalloffResult:
    """
    Uses a LightFalloff Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/light_falloff.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeLightFalloff",
        inputs={"Strength": strength, "Smooth": smooth},
        attrs={},
    )
    return LightFalloffResult(
        quadratic=res._output_socket("quadratic"),
        linear=res._output_socket("linear"),
        constant=res._output_socket("constant"),
    )


class LightPathResult(NamedTuple):
    is_camera_ray: nt.ProcNode[float]
    is_shadow_ray: nt.ProcNode[float]
    is_diffuse_ray: nt.ProcNode[float]
    is_glossy_ray: nt.ProcNode[float]
    is_singular_ray: nt.ProcNode[float]
    is_reflection_ray: nt.ProcNode[float]
    is_transmission_ray: nt.ProcNode[float]
    ray_length: nt.ProcNode[float]
    ray_depth: nt.ProcNode[float]
    diffuse_depth: nt.ProcNode[float]
    glossy_depth: nt.ProcNode[float]
    transparent_depth: nt.ProcNode[float]
    transmission_depth: nt.ProcNode[float]


def light_path() -> LightPathResult:
    """
    Uses a LightPath Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/light_path.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeLightPath",
        inputs={},
        attrs={},
    )

    return LightPathResult(
        is_camera_ray=res._output_socket("is_camera_ray"),
        is_shadow_ray=res._output_socket("is_shadow_ray"),
        is_diffuse_ray=res._output_socket("is_diffuse_ray"),
        is_glossy_ray=res._output_socket("is_glossy_ray"),
        is_singular_ray=res._output_socket("is_singular_ray"),
        is_reflection_ray=res._output_socket("is_reflection_ray"),
        is_transmission_ray=res._output_socket("is_transmission_ray"),
        ray_length=res._output_socket("ray_length"),
        ray_depth=res._output_socket("ray_depth"),
        diffuse_depth=res._output_socket("diffuse_depth"),
        glossy_depth=res._output_socket("glossy_depth"),
        transparent_depth=res._output_socket("transparent_depth"),
        transmission_depth=res._output_socket("transmission_depth"),
    )


def mapping(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    location: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    scale: nt.SocketOrVal[pt.Vector] = (1, 1, 1),
    vector_type: Literal["POINT", "TEXTURE", "VECTOR", "NORMAL"] = "POINT",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a Mapping Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/mapping.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeMapping",
        inputs={
            "Vector": vector,
            "Location": location,
            "Rotation": rotation,
            "Scale": scale,
        },
        attrs={"vector_type": vector_type},
    )


def mix_shader(
    factor: nt.SocketOrVal[float] = 0.5,
    a: nt.ProcNode[nt.Shader] | None = None,
    b: nt.ProcNode[nt.Shader] | None = None,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a MixShader Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/mix.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeMixShader",
        inputs={"Fac": factor, ("Shader", 0): a, ("Shader", 1): b},
        attrs={},
    )


class NormalResult(NamedTuple):
    normal: nt.ProcNode[pt.Vector]
    dot: nt.ProcNode[float]


def normal(normal: nt.SocketOrVal[pt.Vector] = (0, 0, 1)) -> NormalResult:
    """
    Uses a Normal Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/normal.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeNormal",
        inputs={"Normal": normal},
        attrs={},
    )
    return NormalResult(
        normal=res._output_socket("normal"),
        dot=res._output_socket("dot"),
    )


def normal_map(
    strength: nt.SocketOrVal[float] = 1.0,
    color: nt.SocketOrVal[pt.Color] = (0.5, 0.5, 1, 1),
    space: Literal[
        "TANGENT", "OBJECT", "WORLD", "BLENDER_OBJECT", "BLENDER_WORLD"
    ] = "TANGENT",
    uv_map: str = "",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a NormalMap Shader Node.

    This node is discouraged. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/normal_map.html
    """
    raise_shader_normal_error("normal_map", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeNormalMap",
        inputs={"Strength": strength, "Color": color},
        attrs={"space": space, "uv_map": uv_map},
    )


class ObjectInfoResult(NamedTuple):
    location: nt.ProcNode[pt.Vector]
    color: nt.ProcNode[pt.Color]
    alpha: nt.ProcNode[float]
    object_index: nt.ProcNode[int]
    material_index: nt.ProcNode[int]
    random: nt.ProcNode[float]


def object_info() -> ObjectInfoResult:
    """
    Uses a ObjectInfo Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/object_info.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeObjectInfo",
        inputs={},
        attrs={},
    )
    return ObjectInfoResult(
        location=res._output_socket("location"),
        color=res._output_socket("color"),
        alpha=res._output_socket("alpha"),
        object_index=res._output_socket("object_index"),
        material_index=res._output_socket("material_index"),
        random=res._output_socket("random"),
    )


# NOTE: procfunc expects python code to `return LightResult()` instead
'''

def output_aov(
    color: t.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    value: t.SocketOrVal[float] = 0.0,
    aov_name: str = "",
) -> t.ProcNode:
    """
    Uses a OutputAOV Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/output/aov.html
    """

    raise_io_error("output_aov", logger=logger)

    return t.ProcNode.from_nodetype(
        node_type="ShaderNodeOutputAOV",
        inputs={"Color": color, "Value": value},
        attrs={"aov_name": aov_name},
    )

def output_light(
    surface: t.ProcNode[t.Shader] = None,
    is_active_output: bool = True,
    target: TRenderTarget = "ALL",
) -> t.ProcNode:
    """
    Uses a OutputLight Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/output/light.html
    """

    raise_io_error("output_light", logger=logger)

    return t.ProcNode.from_nodetype(
        node_type="ShaderNodeOutputLight",
        inputs={"Surface": surface},
        attrs={"is_active_output": is_active_output, "target": target},
    )

def output_line_style(
    color: t.SocketOrVal[pt.Color] = (1, 0, 1, 1),
    color_fac: t.SocketOrVal[float] = 1.0,
    alpha: t.SocketOrVal[float] = 1.0,
    alpha_fac: t.SocketOrVal[float] = 1.0,
    blend_type: TBlendType = "MIX",
    is_active_output: bool = True,
    target: TRenderTarget = "ALL",
    use_alpha: bool = False,
) -> t.ProcNode:
    """
    Uses a OutputLineStyle Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/output/aov.html
    """

    raise_io_error("output_line_style", logger=logger)

    return t.ProcNode.from_nodetype(
        node_type="ShaderNodeOutputLineStyle",
        inputs={
            "Color": color,
            "Color Fac": color_fac,
            "Alpha": alpha,
            "Alpha Fac": alpha_fac,
        },
        attrs={
            "blend_type": blend_type,
            "is_active_output": is_active_output,
            "target": target,
            "use_alpha": use_alpha,
        },
    )

def output_material(
    surface: t.ProcNode[t.Shader] = None,
    volume: t.ProcNode[t.Shader] = None,
    displacement: t.SocketOrVal[pt.Vector] = (0, 0, 0),
    thickness: t.SocketOrVal[float] = 0.0,
    is_active_output: bool = True,
    target: TRenderTarget = "ALL",
) -> t.ProcNode:
    """
    Uses a OutputMaterial Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/output/material.html
    """

    return t.ProcNode.from_nodetype(
        node_type="ShaderNodeOutputMaterial",
        inputs={
            "Surface": surface,
            "Volume": volume,
            "Displacement": displacement,
            "Thickness": thickness,
        },
        attrs={"is_active_output": is_active_output, "target": target},
    )
'''

'''
def output_world(
    surface: t.ProcNode[t.Shader] = None,
    volume: t.ProcNode[t.Shader] = None,
    is_active_output: bool = True,
    target: TRenderTarget = "ALL",
) -> t.ProcNode:
    """
    Uses a OutputWorld Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/output/world.html
    """
    return t.ProcNode.from_nodetype(
        node_type="ShaderNodeOutputWorld",
        inputs={"Surface": surface, "Volume": volume},
        attrs={"is_active_output": is_active_output, "target": target},
    )
'''


class ParticleInfoResult(NamedTuple):
    index: nt.ProcNode[int]
    random: nt.ProcNode[float]
    age: nt.ProcNode[float]
    lifetime: nt.ProcNode[float]
    location: nt.ProcNode[pt.Vector]
    size: nt.ProcNode[float]
    velocity: nt.ProcNode[pt.Vector]
    angular_velocity: nt.ProcNode[pt.Vector]


def particle_info() -> ParticleInfoResult:
    """
    Uses a ParticleInfo Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/particle_info.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeParticleInfo",
        inputs={},
        attrs={},
    )
    return ParticleInfoResult(
        index=res._output_socket("index"),
        random=res._output_socket("random"),
        age=res._output_socket("age"),
        lifetime=res._output_socket("lifetime"),
        location=res._output_socket("location"),
        size=res._output_socket("size"),
        velocity=res._output_socket("velocity"),
        angular_velocity=res._output_socket("angular_velocity"),
    )


class PointInfoResult(NamedTuple):
    position: nt.ProcNode[pt.Vector]
    radius: nt.ProcNode[float]
    random: nt.ProcNode[float]


def point_info() -> PointInfoResult:
    """
    Uses a PointInfo Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/point_info.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodePointInfo",
        inputs={},
        attrs={},
    )
    return PointInfoResult(
        position=res._output_socket("position"),
        radius=res._output_socket("radius"),
        random=res._output_socket("random"),
    )


def rgb() -> nt.ProcNode[pt.Color]:
    """
    Uses a RGB Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/rgb.html
    """
    return nt.ProcNode.from_nodetype(node_type="ShaderNodeRGB", inputs={}, attrs={})


def rgb_to_bw(
    color: nt.SocketOrVal[pt.Color] = (0.5, 0.5, 0.5, 1),
) -> nt.ProcNode[float]:
    """
    Uses a RGBToBW Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/rgb_to_bw.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeRGBToBW",
        inputs={"Color": color},
        attrs={},
    )


def script(
    bytecode: str = "",
    bytecode_hash: str = "",
    filepath: str = "",
    mode: Literal["INTERNAL", "EXTERNAL"] = "INTERNAL",
    script: Any = None,
    use_auto_update: bool = False,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a Script Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/osl.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeScript",
        inputs={},
        attrs={
            "bytecode": bytecode,
            "bytecode_hash": bytecode_hash,
            "filepath": filepath,
            "mode": mode,
            "script": script,
            "use_auto_update": use_auto_update,
        },
    )


def shader_to_rgb(
    shader: nt.ProcNode[nt.Shader] | None = None,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a ShaderToRGB Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/shader_to_rgb.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeShaderToRGB",
        inputs={"Shader": shader},
        attrs={},
    )


def squeeze(
    value: nt.SocketOrVal[float] = 0.0,
    width: nt.SocketOrVal[float] = 1.0,
    center: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    """
    Uses a Squeeze Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/map_range.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeSqueeze",
        inputs={"Value": value, "Width": width, "Center": center},
        attrs={},
    )


def subsurface_scattering(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    scale: nt.SocketOrVal[float] = 0.05,
    radius: nt.SocketOrVal[pt.Vector] = (1, 0.2, 0.1),
    ior: nt.SocketOrVal[float] = 1.4,
    roughness: nt.SocketOrVal[float] = 1.0,
    anisotropy: nt.SocketOrVal[float] = 0.0,
    normal: nt.SocketOrVal[pt.Vector] = (0.0, 0.0, 0.0),
    falloff: Literal["BURLEY", "RANDOM_WALK", "RANDOM_WALK_SKIN"] = "RANDOM_WALK",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a SubsurfaceScattering Shader Node.

    Args:
        normal: Avoid using this input. We recommend using the shader's Displacement output instead, which supports bumpmapping OR real mesh render/export.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/volume_scatter.html
    """

    if normal != (0.0, 0.0, 0.0):
        raise_shader_normal_error("subsurface_scattering", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeSubsurfaceScattering",
        inputs={
            "Color": color,
            "Scale": scale,
            "Radius": radius,
            "IOR": ior,
            "Roughness": roughness,
            "Anisotropy": anisotropy,
            "Normal": normal,
        },
        attrs={"falloff": falloff},
    )


def tangent(
    axis: Literal["X", "Y", "Z"] = "Z",
    direction_type: Literal["RADIAL", "UV_MAP"] = "RADIAL",
    uv_map: str = "",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a Tangent Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/tangent.html
    """

    if uv_map != "" and direction_type != "UV_MAP":
        raise ValueError("uv_map is only available when direction_type is UV_MAP")

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTangent",
        inputs={},
        attrs={"axis": axis, "direction_type": direction_type, "uv_map": uv_map},
    )


class TextureResult(NamedTuple):
    fac: nt.ProcNode[float]
    color: nt.ProcNode[pt.Color]


def brick(
    vector: nt.SocketOrVal[pt.Vector],
    color1: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    color2: nt.SocketOrVal[pt.Color] = (0.2, 0.2, 0.2, 1),
    mortar: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    scale: nt.SocketOrVal[float] = 5.0,
    mortar_size: nt.SocketOrVal[float] = 0.02,
    mortar_smooth: nt.SocketOrVal[float] = 0.1,
    bias: nt.SocketOrVal[float] = 0.0,
    brick_width: nt.SocketOrVal[float] = 0.5,
    row_height: nt.SocketOrVal[float] = 0.25,
    offset: float = 0.5,
    offset_frequency: int = 2,
    squash: float = 1.0,
    squash_frequency: int = 2,
) -> TextureResult:
    """
    Uses a TexBrick Shader Node.

    Infinigen requires an explicit `vector` input - node will not default to using texture coordinate or world coordinate like blender

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/brick.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("brick", logger=logger)
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexBrick",
        inputs={
            "Vector": vector,
            "Color1": color1,
            "Color2": color2,
            "Mortar": mortar,
            "Scale": scale,
            "Mortar Size": mortar_size,
            "Mortar Smooth": mortar_smooth,
            "Bias": bias,
            "Brick Width": brick_width,
            "Row Height": row_height,
        },
        attrs={
            "offset": offset,
            "offset_frequency": offset_frequency,
            "squash": squash,
            "squash_frequency": squash_frequency,
        },
    )
    return TextureResult(
        fac=res._output_socket("fac"),
        color=res._output_socket("color"),
    )


def checker(
    vector: nt.SocketOrVal[pt.Vector],
    color1: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    color2: nt.SocketOrVal[pt.Color] = (0.2, 0.2, 0.2, 1),
    scale: nt.SocketOrVal[float] = 5.0,
) -> TextureResult:
    """
    Uses a TexChecker Shader Node.

    Infinigen requires an explicit `vector` input - node will not default to using texture coordinate or world coordinate like blender

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/checker.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("checker", logger=logger)
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexChecker",
        inputs={"Vector": vector, "Color1": color1, "Color2": color2, "Scale": scale},
        attrs={},
    )
    return TextureResult(
        fac=res._output_socket("fac"),
        color=res._output_socket("color"),
    )


class CoordResult(NamedTuple):
    generated: nt.ProcNode[pt.Vector]
    normal: nt.ProcNode[pt.Vector]
    uv: nt.ProcNode[pt.Vector]
    object: nt.ProcNode[pt.Vector]
    camera: nt.ProcNode[pt.Vector]
    window: nt.ProcNode[pt.Vector]


def coord(from_instancer: bool = False, object: Any = None) -> CoordResult:
    """
    Uses a TexCoord Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/texture_coordinate.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexCoord",
        inputs={},
        attrs={"from_instancer": from_instancer, "object": object},
    )
    return CoordResult(
        generated=res._output_socket("generated"),
        normal=res._output_socket("normal"),
        uv=res._output_socket("uv"),
        object=res._output_socket("object"),
        camera=res._output_socket("camera"),
        window=res._output_socket("window"),
    )


class GeometryResult(NamedTuple):
    position: nt.ProcNode[pt.Vector]
    normal: nt.ProcNode[pt.Vector]
    tangent: nt.ProcNode[pt.Vector]
    true_normal: nt.ProcNode[pt.Vector]
    incoming: nt.ProcNode[pt.Vector]
    parametric: nt.ProcNode[pt.Vector]
    backfacing: nt.ProcNode[float]
    pointiness: nt.ProcNode[float]
    random_per_island: nt.ProcNode[float]


def geometry() -> GeometryResult:
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeNewGeometry",
        inputs={},
        attrs={},
    )
    return GeometryResult(
        position=res._output_socket("position"),
        normal=res._output_socket("normal"),
        tangent=res._output_socket("tangent"),
        true_normal=res._output_socket("true_normal"),
        incoming=res._output_socket("incoming"),
        parametric=res._output_socket("parametric"),
        backfacing=res._output_socket("backfacing"),
        pointiness=res._output_socket("pointiness"),
        random_per_island=res._output_socket("random_per_island"),
    )


TTextureInterpolationType = Literal["Linear", "Closest", "Cubic", "Smart"]  # TODO


def environment(
    vector: nt.SocketOrVal[pt.Vector],
    image: Any = None,
    interpolation: TTextureInterpolationType = "Linear",
    projection: Literal["EQUIRECTANGULAR", "MIRROR_BALL"] = "EQUIRECTANGULAR",
) -> nt.ProcNode[pt.Color]:
    """
    Uses a TexEnvironment Shader Node.

    Infinigen requires an explicit `vector` input - node will not default to using texture coordinate or world coordinate like blender

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/environment.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("environment", logger=logger)
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexEnvironment",
        inputs={"Vector": vector},
        attrs={
            "image": image,
            "interpolation": interpolation,
            "projection": projection,
        },
    )


def gradient(
    vector: nt.SocketOrVal[pt.Vector],
    gradient_type: Literal[
        "LINEAR",
        "QUADRATIC",
        "EASING",
        "DIAGONAL",
        "SPHERICAL",
        "QUADRATIC_SPHERE",
        "RADIAL",
    ] = "LINEAR",
) -> TextureResult:
    """
    Uses a TexGradient Shader Node.

    Infinigen requires an explicit `vector` input - node will not default to using texture coordinate or world coordinate like blender

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/gradient.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("gradient", logger=logger)
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexGradient",
        inputs={"Vector": vector},
        attrs={"gradient_type": gradient_type},
    )
    return TextureResult(
        fac=res._output_socket("fac"),
        color=res._output_socket("color"),
    )


def ies(
    vector: nt.SocketOrVal[pt.Vector],
    strength: nt.SocketOrVal[float] = 1.0,
    filepath: str = "",
    ies: Any = None,
    mode: Literal["INTERNAL", "EXTERNAL"] = "INTERNAL",
) -> nt.ProcNode[float]:
    """
    Uses a TexIES Shader Node.

    Infinigen requires an explicit `vector` input - node will not default to using texture coordinate or world coordinate like blender

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/ies.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("ies", logger=logger)
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexIES",
        inputs={"Vector": vector, "Strength": strength},
        attrs={"filepath": filepath, "ies": ies, "mode": mode},
    )


def image(
    vector: nt.SocketOrVal[pt.Vector],
    extension: Literal["REPEAT", "EXTEND", "CLIP", "MIRROR"] = "REPEAT",
    image: Any = None,
    interpolation: TTextureInterpolationType = "Linear",
    projection: Literal["FLAT", "BOX", "SPHERE", "CUBE"] = "FLAT",
    projection_blend: float = 0.0,
) -> TextureResult:
    """
    Uses a TexImage Shader Node.

    Infinigen requires an explicit `vector` input - node will not default to using texture coordinate or world coordinate like blender

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/image.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("image", logger=logger)
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexImage",
        inputs={"Vector": vector},
        attrs={
            "extension": extension,
            "image": image,
            "interpolation": interpolation,
            "projection": projection,
            "projection_blend": projection_blend,
        },
    )
    return TextureResult(
        color=res._output_socket("color"),
        fac=res._output_socket("alpha"),
    )


def magic(
    vector: nt.SocketOrVal[pt.Vector],
    scale: nt.SocketOrVal[float] = 5.0,
    distortion: nt.SocketOrVal[float] = 1.0,
    turbulence_depth: int = 2,
) -> TextureResult:
    """
    Uses a TexMagic Shader Node.

    Infinigen requires an explicit `vector` input - node will not default to using texture coordinate or world coordinate like blender

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/magic.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("magic", logger=logger)
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexMagic",
        inputs={"Vector": vector, "Scale": scale, "Distortion": distortion},
        attrs={"turbulence_depth": turbulence_depth},
    )
    return TextureResult(
        fac=res._output_socket("fac"),
        color=res._output_socket("color"),
    )


'''
def musgrave(
    vector: nt.SocketOrVal[pt.Vector],
    scale: nt.SocketOrVal[float] = 5.0,
    detail: nt.SocketOrVal[float] = 2.0,
    dimension: nt.SocketOrVal[float] = 2.0,
    lacunarity: nt.SocketOrVal[float] = 2.0,
    offset: nt.SocketOrVal[float] = 0.0,
    gain: nt.SocketOrVal[float] = 1.0,
    musgrave_type: str = "FBM",
    noise_dimensions: str = "4D",
    w: nt.SocketOrVal[float] = None,
) -> TextureResult:
    """

    Musgrave texture imitation using NoiseTexture for backwards compatibility.

    Converts old Musgrave parameters to new Noise node parameters:
    - roughness = lacunarity ** (-dimension)
    - detail = detail - 1
    - musgrave_type -> noise_type
    - musgrave_dimensions -> noise_dimensions

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/musgrave.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("musgrave", logger=logger)
    # Convert dimension/lacunarity to roughness
    if isinstance(lacunarity, nt.ProcNode) or isinstance(dimension, nt.ProcNode):
        roughness = func.math(
            lacunarity, func.math(0, dimension, operation="SUBTRACT"), operation="POWER"
        )
    else:
        roughness = lacunarity ** (-dimension)
    if isinstance(detail, nt.ProcNode):
        detail_adjusted = func.math(detail, 1, operation="SUBTRACT")
    else:
        detail_adjusted = detail - 1

    logger.warning(
        f"Skipping important musgrave args: {musgrave_type=} {noise_dimensions=}"
    )
    res = noise(
        vector=vector,
        scale=scale,
        detail=detail_adjusted,
        roughness=roughness,
        lacunarity=lacunarity,
        distortion=offset,  # offset maps to distortion
        noise_dimensions=noise_dimensions,
        # noise_node_type=musgrave_type,
        normalize=False,
        w=w,
    )

    return res
'''

TNoiseType = Literal[
    "MULTIFRACTAL",
    "FBM",
    "RIDGED_MULTIFRACTAL",
    "HYBRID_MULTIFRACTAL",
    "HETERO_TERRAIN",
]
TNoiseDimensions = Literal["1D", "2D", "3D", "4D"]


def noise(
    vector: nt.SocketOrVal[pt.Vector] = (0.0, 0.0, 0.0),
    scale: nt.SocketOrVal[float] = 5.0,
    detail: nt.SocketOrVal[float] = 2.0,
    roughness: nt.SocketOrVal[float] = 0.5,
    lacunarity: nt.SocketOrVal[float] = 2.0,
    offset: nt.SocketOrVal[float] = 0.0,
    gain: nt.SocketOrVal[float] = 1.0,
    distortion: nt.SocketOrVal[float] = 0.0,
    noise_dimensions: TNoiseDimensions = "3D",
    noise_type: TNoiseType = "FBM",
    normalize: bool = True,
    w: nt.SocketOrVal[float] = 0.0,
) -> TextureResult:
    """

    Uses a TexNoise Shader Node.

    Args:
     - offset: Only supported for RIDGED_MULTIFRACTAL, HYBRID_MULTIFRACTAL, HETERO_TERRAIN noise types
     - gain: Only supported for RIDGED_MULTIFRACTAL and HYBRID_MULTIFRACTAL noise types
     - distortion: Only supported for RIDGED_MULTIFRACTAL, HYBRID_MULTIFRACTAL, HETERO_TERRAIN noise types
     - w: Only supported for 1D and 4D noise dimensions

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/noise.html
    """

    inputs = {
        "Scale": scale,
        "Detail": detail,
        "Roughness": roughness,
        "Lacunarity": lacunarity,
        "Distortion": distortion,
    }

    if w != 0.0:
        assert noise_dimensions in ["4D", "1D"]
        inputs["W"] = w
    elif noise_dimensions == "1D":
        raise_explicit_noise_vector_error("noise", logger=logger)

    if vector == (0.0, 0.0, 0.0):
        assert noise_dimensions in ["2D", "3D", "4D"]
        inputs["Vector"] = vector
    elif noise_dimensions in ["2D", "3D"]:
        raise_explicit_noise_vector_error("noise", logger=logger)

    _extra_args_modes = ["RIDGED_MULTIFRACTAL", "HYBRID_MULTIFRACTAL"]  # noqa: F841
    if offset != 0.0:
        inputs["Offset"] = offset
    if gain != 1.0:
        inputs["Gain"] = gain

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexNoise",
        inputs=inputs,
        attrs={
            "noise_dimensions": noise_dimensions,
            "noise_type": noise_type,
            "normalize": normalize,
        },
    )
    return TextureResult(
        fac=res._output_socket("fac"),
        color=res._output_socket("color"),
    )


class PointDensityResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    density: nt.ProcNode[float]


def point_density(
    vector: nt.SocketOrVal[pt.Vector],
    interpolation: Literal["Closest", "Linear", "Cubic"] = "Linear",
    object: Any = None,
    particle_color_source: Literal[
        "PARTICLE_AGE", "PARTICLE_SPEED", "PARTICLE_VELOCITY"
    ] = "PARTICLE_AGE",
    particle_system: Any = None,
    point_source: Literal["OBJECT", "PARTICLE_SYSTEM"] = "PARTICLE_SYSTEM",
    radius: float = 0.3,
    resolution: int = 100,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
    vertex_attribute_name: str = "",
    vertex_color_source: Literal[
        "VERTEX_COLOR", "VERTEX_NORMAL", "VERTEX_WEIGHT"
    ] = "VERTEX_COLOR",
) -> PointDensityResult:
    """
    Uses a TexPointDensity Shader Node.

    Infinigen requires an explicit `vector` input - node will not default to using texture coordinate or world coordinate like blender

    TODO: vertex_attribute_name and vertex_color_source are only available for point_source OBJECT

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/point_density.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("point_density", logger=logger)
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexPointDensity",
        inputs={"Vector": vector},
        attrs={
            "interpolation": interpolation,
            "object": object,
            "particle_color_source": particle_color_source,
            "particle_system": particle_system,
            "point_source": point_source,
            "radius": radius,
            "resolution": resolution,
            "space": space,
            "vertex_attribute_name": vertex_attribute_name,
            "vertex_color_source": vertex_color_source,
        },
    )
    return PointDensityResult(
        color=res._output_socket("color"),
        density=res._output_socket("density"),
    )


def sky(
    air_density: float = 1.0,
    altitude: float = 0.0,
    dust_density: float = 1.0,
    ground_albedo: float = 0.3,
    ozone_density: float = 1.0,
    sky_type: Literal["NISHITA", "HOSEK_WILKIE", "PREETHAM"] = "NISHITA",
    sun_direction: tuple = (0.0, 0.0, 1.0),
    sun_disc: bool = True,
    sun_elevation: float = 0.261799,
    sun_intensity: float = 1.0,
    sun_rotation: float = 0.0,
    sun_size: float = 0.009512,
    turbidity: float = 2.2,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a TexSky Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/sky.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexSky",
        inputs={},
        attrs={
            "air_density": air_density,
            "altitude": altitude,
            "dust_density": dust_density,
            "ground_albedo": ground_albedo,
            "ozone_density": ozone_density,
            "sky_type": sky_type,
            "sun_direction": sun_direction,
            "sun_disc": sun_disc,
            "sun_elevation": sun_elevation,
            "sun_intensity": sun_intensity,
            "sun_rotation": sun_rotation,
            "sun_size": sun_size,
            "turbidity": turbidity,
        },
    )


class VoronoiResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    distance: nt.ProcNode[float]
    position: nt.ProcNode[pt.Vector]
    w: nt.ProcNode[float] | None


TDistanceMetric = Literal["EUCLIDEAN", "MANHATTAN", "CHEBYCHEV", "MINKOWSKI"]


def voronoi(
    vector: nt.SocketOrVal[pt.Vector],
    scale: nt.SocketOrVal[float] = 5.0,
    detail: nt.SocketOrVal[float] = 0.0,
    roughness: nt.SocketOrVal[float] = 0.5,
    lacunarity: nt.SocketOrVal[float] = 2.0,
    randomness: nt.SocketOrVal[float] = 1.0,
    exponent: nt.SocketOrVal[float] = 0.0,
    distance: TDistanceMetric = "EUCLIDEAN",
    feature: Literal["F1", "F2"] = "F1",
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: nt.SocketOrVal[float] = 0.0,
) -> VoronoiResult:
    """

    Uses a TexVoronoi Shader Node.

    Args:
        exponent: Only supported for Minkowski distance.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/voronoi.html
    """

    if vector == (0.0, 0.0, 0.0):
        raise_explicit_noise_vector_error("voronoi", logger=logger)

    inputs = {
        "Vector": vector,
        "Scale": scale,
        "Detail": detail,
        "Roughness": roughness,
        "Lacunarity": lacunarity,
        "Randomness": randomness,
    }

    if exponent != 0.0:
        assert distance == "MINKOWSKI", (
            f"exponent is only supported for Minkowski distance, got {distance=}"
        )
        inputs["Exponent"] = exponent
    if w != 0.0:
        assert voronoi_dimensions in ["4D", "1D"]
        inputs["W"] = w

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexVoronoi",
        inputs=inputs,
        attrs={
            "distance": distance,
            "feature": feature,
            "normalize": normalize,
            "voronoi_dimensions": voronoi_dimensions,
        },
    )

    w = res._output_socket("w") if voronoi_dimensions == "4D" else None

    return VoronoiResult(
        distance=res._output_socket("distance"),
        color=res._output_socket("color"),
        position=res._output_socket("position"),
        w=w,
    )


def voronoi_distance(
    vector: nt.SocketOrVal[pt.Vector],
    scale: nt.SocketOrVal[float] = 5.0,
    detail: nt.SocketOrVal[float] = 0.0,
    roughness: nt.SocketOrVal[float] = 0.5,
    lacunarity: nt.SocketOrVal[float] = 2.0,
    randomness: nt.SocketOrVal[float] = 1.0,
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    if vector == (0.0, 0.0, 0.0):
        raise_explicit_noise_vector_error("voronoi_distance", logger=logger)

    inputs = {
        "Vector": vector,
        "Scale": scale,
        "Detail": detail,
        "Roughness": roughness,
        "Lacunarity": lacunarity,
        "Randomness": randomness,
    }

    if w != 0.0:
        assert voronoi_dimensions in ["4D", "1D"]
        inputs["W"] = w

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexVoronoi",
        inputs=inputs,
        attrs={
            "feature": "DISTANCE_TO_EDGE",
            "normalize": normalize,
            "voronoi_dimensions": voronoi_dimensions,
        },
    )


def voronoi_smooth_f1(
    vector: nt.SocketOrVal[pt.Vector],
    scale: nt.SocketOrVal[float] = 5.0,
    detail: nt.SocketOrVal[float] = 0.0,
    roughness: nt.SocketOrVal[float] = 0.5,
    lacunarity: nt.SocketOrVal[float] = 2.0,
    smoothness: nt.SocketOrVal[float] = 0.5,
    randomness: nt.SocketOrVal[float] = 1.0,
    distance: TDistanceMetric = "EUCLIDEAN",
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: nt.SocketOrVal[float] = 0.0,
) -> VoronoiResult:
    if vector == (0.0, 0.0, 0.0) and voronoi_dimensions != "1D":
        raise_explicit_noise_vector_error("voronoi_smooth_f1", logger=logger)
    elif w == 0.0 and voronoi_dimensions != "1D":
        raise_explicit_noise_vector_error("voronoi_smooth_f1", logger=logger)

    inputs = {
        "Vector": vector,
        "Scale": scale,
        "Detail": detail,
        "Roughness": roughness,
        "Lacunarity": lacunarity,
        "Randomness": randomness,
        "Smoothness": smoothness,
    }

    if w != 0.0:
        assert voronoi_dimensions in ["4D", "1D"]
        inputs["W"] = w

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexVoronoi",
        inputs=inputs,
        attrs={
            "distance": distance,
            "feature": "SMOOTH_F1",
            "normalize": normalize,
            "voronoi_dimensions": voronoi_dimensions,
        },
    )

    w = res._output_socket("w") if voronoi_dimensions == "4D" else None

    return VoronoiResult(
        distance=res._output_socket("distance"),
        color=res._output_socket("color"),
        position=res._output_socket("position"),
        w=w,
    )


def voronoi_n_spheres_distance(
    vector: nt.SocketOrVal[pt.Vector],
    scale: nt.SocketOrVal[float] = 5.0,
    randomness: nt.SocketOrVal[float] = 1.0,
    normalize: bool = False,
) -> nt.ProcNode[float]:
    if vector is None:
        raise_explicit_noise_vector_error("voronoi_spheres_distance", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexVoronoi",
        inputs={
            "Vector": vector,
            "Scale": scale,
            "Randomness": randomness,
        },
        attrs={
            "feature": "N_SPHERE_RADIUS",
            "normalize": normalize,
        },
    )


def wave(
    vector: nt.SocketOrVal[pt.Vector],
    scale: nt.SocketOrVal[float] = 5.0,
    distortion: nt.SocketOrVal[float] = 0.0,
    detail: nt.SocketOrVal[float] = 2.0,
    detail_scale: nt.SocketOrVal[float] = 1.0,
    detail_roughness: nt.SocketOrVal[float] = 0.5,
    phase_offset: nt.SocketOrVal[float] = 0.0,
    bands_direction: Literal["X", "Y", "Z", "SPHERICAL"] = "X",
    rings_direction: Literal["X", "Y", "Z", "SPHERICAL"] = "X",
    wave_profile: Literal["SIN", "SAW", "TRI"] = "SIN",
    wave_type: Literal["BANDS", "RINGS"] = "BANDS",
) -> TextureResult:
    """

    Uses a TexWave Shader Node.

    TODO: bands_direction and rings_direction are only available for wave_type BANDS or RINGS respectively

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/wave.html
    """
    if vector is None:
        raise_explicit_noise_vector_error("wave", logger=logger)
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexWave",
        inputs={
            "Vector": vector,
            "Scale": scale,
            "Distortion": distortion,
            "Detail": detail,
            "Detail Scale": detail_scale,
            "Detail Roughness": detail_roughness,
            "Phase Offset": phase_offset,
        },
        attrs={
            "bands_direction": bands_direction,
            "rings_direction": rings_direction,
            "wave_profile": wave_profile,
            "wave_type": wave_type,
        },
    )
    return TextureResult(
        fac=res._output_socket("fac"),
        color=res._output_socket("color"),
    )


def white_noise(
    vector: nt.SocketOrVal[pt.Vector] | None = None,
    noise_dimensions: TNoiseDimensions = "3D",
    w: nt.SocketOrVal[float] = None,
) -> TextureResult:
    """

    Uses a TexWhiteNoise Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/white_noise.html
    """

    if noise_dimensions == "1D" and w is None:
        raise ValueError("w is required for 1D white noise")
    if noise_dimensions in ["2D", "3D", "4D"] and vector is None:
        raise_explicit_noise_vector_error("white_noise", logger=logger)
    if noise_dimensions in ["2D", "3D"] and w is not None:
        raise ValueError("w is not supported for 2D or 3D white noise")

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeTexWhiteNoise",
        inputs={
            "Vector": vector,
            "W": w,
        },
        attrs={"noise_dimensions": noise_dimensions},
    )
    return TextureResult(
        fac=res._output_socket("value"),
        color=res._output_socket("color"),
    )


def uv_along_stroke(use_tips: bool = False) -> nt.ProcNode[pt.Vector]:
    """
    Uses a UVAlongStroke Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/uv_map.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeUVAlongStroke",
        inputs={},
        attrs={"use_tips": use_tips},
    )


def uv_map(from_instancer: bool = False, uv_map: str = "") -> nt.ProcNode[pt.Vector]:
    """
    Uses a UVMap Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/uv_map.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeUVMap",
        inputs={},
        attrs={"from_instancer": from_instancer, "uv_map": uv_map},
    )


class ColorRampResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    alpha: nt.ProcNode[float]


TRampInterpolationType = Literal["EASE", "CARDINAL", "LINEAR", "B_SPLINE", "CONSTANT"]


# Manual
def color_ramp(
    fac: nt.SocketOrVal[float] = 0.5,
    points: list[tuple[float, pt.Color]] | None = None,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
    interpolation: TRampInterpolationType = "LINEAR",
) -> ColorRampResult:
    """
    Uses a ValToRGB (ColorRamp) Shader Node with points support.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/color_ramp.html
    """

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeValToRGB",
        inputs={"Fac": fac},
        attrs={
            "points": points,
            "color_mode": mode,
            "interpolation": interpolation,
        },
    )
    return ColorRampResult(
        color=res._output_socket("Color"),
        alpha=res._output_socket("Alpha"),
    )


def value() -> nt.ProcNode[float]:
    """
    Uses a Value Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/value.html
    """

    raise_io_error("value", logger=logger)

    return nt.ProcNode.from_nodetype(node_type="ShaderNodeValue", inputs={}, attrs={})


def vector_displacement(
    vector: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    midlevel: nt.SocketOrVal[float] = 0.0,
    scale: nt.SocketOrVal[float] = 1.0,
    space: Literal["TANGENT", "OBJECT", "WORLD"] = "TANGENT",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a VectorDisplacement Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/vector_displacement.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorDisplacement",
        inputs={"Vector": vector, "Midlevel": midlevel, "Scale": scale},
        attrs={"space": space},
    )


def vertex_color(layer_name: str = "") -> nt.ProcNode[pt.Color]:
    """
    Uses a VertexColor Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/vertex_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVertexColor",
        inputs={},
        attrs={"layer_name": layer_name},
    )


def volume_absorption(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    density: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a VolumeAbsorption Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/volume_absorption.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVolumeAbsorption",
        inputs={"Color": color, "Density": density},
        attrs={},
    )


def volume_info() -> nt.ProcNode:
    """
    Uses a VolumeInfo Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/volume_info.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVolumeInfo",
        inputs={},
        attrs={},
    )


def volume_principled(
    color: nt.SocketOrVal[pt.Color] = (0.5, 0.5, 0.5, 1),
    color_attribute: nt.SocketOrVal[str] = "",
    density: nt.SocketOrVal[float] = 1.0,
    density_attribute: nt.SocketOrVal[str] = "density",
    anisotropy: nt.SocketOrVal[float] = 0.0,
    absorption_color: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    emission_strength: nt.SocketOrVal[float] = 0.0,
    emission_color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    blackbody_intensity: nt.SocketOrVal[float] = 0.0,
    blackbody_tint: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    temperature: nt.SocketOrVal[float] = 1000.0,
    temperature_attribute: nt.SocketOrVal[str] = "temperature",
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a VolumePrincipled Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/volume_principled.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVolumePrincipled",
        inputs={
            "Color": color,
            "Color Attribute": color_attribute,
            "Density": density,
            "Density Attribute": density_attribute,
            "Anisotropy": anisotropy,
            "Absorption Color": absorption_color,
            "Emission Strength": emission_strength,
            "Emission Color": emission_color,
            "Blackbody Intensity": blackbody_intensity,
            "Blackbody Tint": blackbody_tint,
            "Temperature": temperature,
            "Temperature Attribute": temperature_attribute,
        },
        attrs={},
    )


def volume_scatter(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    density: nt.SocketOrVal[float] = 1.0,
    anisotropy: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a VolumeScatter Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/volume_scatter.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVolumeScatter",
        inputs={"Color": color, "Density": density, "Anisotropy": anisotropy},
        attrs={},
    )


def wavelength(wavelength: nt.SocketOrVal[float] = 500.0) -> nt.ProcNode[pt.Color]:
    """
    Uses a Wavelength Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/wavelength.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeWavelength",
        inputs={"Wavelength": wavelength},
        attrs={},
    )


def wireframe(
    size: nt.SocketOrVal[float] = 0.01, use_pixel_size: bool = False
) -> nt.ProcNode[float]:
    """
    Uses a Wireframe Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/wireframe.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeWireframe",
        inputs={"Size": size},
        attrs={"use_pixel_size": use_pixel_size},
    )
