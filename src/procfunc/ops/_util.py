import logging
from typing import Any, Callable, Literal, TypeVar

import bpy
import numpy as np

from procfunc import types as t
from procfunc.util.bpy_info import bpy_nocollide_data_name

logger = logging.getLogger(__name__)


def _parse_objs(
    objs: t.Object | list[t.Object] | None, active: t.Object | None
) -> tuple[list[bpy.types.Object], bpy.types.Object]:
    if objs is None:
        assert active is not None
        objs = [active.item()]
    elif isinstance(objs, t.Object):
        objs = [objs.item()]
    elif isinstance(objs, list):
        objs = [obj.item() for obj in objs]
    else:
        raise TypeError(f"Unexpected type for objs: {type(objs)}")

    if active is None:
        assert len(objs) > 0
        active = objs[0]
    elif isinstance(active, t.Asset):
        active = active.item()

    if active not in objs:
        objs.append(active)

    assert active is not None
    assert len(objs) > 0
    assert not isinstance(active, t.Asset)

    return objs, active


def _assert_op_finished(result: Any, name: str):
    if (
        not isinstance(result, set)
        or len(result) != 1
        or next(iter(result)) != "FINISHED"
    ):
        raise ValueError(f"{name} got status {result}, expected {'FINISHED'}")


def execute_object_op(
    operator: Callable,
    objs: t.Object | list[t.Object] | None = None,
    active: t.Object | None = None,
    description: str = "",
    **kwargs: Any,
):
    assert not isinstance(active, bpy.types.Object)

    kwargs = {k: v.item() if isinstance(v, t.Asset) else v for k, v in kwargs.items()}

    objs, active = _parse_objs(objs, active)

    # TODO: more efficient via temp_override?
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = active
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in objs:
        o.select_set(True)

    result = operator(**kwargs)
    _assert_op_finished(result, description)


def _apply_selection_masks(
    obj: bpy.types.Object,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
):
    """
    Apply one selection mask of some domain to the object

    If no masks are provided, all elements of the domain are selected.

    NOTE: function must start AND end in EDIT mode
    """

    n_masks = sum(mask is not None for mask in [vertex_mask, edge_mask, face_mask])

    if n_masks == 0:
        logger.debug(f"No edit-masks provided for {obj.name}, selecting all")
        bpy.ops.mesh.select_all(action="SELECT")
        return
    if n_masks > 1:
        raise ValueError(
            "Only one of vertex_mask, edge_mask, or face_mask can be provided"
        )

    bpy.ops.mesh.select_all(action="DESELECT")

    # must select the type of mask we're applying, otherwise re-entering editmode will incorrectly
    # convert face/edge masks into vertex masks, which is lossy.
    select_type = (
        "VERT"
        if vertex_mask is not None
        else "EDGE"
        if edge_mask is not None
        else "FACE"
    )
    bpy.ops.mesh.select_mode(type=select_type)

    # foreach_set operations must run in object mode then switch back to edit mode to re-sync them
    bpy.ops.object.mode_set(mode="OBJECT")

    if vertex_mask is not None:
        assert vertex_mask.shape == (len(obj.data.vertices),)
        assert vertex_mask.dtype == bool
        obj.data.vertices.foreach_set("select", vertex_mask)

    if edge_mask is not None:
        assert edge_mask.shape == (len(obj.data.edges),)
        assert edge_mask.dtype == bool
        obj.data.edges.foreach_set("select", edge_mask)

    if face_mask is not None:
        assert face_mask.shape == (len(obj.data.polygons),)
        assert face_mask.dtype == bool
        obj.data.polygons.foreach_set("select", face_mask)

    bpy.ops.object.mode_set(mode="EDIT")


def extract_face_mask(
    obj: t.MeshObject,
) -> np.ndarray:
    obj = obj.item()
    face_mask = np.zeros(len(obj.data.polygons), dtype=bool)
    obj.data.polygons.foreach_get("select", face_mask)
    return face_mask


def extract_edge_mask(
    obj: t.MeshObject,
) -> np.ndarray:
    obj = obj.item()
    edge_mask = np.zeros(len(obj.data.edges), dtype=bool)
    obj.data.edges.foreach_get("select", edge_mask)
    return edge_mask


def extract_vertex_mask(
    obj: t.MeshObject,
) -> np.ndarray:
    obj = obj.item()
    vertex_mask = np.zeros(len(obj.data.vertices), dtype=bool)
    obj.data.vertices.foreach_get("select", vertex_mask)
    return vertex_mask


def execute_mesh_op(
    operator: Callable,
    obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    empty_mask_mode: Literal["return", "execute", "error"] = "return",
    description: str = "",
    **kwargs: Any,
):
    obj = obj.item()

    logger.debug(f"Executing {operator} on {obj.name=}")

    empty_mask = next(
        (
            mask
            for mask in [vertex_mask, edge_mask, face_mask]
            if mask is not None and mask.sum() == 0
        ),
        None,
    )
    if empty_mask is not None and empty_mask_mode == "error":
        raise ValueError(
            f"Empty mask provided for {operator} on {obj.name=} with {empty_mask_mode=}"
        )

    # TODO: would rather do this with context overrides,
    #   but it messes up the active_object for cases like ops.mesh.separate()
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(True)

    bpy.ops.object.mode_set(mode="EDIT")
    _apply_selection_masks(obj, vertex_mask, edge_mask, face_mask)

    try:
        if empty_mask is not None:
            if empty_mask_mode == "return":
                return
            elif empty_mask_mode == "execute":
                pass
            elif empty_mask_mode == "error":
                raise ValueError(
                    f"Empty mask provided for {operator} on {obj.name=} with {empty_mask_mode=}"
                )
            else:
                raise ValueError(f"Invalid empty_mask_mode: {empty_mask_mode}")

        result = operator(**kwargs)
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")

    _assert_op_finished(result, description)

    return result


TModifyObject = TypeVar("TModifyObject", t.MeshObject, t.CurveObject)


def modify(
    obj: TModifyObject,
    modifier_type: str,
    setitem_keyvals: dict[str, Any] | None = None,
    _skip_apply: bool = False,
    **setattr_keyvals: Any,
) -> TModifyObject:
    if setitem_keyvals is None:
        setitem_keyvals = {}

    mod_name = bpy_nocollide_data_name(modifier_type, obj.item().modifiers)
    modifier = obj.item().modifiers.new(mod_name, modifier_type)
    if modifier is None:
        raise ValueError(
            "modifier.new() returned None, blender might not allow "
            f"{modifier_type=} for {obj.item().type=}"
        )
    modifier.show_viewport = False

    for key, value in setitem_keyvals.items():
        assert not isinstance(value, t.Asset), (
            "TODO may need to conver Assets to item for modifier[x] = y"
        )
        modifier[key] = value

    objs = []
    for key, value in setattr_keyvals.items():
        if isinstance(value, t.Object):
            objs.append(value)
        if isinstance(value, t.Asset):
            value = value.item()

        if hasattr(modifier, key):
            setattr(modifier, key, value)
        else:
            raise AttributeError(f"Modifier {modifier_type} has no attribute {key}")

    if _skip_apply:
        return obj

    execute_object_op(
        bpy.ops.object.modifier_apply,
        objs=objs,
        active=obj,
        modifier=modifier.name,
    )

    if mod_name in obj.item().modifiers:
        raise ValueError(
            f"Modifier {modifier_type} failed to execute with {setitem_keyvals=} and {setattr_keyvals=}"
        )

    return obj
