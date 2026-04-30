from typing import Literal

import bpy
import numpy as np

from procfunc import types as t
from procfunc.util import bpy_info


def read_attribute(
    obj: t.MeshObject | t.CurveObject,
    key: str,
    domain: Literal["POINT", "EDGE", "FACE", "CORNER"] | None = None,
) -> np.ndarray:
    """
    Read attribute data into a numpy array.

    Args:
        obj: Blender object (required if key is provided)
        key: Attribute name (required if obj is provided)
        domain: Attribute domain - POINT, EDGE, FACE, or CORNER. If None, allow any domain
        attr: Blender attribute object (alternative to obj+key)

    Returns:
        numpy array containing the attribute data
    """

    attr = obj.item().data.attributes[key]

    if attr.data_type in bpy_info.UNSUPPORTED_DATATYPES:
        raise TypeError(f"Attribute {key} has unsupported data type {attr.data_type}")
    if attr.domain in bpy_info.UNSUPPORTED_DOMAINS:
        raise TypeError(f"Attribute {key} has unsupported domain {attr.domain}")

    if domain is not None and domain != attr.domain:
        raise ValueError(
            f"Attribute {key} has domain {attr.domain}, requested {domain}"
        )

    n = len(attr.data)

    dim = bpy_info.DATATYPE_DIMS[attr.data_type]
    field = bpy_info.DATATYPE_FIELDS[attr.data_type]
    result_dtype = bpy_info.DATATYPE_TO_PYTYPE[attr.data_type]

    data = np.empty(n * dim, dtype=result_dtype)
    attr.data.foreach_get(field, data)

    if dim > 1:
        data = data.reshape(-1, dim)

    return data


def get_attribute(
    obj: t.MeshObject | t.CurveObject,
    key: str,
    domain: Literal["POINT", "EDGE", "FACE", "CORNER"] | None = None,
) -> np.ndarray | None:
    """
    Get attribute data from a Blender object.

    Args:
        obj: Blender object to read from
        key: Attribute name to read
        domain: Attribute domain - POINT, EDGE, FACE, or CORNER

    Returns:
        numpy array of attribute data, or None if attribute doesn't exist
    """

    if key not in obj.item().data.attributes:
        return None

    return read_attribute(obj, key, domain)


def _promote_data_type_for_shape(data_type: str, shape: tuple[int, ...]) -> str:
    match data_type, shape:
        case "FLOAT", (_x, 3):
            return "FLOAT_VECTOR"
        case "FLOAT", (_x, 2):
            return "FLOAT2"
        case "INT", (_x, 2):
            return "INT32_2D"
        case _, (_,):
            return data_type
        case _:
            raise ValueError(
                f"{_promote_data_type_for_shape.__name__} does not currently support {data_type=} {shape=}. "
                "Please contact the developers if you believe this should be added."
            )


def write_attribute(
    obj: t.MeshObject | t.CurveObject,
    data: np.ndarray | bool | int | float,
    key: str,
    domain: Literal["POINT", "EDGE", "FACE", "CORNER"],
    overwrite: bool = False,
):
    """
    Write numpy array data to a Blender object attribute.
    """

    obj = obj.item()

    if not overwrite and key in obj.data.attributes:
        raise ValueError(
            f"Attribute {key} already exists for {obj.name=}, aborting due to kwarg {overwrite=}"
        )

    expected_count = {
        "POINT": len(obj.data.vertices),
        "EDGE": len(obj.data.edges),
        "FACE": len(obj.data.polygons),
    }

    if isinstance(data, (bool, int, float)):
        if domain in expected_count:
            data = np.full((expected_count[domain],), data, dtype=type(data))

    data_type = bpy_info.PYTYPE_TO_DATATYPE.get(data.dtype)
    if data_type is None:
        raise ValueError(
            f"{write_attribute.__name__} does not currently support {data.dtype}, "
            f"understood dtype to bpy mappings are {bpy_info.PYTYPE_TO_DATATYPE.keys()}. "
            "Please contact the developers if you believe this should be added."
        )

    data_type = _promote_data_type_for_shape(data_type, data.shape)
    dim = bpy_info.DATATYPE_DIMS[data_type]

    if domain in expected_count:
        expected_shape = (
            (expected_count[domain],) if dim == 1 else (expected_count[domain], dim)
        )
        if data.shape != expected_shape:
            raise ValueError(
                f"{write_attribute.__name__} expects data of shape {expected_shape} "
                f"for {domain=} with {data_type=}, got {data.shape}"
            )

    field = bpy_info.DATATYPE_FIELDS.get(data_type)
    if field is None:
        raise ValueError(
            f"{write_attribute.__name__} does not currently support {data_type}, allowed are {bpy_info.DATATYPE_FIELDS.keys()}"
        )

    if overwrite and key in obj.data.attributes:
        attr = obj.data.attributes[key]
    else:
        attr = obj.data.attributes.new(key, data_type, domain)

    try:
        attr.data.foreach_set(field, data.reshape(-1))
    except RuntimeError as e:
        raise RuntimeError(
            f"Blender failed to write attribute {key} for {obj.name=} with {data_type=} {domain=} from {data.shape=} {data.dtype=}"
        ) from e


def _transform_points(points_N3: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    points_homogeneous = np.empty((points_N3.shape[0], 4), dtype=points_N3.dtype)
    points_homogeneous[:, :3] = points_N3
    points_homogeneous[:, 3] = 1
    points = points_homogeneous @ matrix.T
    return points[:, :3]


def local_to_world(obj: t.Object, points_N3: np.ndarray) -> np.ndarray:
    mat = np.array(obj.item().matrix_world)
    return _transform_points(points_N3, mat)


def world_to_local(obj: t.Object, points_N3: np.ndarray) -> np.ndarray:
    mat = np.array(obj.item().matrix_world.inverted())
    return _transform_points(points_N3, mat)


def vertex_positions(obj: t.MeshObject, global_coords: bool = False) -> np.ndarray:
    """
    Read vertex positions from a Blender object.

    Args:
        obj: Blender mesh object
        global_coords: If True, return global coordinates, otherwise return local coordinates
    """

    pos = np.zeros(len(obj.item().data.vertices) * 3)
    obj.item().data.vertices.foreach_get("co", pos)
    pos = pos.reshape(-1, 3)
    if global_coords:
        pos = local_to_world(obj, pos)
    return pos


def write_vertex_positions(
    obj: t.MeshObject, pos: np.ndarray, global_coords: bool = False
):
    if pos.shape != (len(obj.item().data.vertices), 3):
        raise ValueError(
            f"{write_vertex_positions.__name__} expects pos to be of shape (N, 3), "
            f"got {pos.shape} for {obj.item().name=} with {len(obj.item().data.vertices)=}"
        )
    if global_coords:
        pos = world_to_local(obj, pos)
    obj.item().data.vertices.foreach_set("co", pos.reshape(-1))


def edge_indices(obj: t.MeshObject) -> np.ndarray:
    arr = np.zeros(len(obj.item().data.edges) * 2, dtype=int)
    obj.item().data.edges.foreach_get("vertices", arr)
    return arr.reshape(-1, 2)


def polygon_centers(obj: t.MeshObject) -> np.ndarray:
    arr = np.zeros(len(obj.item().data.polygons) * 3)
    obj.item().data.polygons.foreach_get("center", arr)
    return arr.reshape(-1, 3)


def polygon_normals(obj: t.MeshObject) -> np.ndarray:
    arr = np.zeros(len(obj.item().data.polygons) * 3)
    obj.item().data.polygons.foreach_get("normal", arr)
    return arr.reshape(-1, 3)


def polygon_areas(obj: t.MeshObject) -> np.ndarray:
    obj.item().data.polygons.foreach_get("area", arr)


    arr = np.zeros(len(obj.item().data.polygons))


def polygon_vertex_indices(
    obj: t.MeshObject,
    vertex_per_polygon: int,
    safe: bool = True,
) -> np.ndarray:
    """
    Get polygon vertex indices from a Blender object.

    Args:
        obj: Object
        vertex_per_polygon: Number of vertices per polygon in the mesh,
            e.g. 3 if you expect only triangles, 4 if you expect quads, etc.

    TODO: explicitly check / validate that all polygons have the expected number of vertices

    Returns:
        Array of shape (num_polygons, vertex_per_polygon)
    """

    assert vertex_per_polygon >= 3

    if safe:
        for polygon in obj.item().data.polygons:
            if len(polygon.vertices) != vertex_per_polygon:
                raise ValueError(
                    f"Polygon {polygon.index} has {len(polygon.vertices)} vertices, expected {vertex_per_polygon}"
                )

    arr = np.zeros(len(obj.item().data.polygons) * vertex_per_polygon, dtype=int)
    obj.item().data.polygons.foreach_get("vertices", arr)
    return arr.reshape(-1, vertex_per_polygon)


def uv_coords(obj: t.MeshObject, layer: int | None = None) -> np.ndarray:
    uv_layer = (
        obj.item().data.uv_layers[layer]
        if isinstance(layer, int)
        else obj.item().data.uv_layers.active
    )
    arr = np.zeros(len(obj.item().data.loops) * 2)
    uv_layer.data.foreach_get("uv", arr)
    return arr.reshape(-1, 2)


def write_uv_coords(obj: t.MeshObject, uv: np.ndarray, layer: int | None = None):
    uv_layer = (
        obj.item().data.uv_layers[layer]
        if isinstance(layer, int)
        else obj.item().data.uv_layers.active
    )

    if uv.shape != (len(obj.item().data.loops), 2):
        raise ValueError(
            f"{write_uv_coords.__name__} expects uv to be of shape (N, 2), "
            f"got {uv.shape} for {obj.item().name=} with {len(obj.item().data.loops)=}"
        )

    uv_layer.data.foreach_set("uv", uv.reshape(-1))




def bbox_corners(
    obj: t.Object,
    global_coords: bool = True,
) -> np.ndarray:
    """
    Get bounding box corners.

    Args:
        obj: Blender mesh object
        global_coords: If True, return global coordinates, otherwise return local coordinates

    Returns:
        Nx3 array of vertex positions. For global_coords=True, returns actual world-space
        vertex positions (tight bbox). For global_coords=False, returns the 8 local bound_box corners.
    """

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.item().evaluated_get(depsgraph)

    if not global_coords:
        return np.array(obj_eval.bound_box)

    bbox = np.array(obj_eval.bound_box)
    if global_coords:
        mat = np.array(obj_eval.matrix_world)
        ones = np.ones((bbox.shape[0], 1))
        bbox = (mat @ np.hstack([bbox, ones]).T).T[:, :3]
    return bbox


def bbox_min_max(
    obj: t.Object,
    global_coords: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    bbox = bbox_corners(obj, global_coords=global_coords)
    return bbox.min(axis=0), bbox.max(axis=0)


    cos = vertex_positions(obj)[edge_indices(obj).reshape(-1)].reshape(-1, 2, 3)


    cos = vertex_positions(obj)[edge_indices(obj).reshape(-1)].reshape(-1, 2, 3)


    cos = vertex_positions(obj)[edge_indices(obj).reshape(-1)].reshape(-1, 2, 3)








    return arr.reshape(-1)




def write_material_index(
    obj: t.MeshObject, index: int, face_mask: np.ndarray | None = None
) -> None:


__all__ = [
    "get_attribute",
    "read_attribute",
    "write_attribute",
    "local_to_world",
    "world_to_local",
    "vertex_positions",
    "write_vertex_positions",
    "edge_indices",
    "polygon_centers",
    "polygon_normals",
    "polygon_areas",
    "uv_coords",
    "write_uv_coords",
    "bbox_corners",
    "bbox_min_max",
]
