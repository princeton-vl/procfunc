from dataclasses import dataclass
from typing import Any, Callable

import bpy

from procfunc import compute_graph as cg
from procfunc import types as t
from procfunc.nodes import bpy_node_info as bni
from procfunc.nodes import func, math
from procfunc.nodes import types as nt
from procfunc.util.log import add_exception_context_msg


@dataclass
class NodeOperatorResolution:
    pf_func: Callable[..., Any]
    value_type: bni.NodeDataType
    operator_type: cg.OperatorType


def _float_math_defs() -> list[NodeOperatorResolution]:
    return [
        NodeOperatorResolution(math.add, bni.NodeDataType.FLOAT, cg.OperatorType.ADD),
        NodeOperatorResolution(
            math.subtract, bni.NodeDataType.FLOAT, cg.OperatorType.SUB
        ),
        NodeOperatorResolution(
            math.multiply, bni.NodeDataType.FLOAT, cg.OperatorType.MUL
        ),
        NodeOperatorResolution(
            math.divide, bni.NodeDataType.FLOAT, cg.OperatorType.DIV
        ),
        NodeOperatorResolution(math.power, bni.NodeDataType.FLOAT, cg.OperatorType.POW),
        NodeOperatorResolution(
            math.modulo, bni.NodeDataType.FLOAT, cg.OperatorType.MOD
        ),
        NodeOperatorResolution(
            math.greater_than, bni.NodeDataType.FLOAT, cg.OperatorType.GREATER_THAN
        ),
        NodeOperatorResolution(
            math.less_than, bni.NodeDataType.FLOAT, cg.OperatorType.LESS_THAN
        ),
    ]


def _vector_math_defs(node_data_type: bni.NodeDataType) -> list[NodeOperatorResolution]:
    return [
        NodeOperatorResolution(math.vector_add, node_data_type, cg.OperatorType.ADD),
        NodeOperatorResolution(
            math.vector_subtract, node_data_type, cg.OperatorType.SUB
        ),
        NodeOperatorResolution(
            math.vector_multiply, node_data_type, cg.OperatorType.MUL
        ),
        NodeOperatorResolution(math.vector_divide, node_data_type, cg.OperatorType.DIV),
    ]


NODE_OPERATOR_TABLE = [
    *_float_math_defs(),
    *_vector_math_defs(bni.NodeDataType.FLOAT_VECTOR),
    # *_vector_math_defs(NodeDataType.RGBA), # no longer used, instead we will require explicit conversion to vector before math
    NodeOperatorResolution(
        math.vector_modulo, bni.NodeDataType.FLOAT_VECTOR, cg.OperatorType.MOD
    ),
    # NodeOperatorResolution(
    #     func.combine_xyz, bni.NodeDataType.FLOAT_VECTOR, cg.OperatorType.VECTOR_PACK
    # ),
    NodeOperatorResolution(
        func.separate_xyz, bni.NodeDataType.FLOAT_VECTOR, cg.OperatorType.NOOP
    ),
]


def normalize_socket_type(socket_type: str) -> str:
    # Map all vector subtypes to basic NodeSocketVector
    if socket_type.startswith("NodeSocketVector"):
        return "NodeSocketVector"
    elif socket_type.startswith("NodeSocketFloat"):
        return "NodeSocketFloat"
    elif socket_type.startswith("NodeSocketInt"):
        return "NodeSocketInt"
    elif socket_type == "NodeSocketVirtual":
        raise NotImplementedError(
            f"Virtual sockets are not supported, got {socket_type}"
        )
    else:
        return socket_type


def infer_socket_type_from_value(input_val: Any) -> str:
    """Infer the appropriate Blender socket type from an input value."""
    match input_val:
        case bpy.types.NodeSocket():
            socket_type = (
                input_val.bl_idname
                if hasattr(input_val, "bl_idname")
                else input_val.__class__.__name__
            )
            return normalize_socket_type(socket_type)
        case x if isinstance(x, bpy.types.NodeInternal):
            try:
                first_enabled = next(o for o in x.outputs if o.enabled)
                return infer_socket_type_from_value(first_enabled)
            except StopIteration:
                return "NodeSocketFloat"
        case int():
            return "NodeSocketInt"
        case float():
            return "NodeSocketFloat"
        case bool():
            return "NodeSocketBool"
        case str():
            return "NodeSocketString"
        case x if hasattr(x, "__len__"):
            match len(x):
                case 3:
                    return "NodeSocketVector"
                case 4:
                    return "NodeSocketColor"
                case 1 | 2:
                    return "NodeSocketFloat"
                case _:
                    return "NodeSocketFloat"
        case _:
            return "NodeSocketFloat"


def get_active_sockets(
    sockets: bpy.types.bpy_prop_collection,
) -> list[bpy.types.NodeSocket]:
    if len(set(s.is_output for s in sockets)) > 1:
        raise ValueError(f"{sockets=} had a mix of input and output sockets")

    return [
        socket
        for socket in sockets
        if (
            socket.enabled
            and socket.identifier != "__extend__"
            and socket.name != ""  # empty-name sockets are internal to nodegroup wiring
        )
    ]


def get_nth_socket(
    sockets: bpy.types.bpy_prop_collection,  # of bpy.types.NodeSocket
    socket_name: str,
    index: int,
    debug_node_name: str = "",
) -> bpy.types.NodeSocket:
    """
    Get the nth occurrence of a socket with the given name

    """

    socket_name_fuzzy = socket_name.lower()
    socket_spaces = socket_name_fuzzy.replace("_", " ")

    count = 0
    for socket in sockets:
        name_lower = socket.name.lower()
        if socket.enabled and (
            name_lower == socket_spaces or name_lower == socket_name_fuzzy
        ):
            if count == index:
                return socket
            count += 1

    enabled = [s.name for s in sockets if s.enabled]
    disabled = [s.name for s in sockets if not s.enabled]

    if any(d.lower() == socket_spaces for d in disabled):
        raise ValueError(
            f"User attempted to use input {socket_name.lower()!r} for node {debug_node_name} but it is disabled. "
            "We may have failed to set the node's `data_type` or `mode` input arguments"
        )

    raise ValueError(
        f"Node input {debug_node_name} has no enabled output socket "
        f"which fuzzmatches {socket_name=} {index=}, sockets were {enabled=} and {disabled=}"
    )


def get_input_socket_to_connect_to(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    socket_id: tuple[str, int] | str,
    input_val: bpy.types.NodeSocket | bpy.types.Node | Any | None,
) -> bpy.types.NodeSocket:
    assert isinstance(node_tree, bpy.types.NodeTree), node_tree

    if isinstance(socket_id, tuple):
        socket_name, socket_index = socket_id
    elif isinstance(socket_id, str):
        socket_name = socket_id
        socket_index = 0
    else:
        raise ValueError(f"Invalid socket id {socket_id=}")

    socket = get_nth_socket(node.inputs, socket_name, socket_index, node.name)
    assert socket is not None, f"Node {node.name=} has no input {socket_name=}"

    return socket


def assign_default_value(
    target_socket: bpy.types.NodeSocket,
    input_val: Any,
    data_type: bni.NodeDataType | None = None,
):
    if input_val is None:
        return

    if data_type is None:
        data_type = bni.SOCKET_DTYPE_TO_DATATYPE[bni.SocketDType(target_socket.type)]

    assert not isinstance(input_val, nt.ProcNode), input_val
    assert isinstance(data_type, bni.NodeDataType), data_type

    match data_type:
        case bni.NodeDataType.RGBA:
            if len(input_val) == 3:
                input_val = (input_val[0], input_val[1], input_val[2], 1.0)
            assert not any(isinstance(x, nt.ProcNode) for x in input_val), input_val
            target_socket.default_value = input_val
        case bni.NodeDataType.FLOAT_VECTOR:
            if hasattr(input_val, "__len__") and len(input_val) == 3:
                input_val = (input_val[0], input_val[1], input_val[2])
            assert not any(isinstance(x, nt.ProcNode) for x in input_val), input_val
            target_socket.default_value = t.Vector(input_val)
        case bni.NodeDataType.FLOAT:
            target_socket.default_value = float(input_val)
        case (
            bni.NodeDataType.OBJECT
            | bni.NodeDataType.MATERIAL
            | bni.NodeDataType.COLLECTION
        ):
            if isinstance(input_val, (t.Object, t.Material, t.Collection)):
                target_socket.default_value = input_val.item()
            else:
                target_socket.default_value = input_val
        case _:
            with add_exception_context_msg(
                prefix=f"While assigning {input_val=} to {target_socket.name=} with specified {data_type=}"
            ):
                target_socket.default_value = input_val
