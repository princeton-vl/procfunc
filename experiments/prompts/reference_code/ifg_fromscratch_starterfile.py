import bpy
import bpy
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core import surface

def my_shader_function(nw: NodeWrangler):
    
    # TODO

    material_output = nw.new_node(Nodes.MaterialOutput,
        input_kwargs={'Surface': None, 'Displacement': None},
        attrs={'is_active_output': True})

def apply(obj, selection=None, **kwargs):
    surface.add_material(obj, my_shader_function, selection=selection)
material_obj = bpy.context.active_object
apply(material_obj)