import inspect
import logging
from typing import Any, Callable

import bpy

from procfunc.nodes.util import bpy_node_info

logger = logging.getLogger(__name__)

IGNORE_ATTRS = ["color_mapping", "texture_mapping", "active_item", "capture_items"]


def _is_empty_enum(node: bpy.types.Node, attr: str) -> bool:
    prop = node.bl_rna.properties.get(attr)
    return prop is not None and prop.type == "ENUM"


def bpy_node_defaults(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    attr_keys: list[str],
) -> dict[str, Any]:
    temp_default_node = node_tree.nodes.new(node.bl_idname)
    if node.bl_idname.endswith("NodeGroup"):
        temp_default_node.node_tree = node.node_tree
    # data_type must precede operation: FunctionNodeCompare.operation enum
    # values (e.g. BRIGHTER/DARKER) are only valid for certain data_types.
    if hasattr(node, "data_type"):
        temp_default_node.data_type = node.data_type
    if hasattr(node, "operation"):
        temp_default_node.operation = node.operation

    attr_defaults = {}
    for k in attr_keys:
        if hasattr(temp_default_node, k):
            val = getattr(temp_default_node, k)
            # copy mathutils types before removing the node to avoid dangling pointer segfaults.
            # ID datablocks (Scene/Object/Material/...) are persistent — copying them duplicates
            # the asset and breaks equality comparison against the source node's attr.
            if hasattr(val, "copy") and not isinstance(val, bpy.types.ID):
                val = val.copy()
            attr_defaults[k] = val

    node_tree.nodes.remove(temp_default_node)

    return attr_defaults


def _remove_banned_attrs(
    attrs: dict[str, Any],
    blender_attr_vals: dict[str, Any],
):
    for k in IGNORE_ATTRS:
        res = attrs.pop(k, None)
        if (
            res is not None
            and k not in ["capture_items", "active_item"]
            and res != blender_attr_vals[k]
        ):
            logger.warning(
                f"Ignoring {k}={res} which had been changed from its default value {blender_attr_vals[k]!r}"
            )


def _keep_attr(
    node: bpy.types.Node,
    k: str,
    v: Any,
    param: str | None,
    func_defaults: dict[str, Any],
    attr_defaults: dict[str, Any],
) -> bool:
    """Whether to emit attr `k`, or drop it because the binding already reproduces
    its value: compared against the procfunc default when `k` binds to a parameter
    that has one (these intentionally diverge from bpy's), else the bpy default.
    """
    if k == "data_type" and node.bl_idname == "GeometryNodeInputNamedAttribute":
        return True
    if v == "" and _is_empty_enum(node, k):
        return False  # state-gated enum with no valid member: nothing to set
    if param in func_defaults:
        if v == func_defaults[param] and v != attr_defaults.get(k, v):
            logger.debug(
                f"Stripping attr {k!r} ({param!r}) on {node.bl_idname}: source "
                f"value {v!r} equals procfunc default but differs from bpy "
                f"default {attr_defaults[k]!r}"
            )
        return v != func_defaults[param]
    return v != attr_defaults[k]


def generic_attrs(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    attrs: dict[str, Any],
    func: Callable,
    func_spec: dict[str, Any],
) -> dict[str, Any]:
    """The attrs a node contributes to its binding call, filtered against the bpy
    and procfunc defaults and renamed per attr_names_map. Special-case handlers
    call this only if they want it, on whatever subset of attrs they pass in."""
    func_sig = inspect.signature(func)
    func_defaults = {
        param.name: param.default
        for param in func_sig.parameters.values()
        if param.default is not param.empty
    }
    attr_names_map = func_spec.get("attr_names_map") or {}
    attr_defaults = bpy_node_defaults(node_tree, node, list(attrs.keys()))

    resolved = {}
    for k, v in attrs.items():
        param = attr_names_map.get(k, k)
        if not _keep_attr(node, k, v, param, func_defaults, attr_defaults):
            continue
        if param is not None:
            resolved[param] = v

    # we only want to remove MODE_ATTRS which were actually used to resolve the function
    #   (since presumably the restriction implied by these is already enforced by the new function signature)
    resolve_mode_args = func_spec.get("bpy_mode_args")
    if resolve_mode_args is not None:
        for k in resolve_mode_args:
            if k in resolved and k not in func_sig.parameters.keys():
                resolved.pop(k)

    # normalize the data_type spelling to the canonical NodeDataType
    for dtype_attr in ("data_type", "input_type"):
        if dtype_attr in resolved and isinstance(resolved[dtype_attr], str):
            resolved[dtype_attr] = bpy_node_info.datatype_from_bpy_str(
                resolved[dtype_attr]
            )

    _remove_banned_attrs(resolved, attr_defaults)

    return resolved
