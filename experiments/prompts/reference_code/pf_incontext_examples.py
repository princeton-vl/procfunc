

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
