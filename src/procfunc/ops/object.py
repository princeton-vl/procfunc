from typing import Literal

import bpy
import numpy as np

import procfunc as pf
from procfunc import types as t
from procfunc.ops.attr import read_attribute, write_attribute
from procfunc.util.bpy_info import bpy_nocollide_data_name

from ._util import execute_object_op


@pf.tracer.primitive(mutates=["mutates_obj"])
def set_transform(
    mutates_obj: t.MeshObject,
    location: t.Vector | tuple[float, float, float] | None = None,
    rotation_euler: t.Vector | tuple[float, float, float] | None = None,
    scale: t.Vector | tuple[float, float, float] | None = None,
):
    obj = mutates_obj.item()
    if location is not None:
        obj.location = location
    if rotation_euler is not None:
        obj.rotation_euler = rotation_euler
    if scale is not None:
        obj.scale = scale

    # Update view layer so transform affects matrix_world
    bpy.context.view_layer.update()


@pf.tracer.primitive(mutates=["mutates_obj"])
def set_material(
    mutates_obj: t.MeshObject,
    material: "pf.Material | None" = None,
    surface: "pf.ProcNode[pf.Shader] | None" = None,
    displacement: "pf.ProcNode[pf.Vector] | None" = None,
    volume: "pf.ProcNode[pf.Shader] | None" = None,
    selection: np.ndarray | None = None,
):
    """Assign a material to an object.

    Args:
        mutates_obj: Blender object to assign material to
        material: Material to assign. If None, constructs one from surface/displacement/volume.
        surface: Shader to assign to the surface.
        displacement: Vector to assign to the displacement.
        volume: Shader to assign to the volume.
        selection: Boolean array with length equal to number of faces.
                  If provided, assigns material only to selected faces.
    """

    if material is None:
        if all(x is None for x in [surface, displacement, volume]):
            raise ValueError(
                "at least one of material, surface, displacement, or volume must be provided"
            )
        material = pf.Material(
            surface=surface, displacement=displacement, volume=volume
        )

    # mutates_obj.add_dependency(material)

    obj_bpy = mutates_obj.item()

    if selection is None:
        while len(obj_bpy.material_slots) > 0:
            execute_object_op(
                operator=bpy.ops.object.material_slot_remove,
                objs=mutates_obj,
            )
            # TODO remove mutates_obj.dependencies

    orig_slots = len(obj_bpy.material_slots)
    execute_object_op(
        operator=bpy.ops.object.material_slot_add,
        objs=mutates_obj,
    )
    new_slots = len(obj_bpy.material_slots)
    assert new_slots == orig_slots + 1
    target_slot = obj_bpy.material_slots[-1]
    target_slot.material = material.item()

    if selection is None:
        return mutates_obj

    assert isinstance(selection, np.ndarray)
    assert len(selection) == len(obj_bpy.data.polygons)

    if "material_index" in obj_bpy.data.attributes:
        index_arr = read_attribute(mutates_obj, "material_index", domain="FACE")
    else:
        index_arr = np.full(len(obj_bpy.data.polygons), 0, dtype=np.int32)

    index_arr[selection] = target_slot.slot_index
    write_attribute(
        mutates_obj, index_arr, "material_index", domain="FACE", overwrite=True
    )

    return mutates_obj


def alias(obj: t.Object) -> t.Object:
    """Create a linked duplicate that shares the same mesh data."""

    # TODO need to store meshes as dependencies to avoid double free from alias

    new_obj = bpy.data.objects.new(
        bpy_nocollide_data_name(obj.item(), bpy.data.objects), obj.item().data
    )
    bpy.context.collection.objects.link(new_obj)
    return t.MeshObject(new_obj)


@pf.tracer.primitive(mutates=["mutates_obj"])
def shade_flat(
    mutates_obj: t.MeshObject,
    keep_sharp_edges: bool = True,
) -> None:
    """
    Render faces of object with flat shading

    Based on bpy.ops.object.shade_flat
    """
    execute_object_op(
        bpy.ops.object.shade_flat,
        objs=mutates_obj,
        keep_sharp_edges=keep_sharp_edges,
        description=shade_flat.__name__,
    )


@pf.tracer.primitive
def joined(**objects: t.Object) -> t.MeshObject:
    """
    Copies the objects and creates a new object with them merged together
    """

    if len(objects) < 2:
        raise ValueError(
            f"{joined.__name__} requires at least two objects, got {len(objects)}"
        )

    clones = [v.clone() for v in objects.values()]

    execute_object_op(
        bpy.ops.object.join,
        objs=clones,
        description=joined.__name__,
    )
    return t.MeshObject(bpy.context.active_object)


@pf.tracer.primitive(mutates=["mutates_obj_1", "mutates_obj_2"])
def join(
    mutates_obj_1: t.MeshObject,
    mutates_obj_2: t.MeshObject,
) -> None:
    """
    Modifies mutates_obj_1 to point to a joined object of the two, without any copying.

    mutates_obj_2 is invalidated. TODO: make it safely point to the joined object
    """

    execute_object_op(
        bpy.ops.object.join,
        active=mutates_obj_1,
        objs=[mutates_obj_2],
        description=join.__name__,
    )

    # mutates_obj_1.extend_dependencies(mutates_obj_2)
    # mutates_obj_2.invalidate()


def duplicate(
    obj: t.Object,
    linked: bool = False,
    mode: Literal["TRANSLATION", "ROTATION", "RESIZE"] = "TRANSLATION",
) -> None:
    """
    Duplicate selected objects

    Based on bpy.ops.object.duplicate
    """
    bpy.context.view_layer.objects.active = obj.item()
    execute_object_op(
        bpy.ops.object.duplicate,
        objs=[obj],
        linked=linked,
        mode=mode,
        description=duplicate.__name__,
    )
    return t.Object(bpy.context.active_object)


@pf.tracer.primitive(mutates=["mutates_obj"])
def shade_smooth(
    mutates_obj: t.MeshObject,
    keep_sharp_edges: bool = True,
) -> None:
    """
    Render faces of object with smooth shading

    Based on bpy.ops.object.shade_smooth
    """
    execute_object_op(
        bpy.ops.object.shade_smooth,
        objs=mutates_obj,
        keep_sharp_edges=keep_sharp_edges,
        description=shade_smooth.__name__,
    )


# TODO: convert() for POINTCLOUD, CURVES, GREASEPENCIL ?


@pf.tracer.primitive
def curve_to_mesh(
    curve: t.CurveObject,
    merge_customdata: bool = True,
) -> t.MeshObject:
    """
    Convert curve to mesh
    """
    execute_object_op(
        bpy.ops.object.convert,
        active=curve,
        target="MESH",
        keep_original=True,
        merge_customdata=merge_customdata,
        description=curve_to_mesh.__name__,
    )
    return t.MeshObject(bpy.context.active_object)


@pf.tracer.primitive()
def mesh_to_curve(
    mesh: t.MeshObject,
) -> t.CurveObject:
    """
    Convert mesh to curve
    """
    execute_object_op(
        bpy.ops.object.convert,
        active=mesh,
        target="CURVE",
        keep_original=True,
        description=mesh_to_curve.__name__,
    )
    return t.CurveObject(bpy.context.active_object)


def clear_scene():
    for dstruct in [bpy.data.objects, bpy.data.meshes, bpy.data.materials]:
        for o in dstruct:
            dstruct.remove(o)
