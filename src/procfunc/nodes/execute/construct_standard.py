"""Construct a single "standard" ProceduralNode: resolve its contextual node
type for the target tree, set attrs (data_type selectors first, special cases
hooked), and connect or assign each input socket. The layer below operator
dispatch and graph traversal; must not import its sibling construct modules."""

import logging
from typing import Any

import bpy
import numpy as np

from procfunc import compute_graph as cg
from procfunc import types as pt
from procfunc.nodes import bpy_node_info as bni
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import (
    ContextualNode,
    RuntimeResolveDataType,
    resolve_contextual_node,
)

from .construct_special_cases import NODE_SPECIAL_CASES
from .infer_runtime_data_type import (
    map_data_type_for_differing_node_interface,
    resolve_operation_data_type,
)
from .util import (
    assign_default_value,
    get_active_sockets,
    get_input_socket_to_connect_to,
    normalize_socket_type,
)

logger = logging.getLogger(__name__)


def connect_single_input(
    node_tree: bpy.types.NodeTree,
    to_socket: bpy.types.NodeSocket,
    input_val: bpy.types.NodeSocket | Any | None,
):
    if isinstance(input_val, nt.ProcNode):
        raise ValueError(
            f"ProcNode {input_val} is not allowed as input to {to_socket.name}"
        )

    match input_val:
        case None:
            pass
        # case nt.Keyframes():
        #    apply_keyframes(to_input_socket, input_val)
        case bpy.types.NodeSocket() as from_socket:
            _connect_socket(node_tree, from_socket, to_socket, input_val.node.name)
        case bpy.types.NodeInternal():
            raise ValueError(
                f"{input_val=} is a bpy.types.NodeInternal, but this should have been "
                f"resolved to a specific socket at an earlier stage"
            )
        case _ if hasattr(to_socket, "default_value"):
            assign_default_value(to_socket, input_val)
        case np.ndarray() | pt.Matrix() if to_socket.type == "MATRIX":
            value = np.asarray(input_val, dtype=float)
            if value.shape != (4, 4):
                raise ValueError(
                    f"Expected a 4x4 matrix for MATRIX socket "
                    f"{to_socket.name!r}, got shape {value.shape}"
                )
            combine = node_tree.nodes.new("FunctionNodeCombineMatrix")
            for row, col in np.ndindex(4, 4):
                socket = combine.inputs[f"Column {col + 1} Row {row + 1}"]
                socket.default_value = float(value[row, col])
            node_tree.links.new(combine.outputs[0], to_socket)
        case _:
            raise ValueError(
                f"Could not handle {input_val=} as input to {to_socket.name=}"
            )


def connect_multisocket_input(
    node_tree: bpy.types.NodeTree,
    to_socket: bpy.types.NodeSocket,
    input_result: list[bpy.types.NodeSocket | Any | None],
):
    if not to_socket.is_multi_input:
        raise ValueError(
            f"list of sockets {input_result} is not valid to connect to {to_socket} as it is not a "
            f"valid multi-input socket"
        )

    assert isinstance(input_result, list)

    # connect reversed: multi-input links consume in reverse of connection order
    for input_val in reversed(input_result):
        if input_val is None:
            continue
        connect_single_input(node_tree, to_socket, input_val)


def _connect_socket(
    node_tree: bpy.types.NodeTree,
    source_socket: bpy.types.NodeSocket,
    target_socket: bpy.types.NodeSocket,
    source_node_name: str = "unknown",
):
    """Helper function to connect sockets with type compatibility checking."""
    output_type = getattr(source_socket, "bl_idname", source_socket.type)
    input_type = getattr(target_socket, "bl_idname", target_socket.type)

    normalized_output = normalize_socket_type(output_type)
    normalized_input = normalize_socket_type(input_type)

    if not bni.are_socket_types_compatible(normalized_output, normalized_input):
        raise ValueError(
            f"Incompatible socket types: cannot connect {output_type} output to {input_type} input. "
            f"Source: {source_node_name}.{source_socket.name} -> "
            f"Target: {getattr(target_socket.node, 'name', 'unknown')}.{target_socket.name}"
        )

    node_tree.links.new(source_socket, target_socket)


def _get_primary_output_socket(
    node_spec: cg.Node,
    bpy_node: bpy.types.Node,
) -> bpy.types.NodeSocket:
    """
    Sometimes a node will have multiple output sockets, but the user didnt say which one they want.
    """

    enabled = list(get_active_sockets(bpy_node.outputs))
    if len(enabled) == 0:
        raise ValueError(
            f"Got {len(enabled)=} enabled sockets for {node_spec=} {bpy_node.name=}"
        )
    if len(enabled) == 1:
        assert isinstance(enabled[0], bpy.types.NodeSocket), enabled[0]
        return enabled[0]
    names = [socket.name for socket in enabled]

    raise ValueError(
        f"{node_spec=} should have a single anonymous output, "
        f"but there was actually >1 {enabled=} {names=} for {bpy_node.bl_idname=}"
    )


def _set_node_attribute(bl_node: bpy.types.Node, k: str, v: Any):
    if isinstance(v, pt.BlenderAsset):
        v = v.item()
    if not hasattr(bl_node, k):
        available = [
            a for a in dir(bl_node) if not a.startswith("_") and not a.startswith("bl_")
        ]
        raise ValueError(
            f"{bl_node.bl_idname} has no attribute {k!r}={v!r} — likely a "
            f"shader/geometry-only option used in a {bl_node.id_data.bl_idname} "
            f"context. Available attributes: {available}"
        )
    try:
        setattr(bl_node, k, v)
    except Exception as e:
        options = (
            bl_node.bl_rna.properties[k].enum_items.keys()
            if k in bl_node.bl_rna.properties
            and hasattr(bl_node.bl_rna.properties[k], "enum_items")
            else "unknown"
        )
        raise ValueError(
            f"Could not set attribute {k!r} of {bl_node.name} to {v}, {options=}"
        ) from e


def _map_keys(d: dict, map: dict, drop: frozenset = frozenset()) -> dict:
    return {map.get(k, k): v for k, v in d.items() if k not in drop}


def _resolve_output_socket_name(
    source: cg.Node, attribute_name: str, bl_node_tree: bpy.types.NodeTree
) -> str:
    """If `source` is a contextual ProceduralNode, remap the output socket name per its output_keys_map."""
    if not isinstance(source, cg.ProceduralNode):
        return attribute_name
    ctx = ContextualNode.parse_name(source.node_type)
    if ctx is None:
        return attribute_name
    group_type = bni.NodeGroupType(bl_node_tree.bl_idname)
    output_keys_map = resolve_contextual_node(ctx, group_type).output_keys_map
    return output_keys_map.get(attribute_name, attribute_name)


def _resolve_data_type(
    data_type: bni.NodeDataType | RuntimeResolveDataType | None,
    attr_key: str,
    node: cg.Node,
    bl_node: bpy.types.Node,
    node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
) -> Any:
    is_shader = node_tree.bl_idname == bni.NodeGroupType.SHADER.value
    match data_type:
        case RuntimeResolveDataType() as runtime:
            result: bni.NodeDataType = resolve_operation_data_type(
                node,
                input_results,
                runtime,
                coerce_integers=is_shader,
            )
            mapped = map_data_type_for_differing_node_interface(
                result,
                bl_node,
                attr_key,
            )
            logger.debug(
                f"Inferred runtime dtype for {node=}, got  {result=} and mapped to {mapped=}"
            )
            return mapped
        case bni.NodeDataType() as user_provided:
            return map_data_type_for_differing_node_interface(
                user_provided,
                bl_node,
                attr_key,
            )
        case str() as s:
            return map_data_type_for_differing_node_interface(
                bni.NodeDataType(s),
                bl_node,
                attr_key,
            )
        case unknown:
            raise ValueError(
                f"Got misconfigured data_type {unknown=} {type(unknown)=} for {node=}"
            )


def _resolve_contextual_node_type(
    node_type: str,
    bl_node_tree: bpy.types.NodeTree,
    kwargs: dict,
    input_results: dict[str | int, Any],
    attrs: dict,
) -> tuple[str, dict, dict[str | int, Any], dict]:
    """Resolve a contextual `node_type` (one whose concrete blender node differs
    between shader/geometry/compositor/texture trees) to the node type for this
    tree's context, remapping inputs/attrs per the resolution's keymap."""
    contextual = ContextualNode.parse_name(node_type)
    if contextual is None:
        return node_type, kwargs, input_results, attrs

    group_type = bni.NodeGroupType(bl_node_tree.bl_idname)
    resolution = resolve_contextual_node(contextual, group_type)
    keymap = resolution.input_keys_map
    drop = resolution.drop_keys
    if not keymap and not drop:
        return resolution.node_type, kwargs, input_results, attrs

    logger.debug(
        f"Applying keymap {keymap} (dropping {drop}) to {input_results.keys()=} for context {resolution.node_type=} {group_type=}"
    )
    return (
        resolution.node_type,
        _map_keys(kwargs, keymap, drop),
        _map_keys(input_results, keymap, drop),
        _map_keys(attrs, keymap, drop),
    )


def _construct_procnode_standard(
    node: cg.ProceduralNode,
    bl_node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
) -> bpy.types.Node:
    """
    Construct a procnode which is "standard", meaning kind=PROCEDURAL NODE (is not NOT an operator or getattr)

    Returns:
        bpy.types.Node: A blender geometry/shader/compositor node which corresponds to the given procfunc.nodes definition
    """

    assert isinstance(node, cg.ProceduralNode), node

    node_type, kwargs, input_results, attrs = _resolve_contextual_node_type(
        node.node_type,
        bl_node_tree,
        node.kwargs.copy(),
        input_results,
        node.attrs.copy(),
    )

    bl_node = bl_node_tree.nodes.new(node_type)

    for attr_key in ["data_type", "input_type"]:  # Switch node uses input_type
        if attr_key not in attrs:
            continue
        if isinstance(attrs[attr_key], RuntimeResolveDataType) and not hasattr(
            bl_node, attr_key
        ):
            # auto-resolve default landed on a node without this attr; drop it
            attrs.pop(attr_key)
            continue
        attrs[attr_key] = _resolve_data_type(
            attrs[attr_key], attr_key, node, bl_node, bl_node_tree, input_results
        )

    # some nodes need to pop attrs and apply special handling instead of just setattr. we do it here so that they get a chance to
    # remove the attrs / inputs that are problematic before they get applied by code below
    if specialcase := NODE_SPECIAL_CASES.get(node_type):
        specialcase_kwargs = dict(
            node_tree=bl_node_tree,
            bl_node=bl_node,
            attrs=attrs,
            kwargs=kwargs,
            inputs=input_results,
        )
        specialcase(**specialcase_kwargs)

    # data_type / input_type gate which enum values other attrs accept, so set
    # those selectors first
    for k in sorted(attrs, key=lambda k: k not in ("data_type", "input_type")):
        _set_node_attribute(bl_node, k, attrs[k])

    for input_name, input_py in kwargs.items():
        input_result = input_results[input_name]
        if input_result is None:
            # Strict-None policy: None means "leave disconnected" and is only
            # allowed for sockets with no default_value attr at all (Geometry,
            # Shader, Matrix, Virtual) - never rely on Blender's internal
            # defaults, whose values may change across versions. A disabled or
            # missing socket name is a binding bug and propagates as ValueError.
            to_socket = get_input_socket_to_connect_to(
                bl_node_tree, bl_node, input_name, None
            )
            # IMAGE default_value is a datablock pointer; None faithfully means "no image assigned"
            if (
                to_socket.is_multi_input
                or not hasattr(to_socket, "default_value")
                or to_socket.type == "IMAGE"
            ):
                continue
            raise ValueError(
                f"Node {bl_node.name!r} input {to_socket.name!r} (socket type "
                f"{to_socket.type}) received None. Explicitly pass a value; None is "
                f"only allowed for sockets with no default_value attribute "
                f"(e.g. Geometry/Shader) or with a datablock pointer one (Image)."
            )
        to_socket = get_input_socket_to_connect_to(
            bl_node_tree, bl_node, input_name, input_result
        )
        if to_socket.is_multi_input and isinstance(input_py, list):
            assert isinstance(input_result, list), (input_result, to_socket.node.name)
            connect_multisocket_input(bl_node_tree, to_socket, input_result)
        else:
            assert not isinstance(input_result, list), (
                input_result,
                to_socket.node.name,
            )
            connect_single_input(bl_node_tree, to_socket, input_result)

    return bl_node
