import logging
from collections import OrderedDict
from typing import Any

import bpy

from procfunc import compute_graph as cg
from procfunc import context
from procfunc import types as pt
from procfunc.nodes import geo
from procfunc.nodes import types as nt
from procfunc.nodes.bpy_node_info import (
    NodeGroupType,
    SocketType,
)
from procfunc.nodes.geo import store_named_attribute
from procfunc.ops._util import modify
from procfunc.ops.object import mesh_to_curve as ops_mesh_to_curve
from procfunc.ops.primitives.mesh import mesh_single_vertex
from procfunc.tracer import primitive as tracer_primitive
from procfunc.util import pytree
from procfunc.util.bpy_info import bpy_nocollide_data_name

from .construct_nodes import (
    as_nodegroup,
    construct_procnode_to_bpy,
    instantiate_nodegroup,
)

logger = logging.getLogger(__name__)


def _unwrap_and_drop(x: dict[str, nt.ProcNode | None]):
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


def _nodegroup_to_output(
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


def _build_bpy_material(
    surface: nt.ProcNode[nt.Shader] | None = None,
    displacement: nt.ProcNode[pt.Vector] | None = None,
    volume: nt.ProcNode[nt.Shader] | None = None,
) -> bpy.types.Material:
    if all(x is None for x in [surface, displacement, volume]):
        raise ValueError(
            "at least one of surface, displacement, or volume must be provided"
        )

    outputs = _unwrap_and_drop(
        {"surface": surface, "displacement": displacement, "volume": volume}
    )

    material = bpy.data.materials.new(
        bpy_nocollide_data_name("material", bpy.data.materials)
    )
    material.use_nodes = True
    mnt = material.node_tree
    mnt.nodes.clear()

    outputs = pytree.PyTree(outputs)
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=outputs,
        name="to_material",
        metadata={},
    )
    body = as_nodegroup(graph, NodeGroupType.SHADER)
    _nodegroup_to_output(mnt, body, "ShaderNodeOutputMaterial", list(outputs.names()))

    return material


@tracer_primitive
def to_environment(
    surface: nt.ProcNode[nt.Shader] | None = None,
    volume: nt.ProcNode[nt.Shader] | None = None,
) -> pt.World:
    # Get or create world
    if bpy.context.scene.world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    else:
        world = bpy.context.scene.world

    # Enable use of nodes for the world
    world.use_nodes = True
    world.node_tree.nodes.clear()

    outputs = _unwrap_and_drop({"surface": surface, "volume": volume})

    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree(outputs),
        name="to_environment",
        metadata={},
    )

    body = as_nodegroup(graph, NodeGroupType.SHADER)

    _nodegroup_to_output(
        world.node_tree, body, "ShaderNodeOutputWorld", list(outputs.keys())
    )

    return pt.World(world)


@tracer_primitive
def to_light(
    light: pt.LightObject,
    surface: nt.ProcNode[nt.Shader],
) -> pt.LightObject:
    """Apply a shader node graph to a light's internal node tree."""
    lamp_data = light.item().data
    lamp_data.use_nodes = True
    lamp_data.node_tree.nodes.clear()

    outputs = _unwrap_and_drop({"surface": surface})

    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree(outputs),
        name="to_light",
        metadata={},
    )

    body = as_nodegroup(graph, NodeGroupType.SHADER)

    _nodegroup_to_output(
        lamp_data.node_tree, body, "ShaderNodeOutputLight", list(outputs.keys())
    )

    return light


@tracer_primitive
def to_compositor(
    results: dict[str, nt.ProcNode],
):
    bpy.context.scene.use_nodes = True
    nt = bpy.context.scene.node_tree
    nt.nodes.clear()

    cache = {}
    for k, v in results.items():
        construct_procnode_to_bpy(v.item(), nt, cache)

    return bpy.context.scene


def _extract_geometry_singlekey(
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


@tracer_primitive
def to_mesh_object(
    geometry: nt.ProcNode[pt.MeshObject],
    _skip_apply: bool = False,
) -> pt.MeshObject:
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"geometry": geometry.item()}),
        name="to_mesh_object",
        metadata={},
    )
    ng = as_nodegroup(graph, NodeGroupType.GEOMETRY)
    ng_inouts = ng.interface.items_tree

    item = ng_inouts.get("geometry")
    if item is None:
        raise ValueError(
            f"Node group {ng.name} has no output geometry, available are {ng_inouts.keys()}"
        )
    if item.in_out != "OUTPUT":
        raise ValueError(
            f"Node group attempted to extract geometry but it wasnt an output! {item.in_out=}"
        )

    try:
        obj_result = _extract_geometry_singlekey(
            ng,
            "geometry",
            attribute_keys=[],
            realize=True,
            _skip_apply=_skip_apply,
        )
    except RuntimeError as e:
        if "does not contain a mesh" not in str(e):
            raise
        mode = context.globals.warn_mode_empty_geonodes
        if mode == "throw":
            raise
        if mode == "warn":
            logger.warning(
                f"to_mesh_object produced no mesh geometry, returning empty mesh: {e}"
            )
        return mesh_single_vertex()

    assert isinstance(obj_result, pt.MeshObject)

    return obj_result


@tracer_primitive
def to_mesh_object_with_attributes(
    geometry: nt.ProcNode[pt.MeshObject],
    attributes: dict[str, nt.ProcNode[nt.AnyDataVal]] | None = None,
) -> tuple[pt.MeshObject, dict[str, Any]]:
    for k, v in attributes.items():
        geometry = store_named_attribute(geometry, name=k, value=v)

    obj = to_mesh_object(geometry)

    if attributes is None:
        return obj, {}

    attr_dict = {k: obj.item().data.attributes[k] for k in attributes.keys()}
    return obj, attr_dict


@tracer_primitive
def to_curve_object(
    geometry: nt.ProcNode[pt.CurveObject],
) -> pt.CurveObject:
    """
    WARNING: currently discards any bezier config or knots, only extracts the points.Any

    TODO: Need a better geonodes -> curve op from blender, or need to engineer this in via attribute extraction.
    """

    obj = to_mesh_object(geo.curve_to_mesh(geometry, profile_curve=None))
    return ops_mesh_to_curve(obj)


@tracer_primitive
def to_objects_multi(
    geometries: dict[str, nt.ProcNode[pt.MeshObject]],
    attributes: dict[str, dict[str, nt.ProcNode[nt.AnyDataVal]]] | None = None,
) -> OrderedDict[str, pt.MeshObject]:
    """
    Convert a nodegroup which has multiple output geometries into multiple realized objects.

    If the objects should have any attributes, provide node definitions for them in the 'attributes' argument.

    Args:
        geometries: named output geometry nodes to be converted into objects
        attributes: named data attributes which should be annotated on those objects. keys must be a subset of the keys of 'geometries'
        input_obj: optional input object to use for the geometry nodegroups

    Returns:
        - result_objects: dict of {output_key: object}. output keys are the same as the keys of 'geometries'
    """

    if attributes is None:
        attributes = {}

    extra_attr_keys = set(attributes.keys()) - set(geometries.keys())
    if extra_attr_keys:
        raise ValueError(
            f"{to_objects_multi.__name__} got {attributes.keys()=} but these are not a subset of {geometries.keys()=} due to {extra_attr_keys=}"
        )

    attr_keys_dedup = {
        kobj: {f"{kobj}_{kattr}": v for kattr, v in attrs.items()}
        for kobj, attrs in attributes.items()
    }

    all_ng_outputs: dict[str, nt.ProcNode] = geometries.copy()
    for kobj, attrs in attr_keys_dedup.items():
        all_ng_outputs.update(attrs)

    all_ng_outputs = _unwrap_and_drop(all_ng_outputs)  # type: ignore
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree(all_ng_outputs),
        name="to_objects_multi",
        metadata={},
    )
    nodegroup = as_nodegroup(
        graph,
        NodeGroupType.GEOMETRY,
    )
    ng_inouts = nodegroup.interface.items_tree

    result_objects = OrderedDict()

    for k, v in geometries.items():
        item = ng_inouts.get(k)
        if item is None:
            raise ValueError(
                f"Node group {nodegroup.name} has no output {k}, available are {ng_inouts.keys()}"
            )
        if item.in_out != "OUTPUT":
            raise ValueError(
                f"Node group attempted to extract {k=} but it wasnt an output! {item.in_out=}"
            )

        result_objects[k] = _extract_geometry_singlekey(
            nodegroup,
            k,
            attribute_keys=attr_keys_dedup.get(k, {}).keys(),
        )

    return result_objects


@tracer_primitive
def to_aliases(
    geometry: nt.ProcNode[pt.MeshObject],
) -> list[pt.MeshObject]:
    """
    Convert instanced geometry into aliases - separate objects sharing the same mesh data.

    Uses depsgraph to extract instance transforms and creates one bpy.data.object per instance.
    All aliases point directly to the original mesh data from the scene - no copying occurs.
    Each alias has its own transform (position, rotation, scale) but shares mesh data.

    Note: Requires geometry nodes that use actual bpy.data.collections with real objects
    (via collection_info node), not just joined geometry. The instances must be visible
    in the viewport (show_viewport=True) to be detected by the depsgraph.

    Args:
        geometry: node producing instanced geometry (e.g., from instance_on_points)

    Returns:
        list of MeshObject, one per instance, with each instance pointing to the original
        mesh data from the scene
    """

    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"geometry": geometry.item()}),
        name="to_aliases",
        metadata={},
    )
    nodegroup = as_nodegroup(graph, NodeGroupType.GEOMETRY)

    obj_with_modifier = modify(
        mesh_single_vertex(), "NODES", node_group=nodegroup, _skip_apply=True
    )
    temp_obj = obj_with_modifier.item()

    for mod in temp_obj.modifiers:
        mod.show_viewport = True

    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    eval_mesh_to_instances = {}
    eval_mesh_to_copy = {}

    for deps_instance in depsgraph.object_instances:
        if not deps_instance.is_instance:
            continue

        obj = deps_instance.object
        if obj.type != "MESH":
            continue

        if deps_instance.parent is None or deps_instance.parent.original != temp_obj:
            continue

        eval_mesh = obj.data
        if eval_mesh is None:
            continue

        mesh_id = eval_mesh.as_pointer()

        if mesh_id not in eval_mesh_to_instances:
            eval_mesh_to_instances[mesh_id] = []
            eval_mesh_to_copy[mesh_id] = eval_mesh.copy()

        eval_mesh_to_instances[mesh_id].append(deps_instance.matrix_world.copy())

    bpy.data.objects.remove(temp_obj, do_unlink=True)

    result_objects = []

    for mesh_id, matrices in eval_mesh_to_instances.items():
        mesh_data = eval_mesh_to_copy[mesh_id]
        for matrix in matrices:
            alias_obj = bpy.data.objects.new(
                bpy_nocollide_data_name("alias", bpy.data.objects), mesh_data
            )
            alias_obj.matrix_world = matrix
            bpy.context.collection.objects.link(alias_obj)
            result_objects.append(pt.MeshObject(alias_obj))

    return result_objects
