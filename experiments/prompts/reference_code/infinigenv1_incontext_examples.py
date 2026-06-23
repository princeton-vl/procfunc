


def shader_bone(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    texture_coordinate = nw.new_node(Nodes.TextureCoord)
    
    mapping = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["Object"], 'Location': (1.7315, 0.3225, 0.0310)})
    
    noise_texture = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': mapping, 'Scale': 8.6326, 'Detail': 15.0000, 'Roughness': 0.7667})
    
    voronoi_texture = nw.new_node(Nodes.VoronoiTexture, input_kwargs={'Vector': noise_texture.outputs["Fac"], 'Scale': 10.0000})
    
    color_ramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': voronoi_texture.outputs["Color"]})
    color_ramp.color_ramp.elements[0].position = 0.4689
    color_ramp.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp.color_ramp.elements[1].position = 0.5859
    color_ramp.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    mapping_1 = nw.new_node(Nodes.Mapping, input_kwargs={'Vector': texture_coordinate.outputs["Object"]})
    
    noise_texture_1 = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': mapping_1, 'Scale': 124.2583, 'Detail': 15.0000, 'Roughness': 0.7667})
    
    voronoi_texture_1 = nw.new_node(Nodes.VoronoiTexture, input_kwargs={'Vector': noise_texture_1.outputs["Fac"], 'Scale': 10.0248})
    
    color_ramp_1 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': voronoi_texture_1.outputs["Color"]})
    color_ramp_1.color_ramp.elements[0].position = 0.2866
    color_ramp_1.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp_1.color_ramp.elements[1].position = 0.7192
    color_ramp_1.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    multiply = nw.new_node(Nodes.VectorMath,
        input_kwargs={0: color_ramp.outputs["Color"], 1: color_ramp_1.outputs["Color"]},
        attrs={'operation': 'MULTIPLY'})
    
    mapping_2 = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["UV"], 'Scale': (1.0000, 1.0000, 0.0000)})
    
    noise_texture_2 = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Vector': mapping_2, 'Scale': 7.2055})
    
    color_ramp_2 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': noise_texture_2.outputs["Fac"]})
    color_ramp_2.color_ramp.elements[0].position = 0.3457
    color_ramp_2.color_ramp.elements[0].color = [0.3813, 0.2384, 0.1183, 1.0000]
    color_ramp_2.color_ramp.elements[1].position = 0.7344
    color_ramp_2.color_ramp.elements[1].color = [0.4969, 0.5029, 0.4678, 1.0000]
    
    mix = nw.new_node(Nodes.Mix,
        input_kwargs={0: multiply.outputs["Vector"], 6: (0.1912, 0.0452, 0.0103, 1.0000), 7: color_ramp_2.outputs["Color"]},
        attrs={'data_type': 'RGBA'})
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF, input_kwargs={'Base Color': mix.outputs[2], 'Roughness': 0.4409})
    
    glass_bsdf = nw.new_node(Nodes.GlassBSDF)
    
    mix_shader = nw.new_node(Nodes.MixShader, input_kwargs={'Fac': 0.2000, 1: principled_bsdf, 2: glass_bsdf})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': mix_shader}, attrs={'is_active_output': True})



def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_bone, selection=selection)



def shader_nose(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    musgrave_texture = nw.new_node(Nodes.MusgraveTexture, input_kwargs={'Scale': 4.9095, 'Detail': 14.7000, 'Dimension': 1.5000})
    
    color_ramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': musgrave_texture})
    color_ramp.color_ramp.elements[0].position = 0.3580
    color_ramp.color_ramp.elements[0].color = [0.0080, 0.0053, 0.0044, 1.0000]
    color_ramp.color_ramp.elements[1].position = 1.0000
    color_ramp.color_ramp.elements[1].color = [0.7068, 0.4360, 0.3500, 1.0000]
    
    musgrave_texture_1 = nw.new_node(Nodes.MusgraveTexture, input_kwargs={'Scale': 10.0000})
    
    map_range = nw.new_node(Nodes.MapRange, input_kwargs={'Value': musgrave_texture_1, 3: 0.4325, 4: 0.8932})
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': color_ramp.outputs["Color"], 'Roughness': map_range.outputs["Result"]})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': principled_bsdf}, attrs={'is_active_output': True})



def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_nose, selection=selection)



def shader_snake_plant(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    multiply = nw.new_node(Nodes.Math, input_kwargs={0: 0.0010, 1: 2.0000}, attrs={'operation': 'MULTIPLY'})
    
    color_ramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': multiply})
    color_ramp.color_ramp.elements[0].position = 0.3573
    color_ramp.color_ramp.elements[0].color = [1.0000, 1.0000, 1.0000, 1.0000]
    color_ramp.color_ramp.elements[1].position = 0.3773
    color_ramp.color_ramp.elements[1].color = [0.0000, 0.0000, 0.0000, 1.0000]
    
    texture_coordinate = nw.new_node(Nodes.TextureCoord)
    
    mapping = nw.new_node(Nodes.Mapping, input_kwargs={'Vector': texture_coordinate.outputs["Object"]})
    
    noise_texture = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Vector': mapping, 'Scale': 0.2639, 'Roughness': 1.0000})
    
    multiply_1 = nw.new_node(Nodes.VectorMath,
        input_kwargs={0: noise_texture.outputs["Fac"], 1: (1.0000, 1.0000, 0.6000)},
        attrs={'operation': 'MULTIPLY'})
    
    add = nw.new_node(Nodes.VectorMath, input_kwargs={0: multiply_1.outputs["Vector"], 1: mapping})
    
    wave_texture = nw.new_node(Nodes.WaveTexture,
        input_kwargs={'Vector': add.outputs["Vector"], 'Scale': 1.1337, 'Distortion': 2.2397, 'Detail Scale': 7.4417, 'Detail Roughness': 2.0000},
        attrs={'bands_direction': 'Z'})
    
    greater_than = nw.new_node(Nodes.Math,
        input_kwargs={0: wave_texture.outputs["Fac"], 1: 0.5656},
        attrs={'operation': 'GREATER_THAN'})
    
    mapping_1 = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["Object"], 'Scale': (7.0000, 7.0000, 0.0500)})
    
    noise_texture_1 = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Vector': mapping_1, 'Scale': 26.0305})
    
    multiply_2 = nw.new_node(Nodes.Math,
        input_kwargs={0: greater_than, 1: noise_texture_1.outputs["Fac"]},
        attrs={'operation': 'MULTIPLY'})
    
    color_ramp_1 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': multiply_2})
    color_ramp_1.color_ramp.elements[0].position = 0.2318
    color_ramp_1.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp_1.color_ramp.elements[1].position = 0.6201
    color_ramp_1.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    color_ramp_2 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': wave_texture.outputs["Fac"]})
    color_ramp_2.color_ramp.elements[0].position = 0.8194
    color_ramp_2.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp_2.color_ramp.elements[1].position = 0.9424
    color_ramp_2.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    mix = nw.new_node(Nodes.Mix,
        input_kwargs={0: 0.8102, 6: color_ramp_1.outputs["Color"], 7: color_ramp_2.outputs["Color"]},
        attrs={'blend_type': 'ADD', 'data_type': 'RGBA'})
    
    color_ramp_3 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': mix.outputs[2]})
    color_ramp_3.color_ramp.elements[0].position = 0.0000
    color_ramp_3.color_ramp.elements[0].color = [0.0967, 0.2487, 0.0865, 1.0000]
    color_ramp_3.color_ramp.elements[1].position = 1.0000
    color_ramp_3.color_ramp.elements[1].color = [0.0089, 0.0432, 0.0093, 1.0000]
    
    mix_1 = nw.new_node(Nodes.Mix,
        input_kwargs={0: color_ramp.outputs["Color"], 6: (0.5379, 0.5922, 0.1060, 1.0000), 7: color_ramp_3.outputs["Color"]},
        attrs={'data_type': 'RGBA'})
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': mix_1.outputs[2], 'Roughness': 10.3637, 'Clearcoat Roughness': 0.0000})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': principled_bsdf}, attrs={'is_active_output': True})



def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_snake_plant, selection=selection)



def shader_tongue(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    musgrave_texture = nw.new_node(Nodes.MusgraveTexture, input_kwargs={'Scale': 37.8800})
    
    color_ramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': musgrave_texture})
    color_ramp.color_ramp.elements[0].position = 0.2400
    color_ramp.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp.color_ramp.elements[1].position = 1.0000
    color_ramp.color_ramp.elements[1].color = [0.0979, 0.0979, 0.0979, 1.0000]
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': (0.8000, 0.0605, 0.0437, 1.0000), 'Subsurface': 0.0312, 'Subsurface Color': (0.8000, 0.0000, 0.2679, 1.0000), 'Roughness': color_ramp.outputs["Color"]})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': principled_bsdf}, attrs={'is_active_output': True})



def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_tongue, selection=selection)



def shader_wood(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    texture_coordinate = nw.new_node(Nodes.TextureCoord)
    
    mapping = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["Generated"], 'Rotation': (2.1682, 1.0910, 3.1178)})
    
    mapping_1 = nw.new_node(Nodes.Mapping, input_kwargs={'Vector': mapping, 'Scale': (0.5000, 3.0000, 0.5000)})
    
    musgrave_texture = nw.new_node(Nodes.MusgraveTexture,
        input_kwargs={'Vector': mapping_1, 'Scale': 2.0000},
        attrs={'musgrave_dimensions': '4D'})
    
    noise_texture = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': musgrave_texture, 'W': 0.7000, 'Scale': 10.0000},
        attrs={'noise_dimensions': '4D'})
    
    color_ramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': noise_texture.outputs["Fac"]})
    color_ramp.color_ramp.elements.new(0)
    color_ramp.color_ramp.elements[0].position = 0.1727
    color_ramp.color_ramp.elements[0].color = [0.1567, 0.0162, 0.0017, 1.0000]
    color_ramp.color_ramp.elements[1].position = 0.4364
    color_ramp.color_ramp.elements[1].color = [0.2908, 0.1007, 0.0148, 1.0000]
    color_ramp.color_ramp.elements[2].position = 0.5864
    color_ramp.color_ramp.elements[2].color = [0.0814, 0.0344, 0.0125, 1.0000]
    
    color_ramp_1 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': noise_texture.outputs["Fac"]})
    color_ramp_1.color_ramp.elements[0].position = 0.0000
    color_ramp_1.color_ramp.elements[0].color = [0.4855, 0.4855, 0.4855, 1.0000]
    color_ramp_1.color_ramp.elements[1].position = 1.0000
    color_ramp_1.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': color_ramp.outputs["Color"], 'Roughness': color_ramp_1.outputs["Color"]},
        attrs={'subsurface_method': 'BURLEY'})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': principled_bsdf}, attrs={'is_active_output': True})



def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_wood, selection=selection)
