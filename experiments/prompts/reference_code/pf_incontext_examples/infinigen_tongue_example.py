from typing import NamedTuple, Annotated
import numpy as np
import bpy
from procfunc.nodes import types as t
from procfunc.nodes.types import ProcNode, SocketOrVal
import procfunc as pf


def shader_tongue():
    surface_roughness_fac = pf.nodes.texture.noise(
        vector=None,
        scale=37.88,
        detail=1.0,
        roughness=0.25,
        normalize=False,
    )
    
    surface_roughness = pf.nodes.color.color_ramp(
        fac=surface_roughness_fac.fac,
        points=[(0.24, (0.0, 0.0, 0.0, 1.0)), (1.0, (0.098, 0.098, 0.098, 1.0))],
    )
    principled = pf.nodes.shader.principled_bsdf(
        base_color=(0.8, 0.0586124, 0.050695036),
        roughness=surface_roughness.color.astype(dtype=float),
        ior=1.45,
        subsurface_method='RANDOM_WALK_SKIN',
        subsurface_weight=1.0,
        subsurface_radius=(1.0, 0.2, 0.1),
        subsurface_scale=0.0312,
        subsurface_ior=1.4,
        subsurface_anisotropy=0.0,
        distribution='GGX',
        emission_color=(0.0, 0.0, 0.0),
        emission_strength=1.0,
    )
    
    return pf.Material(surface=principled, displacement=None, volume=None)


shader = shader_tongue()