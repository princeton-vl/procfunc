import gc

import bpy
import pytest

import procfunc as pf
from procfunc.ops import object as ops

_GC_CLEANUP_NOT_IMPLEMENTED = pytest.mark.skip(
    reason="BlenderAsset.__del__ cleanup not yet implemented"
)


@_GC_CLEANUP_NOT_IMPLEMENTED
def test_asset_create_del():
    def use_asset():
        bpy.ops.mesh.primitive_plane_add(size=2)
        obj = bpy.context.active_object
        obj.name = "test"
        asset = pf.Object(obj)
        print(asset.item().name)

    use_asset()

    gc.collect()
    assert "test" not in bpy.data.objects


@_GC_CLEANUP_NOT_IMPLEMENTED
def test_asset_double_free():
    obj = pf.Object(bpy.data.objects.new("test", None))

    def use_asset():
        nonlocal obj
        objref2 = pf.Object(obj.item())
        print(objref2.item().name)

    use_asset()
    use_asset()

    gc.collect()
    assert "test" in bpy.data.objects

    del obj

    gc.collect()
    assert "test" not in bpy.data.objects


def test_asset_overwrite():
    def inner(obj: pf.MeshObject):
        obj = obj.item()
        print(obj.name)

    obj = pf.ops.primitives.mesh_cube()
    inner(obj)


# set_material tests


@pf.nodes.node_function
def _dummy_shader():
    return pf.nodes.shader.principled_bsdf()


def create_dummy_shader():
    return _dummy_shader()


def test_set_material_basic_assignment():
    # creates new cube object
    bpy.ops.mesh.primitive_cube_add()
    obj = pf.MeshObject(bpy.context.active_object)

    # dummy shader to assign it as a material
    shader = create_dummy_shader()
    ops.set_material(obj, surface=shader)

    # check that material slot exists
    mat_slots = obj.item().material_slots
    assert len(mat_slots) == 1
    assert mat_slots[0].material is not None
    assert mat_slots[0].material.name in bpy.data.materials


def test_set_material_gc_safe():
    bpy.ops.mesh.primitive_cube_add()
    obj = pf.MeshObject(bpy.context.active_object)

    # test gc with set_material
    shader = create_dummy_shader()
    ops.set_material(obj, surface=shader)
    del shader
    gc.collect()

    mat_slots = obj.item().material_slots
    assert len(mat_slots) == 1
    assert mat_slots[0].material is not None
    assert mat_slots[0].material.name in bpy.data.materials


def test_set_material_overwrites_existing():
    bpy.ops.mesh.primitive_cube_add()
    obj = pf.MeshObject(bpy.context.active_object)

    # assign first and second material
    shader1 = create_dummy_shader()
    shader2 = create_dummy_shader()

    ops.set_material(obj, surface=shader1)
    mat1 = obj.item().material_slots[0].material

    ops.set_material(obj, surface=shader2)
    mat2 = obj.item().material_slots[0].material

    # check if it overwrites correctly
    assert mat1 != mat2


def test_join_preserves_both_materials():
    # create two objects with different materials
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    obj1 = pf.MeshObject(bpy.context.active_object)
    ops.set_material(obj1, surface=create_dummy_shader())

    bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
    obj2 = pf.MeshObject(bpy.context.active_object)
    ops.set_material(obj2, surface=create_dummy_shader())

    # join obj2 into obj1 and delete reference to obj2
    ops.join(obj1, obj2)
    del obj2
    gc.collect()

    # check that obj1 has multiple materials and none are None
    mats = [slot.material for slot in obj1.item().material_slots]
    assert len(mats) >= 2
    assert all(m is not None for m in mats)


@_GC_CLEANUP_NOT_IMPLEMENTED
def test_set_material_object_deletion_cleans_up():
    # create an object and assign a material
    cube = pf.ops.primitives.mesh_cube()
    mat_name = "DeleteMeMat"
    pf.ops.object.set_material(
        cube, surface=pf.nodes.shader.principled_bsdf(base_color=(0, 1, 0, 1))
    )
    cube.item().material_slots[0].material.name = mat_name

    obj_name = cube.item().name
    assert obj_name in bpy.data.objects
    assert mat_name in bpy.data.materials.keys()

    del cube
    gc.collect()

    # after deletion, blender object and material should be removed from data
    assert obj_name not in bpy.data.objects.keys()
    assert mat_name not in bpy.data.materials.keys()


# .join tests


def make_cube_with_material(color=(1, 0, 0, 1)):
    bpy.ops.mesh.primitive_cube_add()
    obj = pf.MeshObject(bpy.context.active_object)
    shader = pf.nodes.shader.principled_bsdf(base_color=color)
    pf.ops.object.set_material(obj, surface=shader)
    return obj


def test_join_merges_materials_safely():
    obj1 = make_cube_with_material(color=(1, 0, 0, 1))  # red
    obj2 = make_cube_with_material(color=(0, 1, 0, 1))  # green

    mat_names = [
        slot.material.name
        for slot in list(obj1.item().material_slots) + list(obj2.item().material_slots)
    ]

    pf.ops.object.join(obj1, obj2)
    del obj2
    gc.collect()

    joined_mats = [slot.material.name for slot in obj1.item().material_slots]
    for name in mat_names:
        assert name in joined_mats


@pytest.mark.skip(reason="invalidate not currently implemented")
def test_join_invalidates_second_object_safely():
    obj1 = make_cube_with_material()
    obj2 = make_cube_with_material()

    _obj2_name = obj2.item().name  # noqa: F841
    mesh_name = obj2.item().data.name

    pf.ops.object.join(obj1, obj2)

    # check for none
    assert obj2._item is None

    del obj2
    gc.collect()

    # mesh may still exist (joined), but should no longer have independent users
    assert mesh_name not in bpy.data.meshes or bpy.data.meshes[mesh_name].users == 0


# def test_join_double_free_crash_repro():
#     obj1 = make_cube_with_material(color=(0.8, 0.2, 0.2, 1))  # reddish
#     obj2 = make_cube_with_material(color=(0.2, 0.8, 0.2, 1))  # greenish

#     mesh2 = obj2.item().data.name
#     mat2 = obj2.item().material_slots[0].material.name

#     pf.ops.object.join(obj1, obj2)
#     obj2._item = bpy.data.objects.get(obj2.item().name, None)

#     # delete obj2 and force GC - this may crash if __del__ tries to clean up its mesh or materials
#     del obj2
#     gc.collect()

#     #  w no crash
#     assert True
