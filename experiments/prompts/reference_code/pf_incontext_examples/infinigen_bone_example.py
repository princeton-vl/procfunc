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
        location=(1.7295163, 0.33822015, -0.026744038),
    )
    
    principled_5 = pf.nodes.texture.noise(vector=mapping, scale=12.834769, detail=15.0, roughness=0.7667)
    
    principled_0_fac_1 = pf.nodes.texture.voronoi(
        vector=principled_5.fac.astype(dtype=pf.Vector),
        scale=10.0,
    )
    principled_4 = pf.nodes.color.color_ramp(
        fac=principled_0_fac_1.color.astype(dtype=float),
        points=[(0.426, (0.0, 0.0, 0.0, 1.0)), (0.592, (1.0, 1.0, 1.0, 1.0))],
    )
    mapping_1 = pf.nodes.shader.mapping(coord.object)
    
    principled_3 = pf.nodes.texture.noise(vector=mapping_1, scale=98.93956, detail=15.0, roughness=0.7667)
    
    principled_0_fac_0 = pf.nodes.texture.voronoi(
        vector=principled_3.fac.astype(dtype=pf.Vector),
        scale=10.022529,
    )
    principled_2 = pf.nodes.color.color_ramp(
        fac=principled_0_fac_0.color.astype(dtype=float),
        points=[(0.262, (0.0, 0.0, 0.0, 1.0)), (0.652, (1.0, 1.0, 1.0, 1.0))],
    )
    principled_base_color_factor = principled_4.color.astype(dtype=pf.Vector) * principled_2.color.astype(dtype=pf.Vector)
    mapping_2 = pf.nodes.shader.mapping(vector=coord.uv, scale=(1.0, 1.0, 0.0))
    
    principled_1 = pf.nodes.texture.noise(vector=mapping_2, scale=5.9899945)
    
    principled_base_color_b = pf.nodes.color.color_ramp(
        fac=principled_1.fac,
        points=[(0.342, (0.381, 0.238, 0.118, 1.0)), (0.796, (0.497, 0.503, 0.468, 1.0))],
    )
    principled_base_color = pf.nodes.color.mix_rgb(
        factor=principled_base_color_factor.astype(dtype=float),
        a=(0.1912, 0.0452, 0.0103),
        b=principled_base_color_b.color,
    )
    principled = pf.nodes.shader.principled_bsdf(
        base_color=principled_base_color,
        roughness=0.4409,
        ior=1.45,
        subsurface_method='RANDOM_WALK_SKIN',
        subsurface_radius=(1.0, 0.2, 0.1),
        subsurface_ior=1.4,
        subsurface_anisotropy=0.0,
        distribution='GGX',
        emission_color=(0.0, 0.0, 0.0),
        emission_strength=1.0,
    )
    glass = pf.nodes.shader.glass_bsdf(ior=1.45, distribution='BECKMANN')
    
    mix_shader = pf.nodes.shader.mix_shader(factor=0.2, a=principled, b=glass)
    
    return pf.Material(surface=mix_shader, displacement=None, volume=None)


shader = shader_bone()