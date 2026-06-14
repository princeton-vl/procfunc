import bpy

from procfunc.util import bpy_data


def test_new_datablocks_removed_across_collections():
    with bpy_data.removing_new_datablocks():
        mesh = bpy.data.meshes.new("_cleanup_mesh")
        bpy.data.objects.new("_cleanup_obj", mesh)
        bpy.data.materials.new("_cleanup_mat")
        bpy.data.images.new("_cleanup_img", 4, 4)
        bpy.data.node_groups.new("_cleanup_ng", "GeometryNodeTree")
        bpy.data.scenes.new("_cleanup_scene")

    for collection in (
        bpy.data.meshes,
        bpy.data.objects,
        bpy.data.materials,
        bpy.data.images,
        bpy.data.node_groups,
        bpy.data.scenes,
    ):
        assert not [b for b in collection if b.name.startswith("_cleanup_")]


def test_preexisting_datablocks_kept():
    keep = bpy.data.meshes.new("_keep_mesh")
    try:
        with bpy_data.removing_new_datablocks():
            bpy.data.meshes.new("_cleanup_mesh2")
        assert "_keep_mesh" in bpy.data.meshes.keys()
    finally:
        bpy.data.meshes.remove(keep)


def test_active_scene_survives():
    active = bpy.context.scene
    with bpy_data.removing_new_datablocks():
        pass
    assert bpy.context.scene is active


def test_removes_on_exception():
    try:
        with bpy_data.removing_new_datablocks():
            bpy.data.meshes.new("_cleanup_exc_mesh")
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert "_cleanup_exc_mesh" not in bpy.data.meshes.keys()
