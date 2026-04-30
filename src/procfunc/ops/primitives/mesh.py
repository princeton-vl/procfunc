from typing import Any

import bpy
import numpy as np
from mathutils import Euler, Vector

from procfunc import types as t


def mesh_single_vertex() -> t.MeshObject:
    mesh = bpy.data.meshes.new(mesh_single_vertex.__name__)
    mesh.vertices.add(1)
    mesh.vertices[0].co = (0, 0, 0)
    obj = bpy.data.objects.new(mesh_single_vertex.__name__, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return t.MeshObject(obj)


"""
def point_cloud(
    points: list[Vector],
    edges: list[tuple[int, int]] | None = None,
) -> t.MeshObject:
    mesh = bpy.data.meshes.new(point_cloud.__name__)
    mesh.from_pydata(points, edges, [])
    obj = bpy.data.objects.new(point_cloud.__name__, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return t.MeshObject(obj)
"""


def mesh_from_numpy(
    vertices: np.ndarray | None = None,
    edges: np.ndarray | None = None,
    faces: np.ndarray | None = None,
) -> t.MeshObject:
    if vertices is None:
        vertices = np.array([])
    if edges is None:
        edges = np.array([])
    if faces is None:
        faces = np.array([])

    mesh = bpy.data.meshes.new(mesh_from_numpy.__name__)
    mesh.from_pydata(vertices, edges, faces)
    obj = bpy.data.objects.new(mesh_from_numpy.__name__, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return t.MeshObject(obj)


def mesh_line(
) -> t.MeshObject:
    idxs = np.arange(len(points))
    edges = np.stack([idxs[:-1], idxs[1:]], axis=-1)

    mesh = bpy.data.meshes.new(mesh_line.__name__)
    mesh.from_pydata(points, edges, [])
    obj = bpy.data.objects.new(mesh_line.__name__, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return t.MeshObject(obj)


def empty(
    disp_type: str = "PLAIN_AXES",
    display_size: float = 0.1,
) -> t.MeshObject:
    obj = bpy.data.objects.new(empty.__name__, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.empty_display_size = display_size
    obj.empty_display_type = disp_type
    return t.MeshObject(obj)


def mesh_uv_sphere(
    segments: int = 32,
    ring_count: int = 16,
    radius: float = 1.0,
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a UV sphere primitive with specified parameters."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=ring_count,
        radius=radius,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=location,
        rotation=rotation,
        scale=scale,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_plane(
    size: float = 2.0,
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a plane primitive with specified parameters."""
    bpy.ops.mesh.primitive_plane_add(
        size=size,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=location,
        rotation=rotation,
        scale=scale,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_cube(
    size: float = 2.0,
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a cube primitive with specified parameters."""
    bpy.ops.mesh.primitive_cube_add(
        size=size,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=Vector(location),
        rotation=Euler(rotation),
        scale=Vector(scale),
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_icosphere(
    subdivisions: int = 2,
    radius: float = 1.0,
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate an icosphere primitive with specified parameters."""
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=subdivisions,
        radius=radius,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=location,
        rotation=rotation,
        scale=scale,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_cylinder(
    vertices: int = 32,
    radius: float = 1.0,
    depth: float = 2.0,
    end_fill_type: str = "NGON",
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a cylinder primitive with specified parameters."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        end_fill_type=end_fill_type,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=location,
        rotation=rotation,
        scale=scale,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_cone(
    vertices: int = 32,
    radius1: float = 1.0,
    radius2: float = 0.0,
    depth: float = 2.0,
    end_fill_type: str = "NGON",
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a cone primitive with specified parameters."""
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        end_fill_type=end_fill_type,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=location,
        rotation=rotation,
        scale=scale,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_torus(
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    major_segments: int = 48,
    minor_segments: int = 12,
    mode: str = "MAJOR_MINOR",
    major_radius: float = 1.0,
    minor_radius: float = 0.25,
    abso_major_rad: float = 1.25,
    abso_minor_rad: float = 0.75,
    generate_uvs: bool = True,
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a torus primitive with specified parameters."""
    bpy.ops.mesh.primitive_torus_add(
        align=align,
        location=location,
        rotation=rotation,
        major_segments=major_segments,
        minor_segments=minor_segments,
        mode=mode,
        major_radius=major_radius,
        minor_radius=minor_radius,
        abso_major_rad=abso_major_rad,
        abso_minor_rad=abso_minor_rad,
        generate_uvs=generate_uvs,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_circle(
    vertices: int = 32,
    radius: float = 1.0,
    fill_type: str = "NOTHING",
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a circle primitive with specified parameters."""
    bpy.ops.mesh.primitive_circle_add(
        vertices=vertices,
        radius=radius,
        fill_type=fill_type,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=location,
        rotation=rotation,
        scale=scale,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_grid(
    x_subdivisions: int = 10,
    y_subdivisions: int = 10,
    size: float = 2.0,
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a grid primitive with specified parameters."""
    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=x_subdivisions,
        y_subdivisions=y_subdivisions,
        size=size,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=location,
        rotation=rotation,
        scale=scale,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)


def mesh_monkey(
    size: float = 2.0,
    calc_uvs: bool = True,
    enter_editmode: bool = False,
    align: str = "WORLD",
    location: Vector = Vector((0.0, 0.0, 0.0)),
    rotation: Euler = Euler((0.0, 0.0, 0.0)),
    scale: Vector = Vector((1.0, 1.0, 1.0)),
    **kwargs: Any,
) -> t.MeshObject:
    """Generate a monkey (Suzanne) primitive with specified parameters."""
    bpy.ops.mesh.primitive_monkey_add(
        size=size,
        calc_uvs=calc_uvs,
        enter_editmode=enter_editmode,
        align=align,
        location=location,
        rotation=rotation,
        scale=scale,
        **kwargs,
    )
    obj = bpy.context.active_object
    return t.MeshObject(obj)
