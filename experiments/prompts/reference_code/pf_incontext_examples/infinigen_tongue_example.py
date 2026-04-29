from typing import NamedTuple, Annotated
import numpy as np
import bpy
from procfunc.nodes import types as t
from procfunc.nodes.types import ProcNode, SocketOrVal
import procfunc as pf


def shader_tongue():
    noise = pf.nodes.shader.noise(scale=37.880001, detail=1.0, roughness=0.25, normalize=False)
    
    color_ramp = pf.nodes.shader.color_ramp(
        fac=noise.fac,
        points=[(0.24, (0.0, 0.0, 0.0, 1.0)), (1.0, (0.098, 0.098, 0.098, 1.0))],
    )
    
    principled = pf.nodes.shader.principled_bsdf(
        base_color=pf.Color((0.8, 0.058612, 0.050695)),
        roughness=color_ramp.color.astype(dtype=float),
        ior=1.45,
        subsurface_method='RANDOM_WALK_SKIN',
        subsurface_weight=1.0,
        subsurface_scale=0.0312,
        subsurface_ior=1.4,
        subsurface_anisotropy=0.0,
        distribution='GGX',
        emission_color=pf.Color((0.0, 0.0, 0.0)),
        emission_strength=1.0,
    )
    
    return pf.Material(surface=principled, displacement=None, volume=None)


shader = shader_tongue()