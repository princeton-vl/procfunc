import argparse
import sys
from pathlib import Path

import bpy
import mathutils
from infinigen.core.nodes.node_info import Nodes
from infinigen.core.nodes.node_wrangler import NodeWrangler

UNIVERSAL_ATTR_NAMES = {
    "show_preview", "__module__", "is_registered_node_type", "bl_rna", "poll",
    "name", "internal_links", "dimensions", "parent", "bl_width_max", "label",
    "input_template", "show_texture", "rna_type", "width_hidden", "show_options",
    "location", "outputs", "use_custom_color", "__doc__", "width", "bl_width_default",
    "inputs", "bl_idname", "socket_value_update", "bl_width_min", "color",
    "bl_height_max", "__slots__", "select", "mute", "bl_height_default",
    "bl_static_type", "bl_height_min", "height", "bl_label", "bl_icon", "hide",
    "output_template", "poll_instance", "draw_buttons_ext", "type", "bl_description",
    "draw_buttons", "update",
}

SPECIAL_CASE_ATTR_NAMES = {
    "color_ramp", "mapping", "texture_mapping", "color_mapping", "image_user",
    "interface", "node_tree", "tag_need_exec",
}

node_types_to_nodetree = {
    "ShaderNode": "ShaderNodeTree",
    "CompositorNode": "CompositorNodeTree",
    "GeometryNode": "GeometryNodeTree",
    "FunctionNode": "GeometryNodeTree",
}

skip_nodes = ["NodeReroute", "NodeGroupInput", "NodeGroupOutput", "ShaderNodeTexMusgrave"]

def map_value_to_repr(value):
    if value is None:
        return None
    elif isinstance(value, float):
        return round(value, 4)
    elif isinstance(value, (int, str, bool)):
        return type(value)(value)
    elif isinstance(value, list):
        return [map_value_to_repr(v) for v in value]
    elif isinstance(value, dict):
        return {k: map_value_to_repr(v) for k, v in value.items()}
    elif "bpy_prop_array" in str(type(value)):
        return tuple((map_value_to_repr(v) for v in value))
    elif isinstance(value, (mathutils.Vector, mathutils.Euler, mathutils.Quaternion, mathutils.Matrix)):
        return tuple((map_value_to_repr(v) for v in value))
    else:
        return None
        #raise ValueError(f"Unknown value type: {type(value)} {value}")

def _attr_reprs(node: bpy.types.Node):

    attr_reprs = []
    for k in dir(node):
        if k.startswith("_"):
            continue
        elif k in SPECIAL_CASE_ATTR_NAMES:
            res = None
        elif k in UNIVERSAL_ATTR_NAMES:
            continue
        else:
            res = getattr(node, k)

        prop = node.bl_rna.properties.get(k)
        if prop is not None and prop.type == "ENUM":
            typestr = "|".join([repr(k) for k in prop.enum_items.keys()])
        else:
            typestr = type(res).__name__

        attr_reprs.append(f"{repr(k)}: {typestr} (default {res!r})")

    return attr_reprs

def _repr_input_socket(input_socket):
    typestr = type(input_socket).__name__
    default_value = getattr(input_socket, "default_value", None)

    if default_value is None:
        return f"{repr(input_socket.name)}: {typestr}"

    default_value = map_value_to_repr(default_value)
    typestr = type(default_value).__name__
    return f"{repr(input_socket.name)}: {typestr} (default {default_value})"

def interface_for_node(enum_name, node_str, node_type):

    nodegroup_type = node_types_to_nodetree[node_type]
    node_tree = bpy.data.node_groups.new(name=f"{node_type}Group", type=nodegroup_type)
    nw = NodeWrangler(node_tree)

    try:
        # Use NodeWrangler to create nodes, which goes through the compatibility layer
        node_type_enum = getattr(Nodes, enum_name)
        node = nw.new_node(node_type_enum)
    except Exception as e:
        print(f"Error creating node {node_str}: {e}")
        bpy.data.node_groups.remove(node_tree)
        return ""

    input_reprs = []
    for name, input_socket in node.inputs.items():
        input_reprs.append(_repr_input_socket(input_socket))
    input_reprs = "{\n\t\t" + ", \n\t\t".join(input_reprs) + "\n\t}"

    attr_reprs = _attr_reprs(node)
    attr_reprs = "{\n\t\t" + ", \n\t\t".join(attr_reprs) + "\n\t}"

    text = f"nw.new_node(\n\tNodes.{enum_name}, \n\tinputs={input_reprs}, \n\tattrs={attr_reprs})\n"

    output_reprs = []
    for name, output_socket in node.outputs.items():
        output_reprs.append(_repr_input_socket(output_socket))
    text += "\n\t.outputs = {\n\t\t" + ", \n\t\t".join(output_reprs) + "\n\t}\n"

    node_tree.nodes.remove(node)
    bpy.data.node_groups.remove(node_tree)

    return text

def node_to_category(node_str):
    if node_str in skip_nodes:
        return ""
    try:
        nodetype = next(k for k, v in node_types_to_nodetree.items() if node_str.startswith(k))
        return nodetype
    except StopIteration:   
        raise ValueError(f"Unknown node type: {node_str}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_file", type=Path)
    parser.add_argument("--node-types", nargs="+", default=None)

    # Handle blender's argv - find args after '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    args = parser.parse_args(argv)

    node_entries = [
        (k, getattr(Nodes, k), node_to_category(getattr(Nodes, k)))
        for k in dir(Nodes)
        if not k.startswith("_")
    ]
    node_entries.sort(key=lambda x: x[2])

    lines = []
    for enum_name, node_str, nodetype in node_entries:
        if node_str in skip_nodes:
            continue
        if args.node_types is not None and nodetype not in args.node_types:
            continue
        lines.append(interface_for_node(enum_name, node_str, nodetype))

    result = "\n".join(lines)
    print(f"Writing {len(lines)=} {len(result)=} nodes to {args.output_file}")
    args.output_file.write_text(result)

if __name__ == "__main__":
    main()