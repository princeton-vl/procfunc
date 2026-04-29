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
        rotation=(1.661534, 2.877532, 5.134246),
    )
    
    mapping_1 = pf.nodes.shader.mapping(vector=mapping, scale=(0.5, 3.0, 0.5))
    noise = pf.nodes.shader.noise(
        vector=mapping_1,
        scale=2.0,
        detail=1.0,
        roughness=0.25,
        noise_dimensions='4D',
        normalize=False,
    )
    
    noise_1 = pf.nodes.shader.noise(
        vector=noise.fac.astype(dtype=pf.Vector),
        scale=10.0,
        noise_dimensions='4D',
        w=0.7,
    )
    color_ramp = pf.nodes.shader.color_ramp(
        fac=noise_1.fac,
        points=[(0.173, (0.157, 0.016, 0.002, 1.0)), (0.436, (0.291, 0.101, 0.015, 1.0)), (0.586, (0.081, 0.034, 0.013, 1.0))],
    )
    
    color_ramp_1 = pf.nodes.shader.color_ramp(
        fac=noise_1.fac,
        points=[(0.0, (0.486, 0.486, 0.486, 1.0)), (1.0, (1.0, 1.0, 1.0, 1.0))],
    )
    principled = pf.nodes.shader.principled_bsdf(
        base_color=color_ramp.color,
        roughness=color_ramp_1.color.astype(dtype=float),
        ior=1.45,
        subsurface_method='BURLEY',
        distribution='GGX',
        emission_color=pf.Color((0.0, 0.0, 0.0)),
        emission_strength=1.0,
    )
    
    return pf.Material(surface=principled, displacement=None, volume=None)


shader = shader_wood()