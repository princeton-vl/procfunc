import logging
from typing import Any, Literal, NamedTuple

import procfunc as pf
from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.util.bindings_util import (
    raise_error_or_warn,
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
    a: nt.ProcNode[nt.Shader] | None,
    b: nt.ProcNode[nt.Shader] | None,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a AddShader Shader Node.

    Both inputs are required: an unconnected shader input renders pure black, so
    callers must pass an explicit None to deliberately leave one disconnected.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/add.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeAddShader",
        inputs={("Shader", 0): a, ("Shader", 1): b},
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
    inputs = {"Color": color, "Distance": distance}
    if normal is not None:
        raise_shader_normal_error("ambient_occlusion", logger=logger)
        inputs["Normal"] = normal

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeAmbientOcclusion",
        inputs=inputs,
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
    inputs = {"Radius": radius}
    if normal is not None:
        raise_shader_normal_error("bevel", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBevel",
        inputs=inputs,
        attrs={"samples": samples},
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

    # Normal omitted unless wired: unconnected means 'use surface normal', and
    # strict-None forbids passing None for a value socket.
    inputs = {
        "Color": color,
        "Roughness": roughness,
        "Anisotropy": anisotropy,
        "Rotation": rotation,
        "Tangent": tangent,
    }
    if normal is not None:
        raise_shader_normal_error("anisotropic_bsdf", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfAnisotropic",
        inputs=inputs,
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

    inputs = {"Color": color, "Roughness": roughness}
    if normal is not None:
        raise_shader_normal_error("diffuse_bsdf", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfDiffuse",
        inputs=inputs,
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

    inputs = {"Color": color, "Roughness": roughness, "IOR": ior}
    if normal is not None:
        raise_shader_normal_error("glass_bsdf", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfGlass",
        inputs=inputs,
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
    normal: nt.SocketOrVal[pt.Vector] | None = None,
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
    tangent: nt.SocketOrVal[pt.Vector] | None = None,
    transmission_weight: nt.SocketOrVal[float] = 0.0,
    coat_weight: nt.SocketOrVal[float] = 0.0,
    coat_roughness: nt.SocketOrVal[float] = 0.03,
    coat_ior: nt.SocketOrVal[float] = 1.5,
    coat_tint: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    coat_normal: nt.SocketOrVal[pt.Vector] | None = None,
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

    if normal is not None or coat_normal is not None:
        raise_shader_normal_error("principled_bsdf", logger=logger)

    inputs = {
        "Base Color": base_color,
        "Metallic": metallic,
        "Roughness": roughness,
        "IOR": ior,
        "Alpha": alpha,
        "Subsurface Weight": subsurface_weight,
        "Subsurface Radius": subsurface_radius,
        "Subsurface Scale": subsurface_scale,
        "Specular IOR Level": specular_ior_level,
        "Specular Tint": specular_tint,
        "Anisotropic": anisotropic,
        "Anisotropic Rotation": anisotropic_rotation,
        "Transmission Weight": transmission_weight,
        "Coat Weight": coat_weight,
        "Coat Roughness": coat_roughness,
        "Coat IOR": coat_ior,
        "Coat Tint": coat_tint,
        "Sheen Weight": sheen_weight,
        "Sheen Roughness": sheen_roughness,
        "Sheen Tint": sheen_tint,
        "Emission Color": emission_color,
        "Emission Strength": emission_strength,
        "Thin Film Thickness": thin_film_thickness,
        "Thin Film IOR": thin_film_ior,
    }

    if normal is not None:
        inputs["Normal"] = normal
    if coat_normal is not None:
        inputs["Coat Normal"] = coat_normal
    if tangent is not None:
        inputs["Tangent"] = tangent
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

    inputs = {"Color": color, "Roughness": roughness, "IOR": ior}
    if normal is not None:
        raise_shader_normal_error("refraction_bsdf", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfRefraction",
        inputs=inputs,
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

    inputs = {"Color": color, "Roughness": roughness}
    if normal is not None:
        raise_shader_normal_error("sheen_bsdf", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfSheen",
        inputs=inputs,
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

    inputs = {"Color": color, "Size": size, "Smooth": smooth}
    if normal is not None:
        raise_shader_normal_error("toon_bsdf", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfToon",
        inputs=inputs,
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

    inputs = {"Color": color}
    if normal is not None:
        raise_shader_normal_error("translucent_bsdf", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBsdfTranslucent",
        inputs=inputs,
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

    inputs = {"Strength": strength, "Distance": distance, "Height": height}
    if normal is not None:
        inputs["Normal"] = normal
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBump",
        inputs=inputs,
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
    normal: nt.SocketOrVal[pt.Vector] | None = None,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a Displacement Shader Node.

    A disconnected Normal defaults to the surface normal, so we omit the input
    entirely when None rather than passing None to a value socket (strict-None policy).

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/displacement.html
    """
    inputs = {"Height": height, "Midlevel": midlevel, "Scale": scale}
    if normal is not None:
        inputs["Normal"] = normal
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeDisplacement",
        inputs=inputs,
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
    inputs = {
        "Base Color": base_color,
        "Specular": specular,
        "Roughness": roughness,
        "Emissive Color": emissive_color,
        "Transparency": transparency,
        "Clear Coat": clear_coat,
        "Clear Coat Roughness": clear_coat_roughness,
    }
    if normal is not None:
        inputs["Normal"] = normal
    if clear_coat_normal is not None:
        inputs["Clear Coat Normal"] = clear_coat_normal
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeEeveeSpecular",
        inputs=inputs,
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
    inputs = {"IOR": ior}
    if normal is not None:
        raise_shader_normal_error("fresnel", logger=logger)
        inputs["Normal"] = normal

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeFresnel",
        inputs=inputs,
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
    factor: nt.SocketOrVal[float],
    a: nt.ProcNode[nt.Shader] | None,
    b: nt.ProcNode[nt.Shader] | None,
) -> nt.ProcNode[nt.Shader]:
    """
    Uses a MixShader Shader Node.

    All inputs are required: an unconnected shader input renders pure black, so
    callers must pass an explicit None to deliberately leave one disconnected.

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


class ShaderToRGBResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    alpha: nt.ProcNode[float]


def shader_to_rgb(
    shader: nt.ProcNode[nt.Shader] | None,
) -> ShaderToRGBResult:
    """
    Uses a ShaderToRGB Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/shader_to_rgb.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeShaderToRGB",
        inputs={"Shader": shader},
        attrs={},
    )
    return ShaderToRGBResult(node._output_socket("color"), node._output_socket("alpha"))


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


class CoordResult(NamedTuple):
    generated: nt.ProcNode[pt.Vector]
    normal: nt.ProcNode[pt.Vector]
    uv: nt.ProcNode[pt.Vector]
    object: nt.ProcNode[pt.Vector]
    camera: nt.ProcNode[pt.Vector]
    window: nt.ProcNode[pt.Vector]
    reflection: nt.ProcNode[pt.Vector]


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
        reflection=res._output_socket("reflection"),
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


class VertexColorResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    alpha: nt.ProcNode[float]


def vertex_color(layer_name: str = "") -> VertexColorResult:
    """
    Uses a VertexColor Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/vertex_color.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVertexColor",
        inputs={},
        attrs={"layer_name": layer_name},
    )
    return VertexColorResult(node._output_socket("color"), node._output_socket("alpha"))


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


class VolumeInfoResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    density: nt.ProcNode[float]
    flame: nt.ProcNode[float]
    temperature: nt.ProcNode[float]


def volume_info() -> VolumeInfoResult:
    """
    Uses a VolumeInfo Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/input/volume_info.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVolumeInfo",
        inputs={},
        attrs={},
    )
    return VolumeInfoResult(
        node._output_socket("color"),
        node._output_socket("density"),
        node._output_socket("flame"),
        node._output_socket("temperature"),
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
