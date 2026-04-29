import logging
from dataclasses import dataclass
from typing import Any

import bpy
import numpy as np

from procfunc import compute_graph as cg
from procfunc.nodes import bpy_node_info as bni
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import (
    RuntimeResolveDataType,
)

logger = logging.getLogger(__name__)


@dataclass
class VectorLike:
    # named/typed version of None to be used with _infer_value_math_type
    pass


def _infer_value_math_type(
    val: bpy.types.NodeSocket | Any,
    py_input: cg.Node | Any,
    coerce_integers: bool = False,
) -> bni.NodeDataType | VectorLike | None:
    """
    What data type of math should we do on this `val`?

    Args:
        val: The value to infer the data type of
        coerce_integers: Whether to coerce integers to floats. Usually used only for shader context, since bl4.2 shaders dont support integer math

    Returns:
        bni.NodeDataType: The data type of math to do on this `val`
        VectorLike: The argument is vaguely vector-like, but we leave it up to other vals to decide between Vector Color etc.
    """

    assert not isinstance(py_input, nt.ProcNode), py_input

    logger.debug(
        f"{_infer_value_math_type.__name__} starting for {type(val)=} {py_input=} {type(py_input)=}"
    )

    if (
        isinstance(py_input, cg.Node)
        and (vt := py_input.metadata.get("known_value_type", None)) is not None
    ):
        socket_type = bni.PYTHON_TYPE_TO_SOCKET_TYPE[vt]
        res = bni.SOCKET_CLASS_TO_DATATYPE[socket_type.value]
        logger.debug(f"used known_value_type={vt} from {py_input=} to infer {res=}")
    elif isinstance(val, bpy.types.NodeSocket):
        res = bni.SOCKET_DTYPE_TO_DATATYPE[bni.SocketDType(val.type)]
        logger.debug(f"used {val.type=} to infer {res=}")
    elif type(val) in bni.PYTHON_TYPE_TO_SOCKET_TYPE:
        res = bni.PYTHON_TYPE_TO_SOCKET_TYPE[type(val)]
        res = bni.SOCKET_CLASS_TO_DATATYPE[res.value]
    elif isinstance(val, (list, tuple, np.ndarray)):
        return VectorLike()
    elif val is None:
        return None
    else:
        raise ValueError(
            f"{_infer_value_math_type.__name__} got {val=} of type {type(val)} "
            f"which is not handled by either {bni.PYTHON_TYPE_TO_SOCKET_TYPE.keys()} "
            f"or {bni.SOCKET_DTYPE_TO_DATATYPE.keys()}"
        )

    if coerce_integers and res == bni.NodeDataType.INT:
        res = bni.NodeDataType.FLOAT

    return res


_vectorlike_types = {bni.NodeDataType.FLOAT_VECTOR, bni.NodeDataType.RGBA}


def infer_operation_type(
    node: cg.Node,
    inputs: dict[str | int, Any],
    coerce_integers: bool,
    filter_keys: list[str] | None = None,
    vectorlike_default: bni.NodeDataType | None = None,
) -> bni.NodeDataType:
    filtered_keys = [
        k for k in node.kwargs.keys() if filter_keys is None or k in filter_keys
    ]
    input_data_types: list[bni.NodeDataType | VectorLike] = [
        _infer_value_math_type(inputs[k], node.kwargs[k], coerce_integers)
        for k in filtered_keys
    ]

    input_data_types.extend(
        [
            _infer_value_math_type(inputs[i], arg, coerce_integers)
            for i, arg in enumerate(node.args)
        ]
    )

    specific_types = [
        v for v in input_data_types if not isinstance(v, VectorLike) and v is not None
    ]

    if len(specific_types) == 0 and len(input_data_types) > 0:
        if vectorlike_default is not None:
            return vectorlike_default
        # we had ALL VectorLike
        raise NotImplementedError(
            f"Need to handle case where all arguments to {node=} are non-type-specific tuples/lists. Potentially just assume Vector?"
        )

    data_type = specific_types[0]

    if any(v != data_type for v in specific_types[1:]):
        dtypes_msg = " ".join([str(v) for v in input_data_types])
        raise ValueError(
            f"Attempted to create operator with non-matching input types {dtypes_msg}. "
            f"Need to use .astype to hint to make arg types match a single operation datatype, e.g. .astype(float) or .astype(pf.Color)"
        )

    if (
        len(specific_types) > 0
        and any(isinstance(v, VectorLike) for v in specific_types)
        and data_type not in [bni.NodeDataType.FLOAT_VECTOR, bni.NodeDataType.RGBA]
    ):
        raise ValueError(
            f"{input_data_types=} has compatibile types EXCEPT that {data_type=} "
            "is not compatible with unspecified tuples/lists (shown as VectorLike)."
        )

    logger.debug(f"inferred {data_type=} for {node=}")

    return data_type


_vectorlike_types = {bni.NodeDataType.FLOAT_VECTOR, bni.NodeDataType.RGBA}


def resolve_operation_data_type(
    node: cg.Node,
    input_results: dict[str | int, Any],
    resolve_options: RuntimeResolveDataType,
    coerce_integers: bool,
) -> bni.NodeDataType:
    vectorlike_options = [
        o for o in resolve_options.data_types if o in _vectorlike_types
    ]
    vectorlike_default = vectorlike_options[0] if len(vectorlike_options) > 0 else None

    data_type = infer_operation_type(
        node,
        input_results,
        coerce_integers,
        filter_keys=resolve_options.dependent_input_names,
        vectorlike_default=vectorlike_default,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            f"{resolve_operation_data_type.__name__} for {node=} inferred {data_type=}"
        )

    return data_type


def map_data_type_for_differing_node_interface(
    data_type: bni.NodeDataType,
    bl_node: bpy.types.Node,
    attr_key: str,
) -> str:
    """
    As of bl4.2, some nodes use differing sets of strings to specify data types.Any

    We look at the options to pick which convention to UserWarning

    NOTE: this may one day become unnecessary in future blender versions,
        but this function will end up silently always doing the same option
    """

    data_type_options: list[str] = list(
        bl_node.bl_rna.properties[attr_key].enum_items.keys()
    )
    if data_type.value in data_type_options:
        # MapRange seems to use the DataType naming convention
        return data_type.value
    as_socket_dtype = bni.DATATYPE_TO_SOCKET_DTYPE[data_type]
    if as_socket_dtype.value in data_type_options:
        # wheras others e.g. Mix use the SocketType naming convention
        return as_socket_dtype.value
    raise ValueError(
        f"Failed resolve {data_type=} or {as_socket_dtype=} to an available {data_type_options=} "
        f"for {bl_node=} {attr_key=}"
    )
