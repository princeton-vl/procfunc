from typing import NamedTuple, Annotated
import numpy as np
import bpy
from procfunc.nodes import types as t
from procfunc.nodes.types import ProcNode, SocketOrVal
import procfunc as pf


def shader_snake_plant():
    surface_base_color_factor = pf.nodes.color.color_ramp(
        fac=0.001 * 2.0,
        points=[(0.374, (1.0, 1.0, 1.0, 1.0)), (0.394, (0.0, 0.0, 0.0, 1.0))],
    )
    
    coord = pf.nodes.shader.coord()
    
    mapping = pf.nodes.shader.mapping(coord.object)
    
    surface_2 = pf.nodes.texture.noise(vector=mapping, scale=0.6966707, roughness=1.0)
    
    surface_0_vector = surface_2.fac.astype(dtype=pf.Vector) * (1.0, 1.0, 0.6)
    surface_1 = pf.nodes.texture.wave(
        vector=surface_0_vector + mapping,
        scale=2.3754084,
        distortion=3.7571707,
        detail_scale=3.011885,
        detail_roughness=2.0,
        bands_direction='Z',
    )
    surface_a = surface_1.fac > 0.51349914
    mapping_1 = pf.nodes.shader.mapping(vector=coord.object, scale=(7.0, 7.0, 0.05))
    
    surface_b = pf.nodes.texture.noise(vector=mapping_1, scale=39.196106)
    
    surface_0_a = pf.nodes.color.color_ramp(
        fac=surface_a * surface_b.fac,
        points=[(0.232, (0.0, 0.0, 0.0, 1.0)), (0.616, (1.0, 1.0, 1.0, 1.0))],
    )
    surface_0_b = pf.nodes.color.color_ramp(
        fac=surface_1.fac,
        points=[(0.788, (0.0, 0.0, 0.0, 1.0)), (0.821, (1.0, 1.0, 1.0, 1.0))],
    )
    surface_0 = pf.nodes.color.mix_rgb(
        factor=0.89756054,
        a=surface_0_a.color,
        b=surface_0_b.color,
        blend_type='ADD',
    )
    surface_base_color_b = pf.nodes.color.color_ramp(
        fac=surface_0.astype(dtype=float),
        points=[(0.0, (0.13, 0.272, 0.132, 1.0)), (1.0, (0.02, 0.047, 0.015, 1.0))],
    )
    surface_base_color = pf.nodes.color.mix_rgb(
        factor=surface_base_color_factor.color.astype(dtype=float),
        a=(0.4951206, 0.5739398, 0.10857947),
        b=surface_base_color_b.color,
    )
    principled = pf.nodes.shader.principled_bsdf(
        base_color=surface_base_color,
        roughness=9.803732,
        ior=1.45,
        subsurface_method='RANDOM_WALK_SKIN',
        subsurface_radius=(1.0, 0.2, 0.1),
        subsurface_ior=1.4,
        subsurface_anisotropy=0.0,
        distribution='GGX',
        coat_roughness=0.0,
        emission_color=(0.0, 0.0, 0.0),
        emission_strength=1.0,
    )
    
    return pf.Material(surface=principled, displacement=None, volume=None)


shader = shader_snake_plant()