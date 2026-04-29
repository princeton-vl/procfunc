import bpy
import mathutils
from numpy.random import uniform, normal, randint
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core.util.color import color_category
from infinigen.core import surface



def shader_nose(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    musgrave_texture = nw.new_node(Nodes.MusgraveTexture, input_kwargs={'Scale': 3.3441, 'Detail': 14.7000, 'Dimension': 1.5000})
    
    color_ramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': musgrave_texture})
    color_ramp.color_ramp.elements[0].position = 0.4737
    color_ramp.color_ramp.elements[0].color = [0.0080, 0.0053, 0.0044, 1.0000]
    color_ramp.color_ramp.elements[1].position = 1.0000
    color_ramp.color_ramp.elements[1].color = [0.7068, 0.4360, 0.3500, 1.0000]
    
    musgrave_texture_1 = nw.new_node(Nodes.MusgraveTexture, input_kwargs={'Scale': 10.0000})
    
    map_range = nw.new_node(Nodes.MapRange, input_kwargs={'Value': musgrave_texture_1, 3: 0.4756, 4: 0.7574})
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': color_ramp.outputs["Color"], 'Roughness': map_range.outputs["Result"]})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': principled_bsdf}, attrs={'is_active_output': True})



def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, shader_nose, selection=selection)