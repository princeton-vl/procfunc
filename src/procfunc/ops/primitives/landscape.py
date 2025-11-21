import math
from dataclasses import dataclass
from typing import Unpack

import bpy
import numpy as np

from procfunc import types as t
from procfunc.ops.addons import require_blender_addon
from procfunc.util.log import clamp_with_log


@dataclass
class LandscapeParameters:
    noise_size: float = 1
    noise_type: str = "hetero_terrain"
    basis_type: str = "BLENDER"
    vl_basis_type: str = "BLENDER"
    distortion: float = 1
    hard_noise: str = "0"
    noise_depth: int = 8
    amplitude: float = 0.5
    frequency: float = 2
    dimension: float = 1
    lacunarity: float = 2
    offset: float = 1
    gain: float = 1
    marble_bias: str = "0"
    marble_sharp: str = "0"
    marble_shape: str = "0"
    height: float = 0.5
    height_invert: bool = False
    height_offset: float = 0
    fx_mixfactor: float = 0
    fx_mix_mode: str = "0"
    fx_type: str = "0"
    fx_bias: str = "0"
    fx_turb: float = 0
    fx_depth: int = 0
    fx_amplitude: float = 0.5
    fx_frequency: float = 2
    fx_size: float = 1
    fx_loc_x: float = 0
    fx_loc_y: float = 0
    fx_height: float = 0.5
    fx_invert: bool = False
    fx_offset: float = 0
    edge_falloff: str = "0"
    falloff_x: float = 4
    falloff_y: float = 4
    edge_level: float = 0
    maximum: float = 0.5
    minimum: float = 0
    strata: float = 1
    strata_type: str = "0"
    water_level: float = 0.01


def landscape(
    rng: np.random.Generator,
    dimensions: t.Vector,
    mesh_resolution: float,
    vert_group: str = "",
    **parameters: Unpack[LandscapeParameters],
) -> t.MeshObject:
    """Execute the Blender landscape add operator with given parameters."""
    require_blender_addon("antlandscape", fail="fatal")

    import logging

    logger = logging.getLogger(__name__)
    subdivision_x = clamp_with_log(
        math.ceil(dimensions.x / mesh_resolution), logger, "subdivision_x", max=2000
    )
    subdivision_y = clamp_with_log(
        math.ceil(dimensions.y / mesh_resolution), logger, "subdivision_y", max=2000
    )

    noise_offset_x: float = rng.uniform(-1e5, 1e5)
    noise_offset_y: float = rng.uniform(-1e5, 1e5)
    noise_offset_z: float = rng.uniform(-1e5, 1e5)

    # TODO: extra subdiv factor for vertical stretch?

    params = dict(
        land_material="",
        water_material="",
        texture_block="",
        at_cursor=False,
        smooth_mesh=False,
        tri_face=False,
        sphere_mesh=False,
        water_plane=False,
        remove_double=False,
        show_main_settings=False,
        show_noise_settings=False,
        show_displace_settings=False,
        auto_refresh=False,
        noise_offset_x=noise_offset_x,
        noise_offset_y=noise_offset_y,
        noise_offset_z=noise_offset_z,
        # necessary or else the object does not appear as bpy.context.active_object for return
        refresh=True,
    )
    params.update(parameters)

    bpy.ops.mesh.landscape_add(
        random_seed=rng.integers(0, 1000000),
        mesh_size=dimensions.z,  # TODO correct???
        mesh_size_x=dimensions.x,
        mesh_size_y=dimensions.y,
        subdivision_x=subdivision_x,
        subdivision_y=subdivision_y,
        ant_terrain_name=landscape.__name__,
        vert_group=vert_group,
        **params,
    )
    return t.MeshObject(bpy.context.active_object)
