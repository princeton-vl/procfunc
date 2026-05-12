"""
Texture node bindings for Blender (ShaderNodeTex*).

These pattern-generator nodes (noise, voronoi, etc.) work in BOTH shader and
geometry node trees. They live in their own module to avoid the misleading
implication that they are shader-only.
"""

import logging
from typing import Any, Literal, NamedTuple

from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import raise_explicit_noise_vector_error

logger = logging.getLogger(__name__)


TNoiseType = Literal[
    "MULTIFRACTAL",
    "FBM",
    "RIDGED_MULTIFRACTAL",
    "HYBRID_MULTIFRACTAL",
    "HETERO_TERRAIN",
]
TNoiseDimensions = Literal["1D", "2D", "3D", "4D"]
TDistanceMetric = Literal["EUCLIDEAN", "MANHATTAN", "CHEBYCHEV", "MINKOWSKI"]
TTextureInterpolationType = Literal["Linear", "Closest", "Cubic", "Smart"]  # TODO


class TextureResult(NamedTuple):
    fac: nt.ProcNode[float]
    color: nt.ProcNode[pt.Color]


class VoronoiResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    distance: nt.ProcNode[float]
    position: nt.ProcNode[pt.Vector]
    w: nt.ProcNode[float] | None


class PointDensityResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    density: nt.ProcNode[float]


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


def voronoi(
    vector: nt.SocketOrVal[pt.Vector] | None = None,
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
        vector: Required for 2D/3D/4D modes. Not used in 1D mode (use w instead).

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/textures/voronoi.html
    """

    inputs = {
        "Scale": scale,
        "Detail": detail,
        "Roughness": roughness,
        "Lacunarity": lacunarity,
        "Randomness": randomness,
    }

    if voronoi_dimensions != "1D":
        if vector is None or vector == (0.0, 0.0, 0.0):
            raise_explicit_noise_vector_error("voronoi", logger=logger)
        inputs["Vector"] = vector

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
    vector: nt.SocketOrVal[pt.Vector] | None = None,
    scale: nt.SocketOrVal[float] = 5.0,
    detail: nt.SocketOrVal[float] = 0.0,
    roughness: nt.SocketOrVal[float] = 0.5,
    lacunarity: nt.SocketOrVal[float] = 2.0,
    randomness: nt.SocketOrVal[float] = 1.0,
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    inputs = {
        "Scale": scale,
        "Detail": detail,
        "Roughness": roughness,
        "Lacunarity": lacunarity,
        "Randomness": randomness,
    }

    if voronoi_dimensions != "1D":
        if vector is None or vector == (0.0, 0.0, 0.0):
            raise_explicit_noise_vector_error("voronoi_distance", logger=logger)
        inputs["Vector"] = vector

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
