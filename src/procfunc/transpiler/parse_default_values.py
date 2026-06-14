from typing import Any

import bpy
import idprop.types
import numpy as np

from procfunc import types as t

# TODO replace with nodes/types.py or bpy_info.py?
SUBCOMPONENT_TYPES = (
    bpy.types.Material,
    bpy.types.Object,
    bpy.types.Collection,
    bpy.types.Image,
    bpy.types.Texture,
)


def normalize_default_value(value: Any, socket_type: str) -> Any:
    if isinstance(value, SUBCOMPONENT_TYPES):
        return value.name
    elif socket_type == "RGBA":
        if len(value) >= 4 and value[3] != 1.0:
            return tuple(value)
        return tuple(value[:3])
    elif isinstance(value, t.Matrix):
        # matrix values are carried as numpy arrays in the compute graph
        # (float32, matching socket storage)
        return np.array(value, dtype=np.float32)
    elif isinstance(value, (bpy.types.bpy_prop_array, t.Vector, t.Euler, t.Quaternion)):
        return tuple(value)
    elif isinstance(value, idprop.types.IDPropertyArray):
        return tuple(value)
    else:
        return value
