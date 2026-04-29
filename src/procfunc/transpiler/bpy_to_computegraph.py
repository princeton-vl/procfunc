import inspect
import logging
from collections import namedtuple
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import bpy
import idprop.types
import numpy as np
import pandas as pd

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc import types as t
from procfunc.nodes import NODES_MANIFEST, bpy_node_info
from procfunc.nodes import bpy_node_info as bni
from procfunc.nodes import types as nt
from procfunc.nodes.execute.util import get_active_sockets, normalize_socket_type
from procfunc.ops import OPS_MANIFEST
from procfunc.transpiler import identifiers
from procfunc.util import bpy_info, log, manifest, pytree

logger = logging.getLogger(__name__)

_NODES_MANIFEST_INDEXED = NODES_MANIFEST.set_index("bpy_name")
_OPS_MANIFEST_INDEXED = OPS_MANIFEST.set_index("bpy_name")

# TODO replace with nodes/types.py or bpy_info.py?
SUBCOMPONENT_TYPES = (
    bpy.types.Material,
    bpy.types.Object,
    bpy.types.Collection,
    bpy.types.Image,
    bpy.types.Texture,
)
MODE_ATTRS = [
    "mode",
    "data_type",
    "operation",
    "rotation_type",
    "feature",
    "distribute_method",
]
IGNORE_ATTRS = ["color_mapping", "texture_mapping", "active_item", "capture_items"]


def handle_specialcase_math(_node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    if cg_node.kwargs.pop("use_clamp", False):
        # our math funcs wont support inline clamp, so we add an extra node when needed
        cg_node = cg.FunctionCallNode(
            func=pf.nodes.math.clamp, args=(cg_node,), kwargs={}
        )
    return cg_node


def handle_specialcase_color_ramp(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    cg_node.kwargs.pop("color_ramp", None)
    cg_node.kwargs["interpolation"] = node.color_ramp.interpolation
    cg_node.kwargs["points"] = [
        (round(point.position, 3), tuple(round(x, 3) for x in point.color))
        for point in node.color_ramp.elements
    ]
    return cg_node


def handle_specialcase_value(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    cg_node.kwargs["value"] = _repr_default_value(
        node.outputs[0].default_value, node.outputs[0].type
    )
    return cg_node


def handle_specialcase_vector_rotate(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    angle = cg_node.kwargs.pop("angle", None)

    match node.rotation_type:
        case "X_AXIS":
            cg_node.kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.func.combine_xyz, args=(angle, 0, 0), kwargs={}
            )
        case "Y_AXIS":
            cg_node.kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.func.combine_xyz, args=(0, angle, 0), kwargs={}
            )
        case "Z_AXIS":
            cg_node.kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.func.combine_xyz, args=(0, 0, angle), kwargs={}
            )
        case "EULER_XYZ" | "AXIS_ANGLE":
            pass
        case _:
            raise ValueError(f"Unknown rotation type {node.rotation_type}")

    return cg_node


def handle_specialcase_curve(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    cg_node.kwargs.pop("mapping", None)

    def _repr_point(point):
        return tuple(round(p, 4) for p in point.location)

    curves = [
        np.array([_repr_point(point) for point in curve.points])
        for curve in node.mapping.curves
    ]
    if len(curves) > 1:
        cg_node.kwargs["curves"] = curves
    else:
        cg_node.kwargs["curve"] = curves[0]

    invalid_handle = next(
        (
            point.handle_type
            for point in node.mapping.curves[0].points
            if point.handle_type != "AUTO"
        ),
        None,
    )
    if invalid_handle:
        logger.warning(
            f"{node.name=} had curve handle {invalid_handle=}, currently only AUTO is supported. "
            "Please use a different handle, or contact the developers to add support for it"
        )

    return cg_node


SPECIAL_CASE_NODES: Callable[[bpy.types.Node, cg.Node], cg.Node] = {
    "ShaderNodeMath": handle_specialcase_math,
    "ShaderNodeValToRGB": handle_specialcase_color_ramp,
    "ShaderNodeVectorRotate": handle_specialcase_vector_rotate,
    # curves share handler
    "ShaderNodeFloatCurve": handle_specialcase_curve,
    "ShaderNodeRGBCurve": handle_specialcase_curve,
    "ShaderNodeVectorCurve": handle_specialcase_curve,
    # values with .outputs[0].default_value can share handler
    "ShaderNodeValue": handle_specialcase_value,
    "ShaderNodeRGB": handle_specialcase_value,
}


class InvalidNodeGraph(Exception):
    def __init__(self, message: str, nodes: list[bpy.types.Node]):
        super().__init__(message)
        self.nodes = nodes


@dataclass
class ParseMemo:
    nodes: dict[tuple[int, str], cg.Node] = field(default_factory=dict)
    """
    (str, str) key is (node_tree.name, node.name)
    """

    links: dict[tuple[int, str, str], cg.Node] = field(default_factory=dict)
    """
    (str, str, str) key is (node_tree.name, node.name, from_socket.identifier)
    """

    compute_graphs: dict[int, tuple[cg.ComputeGraph, dict[str, cg.Node]]] = field(
        default_factory=dict
    )
    """
    int key is id(node_tree)
    """

    assets: dict[tuple[type, str], cg.ComputeGraph] = field(default_factory=dict)
    """
    str key is asset.name
    """


def _find_node_blidname(
    node_tree: bpy.types.NodeTree, bl_idname: str
) -> list[bpy.types.Node]:
    return [node for node in node_tree.nodes if node.bl_idname == bl_idname]


def parse_texture(tex: t.Texture, memo: ParseMemo) -> cg.Node:
    assert tex.use_nodes
    raise NotImplementedError("Texture not implemented")
    # node_tree = parse_node_tree(tex.node_tree, memo)


def _target_attrs(node: bpy.types.Node) -> dict[str, Any]:
    attr_vals = {}
    for k in dir(node):
        if k.startswith("_"):
            continue
        elif k in bpy_node_info.SPECIAL_CASE_ATTR_NAMES:
            attr_vals[k] = None
        elif k not in bpy_node_info.UNIVERSAL_ATTR_NAMES:
            attr_vals[k] = getattr(node, k)

    return attr_vals


def _bpy_node_defaults(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    attr_keys: list[str],
) -> dict[str, Any]:
    temp_default_node = node_tree.nodes.new(node.bl_idname)
    if node.bl_idname.endswith("NodeGroup"):
        temp_default_node.node_tree = node.node_tree
    if hasattr(node, "operation"):
        # assert "operation" not in attr_keys, (node, attr_keys)
        temp_default_node.operation = node.operation

    attr_defaults = {}
    for k in attr_keys:
        if hasattr(temp_default_node, k):
            val = getattr(temp_default_node, k)
            # copy mathutils types before removing the node to avoid dangling pointer segfaults
            if hasattr(val, "copy"):
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


def _parse_getattr(
    res: cg.Node,
    link: bpy.types.NodeLink,
):
    target = link.from_socket.name
    func_spec, _ = _node_to_spec(
        link.from_node.bl_idname, _target_attrs(link.from_node)
    )
    if func_spec is not None and isinstance(func_spec["output_names_map"], dict):
        target = func_spec["output_names_map"].get(target, target)
    target = identifiers.bpy_name_to_pythonid(target)

    res = cg.GetAttributeNode(attribute_name=target, source=res)
    return res


def _create_link_impl_node(
    node_tree: bpy.types.NodeTree,
    link: bpy.types.NodeLink,
    memo: ParseMemo,
) -> cg.Node:
    if link.from_node.bl_idname in ["NodeGroupInput", "NodeGroupOutput"]:
        key = (id(link.from_node), link.from_socket.identifier)
        raise ValueError(
            f"{parse_link.__name__} {node_tree.name=} {key} {link.from_node.name} {link.from_socket.name} -> {link.to_node.name} {link.to_socket.name} "
            f"has {link.from_node.bl_idname=}, which should have been avoided from parsing via {len(memo.links)=}"
        )
    elif link.from_node.bl_idname == "NodeReroute":
        if len(link.from_node.inputs[0].links) == 0:
            raise ValueError(
                f"Node {link.from_node.bl_idname} {link.from_node.name=} in {node_tree.name=} has no inputs"
            )

        # pass through to_socket to avoid potentially having wrong type inference
        res = parse_link(node_tree, link.from_node.inputs[0].links[0], memo)
        assert res is not None, link
        return res
    elif link.from_node.bl_idname == "ShaderNodeSeparateXYZ":
        inp_vec = link.from_node.inputs[0]
        if len(inp_vec.links) == 0:
            # WARN: creates multiple constants without memoizing
            default_value = _repr_default_value(inp_vec.default_value, inp_vec.type)
            source = cg.FunctionCallNode(
                func=pf.nodes.func.constant,
                args=(default_value,),
                kwargs={},
            )
        else:
            # skips over `link.from_node` since we are relying on the ProcNode getattr() to do that, rather than an explicit functioncall
            source = parse_link(node_tree, inp_vec.links[0], memo)

        return cg.GetAttributeNode(
            attribute_name=link.from_socket.name.lower(),
            source=source,
        )
    else:
        res = parse_node(node_tree, link.from_node, memo)
        assert res is not None, link

        outsockets = get_active_sockets(link.from_node.outputs)
        assert len(outsockets) > 0
        if len(outsockets) > 1:
            res = _parse_getattr(res, link)
            assert res is not None, link

        assert res is not None, link
        return res

    raise ValueError("Impossible")


def parse_link(
    node_tree: bpy.types.NodeTree,
    link: bpy.types.NodeLink,
    memo: ParseMemo,
) -> cg.Node:
    """
    Create a cg.Node for the from_node, and prefix it with a GET_ATTRIBUTE
        if this is necessary to disambiguate multiple outputs
    """

    key = (node_tree.session_uid, link.from_node.name, link.from_socket.identifier)

    if link_node := memo.links.get(key):
        assert link_node is not None, key
        res = link_node
    else:
        res = _create_link_impl_node(node_tree, link, memo)
        memo.links[key] = res

    # make all implicit blender typeconversions into explicit .astype calls
    if link.from_socket.type != link.to_socket.type:
        to_socket_type = bpy_node_info.SocketType(
            normalize_socket_type(link.to_socket.bl_idname)
        )
        to_py_type = bpy_node_info.SOCKET_TYPE_TO_PYTHON_TYPE[to_socket_type]

        assert to_py_type is not None, to_socket_type

        logger.debug(
            f"Adding explicit astype({to_py_type}) for {link.from_node.name}.{link.from_socket.name} -> "
            f"{link.to_node.name}.{link.to_socket.name}"
        )

        res = cg.MethodCallNode(
            callee=res,
            method_name="astype",
            args=(),
            kwargs={"dtype": to_py_type},
        )

    assert res is not None, link

    return res


def _repr_default_value(value: Any, socket_type: str) -> Any:
    if isinstance(value, SUBCOMPONENT_TYPES):
        return value.name
    elif socket_type == "RGBA":
        return pf.Color([round(x, 6) for x in value[:3]])
    elif isinstance(
        value, (bpy.types.bpy_prop_array, t.Vector, t.Euler, t.Quaternion, t.Matrix)
    ):
        return tuple(round(v, 6) for v in value)
    elif isinstance(value, idprop.types.IDPropertyArray):
        return tuple(round(v, 6) for v in value)
    elif isinstance(value, float):
        return round(value, 6)
    else:
        return value


def _create_link_input(
    node_tree: bpy.types.NodeTree,
    socket: bpy.types.NodeSocket,
    memo: ParseMemo,
    is_toplevel: bool,
    func_default: Any | None = None,
) -> cg.Node | list[cg.Node] | None:
    if len(socket.links) > 1:
        return [parse_link(node_tree, l, memo) for l in socket.links]

    if len(socket.links) == 1:
        return parse_link(node_tree, socket.links[0], memo)

    if not hasattr(socket, "default_value"):
        return None

    if isinstance(socket.default_value, SUBCOMPONENT_TYPES) and not is_toplevel:
        logger.warning(
            (
                f"Transpiler recommends against {type(socket.default_value)} as default_value but got {socket.default_value.name=} {is_toplevel=}"
                f"please use a typed socket connected from the toplevel nodegroup inputs instead. This makes your subcomponent user-configurable ",
                [socket],
            )
        )

    if isinstance(socket.default_value, bpy.types.Material):
        mat_graph = parse_material(socket.default_value, memo)
        return cg.SubgraphCallNode(subgraph=mat_graph, args=(), kwargs={})

    if isinstance(socket.default_value, bpy.types.Object):
        return t.MeshObject(socket.default_value)

    if isinstance(socket.default_value, bpy.types.Collection):
        return t.Collection(socket.default_value)

    if not hasattr(socket, "default_value"):
        return None

    res = _repr_default_value(getattr(socket, "default_value", None), socket.type)

    if func_default is not None:
        repr_func_default = _repr_default_value(func_default, socket.type)
        if res == repr_func_default:
            return None

    return res


def _create_inputs(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    memo: ParseMemo,
    func_defaults: dict[str, Any],
    names: dict[str, str] | None = None,
    is_toplevel: bool = False,
) -> dict[str, cg.Node]:
    res = {}

    if names is None:
        names = {
            socket.identifier: socket.name
            for socket in node.inputs.values()
            if socket.enabled and socket.name != ""
        }
        names = identifiers.dedup_names_with_suffix(names, first_use_suffix=True)

    inputs = {}
    for identifier, name in names.items():
        socket = next(
            (s for s in node.inputs.values() if s.identifier == identifier), None
        )
        assert socket is not None

        name = identifiers.bpy_name_to_pythonid(name)

        func_default_kwarg = func_defaults.get(name, None)
        res = _create_link_input(
            node_tree,
            socket,
            memo,
            is_toplevel,
            func_default=func_default_kwarg,
        )
        if res is None:
            logger.debug(
                f"Skipping argument for {name=} {socket.node.bl_idname=} {func_default_kwarg=}"
            )
            continue
        inputs[name] = res

    for name in inputs.keys():
        if not identifiers.is_valid_snake_identifier(name):
            raise ValueError(
                f"Input name {name!r} is not a valid identifier. {node.bl_idname=}, {node.inputs.keys()=}"
            )

    return inputs


def _find_manifest_func(
    bpy_name: str,
    mode_vals: dict[str, Any],
    manifest_indexed: pd.DataFrame,
) -> dict | None:
    if bpy_name not in manifest_indexed.index:
        return None

    candidates = manifest_indexed.loc[bpy_name]
    if isinstance(candidates, pd.Series):
        candidates = pd.DataFrame([candidates])

    exploded = candidates["bpy_mode_args"].fillna({}).apply(pd.Series)

    mask = pd.Series([True] * len(candidates), index=candidates.index)
    for mode_attr, val in mode_vals.items():
        # Behavior: if a mode_attr is not in the manifest, we can ignore it.
        #   if its in the manifest, but none match our val, then we can take a

        if val is None:
            continue
        if mode_attr not in exploded.columns:
            continue
        match_mask = exploded[mode_attr] == val
        if match_mask.sum() == 0:
            match_mask = exploded[mode_attr].isna()
        mask &= match_mask

    if mask.sum() == 0:
        raise ValueError(
            f"{bpy_name=} had {len(candidates)=}, but filtering for {mode_vals=} eliminated them all"
        )

    if mask.sum() > 1:
        options_for_modevals = {
            k: list(exploded[k].unique()) if k in exploded.columns else None
            for k in mode_vals.keys()
        }
        raise ValueError(
            f"Found {mask.sum()} nodes with {bpy_name=} {mode_vals=} in manifest, expected exactly 1. "
            f"Options for {mode_vals.keys()=} are {options_for_modevals}"
        )

    matches = candidates.loc[mask]

    if len(matches) == 1:
        return matches.iloc[0].to_dict()
    else:
        return None


def _node_to_spec(
    bl_idname: str,
    attrs: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict]:
    if bpy_info.NodeGroupType.from_str(bl_idname) is not None:
        return None, attrs

    mode_attr_vals = {k: attrs[k] for k in MODE_ATTRS if k in attrs}

    func_row = _find_manifest_func(
        bl_idname,
        mode_attr_vals,
        _NODES_MANIFEST_INDEXED,
    )

    if func_row is None:
        raise ValueError(f"Node {bl_idname} {mode_attr_vals=} had no manifest row")
    elif func_row["name"] in ["LATER", "DECLINE"]:
        raise ValueError(f"Node {bl_idname} {mode_attr_vals=} had {func_row['name']=}")

    return func_row, attrs


def _map_inputs_with_arg_map(
    inputs: dict[str, Any],
    arg_names_map: dict[str, str],
) -> dict[str, Any]:
    mapped_inputs = {}
    for k, v in inputs.items():
        if k in arg_names_map:
            k = arg_names_map[k]
        mapped_inputs[k] = v

    return mapped_inputs


def parse_standard_node(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    memo: ParseMemo,
) -> cg.Node:
    # note: read/write result into memo happens at parse_node level, not here

    if node.bl_idname == "NodeGroupInput":
        raise ValueError(
            f"NodeGroupInput {node} {id(node)=} should have been pre-memo'd in parse_node_tree"
        )

    attrs = _target_attrs(node)
    func_spec, attrs = _node_to_spec(node.bl_idname, attrs)

    func = manifest.import_item_iterative(func_spec["name"].replace("pf.", "procfunc."))
    func_sig = inspect.signature(func)
    arg_names_map = func_spec.get("arg_names_map")

    attr_defaults = _bpy_node_defaults(node_tree, node, list(attrs.keys()))
    is_named_attr = node.bl_idname == "GeometryNodeInputNamedAttribute"
    attrs = {
        k: v
        for k, v in attrs.items()
        if v != attr_defaults[k] or (k == "data_type" and is_named_attr)
    }

    if arg_names_map is not None:
        attrs = {arg_names_map.get(k, k): v for k, v in attrs.items()}

    # we only want to remove MODE_ATTRS which were actually used to resolve the function
    #   (since presumably the restriction implied by these is already enforced by the new function signature)
    resolve_mode_args = func_spec.get("bpy_mode_args")
    if resolve_mode_args is not None:
        for k, v in resolve_mode_args.items():
            if k in attrs and k not in func_sig.parameters.keys():
                attrs.pop(k)

    # we will assume the data_types in an input .blend can always be inferred.
    #   it is the job of the .astype() insertion to preserve enough info for this
    if "data_type" in attrs and node.bl_idname != "GeometryNodeInputNamedAttribute":
        attrs.pop("data_type")

    func_defaults = {
        param.name: param.default
        for param in func_sig.parameters.values()
        if param.default is not param.empty
    }

    inputs = _create_inputs(node_tree, node, memo, func_defaults=func_defaults)
    arg_names_map = func_spec["arg_names_map"]
    if arg_names_map is not None:
        inputs = _map_inputs_with_arg_map(inputs, arg_names_map)

    if overlap := set(attrs.keys()).intersection(set(inputs.keys())):
        raise ValueError(
            f"Node {node.bl_idname} had keys {overlap=} between {attrs.keys()=} and {inputs.keys()=}, which is invalid"
        )

    cg_node = cg.FunctionCallNode(
        func=func,
        args=(),
        kwargs={**attrs, **inputs},
    )

    cg_node_orig = cg_node
    if handler := SPECIAL_CASE_NODES.get(node.bl_idname):
        cg_node = handler(node, cg_node)

    _remove_banned_attrs(cg_node.kwargs, attr_defaults)

    signature = inspect.signature(func)

    # Check if the function accepts **kwargs (VAR_KEYWORD)
    has_var_keyword = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values()
    )

    # Only check for missing parameters if the function doesn't accept **kwargs
    excess_kwargs = set(cg_node_orig.kwargs.keys()) - set(signature.parameters.keys())
    if not has_var_keyword and excess_kwargs:
        node_mode = getattr(node, "mode", None)
        node_operation = getattr(node, "operation", None)
        node_data_type = getattr(node, "data_type", None)
        raise ValueError(
            f"Codegen would attempt to call {func.__name__=} with {excess_kwargs} "
            f"but these attributes do not exist in the procfunc signature, which had {list(signature.parameters.keys())} "
            f"source node had {node.bl_idname} {node.inputs.keys()=} {node_mode=} {node_operation=} {node_data_type=} "
            "Please contact the developers."
        )

    return cg_node


def parse_nodegroup_call(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    memo: ParseMemo,
) -> cg.Node:
    assert hasattr(node, "node_tree"), f"Node {node.bl_idname} has no node_tree"

    sockets = [socket for socket in node.inputs.values() if socket.enabled]
    input_names = {socket.identifier: socket.name for socket in sockets}
    input_names = identifiers.apply_panel_names_to_input_names(
        node.node_tree, input_names, only_dedup=False
    )

    with log.add_exception_context_msg(f"While processing {node.name=}:"):
        graph, _ = parse_node_tree(node.node_tree, memo)

    func_defaults = {
        name: value.kwargs.get("default_value", None)
        for name, value in graph.inputs.items()
    }
    inputs = _create_inputs(
        node_tree,
        node,
        memo,
        func_defaults=func_defaults,
        is_toplevel=False,
        names=input_names,
    )

    return cg.SubgraphCallNode(
        subgraph=graph,
        args=(),
        kwargs=inputs,
    )


def _parse_constant_node(node: bpy.types.Node) -> cg.Node:
    attr_name = bpy_node_info.CONSTANT_NODES[node.bl_idname]

    if attr_name == "DEFAULT_VALUE":
        val = node.outputs[0].default_value
    else:
        val = getattr(node, attr_name)

    return cg.ConstantNode(value=val)


def parse_node(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    memo: ParseMemo,
) -> cg.Node:
    memo_key = (node_tree.session_uid, node.name)
    if node_node := memo.nodes.get(memo_key):
        return node_node

    # logger.debug(f"Parsing node {node_tree.name} {node.bl_idname}")

    if bpy_info.NodeGroupType.from_str(node.bl_idname) is not None:
        res = parse_nodegroup_call(node_tree, node, memo)
    elif node.bl_idname == "NodeReroute":
        raise ValueError(
            f"Node {node.bl_idname} {node.name=} is a NodeReroute, which should have been folded away"
        )
    else:
        res = parse_standard_node(node_tree, node, memo)

    if node.label != "":
        res.metadata["varname"] = identifiers.bpy_name_to_pythonid(node.label)

    memo.nodes[memo_key] = res
    return res


def _find_output_node(
    node_tree: bpy.types.NodeTree,
):
    node_tree_type = bpy_info.NodeTreeType(node_tree.bl_idname)
    ng_type = bpy_info.NODETREE_TO_NODEGROUP[node_tree_type]
    main_output_node_type = bpy_info.NODETREE_TYPE_TO_MAIN_OUTPUT[node_tree_type]

    output_nodes_ng = _find_node_blidname(node_tree, "NodeGroupOutput")
    output_nodes_ctx = _find_node_blidname(node_tree, main_output_node_type)
    output_nodes = output_nodes_ng + output_nodes_ctx

    if len(output_nodes) > 1:
        raise ValueError(f"Found mutltiple {output_nodes=} for {node_tree=}")
    if len(output_nodes) == 0:
        idnames = set(node.bl_idname for node in node_tree.nodes)
        raise ValueError(
            f"No {main_output_node_type=} found "
            f"for {node_tree.bl_idname} of type {ng_type} with {idnames}"
        )
    return output_nodes[0]


def _name_from_socket_and_panels(
    socket: bpy.types.NodeSocket,
    panels: list[bpy.types.NodeSocket],
) -> str:
    for panel in panels:
        match = next(
            (
                psock
                for psock in panel.interface_items.values()
                if psock.identifier == socket.identifier
            ),
            None,
        )
        if match is not None:
            return identifiers.bpy_name_to_pythonid(panel.name + "_" + socket.name)
    return identifiers.bpy_name_to_pythonid(socket.name)


def _infer_geometry_type(node: cg.Node, _depth: int = 0) -> type | None:
    """Infer concrete geometry type by inspecting the procfunc function that produces this node."""
    if _depth > 10:
        return None

    if isinstance(node, cg.FunctionCallNode):
        try:
            hints = get_type_hints(node.func)
        except Exception:
            return None
        return_type = hints.get("return")
        if return_type is None:
            return None
        concrete = _extract_procnode_inner_type(return_type)
        if concrete is not None:
            return concrete
        # Return type is generic (TypeVar) — recurse into geometry input args
        for arg in list(node.args) + list(node.kwargs.values()):
            if isinstance(arg, list):
                for item in arg:
                    if isinstance(item, cg.Node):
                        result = _infer_geometry_type(item, _depth + 1)
                        if result is not None:
                            return result
            elif isinstance(arg, cg.Node):
                result = _infer_geometry_type(arg, _depth + 1)
                if result is not None:
                    return result
        return None

    if isinstance(node, cg.GetAttributeNode):
        source = node.args[0]
        if not isinstance(source, cg.FunctionCallNode):
            return None
        try:
            hints = get_type_hints(source.func)
        except Exception:
            return None
        return_type = hints.get("return")
        if return_type is None:
            return None
        if hasattr(return_type, "__annotations__"):
            field_type = return_type.__annotations__.get(node.attribute_name)
            if field_type is not None:
                return _extract_procnode_inner_type(field_type)
        return None

    return None


def _extract_procnode_inner_type(t: type) -> type | None:
    origin = get_origin(t)
    if origin is nt.ProcNode:
        args = get_args(t)
        if args and not isinstance(args[0], TypeVar):
            return args[0]
    return None


def _socket_to_pf_type(
    socket: bpy.types.NodeSocket,
    is_output: bool,
    interface: Any | None = None,  # unsure type
    use_socket_bounds: bool = False,
    use_specialized_sockets: bool = False,
) -> type:
    """
    Create a python typing str to represent the interface bounds of a blender _socket_to_pf_type

    Args:
        socket: The blender socket to create a python typing str for
        interface: The nodegroup interface of the socket, if one exists
        use_socket_bounds: Whether to use the bounds of the socket's interface.
            Disabled by default since these are often accidentally / imprecisely filled by implementers

    Returns:
        A python typing str to represent the interface bounds of a blender socket
    """

    type_str = normalize_socket_type(socket.bl_idname)
    st = bpy_node_info.SocketType(type_str)
    py_type = bpy_node_info.SOCKET_TYPE_TO_PYTHON_TYPE[st]

    bounds = [None, None]

    if use_socket_bounds and interface is not None:
        if hasattr(interface, "min_value") and interface.min_value > -1000:
            bounds[0] = interface.min_value
        if hasattr(interface, "max_value") and interface.max_value < 1000:
            bounds[1] = interface.max_value
    elif use_specialized_sockets and type_str != socket.bl_idname:
        match socket.bl_idname:
            case "NodeSocketFloatFactor":
                bounds = [0.0, 1.0]
            case "NodeSocketVectorEuler":
                bounds = [(0.0, 0.0, 0.0), (3.141592, 3.141592, 3.141592)]
            case _:
                logger.info(
                    f"No implemented bounds annot for special socket {socket.bl_idname}"
                )

    if bounds[0] is not None or bounds[1] is not None:
        raise NotImplementedError("Range annotation current not supported")
        # py_type = Annotated[float, t.ValueRange{tuple(bounds)}]

    if py_type is None:
        return nt.ProcNode
    elif is_output:
        return nt.ProcNode[py_type]
    else:
        return nt.SocketOrVal[py_type]


def _placeholder_for_graph_input(
    socket: bpy.types.NodeSocket,
    varname: str,
    node_tree: bpy.types.NodeTree,
) -> cg.Node:
    interface = node_tree.interface.items_tree[socket.name]
    if interface.hide_value:
        logger.warning(
            f"{node_tree.name=} {socket.name=} has hide_value=True, "
            "overwriting it to False or else current transpiler implementationl will break"
        )
        interface.hide_value = False

    inner_type = _socket_to_pf_type(
        socket,
        is_output=False,
        interface=interface,
    )

    raw_default = getattr(interface, "default_value", None)
    if raw_default is None:
        raw_default = getattr(socket, "default_value", None)
    default_value = _repr_default_value(raw_default, socket.type)

    norm_soc = normalize_socket_type(socket.bl_idname)
    if default_value is None and norm_soc in [
        "NodeSocketFloat",
        "NodeSocketVector",
    ]:
        raise ValueError(f"{socket.name=} has no default_value and is a {norm_soc=}")

    node = cg.InputPlaceholderNode(
        name=varname,
        default_value=default_value,
        metadata=dict(
            known_value_type=inner_type,
            varname=varname,
        ),
    )
    if default_value is not None:
        node.kwargs["default_value"] = default_value

    return node


def _create_and_memoize_input_placeholders(
    node_tree: bpy.types.NodeTree,
    input_nodes: list[bpy.types.Node],
    memo: ParseMemo,
) -> tuple[dict[str, cg.Node], dict[str, cg.Node]]:
    """
    prefill memo for all output links of all input nodes
    this is so that we never later recurse onto input nodes, since we dont actually want to create input nodes
    the output identifiers of input nodes are defined by the function args instead.

    also: create the placeholder nodes for the input nodes
    """

    panels = [
        socket
        for socket in node_tree.interface.items_tree.values()
        if socket.item_type == "PANEL"
    ]

    placeholders = {}
    id_to_node = {}
    for input_node in input_nodes:
        active_sockets = get_active_sockets(input_node.outputs)
        for socket in active_sockets:
            key = (node_tree.session_uid, input_node.name, socket.identifier)
            if socket.identifier in id_to_node:
                memo.links[key] = id_to_node[socket.identifier]
                continue

            varname = _name_from_socket_and_panels(socket, panels)
            node = _placeholder_for_graph_input(socket, varname, node_tree)

            if varname in placeholders:
                raise ValueError(
                    f"Duplicate varname {varname} for {key=} in {input_node.outputs.keys()=} with existing {placeholders.keys()=}"
                )
            id_to_node[socket.identifier] = node
            placeholders[varname] = node
            memo.links[key] = node

    # logger.debug(
    #    f"{_create_and_memoize_input_placeholders.__name__} {node_tree.name=} memoized {placeholders.keys()=}"
    # )

    return placeholders, id_to_node


def parse_node_tree(
    node_tree: bpy.types.NodeTree,
    memo: ParseMemo,
) -> tuple[cg.ComputeGraph, dict[str, cg.Node]]:
    """

    Note: recursive over nodes and node_trees which is not ideal. TODO convert to stack breadth-first

    """

    assert node_tree.name != "Shader Nodetree", (
        "nodetree name must be nondefault as we use it as a hash key"
    )

    memo_key = node_tree.session_uid
    if res := memo.compute_graphs.get(memo_key):
        return res

    cg_name = node_tree.name
    if cg_name.startswith("nodegroup_"):
        cg_name = cg_name.replace("nodegroup_", "")
    if cg_name.endswith(" (no gc)"):  # comes from v1 to_nodegroup singleton=True
        cg_name = cg_name.replace(" (no gc)", "")
    cg_name = identifiers.bpy_name_to_pythonid(cg_name)

    name_parts = cg_name.split("_")
    if name_parts[0].isdigit():
        cg_name = "_".join(name_parts[1:]) + "_" + name_parts[0]

    if not identifiers.is_valid_snake_identifier(cg_name):
        raise ValueError(f"Invalid cg_name {cg_name} for {node_tree.name}")

    input_nodes = _find_node_blidname(node_tree, "NodeGroupInput")
    output_node = _find_output_node(node_tree)
    inputs, id_to_node = _create_and_memoize_input_placeholders(
        node_tree, input_nodes, memo
    )

    outputs = {}
    for output_name, output_result_socket in output_node.inputs.items():
        if output_name == "":
            continue  # nodegroups seem to have an empty socket with identifier __extend__, skip it
        if len(output_result_socket.links) == 0:
            continue
        if len(output_result_socket.links) > 1:
            raise ValueError(
                f"Node {node_tree.bl_idname} has multiple inputs for {output_name=} {output_result_socket.identifier=} "
                "Multi-output sockets not supported on nodegroup. please contact the developers."
            )

        # logger.debug(
        #     f"Parsing link for {cg_name=} {output_name=} {output_result_socket.identifier=}"
        # )
        output_name = identifiers.bpy_name_to_pythonid(output_name)
        proc_node = parse_link(node_tree, output_result_socket.links[0], memo)
        if proc_node.metadata.get("known_value_type") is None:
            inferred = _infer_geometry_type(proc_node)
            if inferred is not None:
                vt = nt.ProcNode[inferred]
                logger.debug(
                    f"Inferred known_value_type={vt} for {proc_node=} from function signature"
                )
            else:
                vt = _socket_to_pf_type(
                    output_result_socket,
                    is_output=True,
                )
                logger.debug(
                    f"Setting known_value_type={vt} for {proc_node=} for {output_result_socket=}"
                )
            proc_node.metadata["known_value_type"] = vt
        if isinstance(proc_node, cg.InputPlaceholderNode):
            proc_node.default_value = None
        outputs[output_name] = proc_node

    if len(outputs) > 1:
        assert " " not in cg_name, f"cg_name {cg_name} contains spaces"

        # remove .001 suffixes
        typename = identifiers.snake_to_pascal(cg_name).rsplit(".", 1)[0] + "Result"
        output_type = namedtuple(typename, outputs.keys())
        output = output_type(**outputs)
    else:
        output = list(outputs.values())[0]

    compute_graph = cg.ComputeGraph(
        inputs=pytree.PyTree(inputs),
        outputs=pytree.PyTree(output),
        name=cg_name,
        metadata={
            "is_node_function": True,  # causes codegen to apply decorator
        },
    )
    logger.debug(
        f"Parsed node_tree {cg_name} with {len(inputs.keys())} inputs, {len(outputs.keys())} outputs "
        f"and {len(list(cg.traverse_depth_first(compute_graph)))} nodes"
    )

    memo.compute_graphs[memo_key] = (compute_graph, id_to_node)
    return compute_graph, id_to_node


def _parse_geomod_input(
    mod: bpy.types.Modifier,
    name: str,
    node_curr: cg.Node,
    memo: ParseMemo,
) -> cg.Node | None:
    socket = mod.node_group.interface.items_tree[name]

    if socket.socket_type == bni.SocketType.GEOMETRY.value:
        return node_curr

    value = mod[socket.identifier]

    if isinstance(value, bpy.types.Material):
        mat_graph = parse_material(value, memo)
        return cg.SubgraphCallNode(subgraph=mat_graph, args=(), kwargs={})
    if isinstance(value, bpy.types.Object):
        return t.MeshObject(value)
    if isinstance(value, bpy.types.Collection):
        return t.Collection(value)

    datatype = bni.SOCKET_CLASS_TO_DATATYPE[socket.socket_type]
    dtype = bni.DATATYPE_TO_SOCKET_DTYPE[datatype].value
    return _repr_default_value(value, dtype)


def parse_geo_modifier(
    obj: bpy.types.Object,
    node_curr: cg.Node,
    mod: bpy.types.Modifier,
    memo: ParseMemo,
) -> cg.Node:
    # TODO: need to find and memoize the input geometries and input attribute assignments.

    logger.info(f"Parsing geometry node modifier {mod.node_group.name}")

    graph, id_to_node = parse_node_tree(mod.node_group, memo)

    inputs = {}
    for name, soc in mod.node_group.interface.items_tree.items():
        if soc.in_out != "INPUT":
            continue
        if soc.identifier not in id_to_node:
            raise ValueError(
                f"Socket {soc.identifier=} {soc.name=} not found in {id_to_node.keys()}"
            )
        parsed_name = id_to_node[soc.identifier].metadata.get("varname", None)
        assert parsed_name is not None, id_to_node[soc.identifier]
        inputs[parsed_name] = _parse_geomod_input(mod, name, node_curr, memo)

    node_curr = cg.SubgraphCallNode(subgraph=graph, args=(), kwargs=inputs)

    geo_output_keys = [
        soc.name.lower()
        for soc in mod.node_group.interface.items_tree.values()
        if soc.in_out == "OUTPUT" and soc.socket_type == bni.SocketType.GEOMETRY.value
    ]
    attribute_output_keys = [
        soc.name.lower()
        for soc in mod.node_group.interface.items_tree.values()
        if soc.in_out == "OUTPUT" and soc.socket_type != bni.SocketType.GEOMETRY.value
    ]
    geo_output_getattrs = {
        k: cg.GetAttributeNode(source=node_curr, attribute_name=k)
        for k in geo_output_keys
    }
    attribute_output_getattrs = {
        k: cg.GetAttributeNode(source=node_curr, attribute_name=k)
        for k in attribute_output_keys
    }

    match len(geo_output_keys), len(attribute_output_keys):
        case 1, 0:
            return cg.FunctionCallNode(
                pf.nodes.to_mesh_object, args=(node_curr,), kwargs={}
            )
        case 1, _:
            return cg.FunctionCallNode(
                pf.nodes.to_mesh_object_with_attributes,
                kwargs={**geo_output_getattrs, **attribute_output_getattrs},
            )
        case _, _:
            return cg.FunctionCallNode(
                pf.nodes.to_objects_multi,
                args=(geo_output_getattrs, attribute_output_getattrs),
            )
        case _:
            raise ValueError(
                f"Expected 1 geo output and 0 or 1 attribute output, found {len(geo_output_keys)} and {len(attribute_output_keys)}"
            )


def parse_modifier(
    obj: bpy.types.Object,
    node_curr: cg.Node,
    mod: bpy.types.Modifier,
    memo: ParseMemo,
) -> cg.Node:
    if mod.type == "NODES":
        return parse_geo_modifier(obj, node_curr, mod, memo)

    mode_vals = {"type": mod.type, "operation": getattr(mod, "operation", None)}
    func_row = _find_manifest_func(
        "bpy.ops.object.modifier_add", mode_vals, _OPS_MANIFEST_INDEXED
    )
    if func_row is None:
        raise ValueError(f"Modifier {mod.type} {mode_vals=} not found in manifest")
    func_name = func_row["name"].replace("pf.", "procfunc.")
    func = manifest.import_item_iterative(func_name)

    inputs = {
        k: getattr(mod, k)
        for k in inspect.signature(func).parameters.keys()
        if k != "mutates_obj" and hasattr(mod, k)
    }

    res = cg.FunctionCallNode(func=func, args=(node_curr,), kwargs=inputs)
    return cg.MutatedArgumentNode(original_node=node_curr, mutator_call_node=res)


def _replace_vector_inpnodes_as_arg(
    node_tree: bpy.types.NodeTree,
    memo: ParseMemo,
) -> cg.Node:
    vector_input_nodes = _find_node_blidname(node_tree, "ShaderNodeTexCoord")
    vector_input_nodes += _find_node_blidname(node_tree, "ShaderNodeNewGeometry")

    vector_links = [
        link
        for node in vector_input_nodes
        for output in node.outputs.values()
        for link in output.links
    ]

    vector_placeholder = cg.InputPlaceholderNode(
        name="vector",
        default_value=None,
        metadata={"known_value_type": pf.ProcNode[pf.Vector], "varname": "vector"},
    )

    for node in vector_input_nodes:
        memo.nodes[(node_tree.session_uid, node.name)] = vector_placeholder

    for link in vector_links:
        key = (node_tree.session_uid, link.from_node.name, link.from_socket.identifier)
        memo.links[key] = vector_placeholder

    return vector_placeholder


_MATERIAL_OUTPUT_SOCKETS = ["Surface", "Displacement", "Volume"]


def parse_material(
    mat: bpy.types.Material, memo: ParseMemo, coord_inp_as_arg: bool = False
) -> cg.ComputeGraph:
    memo_key = (type(mat), mat.name)
    if mat_node := memo.assets.get(memo_key):
        return mat_node

    node_tree = mat.node_tree

    inputs_dict = {}

    if coord_inp_as_arg:
        vector_placeholder = _replace_vector_inpnodes_as_arg(node_tree, memo)
        inputs_dict["vector"] = vector_placeholder

    (output_node,) = _find_node_blidname(node_tree, "ShaderNodeOutputMaterial")

    outputs_dict = {}
    for key in _MATERIAL_OUTPUT_SOCKETS:
        expect_type = pf.Vector if key == "Displacement" else pf.Shader
        if output_node.inputs[key].is_linked:
            res = parse_link(node_tree, output_node.inputs[key].links[0], memo)
            res.metadata["known_value_type"] = pf.ProcNode[expect_type]
        else:
            res = cg.ConstantNode(value=None)
            res.metadata["known_value_type"] = Union[pf.ProcNode[expect_type], None]
        outputs_dict[key.lower()] = res

    func_name = identifiers.bpy_name_to_pythonid(mat.name)
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree(inputs_dict),
        outputs=pytree.PyTree(t.Material(**outputs_dict)),
        name=func_name,
        metadata={},  # TODO
    )

    memo.assets[memo_key] = graph
    return graph


def parse_primitive(obj: t.Object) -> cg.Node:
    return cg.FunctionCallNode(pf.ops.primitives.mesh_monkey, args=(), kwargs={})


def parse_object(
    obj: bpy.types.Object,
    memo: ParseMemo,
    object_mode: Literal["monkey", "active", "named"] = "monkey",
    include_set_material: bool = True,
) -> cg.ComputeGraph:
    memo_key = (type(obj), obj.name)
    if obj_node := memo.assets.get(memo_key):
        return obj_node

    # TODO assert starting from single vertex?
    match object_mode:
        case "monkey":
            node_curr = cg.FunctionCallNode(
                pf.ops.primitives.mesh_monkey, args=(), kwargs={}
            )
        case "active":
            node_curr = cg.ConstantNode(
                value=cg.LiteralConstant("pf.MeshObject(bpy.context.active_object)")
            )
        case "named":
            node_curr = cg.ConstantNode(
                value=cg.LiteralConstant(
                    f"pf.MeshObject(bpy.data.objects[{obj.name!r}])"
                )
            )
        case _:
            raise ValueError(f"Invalid object mode: {object_mode}")

    coord = cg.FunctionCallNode(pf.nodes.shader.coord, args=(), kwargs={})
    coord = cg.GetAttributeNode(source=coord, attribute_name="generated")

    if include_set_material:
        for mat in obj.material_slots:
            mat_graph = parse_material(mat.material, memo)
            mat_kwargs = (
                {"vector": coord} if "vector" in mat_graph.inputs.obj().keys() else {}
            )
            mat_call = cg.SubgraphCallNode(
                subgraph=mat_graph, args=(), kwargs=mat_kwargs
            )

            node_curr = cg.FunctionCallNode(
                pf.ops.object.set_material,
                args=(node_curr,),
                kwargs={"material": mat_call},
            )

    for mod in obj.modifiers:
        node_curr = parse_modifier(obj, node_curr, mod, memo)

    name = "object_" + identifiers.bpy_name_to_pythonid(obj.name) + "_generate"
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"result": node_curr}),
        name=name,
        metadata={"func": parse_object, "object": obj.name},
    )

    memo.assets[memo_key] = graph
    return graph


def parse_scene(
    scene: bpy.types.Scene,
    memo: ParseMemo,
) -> cg.Node:
    raise NotImplementedError("Scene not implemented")
