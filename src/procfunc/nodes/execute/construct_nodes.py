import logging
from typing import Any

import bpy

from procfunc import compute_graph as cg
from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.util import bpy_node_info as bni
from procfunc.util import pytree
from procfunc.util.bpy_info import bpy_nocollide_data_name
from procfunc.util.log import add_exception_context_msg

from . import construct_operator, construct_standard
from .util import (
    get_nth_socket,
    normalize_socket_type,
)

logger = logging.getLogger(__name__)


def instantiate_nodegroup(
    node_tree: bpy.types.NodeTree,
    nodegroup: bpy.types.NodeTree,
) -> bpy.types.Node:
    nodegroup_instance_type = bni.NODEGROUPTYPE_TO_INSTANCE_NODE[node_tree.bl_idname]
    bpy_nodegroup_call = node_tree.nodes.new(nodegroup_instance_type)
    bpy_nodegroup_call.node_tree = nodegroup
    return bpy_nodegroup_call


def _construct_subgraph_call(
    node: cg.SubgraphCallNode,
    bl_node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
) -> bpy.types.Node | bpy.types.NodeSocket | bpy.types.Material:
    node_group_type = bni.NodeGroupType(bl_node_tree.bl_idname)
    nodegroup = as_nodegroup(node.subgraph, node_group_type)
    bpy_nodegroup_call = instantiate_nodegroup(bl_node_tree, nodegroup)

    for input_name, input_py in node.kwargs.items():
        input_val = input_results[input_name]
        if input_val is None:
            continue
        to_socket = bpy_nodegroup_call.inputs[input_name]
        construct_standard.connect_single_input(
            node_tree=bl_node_tree,
            to_socket=to_socket,
            input_val=input_val,
        )

    return bpy_nodegroup_call


def _dispatch_construct_procnode_by_type(
    node: cg.Node,
    bl_node_tree: bpy.types.NodeTree,
    cache: dict[cg.Node, bpy.types.Node],
    input_results: dict[str | int, Any],
):
    match node:
        case cg.GetAttributeNode():
            raise ValueError(
                f"{node=} must be resolved by construct_procnode_to_bpy before dispatch"
            )
        case cg.ProceduralNode():
            return construct_standard._construct_procnode_standard(
                node, bl_node_tree, input_results
            )
        case cg.FunctionCallNode():
            result = construct_operator._construct_operator_call(
                node, bl_node_tree, input_results
            )
            if isinstance(result, cg.Node):
                return construct_procnode_to_bpy(result, bl_node_tree, cache)
            return result
        case cg.SubgraphCallNode():
            return _construct_subgraph_call(node, bl_node_tree, input_results)
        case cg.InputPlaceholderNode():
            input_node = next(
                n for n in bl_node_tree.nodes if n.bl_idname == "NodeGroupInput"
            )
            assert input_node is not None, bl_node_tree.nodes.keys()
            return input_node.outputs[node.input_name]
        case _:
            raise ValueError(f"Got misconfigured {node=}")


def construct_procnode_to_bpy(
    node: cg.Node,
    bl_node_tree: bpy.types.NodeTree,
    cache: dict[cg.Node, bpy.types.Node] | None = None,
) -> bpy.types.NodeSocket | bpy.types.NodeInternal:
    assert node is not None
    assert isinstance(bl_node_tree, bpy.types.NodeTree), bl_node_tree

    if cache is None:
        cache = {}
    elif cached := cache.get(node, None):
        return cached

    if isinstance(node, cg.GetAttributeNode):
        assert len(node.args) == 1, node.args
        assert len(node.kwargs) == 0, node.kwargs
        source = node.args[0]
        if isinstance(source, cg.SubgraphCallNode):
            # an absent subgraph output leaf (None, e.g. a Material with no
            # displacement) has no output socket; resolve to it directly
            for k, v in source.subgraph.outputs.items(nocontainer_name="result"):
                if k == node.attribute_name and not isinstance(v, cg.Node):
                    return v
        base_node = construct_procnode_to_bpy(source, bl_node_tree, cache)
        assert isinstance(base_node, bpy.types.Node), base_node
        socket_name = construct_standard._resolve_output_socket_name(
            source, node.attribute_name, bl_node_tree
        )
        return get_nth_socket(base_node.outputs, socket_name, 0, base_node.type)

    def _construct_leaf(input_val: cg.Node | Any | None):
        if not isinstance(input_val, cg.Node):
            return input_val
        bpy_res = construct_procnode_to_bpy(input_val, bl_node_tree, cache)
        if isinstance(bpy_res, bpy.types.NodeInternal):
            # nodes that need non-socket input (GetAttribute) wont reach here, so we can return the primary socket
            return construct_standard._get_primary_output_socket(input_val, bpy_res)
        return bpy_res

    # resolve pt.Material before PyTree traversal, since Material is a registered
    # PyTree container and would be destructured into shader ProcNodes otherwise
    kwargs_for_tree = {
        k: v.item() if isinstance(v, pt.Material) else v for k, v in node.kwargs.items()
    }

    input_sockets: dict = pytree.PyTree(kwargs_for_tree).map(_construct_leaf).obj()
    input_sockets.update(
        {
            i: v
            for i, v in enumerate(pytree.PyTree(node.args).map(_construct_leaf).obj())
        }
    )

    if (
        lowered := construct_operator._lower_compare_outside_geometry(
            node, bl_node_tree, input_sockets
        )
    ) is not None:
        result = construct_procnode_to_bpy(lowered, bl_node_tree, cache)
        cache[node] = result
        return result

    with add_exception_context_msg(
        f"While instantiating {nt.node_definition_context_message(node)}{node=}:\n"
    ):
        result = _dispatch_construct_procnode_by_type(
            node, bl_node_tree, cache, input_sockets
        )

    assert isinstance(result, (bpy.types.Node, bpy.types.NodeSocket)), result

    logger.debug(
        f"{construct_procnode_to_bpy.__name__} for {node=} produced {type(result)=}"
    )
    cache[node] = result
    return result


def _graph_requires_scene_tree(graph: cg.ComputeGraph) -> bool:
    return any(
        isinstance(node, cg.ProceduralNode)
        and node.node_type in bni.SCENE_BOUND_NODE_TYPES
        for subgraph in cg.traverse_nested_graphs(graph)
        for node in cg.traverse_depth_first(subgraph)
    )


def _construct_nodegroup(
    graph: cg.ComputeGraph,
    node_tree_type: bni.NodeGroupType,
) -> bpy.types.NodeTree:
    # Scene-bound compositor nodes (e.g. Render Layers) poll False inside a
    # standalone node group, so build on the active scene's compositing tree
    # instead, replacing its contents. That tree still accepts group IO nodes
    # and an interface, so the rest of the scaffold below is unchanged.
    if _graph_requires_scene_tree(graph):
        scene = bpy.context.scene
        scene.use_nodes = True
        nodegroup = scene.node_tree
    else:
        name = (
            graph.name
            if graph.name is not None
            else bpy_nocollide_data_name(graph, bpy.data.node_groups)
        )
        nodegroup = bpy.data.node_groups.new(name, node_tree_type.value)

    nodegroup.interface.clear()
    nodegroup.nodes.clear()

    input_node = nodegroup.nodes.new("NodeGroupInput")
    output_node = nodegroup.nodes.new("NodeGroupOutput")

    cache = {}

    for k, v in graph.inputs.items():
        v_type = v.metadata.get("known_value_type", None)
        if v_type is None:
            raise ValueError(f"Got {v=} with no known value type")
        socket_type = bni.PYTHON_TYPE_TO_SOCKET_TYPE[v_type]
        nodegroup.interface.new_socket(
            name=k,
            in_out="INPUT",
            socket_type=socket_type.value,
        )
        cache[v] = input_node.outputs[k]

    for k, v in graph.outputs.items(nocontainer_name="result"):
        # an absent output (None, e.g. a Material with no displacement) gets no
        # output socket
        if not isinstance(v, cg.Node):
            continue

        res = construct_procnode_to_bpy(v, nodegroup, cache)

        # accessor nodes can resolve to an absent output (None, e.g. a
        # Material's missing displacement read through a subgraph boundary)
        if not isinstance(res, (bpy.types.Node, bpy.types.NodeSocket)):
            continue

        if isinstance(res, bpy.types.Node):
            res = construct_standard._get_primary_output_socket(v, res)
        assert isinstance(res, bpy.types.NodeSocket), res

        nodegroup.interface.new_socket(
            name=k,
            in_out="OUTPUT",
            socket_type=normalize_socket_type(res.bl_idname),
        )

        to_socket = output_node.inputs[k]
        construct_standard.connect_single_input(nodegroup, to_socket, res)

    return nodegroup


def as_nodegroup(
    graph: cg.ComputeGraph,
    node_tree_type: bni.NodeGroupType,
) -> bpy.types.NodeTree:
    # Scene-bound graphs (e.g. Render Layers) are built on the active scene's
    # compositing tree, replacing its contents.
    ops = graph.metadata.get("operations", [])
    use_cache = len(ops) > 0 and ops[0][0].__name__ == "node_function"

    if use_cache:
        cached = graph.metadata["bpy_cached_impls"].get(node_tree_type, None)
        if cached is not None:
            return cached

    with add_exception_context_msg(
        prefix=f"While constructing nodegroup for {graph=} {node_tree_type=}:\n",
    ):
        nodegroup = _construct_nodegroup(graph, node_tree_type)

    if use_cache:
        graph.metadata["bpy_cached_impls"][node_tree_type] = nodegroup

    return nodegroup
