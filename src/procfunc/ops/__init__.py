from pandas import read_json as _read_json

from procfunc.nodes.util.bpy_versioning import bpy_version as _bpy_version
from procfunc.tracer import autowrap_module as _autowrap
from procfunc.util.manifest import filter_manifest_by_bpy_version as _filter_by_version
from procfunc.util.manifest import module_path

from . import (
    attr,
    collection,
    curve,
    file,
    mesh,
    modifier,
    object,
    primitives,
    uv,
)

_autowrap(collection)
_autowrap(attr)
_autowrap(curve)
_autowrap(primitives)

OPS_MANIFEST_PATH = module_path() / "ops" / "manifest.json"
OPS_MANIFEST = _filter_by_version(_read_json(OPS_MANIFEST_PATH), _bpy_version())

__all__ = [
    "collection",
    "file",
    "mesh",
    "modifier",
    "object",
    "attr",
    "curve",
    "primitives",
    "uv",
]
