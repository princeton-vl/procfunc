

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
