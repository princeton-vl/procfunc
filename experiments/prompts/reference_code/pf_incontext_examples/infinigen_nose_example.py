from typing import NamedTuple, Annotated
import numpy as np
import bpy
from procfunc.nodes import types as t
from procfunc.nodes.types import ProcNode, SocketOrVal
import procfunc as pf


def shader_nose():
    surface_base_color_fac = pf.nodes.texture.noise(
        vector=None,
        scale=3.0750935,
        detail=13.7,
        roughness=0.35355338,
        normalize=False,
    )
    
    surface_base_color = pf.nodes.color.color_ramp(
        fac=surface_base_color_fac.fac,
        points=[(0.498, (0.008, 0.005, 0.004, 1.0)), (1.0, (0.707, 0.436, 0.35, 1.0))],
    )
    surface_roughness_value = pf.nodes.texture.noise(
        vector=None,
        scale=10.0,
        detail=1.0,
        roughness=0.25,
        normalize=False,
    )
    surface_roughness = pf.nodes.math.map_range(
        value=surface_roughness_value.fac,
        to_max=0.61311,
        to_min=0.3469062,
    )
    principled = pf.nodes.shader.principled_bsdf(
        base_color=surface_base_color.color,
        roughness=surface_roughness,
        ior=1.45,
        subsurface_method='RANDOM_WALK_SKIN',
        subsurface_radius=(1.0, 0.2, 0.1),
        subsurface_ior=1.4,
        subsurface_anisotropy=0.0,
        distribution='GGX',
        emission_color=(0.0, 0.0, 0.0),
        emission_strength=1.0,
    )
    
    return pf.Material(surface=principled, displacement=None, volume=None)


shader = shader_nose()