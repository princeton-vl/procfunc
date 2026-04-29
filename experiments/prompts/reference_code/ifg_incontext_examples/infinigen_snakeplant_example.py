import bpy
import mathutils
from numpy.random import uniform, normal, randint
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core.util.color import color_category
from infinigen.core import surface



def shader_snake_plant(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    multiply = nw.new_node(Nodes.Math, input_kwargs={0: 0.0010, 1: 2.0000}, attrs={'operation': 'MULTIPLY'})
    
    color_ramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': multiply})
    color_ramp.color_ramp.elements[0].position = 0.4145
    color_ramp.color_ramp.elements[0].color = [1.0000, 1.0000, 1.0000, 1.0000]
    color_ramp.color_ramp.elements[1].position = 0.4345
    color_ramp.color_ramp.elements[1].color = [0.0000, 0.0000, 0.0000, 1.0000]
    
    texture_coordinate = nw.new_node(Nodes.TextureCoord)
    
    mapping = nw.new_node(Nodes.Mapping, input_kwargs={'Vector': texture_coordinate.outputs["Object"]})
    
    noise_texture = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Vector': mapping, 'Scale': 0.5985, 'Roughness': 1.0000})
    
    multiply_1 = nw.new_node(Nodes.VectorMath,
        input_kwargs={0: noise_texture.outputs["Fac"], 1: (1.0000, 1.0000, 0.6000)},
        attrs={'operation': 'MULTIPLY'})
    
    add = nw.new_node(Nodes.VectorMath, input_kwargs={0: multiply_1.outputs["Vector"], 1: mapping})
    
    wave_texture = nw.new_node(Nodes.WaveTexture,
        input_kwargs={'Vector': add.outputs["Vector"], 'Scale': 2.4003, 'Distortion': 2.3348, 'Detail Scale': 7.8202, 'Detail Roughness': 2.0000},
        attrs={'bands_direction': 'Z'})
    
    greater_than = nw.new_node(Nodes.Math,
        input_kwargs={0: wave_texture.outputs["Fac"], 1: 0.2357},
        attrs={'operation': 'GREATER_THAN'})
    
    mapping_1 = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["Object"], 'Scale': (7.0000, 7.0000, 0.0500)})
    
    noise_texture_1 = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Vector': mapping_1, 'Scale': 21.4871})
    
    multiply_2 = nw.new_node(Nodes.Math,
        input_kwargs={0: greater_than, 1: noise_texture_1.outputs["Fac"]},
        attrs={'operation': 'MULTIPLY'})
    
    color_ramp_1 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': multiply_2})
    color_ramp_1.color_ramp.elements[0].position = 0.2318
    color_ramp_1.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp_1.color_ramp.elements[1].position = 0.6756
    color_ramp_1.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    color_ramp_2 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': wave_texture.outputs["Fac"]})
    color_ramp_2.color_ramp.elements[0].position = 0.6214
    color_ramp_2.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp_2.color_ramp.elements[1].position = 0.6551
    color_ramp_2.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    mix = nw.new_node(Nodes.Mix,
        input_kwargs={0: 0.8479, 6: color_ramp_1.outputs["Color"], 7: color_ramp_2.outputs["Color"]},
        attrs={'blend_type': 'ADD', 'data_type': 'RGBA'})
    
    color_ramp_3 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': mix.outputs[2]})
    color_ramp_3.color_ramp.elements[0].position = 0.0000
    color_ramp_3.color_ramp.elements[0].color = [0.1835, 0.3931, 0.1585, 1.0000]
    color_ramp_3.color_ramp.elements[1].position = 1.0000
    color_ramp_3.color_ramp.elements[1].color = [0.0164, 0.0441, 0.0207, 1.0000]
    
    mix_1 = nw.new_node(Nodes.Mix,
        input_kwargs={0: color_ramp.outputs["Color"], 6: (0.6837, 0.7008, 0.1067, 1.0000), 7: color_ramp_3.outputs["Color"]},
        attrs={'data_type': 'RGBA'})
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': mix_1.outputs[2], 'Roughness': 11.7247, 'Clearcoat Roughness': 0.0000})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': principled_bsdf}, attrs={'is_active_output': True})



def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_snake_plant, selection=selection)