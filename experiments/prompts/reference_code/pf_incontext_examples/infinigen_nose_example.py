from typing import NamedTuple, Annotated
import numpy as np
import bpy
from procfunc.nodes import types as t
from procfunc.nodes.types import ProcNode, SocketOrVal
import procfunc as pf


def shader_nose():
    noise = pf.nodes.shader.noise(scale=2.403823, detail=13.7, roughness=0.353553, normalize=False)
    
    color_ramp = pf.nodes.shader.color_ramp(
        fac=noise.fac,
        points=[(0.531, (0.008, 0.005, 0.004, 1.0)), (1.0, (0.707, 0.436, 0.35, 1.0))],
    )
    
    noise_1 = pf.nodes.shader.noise(scale=10.0, detail=1.0, roughness=0.25, normalize=False)
    
    surface_roughness = pf.nodes.func.map_range(value=noise_1.fac, to_max=0.470674, to_min=0.393443)
    
    principled = pf.nodes.shader.principled_bsdf(
        base_color=color_ramp.color,
        roughness=surface_roughness,
        ior=1.45,
        subsurface_method='RANDOM_WALK_SKIN',
        subsurface_ior=1.4,
        subsurface_anisotropy=0.0,
        distribution='GGX',
        emission_color=pf.Color((0.0, 0.0, 0.0)),
        emission_strength=1.0,
    )
    
    return pf.Material(surface=principled, displacement=None, volume=None)


shader = shader_nose()