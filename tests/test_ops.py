from typing import Literal

import bpy
import numpy as np
import pytest

import procfunc as pf
from procfunc.util.manifest import import_item_iterative

_PRIMITIVE_FUNCS = pf.util.manifest.filter_manifest(
    pf.ops.OPS_MANIFEST,
    filter={"category": "primitive"},
    exclude={"name": ["LATER", "DECLINE"]},
    require_nonempty=["name"],
    min_entries=10,
)


def devmat(r: float) -> pf.Material:
    surface = pf.nodes.shader.principled_bsdf(base_color=(r, 1, 1, 1))
    return pf.Material(surface=surface)


@pytest.mark.parametrize(
    "func_name",
    list(_PRIMITIVE_FUNCS["name"].values),
)
def test_primitives(func_name: str):
    func = import_item_iterative(func_name.replace("pf.", "procfunc."))
    obj = func()

    assert obj is not None

    if "mesh" in func_name:
        assert obj.item().type == "MESH"
        assert len(obj.item().data.vertices) > 0
    elif "curve" in func_name:
        assert obj.item().type == "CURVE"
    elif "lamp" in func_name:
        assert obj.item().type == "LIGHT"
    else:
        raise ValueError(f"Unknown primitive type: {func_name}")


_MODIFIER_FUNCS = pf.util.manifest.filter_manifest(
    pf.ops.OPS_MANIFEST,
    filter={"category": "modifier"},
    exclude={"name": ["LATER", "DECLINE"]},
    require_nonempty=["name"],
    min_entries=15,
)


@pytest.mark.parametrize(
    "func_name,arguments",
    list(_MODIFIER_FUNCS[["name", "arguments"]].itertuples(index=False)),
    ids=_MODIFIER_FUNCS["name"].values,
)
def test_ops_modifier(func_name: str, arguments: str):
    arguments_list = arguments.split("-") if isinstance(arguments, str) else []
    assert "|" not in arguments

    func = import_item_iterative(func_name.replace("pf.", "procfunc."))

    inputs = {}
    inputs["mutates_obj"] = pf.ops.primitives.mesh_cube()

    if "target" in arguments:
        inputs["target"] = pf.ops.primitives.mesh_icosphere()
        target_before = inputs["target"].clone()

    obj = func(**inputs)

    assert obj is not None
    assert obj.item().type == "MESH"
    assert len(obj.item().modifiers) == 0  # Should be applied and removed

    if "target" in arguments_list:
        assert _mesh_equal(target_before, inputs["target"])


_MESH_FUNCS_MASKARGS = pf.util.manifest.filter_manifest(
    pf.ops.OPS_MANIFEST,
    filter={"category": "mesh"},
    exclude={
        "name": ["LATER", "DECLINE"],
        "is_unittest_specialcase": True,
    },
    require_nonempty=["name", "arguments"],
    min_entries=2,
)

# split parameterized mask types into multiple parameterized tests
_MESH_FUNCS_MASKARGS = _MESH_FUNCS_MASKARGS.explode("arguments")
_MESH_FUNCS_MASKARGS["arguments"] = _MESH_FUNCS_MASKARGS["arguments"].fillna(value="")


def _mesh_equal(obj1: pf.MeshObject, obj2: pf.MeshObject) -> bool:
    d1 = obj1.item().data
    d2 = obj2.item().data

    if len(d1.vertices) != len(d2.vertices):
        return False
    if len(d1.edges) != len(d2.edges):
        return False
    if len(d1.polygons) != len(d2.polygons):
        return False

    if not np.allclose(
        pf.ops.attr.vertex_positions(obj1, global_coords=True),
        pf.ops.attr.vertex_positions(obj2, global_coords=True),
    ):
        return False

    if not np.equal(
        pf.ops.attr.edge_indices(obj1),
        pf.ops.attr.edge_indices(obj2),
    ).all():
        return False

    for i in range(len(obj1.item().data.polygons)):
        if len(obj1.item().data.polygons[i].vertices) != len(
            obj2.item().data.polygons[i].vertices
        ):
            return False

        for j in range(len(obj1.item().data.polygons[i].vertices)):
            if (
                obj1.item().data.polygons[i].vertices[j]
                != obj2.item().data.polygons[i].vertices[j]
            ):
                return False

    if not np.allclose(
        pf.ops.attr.polygon_normals(obj1),
        pf.ops.attr.polygon_normals(obj2),
    ):
        return False

    return True


@pytest.mark.parametrize(
    "func_name,arguments",
    list(_MESH_FUNCS_MASKARGS[["name", "arguments"]].itertuples(index=False)),
)
def test_ops_mesh(func_name: str, arguments: list[str]):
    func = import_item_iterative(func_name.replace("pf.", "procfunc."))

    base_obj = pf.ops.primitives.mesh_cube()
    mask_lens = {
        "vertex_mask": len(base_obj.item().data.vertices),
        "edge_mask": len(base_obj.item().data.edges),
        "face_mask": len(base_obj.item().data.polygons),
    }

    if not arguments or arguments == "none":
        mask_kwargs = {}
    else:
        mask_len = mask_lens[arguments]
        mask = np.arange(mask_len) > mask_len // 2
        mask_kwargs = {arguments: mask}

    mut = base_obj.clone()

    n_obj_before = len(bpy.data.objects)
    n_baseverts_before = len(base_obj.item().data.vertices)
    func(mutates_obj=mut, **mask_kwargs)

    n_baseverts_after = len(base_obj.item().data.vertices)
    assert n_baseverts_after == n_baseverts_before, (
        f"{func_name} incorrectly modified base_obj not mut_obj ?? {n_baseverts_before=} {n_baseverts_after=}"
    )
    assert n_obj_before == len(bpy.data.objects), (
        f"{func_name} incorrectly changed number of objects in bpy.data.objects ?? {n_obj_before=} {len(bpy.data.objects)=}"
    )

    assert not _mesh_equal(base_obj, mut), (
        f"{func_name} failed with {arguments}, {mut.item().name} remained unchanged from {base_obj.item().name}"
    )


def test_ops_mesh_separate_mask():
    obj = pf.ops.primitives.mesh_cube()

    nface = len(obj.item().data.polygons)
    face_mask = np.arange(nface) < nface // 3
    assert face_mask.sum() == nface // 3

    splitobj = pf.ops.mesh.separate_mask(mutates_obj=obj, face_mask=face_mask)

    assert splitobj.item() is not obj.item()
    assert len(splitobj.item().data.polygons) == nface // 3
    assert len(obj.item().data.polygons) == nface - nface // 3


_OBJECT_FUNCS = pf.util.manifest.filter_manifest(
    pf.ops.OPS_MANIFEST,
    filter={"category": "object"},
    exclude={
        "name": ["LATER", "DECLINE"],
        "is_unittest_specialcase": True,
    },
    require_nonempty=["name"],
    min_entries=1,
)


@pytest.mark.parametrize(
    "func_name,arguments",
    list(_OBJECT_FUNCS[["name", "arguments"]].itertuples(index=False)),
    ids=_OBJECT_FUNCS["name"].values,
)
def test_ops_object(func_name: str, arguments: list[str]):
    func = import_item_iterative(func_name.replace("pf.", "procfunc."))

    arguments_dict = {}
    for arg in arguments:
        match arg:
            case "mesh":
                arguments_dict["mesh"] = pf.ops.primitives.mesh_cube()
            case "curve":
                arguments_dict["curve"] = pf.ops.primitives.curve_circle()
            case "object" | "mutates_obj":
                arguments_dict[arg] = pf.ops.primitives.mesh_cube()
            case "objects":
                arguments_dict["cube1"] = pf.ops.primitives.mesh_cube()
                arguments_dict["cube2"] = pf.ops.primitives.mesh_cube()
            case "material":
                arguments_dict[arg] = devmat(1.0)
            case _:
                raise ValueError(f"Unknown argument: {arg}")

    func(**arguments_dict)


def test_mesh_to_curve():
    line = pf.ops.primitives.mesh_line(points=[(0, 0, 0), (1, 1, 1)])
    curve = pf.ops.object.mesh_to_curve(line)
    assert curve.item().type == "CURVE"
    assert len(curve.item().data.splines[0].points) == 2


def test_curve_to_mesh():
    curve = pf.ops.primitives.curve_circle()
    mesh = pf.ops.object.curve_to_mesh(curve)
    assert mesh.item().type == "MESH"
    # TODO


def test_objects_joined():
    cube1 = pf.ops.primitives.mesh_cube()
    cube2 = pf.ops.primitives.mesh_cube()
    joined = pf.ops.object.joined(cube1=cube1, cube2=cube2)
    assert joined.item().type == "MESH"
    assert len(joined.item().data.polygons) == 12

    assert len(cube1.item().data.polygons) == 6
    assert len(cube2.item().data.polygons) == 6


@pytest.mark.skip(reason="invalidate not currently implemented")
def test_objects_join():
    cube1 = pf.ops.primitives.mesh_cube()
    cube2 = pf.ops.primitives.mesh_cube()
    pf.ops.object.join(mutates_obj_1=cube1, mutates_obj_2=cube2)

    assert len(cube1.item().data.polygons) == 12

    with pytest.raises(ValueError):
        cube2.item()


_CURVE_FUNCS = pf.util.manifest.filter_manifest(
    pf.ops.OPS_MANIFEST,
    filter={"category": "curve"},
    exclude={"name": ["LATER", "DECLINE"]},
    require_nonempty=["name"],
    min_entries=1,
)


@pytest.mark.parametrize(
    "func_name",
    list(_CURVE_FUNCS["name"].values),
)
def test_ops_curve(func_name: str):
    _func = import_item_iterative(func_name.replace("pf.", "procfunc."))  # noqa: F841
    pass


CUBE_COUNTS = {
    "POINT": 8,
    "EDGE": 12,
    "FACE": 6,
}
ATTR_CASES = [
    ("FLOAT", "POINT"),  # vertices
    ("FLOAT", "EDGE"),  # edges
    ("FLOAT", "FACE"),  # faces
    ("INT", "POINT"),
    ("INT", "EDGE"),
    ("INT", "FACE"),
    ("BOOLEAN", "POINT"),
    ("BOOLEAN", "EDGE"),
    ("BOOLEAN", "FACE"),
    ("FLOAT_VECTOR", "POINT"),
    ("FLOAT_VECTOR", "EDGE"),
    ("FLOAT_VECTOR", "FACE"),
]


@pytest.mark.parametrize("attr_type,domain", ATTR_CASES)
def test_write_read_cube_attrs(
    attr_type: str,
    domain: Literal["POINT", "EDGE", "FACE"],
):
    obj = pf.ops.primitives.mesh_cube()

    expected_count = CUBE_COUNTS[domain]

    # Generate appropriate test data based on type
    if attr_type == "FLOAT":
        data = np.random.uniform(-1, 1, expected_count).astype(np.float32)
    elif attr_type == "INT":
        data = np.random.randint(0, 10, expected_count).astype(np.int32)
    elif attr_type == "BOOLEAN":
        data = np.random.uniform(0, 1, expected_count) > 0.5
    elif attr_type == "FLOAT_VECTOR":
        data = np.random.uniform(-1, 1, (expected_count, 3)).astype(np.float32)
    else:
        raise ValueError(f"Unknown attribute type: {attr_type}")

    # Write and read back
    name = f"test_{attr_type.lower()}_{domain.lower()}"
    pf.ops.attr.write_attribute(
        data=data,
        obj=obj,
        key=name,
        domain=domain,
    )
    result = pf.ops.attr.get_attribute(obj, name)

    # Verify data matches
    np.testing.assert_array_almost_equal(data, result)


def test_nonexistent_attr():
    obj = pf.ops.primitives.mesh_cube()

    # Should return None for non-existent attribute
    result = pf.ops.attr.get_attribute(obj, "nonexistent", "POINT")
    assert result is None


def test_all_attr_types_and_domains():
    obj = pf.ops.primitives.mesh_cube()
    counts = {"POINT": 8, "EDGE": 12, "FACE": 6, "CORNER": 24}

    cases = {
        "FLOAT": lambda n: np.random.uniform(0, 1, n).astype(np.float32),
        "INT": lambda n: np.random.randint(0, 10, n).astype(np.int32),
        "BOOLEAN": lambda n: np.random.uniform(0, 1, n) > 0.5,
        "FLOAT2": lambda n: np.random.uniform(0, 1, (n, 2)).astype(np.float32),
        "INT32_2D": lambda n: np.random.randint(0, 10, (n, 2)).astype(np.int32),
        "FLOAT_VECTOR": lambda n: np.random.uniform(0, 1, (n, 3)).astype(np.float64),
    }

    for domain, n in counts.items():
        for dtype, make_data in cases.items():
            data = make_data(n)
            key = f"test_{dtype}_{domain}".lower()
            pf.ops.attr.write_attribute(obj=obj, data=data, key=key, domain=domain)
            result = pf.ops.attr.read_attribute(obj, key)
            np.testing.assert_array_almost_equal(
                result, data, err_msg=f"{dtype} {domain}"
            )


def test_add_material_basic():
    cube = pf.ops.primitives.mesh_cube()
    mat = devmat(1.0)
    pf.ops.object.set_material(cube, surface=mat.surface)
    assert len(cube.item().material_slots) == 1


def test_add_material_not_garbage_collected():
    namestr = "test"

    def inner():
        cube = pf.ops.primitives.mesh_cube()
        mat = devmat(1.0)
        pf.ops.object.set_material(cube, surface=mat.surface)
        cube.item().material_slots[0].material.name = namestr
        return cube

    cube = inner()
    assert isinstance(cube, pf.Asset)
    assert namestr in list(bpy.data.materials.keys())
    assert cube.item().material_slots[0].material.name == namestr


def test_bbox_after_set_transform():
    # bbox_min_max must account for object-level transform set via set_transform
    obj = pf.ops.primitives.mesh_cube()
    pf.ops.object.set_transform(obj, location=pf.Vector((5, 0, 0)))
    assert obj.item().location == pf.Vector((5, 0, 0))
    bmin, bmax = pf.ops.attr.bbox_min_max(obj)
    assert bmin[0] == 4, f"Expected 4 (cube at x=5, half-size=1), got {bmin[0]}"


def test_transform():
    obj = pf.ops.primitives.mesh_cube()
    pf.ops.mesh.transform(obj, location=pf.Vector((2, 0, 0)))
    assert obj.item().location == pf.Vector((0, 0, 0))
    bmin, bmax = pf.ops.attr.bbox_min_max(obj)
    assert bmin[0] == 1

    # TODO: test should fail for symmetry / wrong direction
    obj = pf.ops.primitives.mesh_cube()
    pf.ops.mesh.transform(obj, rotation_euler=np.deg2rad((45, 0, 0)))
    assert obj.item().rotation_euler == pf.Euler((0, 0, 0))
    bmin, bmax = pf.ops.attr.bbox_min_max(obj)
    assert np.isclose(bmin[2], -1.4142135623730951)

    obj = pf.ops.primitives.mesh_cube()
    pf.ops.mesh.transform(obj, scale=pf.Vector((2, 2, 2)))
    assert obj.item().scale == pf.Vector((1, 1, 1))
    bmin, bmax = pf.ops.attr.bbox_min_max(obj)
    assert (bmin == pf.Vector((-2, -2, -2))).all()
    assert (bmax == pf.Vector((2, 2, 2))).all()


def test_separate_loose():
    obj = pf.ops.primitives.mesh_cube()
    obj2 = pf.ops.primitives.mesh_cube()
    pf.ops.mesh.transform(obj, location=pf.Vector((2, 0, 0)))
    pf.ops.object.join(obj, obj2)
    assert len(obj.item().data.polygons) == 12

    objs = pf.ops.mesh.separate_loose(obj)
    assert len(objs) == 2
    assert len(objs[0].item().data.polygons) == 6
    assert len(objs[1].item().data.polygons) == 6


def test_return_mask():
    # inset
    obj = pf.ops.primitives.mesh_cube()
    input_mask = np.arange(len(obj.item().data.polygons)) <= 1
    out_mask = pf.ops.mesh.inset(obj, input_mask)
    assert len(out_mask) == len(obj.item().data.polygons)
    assert out_mask.sum() == 2

    # inset individual
    obj = pf.ops.primitives.mesh_cube()
    out_mask = pf.ops.mesh.inset_individual(obj, input_mask)
    assert len(out_mask) == len(obj.item().data.polygons)
    assert out_mask.sum() == 2

    # region_to_loop
    obj = pf.ops.primitives.mesh_cube()
    input_mask = np.arange(len(obj.item().data.polygons)) == 0
    out_mask = pf.ops.mesh.region_to_loop(obj, input_mask)
    assert len(out_mask) == len(obj.item().data.edges)
    assert out_mask.sum() == 4


def test_uv_project_creates_named_layer():
    """Test that UV projection creates a UV layer with the specified name."""
    obj = pf.ops.primitives.mesh_cylinder()
    mesh = obj.item().data

    if "UVMap" in mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers["UVMap"])

    pf.ops.uv.cylinder_project(obj, uv_name="TestUV")

    assert "TestUV" in mesh.uv_layers
    assert mesh.uv_layers.active.name == "TestUV"
