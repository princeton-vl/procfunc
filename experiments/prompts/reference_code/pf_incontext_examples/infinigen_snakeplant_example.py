from typing import NamedTuple, Annotated
import numpy as np
import bpy
from procfunc.nodes import types as t
from procfunc.nodes.types import ProcNode, SocketOrVal
import procfunc as pf


def shader_snake_plant():
    color_ramp = pf.nodes.shader.color_ramp(
        fac=0.001 * 0.0,
        points=[(0.366, (1.0, 1.0, 1.0, 1.0)), (0.386, (0.0, 0.0, 0.0, 1.0))],
    )
    
    coord = pf.nodes.shader.coord()
    
    mapping = pf.nodes.shader.mapping(coord.object)
    
    noise = pf.nodes.shader.noise(vector=mapping, scale=0.530729, roughness=1.0)
    
    wave_vector = noise.fac.astype(dtype=pf.Vector) * (1.0, 1.0, 0.6)
    
    wave = pf.nodes.shader.wave(
        vector=wave_vector + mapping,
        scale=1.784055,
        distortion=2.673235,
        detail_scale=5.038811,
        detail_roughness=2.0,
        bands_direction='Z',
    )
    color_a = wave.fac > 0.226164
    
    mapping_1 = pf.nodes.shader.mapping(vector=coord.object, scale=(7.0, 7.0, 0.05))
    
    noise_1 = pf.nodes.shader.noise(vector=mapping_1, scale=32.977795)
    
    color_ramp_1 = pf.nodes.shader.color_ramp(
        fac=color_a * noise_1.fac,
        points=[(0.232, (0.0, 0.0, 0.0, 1.0)), (0.58, (1.0, 1.0, 1.0, 1.0))],
    )
    
    color_ramp_2 = pf.nodes.shader.color_ramp(
        fac=wave.fac,
        points=[(0.616, (0.0, 0.0, 0.0, 1.0)), (0.744, (1.0, 1.0, 1.0, 1.0))],
    )
    color = pf.nodes.func.mix_rgb(
        factor=0.81574,
        a=color_ramp_1.color,
        b=color_ramp_2.color,
        blend_type='ADD',
    )
    color_ramp_3 = pf.nodes.shader.color_ramp(
        fac=color.astype(dtype=float),
        points=[(0.0, (0.172, 0.395, 0.181, 1.0)), (1.0, (0.007, 0.031, 0.009, 1.0))],
    )
    surface_base_color = pf.nodes.func.mix_rgb(
        factor=color_ramp.color.astype(dtype=float),
        a=pf.Color((0.374098, 0.388528, 0.057165)),
        b=color_ramp_3.color,
    )
    
    principled = pf.nodes.shader.principled_bsdf(
        base_color=surface_base_color,
        roughness=8.206116,
        ior=1.45,
        subsurface_method='RANDOM_WALK_SKIN',
        subsurface_ior=1.4,
        subsurface_anisotropy=0.0,
        distribution='GGX',
        coat_roughness=0.0,
        emission_color=pf.Color((0.0, 0.0, 0.0)),
        emission_strength=1.0,
    )
    
    return pf.Material(surface=principled, displacement=None, volume=None)


shader = shader_snake_plant()