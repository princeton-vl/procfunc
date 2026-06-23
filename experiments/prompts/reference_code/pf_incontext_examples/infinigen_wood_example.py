from typing import NamedTuple, Annotated
import numpy as np
import bpy
from procfunc.nodes import types as t
from procfunc.nodes.types import ProcNode, SocketOrVal
import procfunc as pf


def shader_wood():
    coord = pf.nodes.shader.coord()
    
    mapping = pf.nodes.shader.mapping(
        vector=coord.generated,
        rotation=(1.4537333, 0.031345047, 6.245125),
    )
    
    mapping_1 = pf.nodes.shader.mapping(vector=mapping, scale=(0.5, 3.0, 0.5))
    surface_0 = pf.nodes.texture.noise(
        vector=mapping_1,
        scale=2.0,
        detail=1.0,
        roughness=0.25,
        noise_dimensions='4D',
        normalize=False,
        w=0.0,
    )
    
    surface_base_color_fac = pf.nodes.texture.noise(
        vector=surface_0.fac.astype(dtype=pf.Vector),
        scale=10.0,
        noise_dimensions='4D',
        w=0.7,
    )
    surface_base_color = pf.nodes.color.color_ramp(
        fac=surface_base_color_fac.fac,
        points=[(0.173, (0.157, 0.016, 0.002, 1.0)), (0.436, (0.291, 0.101, 0.015, 1.0)), (0.586, (0.081, 0.034, 0.013, 1.0))],
    )
    surface_roughness = pf.nodes.color.color_ramp(
        fac=surface_base_color_fac.fac,
        points=[(0.0, (0.486, 0.486, 0.486, 1.0)), (1.0, (1.0, 1.0, 1.0, 1.0))],
    )
    principled = pf.nodes.shader.principled_bsdf(
        base_color=surface_base_color.color,
        roughness=surface_roughness.color.astype(dtype=float),
        ior=1.45,
        subsurface_method='BURLEY',
        subsurface_radius=(1.0, 0.2, 0.1),
        distribution='GGX',
        emission_color=(0.0, 0.0, 0.0),
        emission_strength=1.0,
    )
    
    return pf.Material(surface=principled, displacement=None, volume=None)


shader = shader_wood()