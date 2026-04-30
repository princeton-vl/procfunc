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


# Flat re-exports of node functions: pf.nodes.add instead of pf.nodes.math.add.
# Compositor stays namespaced (different bpy class hierarchy). The 6 collision
# pairs (greater_than/less_than, object_info) keep type-prefixed names.
_COLLISION_ALIASES = {
    ("math", "greater_than"): "math_greater_than",
    ("math", "less_than"): "math_less_than",
    ("func", "greater_than"): "func_greater_than",
    ("func", "less_than"): "func_less_than",
    ("geo", "object_info"): "geo_object_info",
    ("shader", "object_info"): "shader_object_info",
}
_FLAT_EXPORTS: list[str] = []
for _mod_name, _mod in [
    ("math", math),
    ("func", func),
    ("geo", geo),
    ("shader", shader),
]:
    for _attr in dir(_mod):
        if _attr.startswith("_"):
            continue
        _obj = getattr(_mod, _attr)
        if not callable(_obj):
            continue
        _flat = _COLLISION_ALIASES.get((_mod_name, _attr), _attr)
        if _flat in globals() and _flat not in _FLAT_EXPORTS:
            # Already a public name (submodule, type, helper) — skip.
            continue
        globals()[_flat] = _obj
        _FLAT_EXPORTS.append(_flat)

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
] + _FLAT_EXPORTS
