
def shader_bone(nw: NodeWrangler):
    # Code generated using version 2.4.3 of the node_transpiler

    texture_coordinate = nw.new_node(Nodes.TextureCoord)
    
    mapping = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["Object"], 'Location': (1.7 + uniform(-1, 1) * 0.05, 0.29999999999999999 + uniform(-1, 1) * 0.05, uniform(-1, 1) * 0.05)})
    
    noise_texture_2 = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': mapping, 'Scale': 10.800000000000001 + uniform(-1, 1) * 3, 'Detail': 15.0, 'Roughness': 0.76670000000000005})
    
    voronoi_texture_1 = nw.new_node(Nodes.VoronoiTexture,
        input_kwargs={'Vector': noise_texture_2.outputs["Fac"], 'Scale': 10.0})
    
    colorramp_2 = nw.new_node(Nodes.ColorRamp,
        input_kwargs={'Fac': voronoi_texture_1.outputs["Color"]})
    colorramp_2.color_ramp.elements[0].position = 0.4364 + uniform(-1, 1) * 0.05
    colorramp_2.color_ramp.elements[0].color = (0, 0, 0, 1.0)
    colorramp_2.color_ramp.elements[1].position = 0.58 + uniform(-1, 1) * 0.05
    colorramp_2.color_ramp.elements[1].color = (1, 1, 1, 1.0)
    
    mapping_2 = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["Object"]})
    
    noise_texture = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': mapping_2, 'Scale': 98.900000000000006 + uniform(-0.3, 1) * 30, 'Detail': 15.0, 'Roughness': 0.76670000000000005})
    
    voronoi_texture = nw.new_node(Nodes.VoronoiTexture,
        input_kwargs={'Vector': noise_texture.outputs["Fac"], 'Scale': 10.0 + uniform(-1, 1) * 0.05})
    
    colorramp = nw.new_node(Nodes.ColorRamp,
        input_kwargs={'Fac': voronoi_texture.outputs["Color"]})
    colorramp.color_ramp.elements[0].position = 0.3089 + uniform(-1, 1) * 0.05
    colorramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    colorramp.color_ramp.elements[1].position = 0.673 + uniform(-1, 1) * 0.05
    colorramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    
    multiply = nw.new_node(Nodes.VectorMath,
        input_kwargs={0: colorramp_2.outputs["Color"], 1: colorramp.outputs["Color"]},
        attrs={'operation': 'MULTIPLY'})
    
    mapping_1 = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["UV"], 'Scale': (1.0, 1.0, 0.0)})
    
    noise_texture_1 = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': mapping_1, 'Scale': 6.4000000000000004 + uniform(-1, 1) * 1})
    
    colorramp_1 = nw.new_node(Nodes.ColorRamp,
        input_kwargs={'Fac': noise_texture_1.outputs["Fac"]})
    colorramp_1.color_ramp.elements[0].position = 0.3682 + uniform(-1, 1) * 0.05
    colorramp_1.color_ramp.elements[0].color = (0.38129999999999997, 0.2384, 0.1183, 1.0)
    colorramp_1.color_ramp.elements[1].position = 0.7591 + uniform(-1, 1) * 0.05
    colorramp_1.color_ramp.elements[1].color = (0.49690000000000001, 0.50290000000000001, 0.46779999999999999, 1.0)
    
    mix = nw.new_node(Nodes.MixRGB,
        input_kwargs={'Fac': multiply.outputs["Vector"], 'Color1': (0.19120000000000001, 0.045199999999999997, 0.0103, 1.0), 'Color2': colorramp_1.outputs["Color"]})
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': mix, 'Roughness': 0.44090000000000001})
    
    glass_bsdf = nw.new_node('ShaderNodeBsdfGlass')
    
    mix_shader = nw.new_node(Nodes.MixShader,
        input_kwargs={'Fac': 0.2, 1: principled_bsdf, 2: glass_bsdf})
    
    material_output = nw.new_node(Nodes.MaterialOutput,
        input_kwargs={'Surface': mix_shader})



def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_bone, selection=selection)

# material_obj is what we want to apply this onto.
apply(material_obj)


def shader_nose(nw: NodeWrangler):
    # Code generated using version 2.4.3 of the node_transpiler
    musgrave_texture = nw.new_node(Nodes.MusgraveTexture,
        input_kwargs={'Scale': U(2, 6), 'Detail': 14.699999999999999, 'Dimension': 1.5})
    
    colorramp = nw.new_node(Nodes.ColorRamp,
        input_kwargs={'Fac': musgrave_texture})
    colorramp.color_ramp.elements[0].position = U(0.2, 0.6)
    colorramp.color_ramp.elements[0].color = (0.008, 0.0053, 0.0044, 1.0)
    colorramp.color_ramp.elements[1].position = 1.0
    colorramp.color_ramp.elements[1].color = (0.7068, 0.436, 0.35, 1.0)
    
    musgrave_texture_1 = nw.new_node(Nodes.MusgraveTexture,
        input_kwargs={'Scale': 10.0})
    
    map_range = nw.new_node(Nodes.MapRange,
        input_kwargs={'Value': musgrave_texture_1, 3: N(0.4, 0.1), 4: N(0.7, 0.15)})
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': colorramp.outputs["Color"], 'Roughness': map_range.outputs["Result"]})
    
    material_output = nw.new_node(Nodes.MaterialOutput,
        input_kwargs={'Surface': principled_bsdf})


def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_nose, selection=selection)

# material_obj is what we want to apply this onto.
apply(material_obj)

def shader_snake_plant(nw: NodeWrangler):
    # Code generated using version 2.4.3 of the node_transpiler

    r = 2.0 * np.random.choice([0, 1], p=(0.4, 0.6))
    multiply = nw.new_node(Nodes.Math,
                           input_kwargs={0: 0.001, 1: r},
                           attrs={'operation': 'MULTIPLY'})

    colorramp_1 = nw.new_node(Nodes.ColorRamp,
                              input_kwargs={'Fac': multiply})
    e = U(0.34, 0.42)
    colorramp_1.color_ramp.elements[0].position = e
    colorramp_1.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
    colorramp_1.color_ramp.elements[1].position = e + 0.02
    colorramp_1.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)

    texture_coordinate_1 = nw.new_node(Nodes.TextureCoord)

    mapping_1 = nw.new_node(Nodes.Mapping,
                            input_kwargs={'Vector': texture_coordinate_1.outputs["Object"]})

    noise_texture = nw.new_node(Nodes.NoiseTexture,
                                input_kwargs={'Vector': mapping_1, 'Scale': U(0.2, 1.0), 'Roughness': 1.0})

    multiply_1 = nw.new_node(Nodes.VectorMath,
                             input_kwargs={0: noise_texture.outputs["Fac"], 1: (1.0, 1.0, 0.6)},
                             attrs={'operation': 'MULTIPLY'})

    add = nw.new_node(Nodes.VectorMath,
                      input_kwargs={0: multiply_1.outputs["Vector"], 1: mapping_1})

    wave_texture = nw.new_node(Nodes.WaveTexture,
                               input_kwargs={'Vector': add.outputs["Vector"], 'Scale': U(1.0, 2.5),
                                             'Distortion': U(2.0, 4.5),
                                             'Detail Scale': U(2.0, 8.0), 'Detail Roughness': 2.0},
                               attrs={'bands_direction': 'Z'})

    w = U(0.2, 0.7)
    greater_than = nw.new_node(Nodes.Math,
                               input_kwargs={0: wave_texture.outputs["Fac"], 1: w},
                               attrs={'operation': 'GREATER_THAN'})

    mapping_2 = nw.new_node(Nodes.Mapping,
                            input_kwargs={'Vector': texture_coordinate_1.outputs["Object"], 'Scale': (7.0, 7.0, 0.05)})

    noise_texture_1 = nw.new_node(Nodes.NoiseTexture,
                                  input_kwargs={'Vector': mapping_2, 'Scale': U(20.0, 40.0)})

    multiply_2 = nw.new_node(Nodes.Math,
                             input_kwargs={0: greater_than, 1: noise_texture_1.outputs["Fac"]},
                             attrs={'operation': 'MULTIPLY'})

    colorramp_8 = nw.new_node(Nodes.ColorRamp,
                              input_kwargs={'Fac': multiply_2})
    colorramp_8.color_ramp.elements[0].position = 0.2318
    colorramp_8.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    colorramp_8.color_ramp.elements[1].position = U(0.55, 0.75)
    colorramp_8.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

    r = 0.6 + (w - 0.2) * 0.6
    colorramp_4 = nw.new_node(Nodes.ColorRamp,
                              input_kwargs={'Fac': wave_texture.outputs["Fac"]})
    colorramp_4.color_ramp.elements[0].position = 0.6 + (w - 0.2) * 0.6
    colorramp_4.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    colorramp_4.color_ramp.elements[1].position = np.minimum(1.0, r + U(0.02, 0.15))
    colorramp_4.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

    mix_1 = nw.new_node(Nodes.MixRGB,
                        input_kwargs={'Fac': U(0.8, 1.0), 'Color1': colorramp_8.outputs["Color"],
                                      'Color2': colorramp_4.outputs["Color"]},
                        attrs={'blend_type': 'ADD'})

    c = [U(0.28, 0.36), U(0.35, 0.80), U(0.20, 0.45)]
    colorramp_3 = nw.new_node(Nodes.ColorRamp,
                              input_kwargs={'Fac': mix_1})
    colorramp_3.color_ramp.elements[0].position = 0.0
    colorramp_3.color_ramp.elements[0].color = hsv2rgba(c)
    colorramp_3.color_ramp.elements[1].position = 1.0
    c[2] = U(0.03, 0.07)
    c[1] = U(0.5, 0.8)
    c[0] += N(0, 0.015)
    colorramp_3.color_ramp.elements[1].color = hsv2rgba(c)

    mix = nw.new_node(Nodes.MixRGB,
                      input_kwargs={'Fac': colorramp_1.outputs["Color"], 'Color1': (*colorsys.hsv_to_rgb(
                          *[U(0.16, 0.23), U(0.8, 0.95), U(0.35, 0.8)]), 1.0),
                                    'Color2': colorramp_3.outputs["Color"]})

    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
                                  input_kwargs={'Base Color': mix, 'Roughness': U(8.0, 15.0), 'Clearcoat Roughness': 0.0})

    material_output = nw.new_node(Nodes.MaterialOutput,
                                  input_kwargs={'Surface': principled_bsdf})


def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_snake_plant, selection=selection)

# material_obj is what we want to apply this onto.
apply(material_obj)

def shader_tongue(nw: NodeWrangler):
    # Code generated using version 2.4.3 of the node_transpiler

    musgrave_texture = nw.new_node(Nodes.MusgraveTexture,
        input_kwargs={'Scale': 37.88})
    
    colorramp = nw.new_node(Nodes.ColorRamp,
        input_kwargs={'Fac': musgrave_texture})
    colorramp.color_ramp.elements[0].position = 0.24
    colorramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    colorramp.color_ramp.elements[1].position = 1.0
    colorramp.color_ramp.elements[1].color = (0.0979, 0.0979, 0.0979, 1.0)
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': (0.8, 0.0605, 0.0437, 1.0), 'Subsurface': 0.0312, 'Subsurface Color': (0.8, 0.0, 0.2679, 1.0), 'Roughness': colorramp.outputs["Color"]})
    
    material_output = nw.new_node(Nodes.MaterialOutput,
        input_kwargs={'Surface': principled_bsdf})

def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_tongue, selection=selection)

# material_obj is what we want to apply this onto.
apply(material_obj)
# Copyright (c) Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Mingzhe Wang



def shader_wood(nw: NodeWrangler, rand=False, **input_kwargs):
    # Code generated using version 2.4.3 of the node_transpiler

    texture_coordinate_1 = nw.new_node(Nodes.TextureCoord)
    
    mapping_2 = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate_1.outputs["Generated"], 'Rotation': uniform(0,ma.pi*2, 3)})
    
    mapping_1 = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': mapping_2, 'Scale': (0.5, sample_range(2, 4) if rand else 3, 0.5)})
    
    musgrave_texture_2 = nw.new_node(Nodes.MusgraveTexture,
        input_kwargs={'Vector': mapping_1, 'Scale': 2.0},
        attrs={'musgrave_dimensions': '4D'})
    if rand:
        musgrave_texture_2.inputs['W'].default_value = sample_range(0, 5)
        musgrave_texture_2.inputs['Scale'].default_value = sample_ratio(2.0, 3/4, 4/3)
    
    noise_texture_1 = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': musgrave_texture_2, 'W': 0.7, 'Scale': 10.0},
        attrs={'noise_dimensions': '4D'})
    if rand:
        noise_texture_1.inputs['W'].default_value = sample_range(0, 5)
        noise_texture_1.inputs['Scale'].default_value = sample_ratio(5, 0.5, 2)
    
    colorramp_2 = nw.new_node(Nodes.ColorRamp,
        input_kwargs={'Fac': noise_texture_1.outputs["Fac"]})
    colorramp_2.color_ramp.elements.new(0)
    colorramp_2.color_ramp.elements[0].position = 0.1727
    colorramp_2.color_ramp.elements[0].color = (0.1567, 0.0162, 0.0017, 1.0)
    colorramp_2.color_ramp.elements[1].position = 0.4364
    colorramp_2.color_ramp.elements[1].color = (0.2908, 0.1007, 0.0148, 1.0)
    colorramp_2.color_ramp.elements[2].position = 0.5864
    colorramp_2.color_ramp.elements[2].color = (0.0814, 0.0344, 0.0125, 1.0)
    if rand:
        colorramp_2.color_ramp.elements[0].position += sample_range(-0.05, 0.05)
        colorramp_2.color_ramp.elements[1].position += sample_range(-0.1, 0.1)
        colorramp_2.color_ramp.elements[2].position += sample_range(-0.05, 0.05)
        for e in colorramp_2.color_ramp.elements:
            sample_color(e.color, offset=0.03)

    colorramp_4 = nw.new_node(Nodes.ColorRamp,
        input_kwargs={'Fac': noise_texture_1.outputs["Fac"]})
    colorramp_4.color_ramp.elements[0].position = 0.0
    colorramp_4.color_ramp.elements[0].color = (0.4855, 0.4855, 0.4855, 1.0)
    colorramp_4.color_ramp.elements[1].position = 1.0
    colorramp_4.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    
    principled_bsdf_1 = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': colorramp_2.outputs["Color"], 'Roughness': colorramp_4.outputs["Color"]},
        attrs={'subsurface_method': 'BURLEY'})
    
    material_output = nw.new_node(Nodes.MaterialOutput,
        input_kwargs={'Surface': principled_bsdf_1})

def apply(obj, geo_kwargs=None, shader_kwargs=None, **kwargs):
    surface.add_material(obj, shader_wood, reuse=False, input_kwargs=shader_kwargs)

# material_obj is what we want to apply this onto.
apply(material_obj)
