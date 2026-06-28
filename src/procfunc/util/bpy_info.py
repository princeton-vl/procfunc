import logging
from enum import Enum
from typing import Any

import bpy
import numpy as np

from procfunc import types as t

logger = logging.getLogger(__name__)


# Attribute data type dimensions
DATATYPE_DIMS = {
    "FLOAT": 1,
    "INT": 1,
    "INT8": 1,
    "FLOAT_VECTOR": 3,
    "FLOAT2": 2,
    "FLOAT_COLOR": 4,
    "BYTE_COLOR": 4,
    "RGBA": 4,
    "BOOLEAN": 1,
    "INT32_2D": 2,
    "QUATERNION": 4,
    "FLOAT4X4": 16,
}

# Attribute data type field names for foreach_get/foreach_set
DATATYPE_FIELDS = {
    "FLOAT": "value",
    "INT": "value",
    "INT8": "value",
    "FLOAT_VECTOR": "vector",
    "FLOAT2": "vector",
    "FLOAT_COLOR": "color",
    "BYTE_COLOR": "color",
    "RGBA": "color",
    "BOOLEAN": "value",
    "INT32_2D": "value",
    "QUATERNION": "value",
    "FLOAT4X4": "value",
}

# Attribute data type to Python type mapping
DATATYPE_TO_PYTYPE = {
    "INT": int,
    "FLOAT": np.float32,
    "FLOAT_VECTOR": np.float64,
    "FLOAT_COLOR": np.float32,
    "RGBA": np.float32,
    "BOOLEAN": bool,
}

# Python type to attribute data type mapping
PYTYPE_DATATYPE_TABLE = [
    (int, "INT"),
    (np.dtype(np.int32), "INT"),
    (float, "FLOAT"),
    (np.dtype(np.float32), "FLOAT"),
    (np.dtype(np.float64), "FLOAT"),
    (bool, "BOOLEAN"),
    (np.dtype(np.bool_), "BOOLEAN"),
    (t.Color, "RGBA"),
    (t.Vector, "FLOAT_VECTOR"),
    (t.Euler, "FLOAT_VECTOR"),
    (t.Quaternion, "FLOAT_VECTOR"),
    (t.Matrix, "FLOAT_VECTOR"),
]
PYTYPE_TO_DATATYPE = {k: v for k, v in PYTYPE_DATATYPE_TABLE}
DATATYPE_TO_PYTYPE = {v: k for k, v in PYTYPE_DATATYPE_TABLE}
DATATYPE_TO_PYTYPE["FLOAT2"] = np.float32
DATATYPE_TO_PYTYPE["INT8"] = np.int8
DATATYPE_TO_PYTYPE["INT32_2D"] = np.int32
DATATYPE_TO_PYTYPE["BYTE_COLOR"] = np.uint8
DATATYPE_TO_PYTYPE["QUATERNION"] = np.float32
DATATYPE_TO_PYTYPE["FLOAT4X4"] = np.float32

UNSUPPORTED_DATATYPES = {"STRING"}
UNSUPPORTED_DOMAINS = {"LAYER"}


class NodeGroupType(Enum):
    GEOMETRY = "GeometryNodeGroup"
    SHADER = "ShaderNodeGroup"
    COMPOSITOR = "CompositorNodeGroup"
    TEXTURE = "TextureNodeGroup"

    @classmethod
    def from_str(cls, s: str) -> "NodeGroupType | None":
        try:
            return cls(s)
        except ValueError:
            return None


class NodeTreeType(Enum):
    GEOMETRY = "GeometryNodeTree"
    SHADER = "ShaderNodeTree"
    COMPOSITOR = "CompositorNodeTree"
    TEXTURE = "TextureNodeTree"


NODETREE_TO_NODEGROUP = {
    NodeTreeType.GEOMETRY: NodeGroupType.GEOMETRY,
    NodeTreeType.SHADER: NodeGroupType.SHADER,
    NodeTreeType.COMPOSITOR: NodeGroupType.COMPOSITOR,
    NodeTreeType.TEXTURE: NodeGroupType.TEXTURE,
}

NODETREE_TYPE_TO_MAIN_OUTPUT = {
    NodeTreeType.GEOMETRY: "GeometryNodeOutput",
    NodeTreeType.SHADER: "ShaderNodeOutputMaterial",
    NodeTreeType.COMPOSITOR: "CompositorNodeOutput",
    NodeTreeType.TEXTURE: "TextureNodeOutput",
}

NODEGROUP_TYPE_TO_INPUT_NODE = {
    NodeGroupType.GEOMETRY: "GeometryNodeInput",
    NodeGroupType.SHADER: "ShaderNodeInput",
    NodeGroupType.COMPOSITOR: "CompositorNodeInput",
    NodeGroupType.TEXTURE: "TextureNodeInput",
}


# Blender datablock names are capped at 63 chars; reserve N hex chars + 1 separator.
BPY_NAME_CAP = 63
NOCOLLIDE_HEX_LEN = 8
NOCOLLIDE_PREFIX_LEN = BPY_NAME_CAP - 1 - NOCOLLIDE_HEX_LEN


def bpy_nocollide_data_name(
    x: Any,
    bpy_data: bpy.types.bpy_prop_collection,
) -> str:
    base = x if isinstance(x, str) else getattr(x, "name", None)
    prefix = (base[:NOCOLLIDE_PREFIX_LEN] if base else "") or "data"

    if prefix not in bpy_data:
        return prefix

    # Deterministic suffix probe (uuid4 was not reproducible); `name in bpy_data` is an
    # O(1) name lookup, and a fresh suffix is almost always free on the first try.
    i = 1
    while f"{prefix}_{i}" in bpy_data:
        i += 1
    return f"{prefix}_{i}"
