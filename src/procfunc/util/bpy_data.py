"""Bound bpy.data growth by removing datablocks created inside a block."""

from collections.abc import Iterator
from contextlib import contextmanager

import bpy

# session/UI-owned collections, never test content
_NON_CONTENT = frozenset({"libraries", "screens", "window_managers", "workspaces"})


def _collection_names() -> list[str]:
    return [
        prop.identifier
        for prop in bpy.data.bl_rna.properties
        if prop.type == "COLLECTION" and prop.identifier not in _NON_CONTENT
    ]


@contextmanager
def removing_new_datablocks() -> Iterator[None]:
    """Remove every content datablock (objects, materials, node groups,
    images, scenes, ...) created inside the block. The active scene is never
    removed: bpy requires one scene, and removing the active one mid-session
    is unsafe. Suitable as a per-test cleanup fixture, here and downstream.
    """
    names = _collection_names()
    before = {name: set(getattr(bpy.data, name)) for name in names}
    try:
        yield
    finally:
        doomed = []
        for name in names:
            new = set(getattr(bpy.data, name)) - before[name]
            if name == "scenes":
                new.discard(bpy.context.scene)
            doomed.extend(new)
        if doomed:
            bpy.data.batch_remove(doomed)
