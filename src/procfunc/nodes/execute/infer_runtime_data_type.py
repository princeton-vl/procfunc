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
    # named/typed version of None to be used with _infer_value_math_type.
    # `length` is the tuple/list length when known (used to disambiguate
    # 4-tuples as RGBA vs 3-tuples as FLOAT_VECTOR).
    length: int | None = None


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
    elif (st := bni.value_type_to_socket_type(type(val))) is not None:
        res = bni.SOCKET_CLASS_TO_DATATYPE[st.value]
    elif isinstance(val, (list, tuple, np.ndarray)):
        return VectorLike(length=len(val))
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
    vectorlike_options: list[bni.NodeDataType] | None = None,
) -> bni.NodeDataType:
    # kwargs keys may be tuple socket ids like ("A", 0); match on the name part
    def _key_name(k):
        return k[0] if isinstance(k, tuple) else k

    filtered_keys = [
        k
        for k in node.kwargs.keys()
        if filter_keys is None or _key_name(k) in filter_keys
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

    # A 4-component tuple/list is an RGBA color, so prefer RGBA when the node
    # offers it; otherwise fall back to its first vector-like type.
    has_length4 = any(
        isinstance(v, VectorLike) and v.length == 4 for v in input_data_types
    )
    vectorlike_options = vectorlike_options or []
    if has_length4 and bni.NodeDataType.RGBA in vectorlike_options:
        vectorlike_default = bni.NodeDataType.RGBA
    else:
        vectorlike_default = vectorlike_options[0] if vectorlike_options else None

    if len(specific_types) == 0 and len(input_data_types) > 0:
        if vectorlike_default is None:
            # we had ALL VectorLike
            raise NotImplementedError(
                f"Need to handle case where all arguments to {node=} are non-type-specific tuples/lists. Potentially just assume Vector?"
            )
        if has_length4 and vectorlike_default is bni.NodeDataType.FLOAT_VECTOR:
            raise ValueError(
                f"{node=} got a length-4 tuple/list but only FLOAT_VECTOR (a "
                "3-component type) is available here; this node has no RGBA/4-component "
                "data type. Pass a 3-tuple or use pf.Color/.astype to disambiguate."
            )
        return vectorlike_default

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

    data_type = infer_operation_type(
        node,
        input_results,
        coerce_integers,
        filter_keys=resolve_options.dependent_input_names,
        vectorlike_options=vectorlike_options,
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
    # Others use the SocketType naming convention; a single NodeDataType may
    # have several SocketDType spellings (e.g. RGBA is "FLOAT_COLOR" on
    # FunctionNodeRandomValue but "RGBA" elsewhere), so try them all.
    socket_dtype_aliases = [
        sdt.value
        for sdt, mapped in bni.SOCKET_DTYPE_TO_DATATYPE.items()
        if mapped is data_type
    ]
    for alias in socket_dtype_aliases:
        if alias in data_type_options:
            return alias
    # attribute nodes spell rotation/matrix differently from any SocketDType
    as_attr_type = bni.DATATYPE_TO_ATTRIBUTE_TYPE.get(data_type)
    if as_attr_type is not None and as_attr_type.value in data_type_options:
        return as_attr_type.value
    raise ValueError(
        f"Failed resolve {data_type=}, {socket_dtype_aliases=} or {as_attr_type=} "
        f"to an available {data_type_options=} for {bl_node=} {attr_key=}"
    )
