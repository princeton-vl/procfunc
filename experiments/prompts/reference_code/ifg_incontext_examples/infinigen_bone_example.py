import bpy
import mathutils
from numpy.random import uniform, normal, randint
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core.util.color import color_category
from infinigen.core import surface



def shader_bone(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    texture_coordinate = nw.new_node(Nodes.TextureCoord)
    
    mapping = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["Object"], 'Location': (1.6829, 0.3078, 0.0418)})
    
    noise_texture = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': mapping, 'Scale': 10.4943, 'Detail': 15.0000, 'Roughness': 0.7667})
    
    voronoi_texture = nw.new_node(Nodes.VoronoiTexture, input_kwargs={'Vector': noise_texture.outputs["Fac"], 'Scale': 10.0000})
    
    color_ramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': voronoi_texture.outputs["Color"]})
    color_ramp.color_ramp.elements[0].position = 0.4484
    color_ramp.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp.color_ramp.elements[1].position = 0.5451
    color_ramp.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    mapping_1 = nw.new_node(Nodes.Mapping, input_kwargs={'Vector': texture_coordinate.outputs["Object"]})
    
    noise_texture_1 = nw.new_node(Nodes.NoiseTexture,
        input_kwargs={'Vector': mapping_1, 'Scale': 92.0644, 'Detail': 15.0000, 'Roughness': 0.7667})
    
    voronoi_texture_1 = nw.new_node(Nodes.VoronoiTexture, input_kwargs={'Vector': noise_texture_1.outputs["Fac"], 'Scale': 10.0362})
    
    color_ramp_1 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': voronoi_texture_1.outputs["Color"]})
    color_ramp_1.color_ramp.elements[0].position = 0.3117
    color_ramp_1.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    color_ramp_1.color_ramp.elements[1].position = 0.6845
    color_ramp_1.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    multiply = nw.new_node(Nodes.VectorMath,
        input_kwargs={0: color_ramp.outputs["Color"], 1: color_ramp_1.outputs["Color"]},
        attrs={'operation': 'MULTIPLY'})
    
    mapping_2 = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["UV"], 'Scale': (1.0000, 1.0000, 0.0000)})
    
    noise_texture_2 = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Vector': mapping_2, 'Scale': 6.0377})
    
    color_ramp_2 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': noise_texture_2.outputs["Fac"]})
    color_ramp_2.color_ramp.elements[0].position = 0.3864
    color_ramp_2.color_ramp.elements[0].color = [0.3813, 0.2384, 0.1183, 1.0000]
    color_ramp_2.color_ramp.elements[1].position = 0.7645
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