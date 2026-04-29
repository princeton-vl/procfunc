from typing import NamedTuple, Annotated
import numpy as np
import bpy
from procfunc.nodes import types as t
from procfunc.nodes.types import ProcNode, SocketOrVal
import procfunc as pf


def shader_bone():
    coord = pf.nodes.shader.coord()
    
    mapping = pf.nodes.shader.mapping(
        vector=coord.object,
        location=(1.739509, 0.347844, -0.03725),
    )
    
    noise = pf.nodes.shader.noise(vector=mapping, scale=10.767232, detail=15.0, roughness=0.7667)
    
    voronoi = pf.nodes.shader.voronoi(vector=noise.fac.astype(dtype=pf.Vector), scale=10.0)
    
    color_ramp = pf.nodes.shader.color_ramp(
        fac=voronoi.color.astype(dtype=float),
        points=[(0.404, (0.0, 0.0, 0.0, 1.0)), (0.539, (1.0, 1.0, 1.0, 1.0))],
    )
    
    mapping_1 = pf.nodes.shader.mapping(coord.object)
    
    noise_1 = pf.nodes.shader.noise(vector=mapping_1, scale=105.687286, detail=15.0, roughness=0.7667)
    
    voronoi_1 = pf.nodes.shader.voronoi(vector=noise_1.fac.astype(dtype=pf.Vector), scale=9.984632)
    
    color_ramp_1 = pf.nodes.shader.color_ramp(
        fac=voronoi_1.color.astype(dtype=float),
        points=[(0.349, (0.0, 0.0, 0.0, 1.0)), (0.692, (1.0, 1.0, 1.0, 1.0))],
    )
    
    principled_base_color_factor = color_ramp.color.astype(dtype=pf.Vector) * color_ramp_1.color.astype(dtype=pf.Vector)
    
    mapping_2 = pf.nodes.shader.mapping(vector=coord.uv, scale=(1.0, 1.0, 0.0))
    
    noise_2 = pf.nodes.shader.noise(vector=mapping_2, scale=6.266839)
    
    color_ramp_2 = pf.nodes.shader.color_ramp(
        fac=noise_2.fac,
        points=[(0.355, (0.381, 0.238, 0.118, 1.0)), (0.738, (0.497, 0.503, 0.468, 1.0))],
    )
    
    principled_base_color = pf.nodes.func.mix_rgb(
        factor=principled_base_color_factor.astype(dtype=float),
        a=pf.Color((0.1912, 0.0452, 0.0103)),
        b=color_ramp_2.color,
    )
    
    principled = pf.nodes.shader.principled_bsdf(
        base_color=principled_base_color,
        roughness=0.4409,
        ior=1.45,
        subsurface_method='RANDOM_WALK_SKIN',
        subsurface_ior=1.4,
        subsurface_anisotropy=0.0,
        distribution='GGX',
        emission_color=pf.Color((0.0, 0.0, 0.0)),
        emission_strength=1.0,
    )
    glass = pf.nodes.shader.glass_bsdf(ior=1.45, normal=(0.0, 0.0, 0.0), distribution='BECKMANN')
    
    mix_shader = pf.nodes.shader.mix_shader(factor=0.2, a=principled, b=glass)
    
    return pf.Material(surface=mix_shader, displacement=None, volume=None)


shader = shader_bone()