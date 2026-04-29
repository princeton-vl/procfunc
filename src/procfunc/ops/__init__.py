from pandas import read_json as _read_json

from procfunc.tracer import autowrap_module as _autowrap
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
OPS_MANIFEST = _read_json(OPS_MANIFEST_PATH)

__all__ = [
    "collection",
    "file",
    "mesh",
    "modifier",
    "object",
    "attr",
    "curve",
    "uv",
]
