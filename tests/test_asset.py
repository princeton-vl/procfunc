
import bpy
import pytest


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

    assert "test" in bpy.data.objects

    del obj

    assert "test" not in bpy.data.objects


def test_asset_overwrite():
    def inner(obj: pf.MeshObject):
        obj = obj.item()
        print(obj.name)

    obj = pf.ops.primitives.mesh_cube()
    inner(obj)


# set_material tests


def _dummy_shader():
    return pf.nodes.shader.principled_bsdf()


def create_dummy_shader():
    return _dummy_shader()





















@_GC_CLEANUP_NOT_IMPLEMENTED
    pf.ops.object.set_material(
        cube, surface=pf.nodes.shader.principled_bsdf(base_color=(0, 1, 0, 1))
    )





# .join tests


    shader = pf.nodes.shader.principled_bsdf(base_color=color)



    mat_names = [
        slot.material.name
        for slot in list(obj1.item().material_slots) + list(obj2.item().material_slots)
    ]




@pytest.mark.skip(reason="invalidate not currently implemented")

    _obj2_name = obj2.item().name  # noqa: F841










