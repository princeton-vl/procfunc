from typing import Callable, List, Optional

import bpy

import procfunc as pf
from procfunc import types as t


def _new_collection(name: str, reuse: bool = True) -> t.Collection:
    """Create a new collection or reuse existing one with the same name."""
    if reuse and name in bpy.data.collections:
        return t.Collection(bpy.data.collections[name])
    else:
        col = bpy.data.collections.new(name=name)
        bpy.context.scene.collection.children.link(col)
        return t.Collection(col)


def _unlink_from_all(obj: bpy.types.Object) -> None:
    """Remove object from all collections."""
    for c in list(bpy.data.collections) + [bpy.context.scene.collection]:
        if obj.name in c.objects:
            c.objects.unlink(obj)


def _link_to_collection(
    objs: bpy.types.Object | List[bpy.types.Object],
    collection: bpy.types.Collection | str,
    exclusive: bool = True,
) -> t.Collection:
    """Link objects to a collection."""
    if isinstance(collection, str):
        collection = _new_collection(collection)

    if isinstance(objs, bpy.types.Object):
        objs = [objs]
    else:
        objs = list(objs)

    for o in objs:
        if exclusive:
            _unlink_from_all(o)
        collection.objects.link(o)  # type: ignore

    return collection


def _traverse_children(
    obj: bpy.types.Object,
    fn: Callable[[bpy.types.Object], None],
):
    """Recursively traverse object children."""
    fn(obj)
    for child in obj.children:
        _traverse_children(child, fn)


@pf.tracer.primitive
def group_objects(
    *args: t.Object | t.Object | List[t.Object | t.Object],
    name: Optional[str] = None,
) -> t.Collection:
    """Create a collection containing the specified objects and their children.

    Args:
        *args: Objects or lists of objects to include
        name: Name of the collection

    Returns:
        Collection containing all objects
    """
    if name is None:
        name = "Generated Collection"

    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)

    for obj in args:
        if obj is None:
            continue
        if isinstance(obj, list):
            for o in obj:
                if o is not None:
                    _traverse_children(o.item(), lambda o: _link_to_collection(o, col))
        elif isinstance(obj, t.Object):
            _traverse_children(obj.item(), lambda o: _link_to_collection(o, col))
        else:
            raise ValueError(f"Invalid object type: {type(obj)}")

    return t.Collection(col)
