from pandas import read_json as _read_json

from procfunc.tracer import autowrap_module as _autowrap
from procfunc.util.manifest import module_path

from . import compositor, func, geo, math, shader
from .bpy_node_info import NodeDataType, NodeGroupType, SocketType

# ruff: noqa: E402
_autowrap(compositor, allow_exec=False)
_autowrap(func, allow_exec=False)
_autowrap(geo, allow_exec=False)
_autowrap(math, allow_exec=False)
_autowrap(shader, allow_exec=False)

from .execute.execute import (
    as_nodegroup,
    to_aliases,
    to_compositor,
    to_curve_object,
    to_environment,
    to_light,
    to_mesh_object,
    to_mesh_object_with_attributes,
    to_objects_multi,
)
from .execute.util import NODE_OPERATOR_TABLE
from .node_function import node_function
from .types import (
    ProcNode,
    Shader,
    SocketOrVal,
)

NODES_MANIFEST_PATH = module_path() / "nodes" / "manifest.json"
assert NODES_MANIFEST_PATH.exists(), f"Manifest not found at {NODES_MANIFEST_PATH}"
NODES_MANIFEST = _read_json(NODES_MANIFEST_PATH)

__all__ = [
    # Node category submodules
    "compositor",
    "func",
    "geo",
    "math",
    "shader",
    # Core types
    "ProcNode",
    "Shader",
    "SocketOrVal",
    "NodeDataType",
    "NodeGroupType",
    "SocketType",
    # Graph execution
    "as_nodegroup",
    "to_aliases",
    "to_compositor",
    "to_curve_object",
    "to_environment",
    "to_light",
    "to_material",
    "to_mesh_object",
    "to_mesh_object_with_attributes",
    "to_objects_multi",
    # User-facing decorator for custom node functions
    "node_function",
]
