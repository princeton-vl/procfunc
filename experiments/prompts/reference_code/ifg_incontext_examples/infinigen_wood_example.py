import bpy
import mathutils
from numpy.random import uniform, normal, randint
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core.util.color import color_category
from infinigen.core import surface



def shader_wood(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    texture_coordinate = nw.new_node(Nodes.TextureCoord)
    
    mapping = nw.new_node(Nodes.Mapping,
        input_kwargs={'Vector': texture_coordinate.outputs["Generated"], 'Rotation': (5.4664, 1.1366, 2.6948)})
    
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