import bpy
import mathutils
from numpy.random import uniform, normal, randint
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core.util.color import color_category
from infinigen.core import surface



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