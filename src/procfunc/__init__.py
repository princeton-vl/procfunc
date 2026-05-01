# ruff: noqa: I001, F401
# ensure this gets imported first so that mathutils etc is available even if later modules dont import bpy
import bpy

__version__ = "0.30.2"

from numpy.random import Generator as RNG

# ensure these are always imported first and in the right order
import bpy as _bpy
import mathutils as _mu

from . import (
    compute_graph,
    control,
    nodes,
    ops,
    random,
    tracer,
    util,
    context,
    color,
    transforms,
)
from .types import (
    Vector,
    Color,
    Euler,
    Quaternion,
    Matrix,
    BVHTree,
    Object,
    CameraObject,
    MeshObject,
    CurveObject,
    VolumeObject,
    EmptyObject,
    ArmatureObject,
    HairObject,
    LatticeObject,
    LightObject,
    LightProbeObject,
    MetaObject,
    Material,
    Texture,
    Collection,
    Image,
    ViewLayer,
    Asset,
    World,
)
from .nodes import ProcNode, Shader, NodeDataType
from .tracer import trace, autowrap_module, add_search_scope
from .util.manifest import module_path

autowrap_module(random)
autowrap_module(color)
add_search_scope(nodes)
add_search_scope(ops)

__all__ = [
    # Subpackages
    "compute_graph",
    "control",
    "context",
    "color",
    "nodes",
    "ops",
    "random",
    "tracer",
    "transforms",
    "util",
    # Node graph primitives
    "ProcNode",
    "Shader",
    "NodeDataType",
    # Tracing entrypoints
    "trace",
    # Utilities
    "RNG",
    "module_path",
    # NOTE: Blender wrapper types (Object, MeshObject, Material, Texture, ...)
    # are re-exported above for convenience but live in procfunc.types — see
    # that page for documentation. Blender/mathutils re-exports (Vector, Color,
    # Euler, Quaternion, Matrix, BVHTree, NodeGroup, Scene, ViewLayer) are
    # likewise kept importable but documented upstream by Blender.
]
