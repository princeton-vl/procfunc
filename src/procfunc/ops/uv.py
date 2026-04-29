from typing import Literal

import bpy
import numpy as np

import procfunc as pf
from procfunc import types as t
from procfunc.ops._util import execute_mesh_op


def _ensure_uv_layer(obj: bpy.types.Object, uv_name: str) -> None:
    """Ensure a UV layer exists with the given name, removing any existing one first."""
    mesh = obj.data
    if uv_name in mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers[uv_name])
    new_layer = mesh.uv_layers.new(name=uv_name)
    mesh.uv_layers.active = new_layer


@pf.tracer.primitive(mutates=["mutates_obj"])
def cube_project(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    uv_name: str = "UVMap",
    cube_size: float = 1.0,
    correct_aspect: bool = True,
    clip_to_bounds: bool = False,
    scale_to_bounds: bool = False,
) -> None:
    """
    Project the UV vertices of the mesh over the six faces of a cube

    Based on bpy.ops.uv.cube_project

    Args:
        vertex_mask: Boolean array selecting vertices to project.
        edge_mask: Boolean array selecting edges to project.
        face_mask: Boolean array selecting faces to project.
        uv_name: Name of the UV layer to create/replace.
    """
    _ensure_uv_layer(mutates_obj.item(), uv_name)
    execute_mesh_op(
        bpy.ops.uv.cube_project,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        cube_size=cube_size,
        correct_aspect=correct_aspect,
        clip_to_bounds=clip_to_bounds,
        scale_to_bounds=scale_to_bounds,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def cylinder_project(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    uv_name: str = "UVMap",
    direction: Literal[
        "VIEW_ON_EQUATOR", "VIEW_ON_POLES", "ALIGN_TO_OBJECT"
    ] = "VIEW_ON_EQUATOR",
    align: Literal["POLAR_ZX", "POLAR_ZY"] = "POLAR_ZX",
    pole: Literal["PINCH", "FAN"] = "PINCH",
    seam: bool = False,
    radius: float = 1.0,
    correct_aspect: bool = True,
    clip_to_bounds: bool = False,
    scale_to_bounds: bool = False,
) -> None:
    """
    Project the UV vertices of the mesh over the curved wall of a cylinder

    Based on bpy.ops.uv.cylinder_project

    Args:
        vertex_mask: Boolean array selecting vertices to project.
        edge_mask: Boolean array selecting edges to project.
        face_mask: Boolean array selecting faces to project.
        uv_name: Name of the UV layer to create/replace.
    """
    _ensure_uv_layer(mutates_obj.item(), uv_name)
    execute_mesh_op(
        bpy.ops.uv.cylinder_project,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        direction=direction,
        align=align,
        pole=pole,
        seam=seam,
        radius=radius,
        correct_aspect=correct_aspect,
        clip_to_bounds=clip_to_bounds,
        scale_to_bounds=scale_to_bounds,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def project_from_view(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    uv_name: str = "UVMap",
    orthographic: bool = False,
    camera_bounds: bool = True,
    correct_aspect: bool = True,
    clip_to_bounds: bool = False,
    scale_to_bounds: bool = False,
) -> None:
    """
    Project the UV vertices of the mesh as seen in current 3D view

    Based on bpy.ops.uv.project_from_view

    Args:
        vertex_mask: Boolean array selecting vertices to project.
        edge_mask: Boolean array selecting edges to project.
        face_mask: Boolean array selecting faces to project.
        uv_name: Name of the UV layer to create/replace.
    """
    _ensure_uv_layer(mutates_obj.item(), uv_name)
    execute_mesh_op(
        bpy.ops.uv.project_from_view,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        orthographic=orthographic,
        camera_bounds=camera_bounds,
        correct_aspect=correct_aspect,
        clip_to_bounds=clip_to_bounds,
        scale_to_bounds=scale_to_bounds,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def smart_project(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    uv_name: str = "UVMap",
    angle_limit: float = 1.15192,
    margin_method: Literal["SCALED", "ADD", "FRACTION"] = "SCALED",
    rotate_method: Literal[
        "AXIS_ALIGNED", "AXIS_ALIGNED_X", "AXIS_ALIGNED_Y"
    ] = "AXIS_ALIGNED_Y",
    island_margin: float = 0.0,
    area_weight: float = 0.0,
    correct_aspect: bool = True,
    scale_to_bounds: bool = False,
) -> None:
    """
    Projection unwraps the selected faces of mesh objects

    Based on bpy.ops.uv.smart_project

    Args:
        vertex_mask: Boolean array selecting vertices to project.
        edge_mask: Boolean array selecting edges to project.
        face_mask: Boolean array selecting faces to project.
        uv_name: Name of the UV layer to create/replace.
    """
    _ensure_uv_layer(mutates_obj.item(), uv_name)
    execute_mesh_op(
        bpy.ops.uv.smart_project,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        angle_limit=angle_limit,
        margin_method=margin_method,
        rotate_method=rotate_method,
        island_margin=island_margin,
        area_weight=area_weight,
        correct_aspect=correct_aspect,
        scale_to_bounds=scale_to_bounds,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def sphere_project(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    uv_name: str = "UVMap",
    direction: Literal[
        "VIEW_ON_EQUATOR", "VIEW_ON_POLES", "ALIGN_TO_OBJECT"
    ] = "VIEW_ON_EQUATOR",
    align: Literal["POLAR_ZX", "POLAR_ZY"] = "POLAR_ZX",
    pole: Literal["PINCH", "FAN"] = "PINCH",
    seam: bool = False,
    correct_aspect: bool = True,
    clip_to_bounds: bool = False,
    scale_to_bounds: bool = False,
) -> None:
    """
    Project the UV vertices of the mesh over the curved surface of a sphere

    Based on bpy.ops.uv.sphere_project

    Args:
        vertex_mask: Boolean array selecting vertices to project.
        edge_mask: Boolean array selecting edges to project.
        face_mask: Boolean array selecting faces to project.
        uv_name: Name of the UV layer to create/replace.
    """
    _ensure_uv_layer(mutates_obj.item(), uv_name)
    execute_mesh_op(
        bpy.ops.uv.sphere_project,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        direction=direction,
        align=align,
        pole=pole,
        seam=seam,
        correct_aspect=correct_aspect,
        clip_to_bounds=clip_to_bounds,
        scale_to_bounds=scale_to_bounds,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def unwrap(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    uv_name: str = "UVMap",
    method: Literal["ANGLE_BASED", "CONFORMAL"] = "ANGLE_BASED",
    fill_holes: bool = True,
    correct_aspect: bool = True,
    use_subsurf_data: bool = False,
    margin_method: Literal["SCALED", "ADD", "FRACTION"] = "SCALED",
    margin: float = 0.001,
) -> None:
    """
    Unwrap the mesh of the object being edited

    Based on bpy.ops.uv.unwrap

    Args:
        vertex_mask: Boolean array selecting vertices to unwrap.
        edge_mask: Boolean array selecting edges to unwrap.
        face_mask: Boolean array selecting faces to unwrap.
        uv_name: Name of the UV layer to create/replace.
    """
    _ensure_uv_layer(mutates_obj.item(), uv_name)
    execute_mesh_op(
        bpy.ops.uv.unwrap,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        method=method,
        fill_holes=fill_holes,
        correct_aspect=correct_aspect,
        use_subsurf_data=use_subsurf_data,
        margin_method=margin_method,
        margin=margin,
    )
