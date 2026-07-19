import logging

import bpy

from procfunc import compute_graph as cg
from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.util.bpy_node_info import SocketType
from procfunc.ops._util import modify
from procfunc.ops.primitives.mesh import mesh_single_vertex
from procfunc.util.bpy_info import bpy_nocollide_data_name

from . import construct_standard
from .construct_nodes import construct_procnode_to_bpy, instantiate_nodegroup

logger = logging.getLogger(__name__)


def unwrap_and_drop(x: dict[str, nt.ProcNode | None]):
    return {
        k: v.item() if isinstance(v, nt.ProcNode) else v
        for k, v in x.items()
        if v is not None
    }


def get_interface_by_name(
    nodegroup: pt.NodeGroup, socket_name: str, in_out: str
) -> bpy.types.NodeSocket:
    return next(
        (
            item
            for item in nodegroup.interface.items_tree.values()
            if item.name == socket_name and item.in_out == in_out
        ),
        None,
    )


def get_interface_by_type(
    nodegroup: pt.NodeGroup, socket_type: SocketType, in_out: str
) -> bpy.types.NodeSocket:
    return next(
        (
            item
            for item in nodegroup.interface.items_tree.values()
            if item.socket_type == socket_type.value and item.in_out == in_out
        ),
        None,
    )


def nodegroup_to_output(
    node_tree: bpy.types.NodeTree,
    from_nodegroup: bpy.types.NodeGroup,
    output_node_type: str,
    output_keys: list[str],
):
    bpy_nodegroup_call = instantiate_nodegroup(node_tree, from_nodegroup)
    output_node = node_tree.nodes.new(output_node_type)

    for key in output_keys:
        if key.lower() not in bpy_nodegroup_call.outputs:
            continue

        from_socket = bpy_nodegroup_call.outputs[key.lower()]
        to_socket = output_node.inputs[key.capitalize()]

        node_tree.links.new(from_socket, to_socket)

    unused_keys = set(bpy_nodegroup_call.outputs.keys()) - {
        k.lower() for k in output_keys
    }

    if unused_keys:
        raise ValueError(
            f"Shader had unused extra outputs {unused_keys} while connecting to {output_node_type}. "
            f"output only makes use of {[x.lower() for x in output_keys]}"
        )

    return output_node


def construct_outputs_to_output_node(
    node_tree: bpy.types.NodeTree,
    outputs: dict[str, cg.Node],
    output_node_type: str,
) -> bpy.types.Node:
    output_node = node_tree.nodes.new(output_node_type)
    cache = {}
    for key, node in outputs.items():
        res = construct_procnode_to_bpy(node, node_tree, cache)
        if isinstance(res, bpy.types.Node):
            res = construct_standard._get_primary_output_socket(node, res)
        construct_standard.connect_single_input(
            node_tree, output_node.inputs[key.capitalize()], res
        )
    return output_node


def build_bpy_material(
    surface: nt.ProcNode[nt.Shader] | None = None,
    displacement: nt.ProcNode[pt.Vector] | None = None,
    volume: nt.ProcNode[nt.Shader] | None = None,
) -> bpy.types.Material:
    for key, val in {
        "surface": surface,
        "displacement": displacement,
        "volume": volume,
    }.items():
        if val is not None and not isinstance(val, (nt.ProcNode, cg.Node)):
            raise TypeError(
                f"Material {key} must be a ProcNode or None, got {type(val)}: {val!r}"
            )

    # optimization: a constant zero displacement has no effect, so drop it and
    # leave the output socket disconnected rather than emitting a dead subgraph
    if displacement is not None and pt.is_zero_displacement(displacement):
        displacement = None

    if all(x is None for x in [surface, displacement, volume]):
        raise ValueError(
            "at least one of surface, displacement, or volume must be provided"
        )

    outputs = unwrap_and_drop(
        {"surface": surface, "displacement": displacement, "volume": volume}
    )

    material = bpy.data.materials.new(
        bpy_nocollide_data_name("material", bpy.data.materials)
    )
    material.use_nodes = True
    mnt = material.node_tree
    mnt.nodes.clear()

    construct_outputs_to_output_node(mnt, outputs, "ShaderNodeOutputMaterial")

    return material


def extract_geometry_singlekey(
    nodegroup: pt.NodeGroup,
    output_key: str,
    attribute_keys: list[str] | None = None,
    is_curve: bool = False,
    realize: bool = False,
    _skip_apply: bool = False,
) -> pt.MeshObject | pt.CurveObject:
    """
    Extract the object corresponding to the 'output_key' output socket of 'nodegroup'

    NOTE: we do this by executing the whole nodegroup with just that output socket connected, which may be inefficient.
    """

    if attribute_keys is None:
        attribute_keys = []

    if get_interface_by_name(nodegroup, output_key, "OUTPUT") is None:
        raise ValueError(
            f"Node group {nodegroup.name} has no output {output_key}, available are {nodegroup.interface.items_tree.keys()}"
        )

    outer_nodegroup = bpy.data.node_groups.new("wrapper", "GeometryNodeTree")
    outer_nodegroup_output_node = outer_nodegroup.nodes.new("NodeGroupOutput")
    nodegroup_instance = instantiate_nodegroup(outer_nodegroup, nodegroup)

    if _skip_apply:
        nodegroup.use_fake_user = True
        outer_nodegroup.use_fake_user = True

    outer_nodegroup.interface.new_socket(
        name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )

    for attr_key in attribute_keys:
        if attr_key not in nodegroup.interface.items_tree:
            raise ValueError(
                f"Node group {nodegroup.name} has no output {attr_key=}, available are {nodegroup.interface.items_tree.keys()}"
            )

        if attr_key not in nodegroup_instance.outputs:
            raise ValueError(
                f"Node group {nodegroup.name} has no output {attr_key=}, available are {nodegroup.interface.items_tree.keys()}"
            )

        item = nodegroup.interface.items_tree.get(attr_key)
        if item is None or item.in_out != "OUTPUT":
            raise ValueError(
                f"Attempted to output {attr_key=} from {nodegroup.interface.items_tree.keys()=}, "
                f"but it wasnt an output! {item is None or item.in_out=}"
            )
        outer_nodegroup.interface.new_socket(
            name=attr_key, in_out="OUTPUT", socket_type=item.socket_type
        )

        if attr_key not in outer_nodegroup_output_node.inputs:
            raise ValueError(
                f"Node group {nodegroup.name} has no output {attr_key=}, available are {outer_nodegroup_output_node.inputs.keys()}"
            )

        outer_nodegroup.links.new(
            nodegroup_instance.outputs[attr_key],
            outer_nodegroup_output_node.inputs[attr_key],
        )

    if is_curve:
        curve_to_mesh = outer_nodegroup.nodes.new("GeometryNodeCurveToMesh")
        outer_nodegroup.links.new(
            nodegroup_instance.outputs[output_key], curve_to_mesh.inputs["Curve"]
        )
        outer_nodegroup.links.new(
            curve_to_mesh.outputs["Mesh"],
            outer_nodegroup_output_node.inputs["Geometry"],
        )
    else:
        geo_output = nodegroup_instance.outputs[output_key]
        if realize:
            realize_node = outer_nodegroup.nodes.new("GeometryNodeRealizeInstances")
            outer_nodegroup.links.new(geo_output, realize_node.inputs["Geometry"])
            geo_output = realize_node.outputs["Geometry"]
        outer_nodegroup.links.new(
            geo_output,
            outer_nodegroup_output_node.inputs["Geometry"],
        )

    res = modify(
        mesh_single_vertex(),
        "NODES",
        node_group=outer_nodegroup,
        _skip_apply=_skip_apply,
    )

    if _skip_apply:
        return res

    for attr_key in attribute_keys:
        if attr_key not in res.item().data.attributes:
            raise ValueError(
                f"Expected {nodegroup.name} to output {attr_key=} but for {res} but it was not found. "
                f"available are {res.item().data.attributes.keys()}"
            )

    return res
