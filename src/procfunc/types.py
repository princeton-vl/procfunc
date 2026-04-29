import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, NamedTuple, TypeAlias, TypeVar

import bpy
import mathutils

from procfunc.util.pytree import register_pytree_container

T = TypeVar("T")

logger = logging.getLogger(__name__)

__all__ = [
    "Asset",
    "BlenderAsset",
    "ObjectType",
    "Object",
    "CameraObject",
    "MeshObject",
    "CurveObject",
    "EmptyObject",
    "ArmatureObject",
    "HairObject",
    "LatticeObject",
    "LightObject",
    "LightProbeObject",
    "MetaObject",
    "Material",
    "Texture",
    "Image",
    "Collection",
    "VolumeObject",
    "PointCloudObject",
    "World",
    "ValueRange",
]

INVALIDATED_USAGE_ID = -100


@dataclass
class AssetUsageTable:
    counts: dict[int, int] = field(default_factory=lambda: defaultdict(int))


_global_usage_table = AssetUsageTable()


def _bpy_data_col_for_asset(item: T) -> bpy.types.bpy_prop_collection:
    match item.bl_rna.name:
        case "Object":
            return bpy.data.objects
        case "Material":
            return bpy.data.materials
        case "Image Texture":
            return bpy.data.textures
        case _:
            raise TypeError(
                f"{BlenderAsset.__name__} doesnt yet support: {item} with type {item.bl_rna.name}"
            )


class Asset(Generic[T]):
    def item(self) -> T:
        raise NotImplementedError("Subclasses of Asset must implement item()")


class BlenderAsset(Asset, Generic[T]):
    """
    A pythonic wrapper around a blender object,material,texture, or other bpy.data.stuffgoeshere member.

    We reference count the underlying asset and delete it when no python references remain.
    """

    def __init__(self, item: T):
        if isinstance(item, Asset):
            raise ValueError(
                f"Attempted to wrap {item=} in a second {self.__class__.__name__} wrapper. This is almost certainly not intended"
            )

        self._item = item
        _global_usage_table.counts[id(item)] += 1
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Asset ref {id(self)} created for {self._item.name}. remaining refs: {_global_usage_table.counts[id(self._item)]}"
            )

        # self._dependencies: list[Asset] = []

    def item(self) -> T:
        if _global_usage_table.counts[id(self._item)] == INVALIDATED_USAGE_ID:
            raise ValueError(
                "Cant access .item() since asset has been explicitly invalidated by a previous operation"
            )

        return self._item


'''
    def add_dependency(self, dependency: "Asset"):
        self._dependencies.append(dependency)

    def extend_dependencies(self, other: "Asset"):
        self._dependencies.extend(other._dependencies)

    def update(self, other: "Asset"):
        """
        Updates this asset to point to the same underlying item as other.
        """

        self._item = other._item
        self._dependencies = other._dependencies
        _global_usage_table.counts[id(self._item)] += 1

    def invalidate(self):
        self._item = None
        self._dependencies = []
        _global_usage_table.counts[id(self._item)] = INVALIDATED_USAGE_ID

    def __del__(self):
        # return

        if self._item is None:
            return
        return  # TODO
        item_id = id(self._item)
        count = _global_usage_table.counts.get(item_id, 0)

        count -= 1

        # new bad ref counter
        if count < 0:
            raise ValueError(
                f"Asset ref {id(self)} reached negative ref count for item {self._item.name}"
            )

        _global_usage_table.counts[item_id] = count

        if count == 0:
            try:
                bpy_col = _bpy_data_col_for_asset(self._item)
                if self._item.name in bpy_col:
                    bpy_col.remove(self._item, do_unlink=True)
            except ReferenceError:
                logger.warning(
                    f"{self.__class__.__name__} __del__ failed - item already deleted"
                )

            del _global_usage_table.counts[item_id]

        self._item = None
'''


class ObjectType(Enum):
    ARMATURE = "ARMATURE"
    CAMERA = "CAMERA"
    CURVE = "CURVE"
    EMPTY = "EMPTY"
    FONT = "FONT"
    HAIR = "HAIR"
    LATTICE = "LATTICE"
    LIGHT = "LIGHT"
    LIGHT_PROBE = "LIGHT_PROBE"
    MESH = "MESH"
    META = "META"
    POINTCLOUD = "POINTCLOUD"
    SURFACE = "SURFACE"
    VOLUME = "VOLUME"
    # GPENCIL = "GPENCIL"
    # GREASEPENCIL = "GREASEPENCIL"
    # SPEAKER = "SPEAKER"


Vector: TypeAlias = mathutils.Vector
Color: TypeAlias = mathutils.Color
Euler: TypeAlias = mathutils.Euler
Quaternion: TypeAlias = mathutils.Quaternion
Matrix: TypeAlias = mathutils.Matrix
BVHTree: TypeAlias = mathutils.bvhtree.BVHTree

NodeGroup: TypeAlias = bpy.types.NodeGroup
Scene: TypeAlias = bpy.types.Scene
ViewLayer: TypeAlias = bpy.types.ViewLayer


class Object(BlenderAsset[bpy.types.Object]):
    def __init__(self, obj: bpy.types.Object):
        assert isinstance(obj, bpy.types.Object)
        super().__init__(obj)

    def __repr__(self):
        return f"pf.{self.__class__.__name__}(bpy.data.objects[{self._item.name!r}])"

    def clone(self):
        new_obj = self._item.copy()
        new_obj.data = self._item.data.copy()
        bpy.context.collection.objects.link(new_obj)
        return self.__class__(new_obj)


class CameraObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.CAMERA.value
        super().__init__(obj)


class MeshObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.MESH.value
        super().__init__(obj)

        if len(obj.children) > 0:
            raise ValueError(
                f"MeshObject {obj.name} had children {obj.children}, but this is not allowed for {self.__class__.__name__}"
            )
        if obj.parent is not None:
            logger.warning(f"MeshObject {obj.name} had a parent {obj.parent}")


class CurveObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.CURVE.value
        super().__init__(obj)


class EmptyObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.EMPTY.value
        super().__init__(obj)


class ArmatureObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.ARMATURE.value
        super().__init__(obj)


class HairObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.HAIR.value
        super().__init__(obj)


class LatticeObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.LATTICE.value
        super().__init__(obj)


class LightObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.LIGHT.value
        super().__init__(obj)


class LightProbeObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.LIGHT_PROBE.value
        super().__init__(obj)


class MetaObject(Object):
    def __init__(self, obj: bpy.types.Object):
        assert obj.type == ObjectType.META.value
        super().__init__(obj)


@dataclass
class Material:
    surface: Any = None
    displacement: Any = None
    volume: Any = None
    _bpy_material: Any = field(default=None, init=False, repr=False)

    def item(self) -> bpy.types.Material:
        if self._bpy_material is None:
            from procfunc.nodes.execute.execute import _build_bpy_material

            self._bpy_material = _build_bpy_material(
                surface=self.surface,
                displacement=self.displacement,
                volume=self.volume,
            )
        return self._bpy_material


class Texture(BlenderAsset[bpy.types.Texture]):
    def __init__(self, tex: bpy.types.Texture):
        assert isinstance(tex, bpy.types.Texture)
        super().__init__(tex)


class Image(BlenderAsset[bpy.types.Image]):
    def __init__(self, img: bpy.types.Image):
        assert isinstance(img, bpy.types.Image)
        super().__init__(img)


class Collection:
    def __init__(
        self, objects: "list[Object] | bpy.types.Collection", name: str = "collection"
    ):
        if isinstance(objects, bpy.types.Collection):
            self._collection = objects
            self._objects = [Object(o) for o in objects.objects]
        else:
            self._objects = objects
            self._collection = bpy.data.collections.new(name=name)
            for obj in objects:
                self._collection.objects.link(obj.item())

    def __repr__(self):
        return f"pf.Collection(bpy.data.collections[{self._collection.name!r}])"

    def map(
        self,
        fn: Callable[[Object], Object],
        skip_none: bool = True,
    ) -> "Collection":
        objs = []
        for obj in self._objects:
            result = fn(obj)
            if result is None and skip_none:
                continue
            objs.append(result)
        return Collection(objs, name=self._collection.name + "_" + fn.__name__)

    def __len__(self):
        return len(self._objects)

    def __iter__(self):
        return iter(self._objects)

    def item(self) -> bpy.types.Collection:
        return self._collection


class VolumeObject(BlenderAsset[bpy.types.Volume]):
    def __init__(self, vol: bpy.types.Volume):
        assert isinstance(vol, bpy.types.Volume)
        super().__init__(vol)


class PointCloudObject(BlenderAsset[bpy.types.PointCloud]):
    def __init__(self, vol: bpy.types.PointCloud):
        assert isinstance(vol, bpy.types.PointCloud)
        super().__init__(vol)


class World(BlenderAsset[bpy.types.World]):
    def __init__(self, world: bpy.types.World):
        assert isinstance(world, bpy.types.World)
        super().__init__(world)

    def __del__(self):
        pass  # no cleanup for these


# TODO Font, PointCloud, Surface, Volume, Scene? World? ViewLayer?

TRangeType = TypeVar("TRangeType")


class ValueRange(NamedTuple, Generic[TRangeType]):
    min: TRangeType | None
    max: TRangeType | None


register_pytree_container(
    Material,
    flatten_func=lambda m: ([m.surface, m.displacement, m.volume], None),
    unflatten_func=lambda vals, _: Material(
        surface=vals[0], displacement=vals[1], volume=vals[2]
    ),
    names_func=lambda m: ["surface", "displacement", "volume"],
)
