from dataclasses import asdict, dataclass
from typing import Literal, Tuple, Unpack

import bpy
import numpy as np

import procfunc as pf
from procfunc import types as t
from procfunc.ops._util import (
    execute_mesh_op,
    execute_object_op,
    extract_edge_mask,
    extract_face_mask,
    extract_vertex_mask,
)

TProportionalEditFalloff = Literal[
    "SMOOTH",
    "SPHERE",
    "ROOT",
    "INVERSE_SQUARE",
    "SHARP",
    "LINEAR",
    "CONSTANT",
    "RANDOM",
]


@pf.tracer.primitive(mutates=["mutates_obj"])
def transform_apply(
    mutates_obj: t.MeshObject,
    location: bool = True,
    rotation: bool = True,
    scale: bool = True,
):
    execute_object_op(
        bpy.ops.object.transform_apply,
        objs=mutates_obj,
        location=location,
        rotation=rotation,
        scale=scale,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def transform(
    mutates_obj: t.MeshObject,
    location: t.Vector | None = None,
    rotation_euler: t.Vector | t.Euler | None = None,
    scale: t.Vector | None = None,
):
    obj = mutates_obj.item()

    if location is not None:
        obj.location += t.Vector(location)
    if rotation_euler is not None:
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = obj.rotation_quaternion @ t.Quaternion(rotation_euler)
    if scale is not None:
        obj.scale = obj.scale * t.Vector(scale)

    transform_apply(
        mutates_obj,
        location=location is not None,
        rotation=rotation_euler is not None,
        scale=scale is not None,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def delete_geometry(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    type: Literal["VERT", "EDGE", "FACE", "EDGE_FACE", "ONLY_FACE"] = "VERT",
) -> None:
    """Based on bpy.ops.mesh.delete"""
    execute_mesh_op(
        bpy.ops.mesh.delete,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        type=type,
    )


@dataclass
class ProportionalEditProperties:
    falloff: TProportionalEditFalloff | None = None
    size: float = 1.0
    connected: bool = False
    projected: bool = False


@pf.tracer.primitive(mutates=["mutates_obj"])
def extrude_edges(
    mutates_obj: t.MeshObject,
    edge_mask: np.ndarray | None = None,
    use_normal_flip: bool = False,
    mirror: bool = False,
    value: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    orient_type: Literal[
        "GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR"
    ] = "GLOBAL",
    constraint_axis: Tuple[bool, bool, bool] = (False, False, False),
    **proportional_edit_kwargs: Unpack[ProportionalEditProperties],
) -> None:
    """
    Extrude individual edges and move

    Based on bpy.ops.mesh.extrude_edges_move

    Args:
        edge_mask: Boolean array selecting edges to extrude.
    """

    proportional_edit = ProportionalEditProperties(**proportional_edit_kwargs)

    execute_mesh_op(
        bpy.ops.mesh.extrude_edges_move,
        mutates_obj,
        edge_mask=edge_mask,
        MESH_OT_extrude_edges_indiv={
            "use_normal_flip": use_normal_flip,
            "mirror": mirror,
        },
        TRANSFORM_OT_translate={
            "value": value,
            "orient_type": orient_type,
            "constraint_axis": constraint_axis,
            "mirror": mirror,
            "use_proportional_edit": proportional_edit.falloff is not None,
            "proportional_edit_falloff": proportional_edit.falloff or "SMOOTH",
            "proportional_size": proportional_edit.size,
            "use_proportional_connected": proportional_edit.connected,
            "use_proportional_projected": proportional_edit.projected,
        },
    )


def region_to_loop(
    obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
) -> np.ndarray:
    """
    Select boundary edges of face regions

    Based on bpy.ops.mesh.region_to_loop

    Args:
        face_mask: Boolean array selecting face regions to convert to loops.

    Returns:
        Boolean array selecting edges that were converted to loops.
    """
    execute_mesh_op(
        bpy.ops.mesh.region_to_loop,
        obj,
        face_mask=face_mask,
    )

    return extract_edge_mask(obj)


# Conversion functions moved to ops.object.py


@pf.tracer.primitive(mutates=["mutates_obj"])
def bridge_edge_loops(
    mutates_obj: t.MeshObject,
    edge_mask: np.ndarray | None = None,
    type: Literal["SINGLE", "PAIRS", "FAN"] = "SINGLE",
    use_merge: bool = False,
    merge_factor: float = 0.5,
    twist_offset: int = 0,
    number_cuts: int = 0,
    interpolation: Literal["PATH", "SURFACE"] = "PATH",
    smoothness: float = 1.0,
    profile_shape_factor: float = 0.0,
    profile_shape: Literal[
        "SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE", "SHARP", "LINEAR"
    ] = "SMOOTH",
) -> None:
    """
    Create faces between two edge loops

    Based on bpy.ops.mesh.bridge_edge_loops

    Args:
        edge_mask: Boolean array selecting edges to bridge between.
    """
    execute_mesh_op(
        bpy.ops.mesh.bridge_edge_loops,
        mutates_obj,
        edge_mask=edge_mask,
        type=type,
        use_merge=use_merge,
        merge_factor=merge_factor,
        twist_offset=twist_offset,
        number_cuts=number_cuts,
        interpolation=interpolation,
        smoothness=smoothness,
        profile_shape_factor=profile_shape_factor,
        profile_shape=profile_shape,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def normals_make_consistent(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    inside: bool = False,
) -> None:
    """
    Make face normals point outside or inside

    Based on bpy.ops.mesh.normals_make_consistent

    Args:
        face_mask: Boolean array selecting faces to make consistent. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.normals_make_consistent,
        mutates_obj,
        face_mask=face_mask,
        inside=inside,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def remove_doubles(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    threshold: float = 0.0001,
    use_unselected: bool = False,
    use_sharp_edge_from_normals: bool = False,
) -> None:
    """
    Remove duplicate vertices

    Based on bpy.ops.mesh.remove_doubles

    Args:
        vertex_mask: Boolean array selecting vertices to check for duplicates. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.remove_doubles,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        threshold=threshold,
        use_unselected=use_unselected,
        use_sharp_edge_from_normals=use_sharp_edge_from_normals,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def quads_convert_to_tris(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    # quad_method: Literal[
    #    "BEAUTY", "FIXED", "FIXED_ALTERNATE", "SHORTEST_DIAGONAL"
    # ] = "BEAUTY",
    # ngon_method: Literal["BEAUTY", "CLIP"] = "BEAUTY",
) -> None:
    """
    Convert quad faces to triangular faces

    Based on bpy.ops.mesh.quads_convert_to_tris

    Args:
        face_mask: Boolean array selecting faces to convert. If None, operates on entire mesh.

    Note: quad_method and ngon_method not currently included, they are never used in infinigen
    but could be re-added if useful

    """
    execute_mesh_op(
        bpy.ops.mesh.quads_convert_to_tris,
        mutates_obj,
        face_mask=face_mask,
        quad_method="BEAUTY",
        ngon_method="BEAUTY",
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def separate_mask(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
) -> t.MeshObject:
    """
    Separate selected geometry into a new mesh

    Based on bpy.ops.mesh.separate

    Args:
        vertex_mask: Boolean array selecting vertices to separate.
        edge_mask: Boolean array selecting edges to separate.
        face_mask: Boolean array selecting faces to separate.

    Note: we dont currently support the type="MATERIAL" option, please extract this mask explicitly and pass it in.
    """
    execute_mesh_op(
        bpy.ops.mesh.separate,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        type="SELECTED",
    )

    assert len(bpy.context.selected_objects) == 2, (
        f"{mutates_obj.item().name=} {list(bpy.context.selected_objects)}"
    )
    result_obj = bpy.context.selected_objects[1]
    assert result_obj is not mutates_obj.item(), (
        f"{mutates_obj.item().name=} {result_obj.name=} {bpy.data.objects.keys()}"
    )
    return t.MeshObject(result_obj)


@pf.tracer.primitive(mutates=["mutates_obj"])
def separate_loose(
    mutates_obj: t.MeshObject,
) -> list[t.MeshObject]:
    """
    Separate loose mesh islands into new objects

    Based on bpy.ops.mesh.separate

    """
    execute_mesh_op(
        bpy.ops.mesh.separate,
        mutates_obj,
        type="LOOSE",
    )

    return [t.MeshObject(o) for o in bpy.context.selected_objects]


@pf.tracer.primitive(mutates=["mutates_obj"])
def fill_grid(
    mutates_obj: t.MeshObject,
    edge_mask: np.ndarray,
    span: int = 1,
    offset: int = 0,
    use_interp_simple: bool = False,
) -> None:
    """
    Fill grid from two edge loops

    Based on bpy.ops.mesh.fill_grid

    Args:
        edge_mask: Boolean array selecting edge loops to fill between.
    """
    execute_mesh_op(
        bpy.ops.mesh.fill_grid,
        mutates_obj,
        edge_mask=edge_mask,
        span=span,
        offset=offset,
        use_interp_simple=use_interp_simple,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def edge_face_add(
    mutates_obj: t.MeshObject,
    edge_mask: np.ndarray,
) -> None:
    """
    Add an edge or face to selected

    Based on bpy.ops.mesh.edge_face_add

    Args:
        edge_mask: Boolean array selecting edges to add faces to.
    """
    execute_mesh_op(
        bpy.ops.mesh.edge_face_add,
        mutates_obj,
        edge_mask=edge_mask,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def duplicate(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
):
    """
    Duplicate selected faces

    Args:
        mutate_obj: MeshObject providing source and destination geometry
        vertex_mask: If enabled, duplicate these vertices
        edge_mask: If enabled, duplicate these edges
        face_mask: If enabled, duplicate these faces

    Returns:
        mask over vertices edges or faces, depending on which mask was provided
    """
    execute_mesh_op(
        bpy.ops.mesh.duplicate,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
    )

    if vertex_mask is not None:
        return extract_vertex_mask(mutates_obj)
    if edge_mask is not None:
        return extract_edge_mask(mutates_obj)
    if face_mask is not None:
        return extract_face_mask(mutates_obj)
    return None


@pf.tracer.primitive(mutates=["mutates_obj"])
def extrude_faces(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    use_normal_flip: bool = False,
    use_dissolve_ortho_edges: bool = False,
    mirror: bool = False,
    value: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    orient_type: Literal[
        "GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR"
    ] = "GLOBAL",
    constraint_axis: Tuple[bool, bool, bool] = (False, False, False),
    **proportional_edit_kwargs: Unpack[ProportionalEditProperties],
) -> None:
    """
    Extrude region and move result

    Based on bpy.ops.mesh.extrude_region_move

    Args:
        face_mask: Boolean array selecting faces to extrude. If None, operates on entire mesh.
    """
    proportional_edit = ProportionalEditProperties(**proportional_edit_kwargs)
    execute_mesh_op(
        bpy.ops.mesh.extrude_region_move,
        mutates_obj,
        face_mask=face_mask,
        MESH_OT_extrude_region={
            "use_normal_flip": use_normal_flip,
            "use_dissolve_ortho_edges": use_dissolve_ortho_edges,
            "mirror": mirror,
        },
        TRANSFORM_OT_translate={
            "value": value,
            "orient_type": orient_type,
            "constraint_axis": constraint_axis,
            "mirror": mirror,
            "use_proportional_edit": proportional_edit.falloff is not None,
            "proportional_edit_falloff": proportional_edit.falloff or "SMOOTH",
            "proportional_size": proportional_edit.size,
            "use_proportional_connected": proportional_edit.connected,
            "use_proportional_projected": proportional_edit.projected,
        },
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def subdivide(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    number_cuts: int = 1,
    smoothness: float = 0.0,
    ngon: bool = True,
    quadcorner: Literal["STRAIGHT_CUT", "INNER_VERT", "PATH", "FAN"] = "STRAIGHT_CUT",
    fractal: float = 0.0,
    fractal_along_normal: float = 0.0,
    seed: int = 0,
) -> None:
    """
    Subdivide selected edges

    Based on bpy.ops.mesh.subdivide

    Args:
        face_mask: Boolean array selecting faces to subdivide. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.subdivide,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        number_cuts=number_cuts,
        smoothness=smoothness,
        ngon=ngon,
        quadcorner=quadcorner,
        fractal=fractal,
        fractal_along_normal=fractal_along_normal,
        seed=seed,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def unsubdivide(
    mutates_obj: t.MeshObject,
    iterations: int = 2,
) -> None:
    """
    Un-subdivide selected edges and faces

    Based on bpy.ops.mesh.unsubdivide

    Args:
        iterations: Number of times to un-subdivide.
    """
    execute_mesh_op(
        bpy.ops.mesh.unsubdivide,
        mutates_obj,
        iterations=iterations,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def inset(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    use_boundary: bool = True,
    use_even_offset: bool = True,
    use_relative_offset: bool = False,
    use_edge_rail: bool = False,
    thickness: float = 0.0,
    depth: float = 0.0,
    use_outset: bool = False,
    use_select_inset: bool = False,
    use_individual: bool = False,
    use_interpolate: bool = True,
) -> np.ndarray:
    """
    Inset new faces into selected faces

    Based on bpy.ops.mesh.inset

    # TODO: use_select_inset as np.array output

    Args:
        face_mask: Boolean array selecting faces to inset. If None, operates on entire mesh.

    Returns:
        Boolean array selecting faces that were inset.
    """

    execute_mesh_op(
        bpy.ops.mesh.inset,
        mutates_obj,
        face_mask=face_mask,
        use_boundary=use_boundary,
        use_even_offset=use_even_offset,
        use_relative_offset=use_relative_offset,
        use_edge_rail=use_edge_rail,
        thickness=thickness,
        depth=depth,
        use_outset=use_outset,
        use_select_inset=use_select_inset,
        use_individual=use_individual,
        use_interpolate=use_interpolate,
    )

    return extract_face_mask(mutates_obj)


@pf.tracer.primitive(mutates=["mutates_obj"])
def inset_individual(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    use_boundary: bool = True,
    use_even_offset: bool = True,
    use_relative_offset: bool = False,
    use_edge_rail: bool = False,
    thickness: float = 0.0,
    depth: float = 0.0,
    use_outset: bool = False,
    use_interpolate: bool = True,
):
    execute_mesh_op(
        bpy.ops.mesh.inset,
        mutates_obj,
        face_mask=face_mask,
        use_boundary=use_boundary,
        use_even_offset=use_even_offset,
        use_relative_offset=use_relative_offset,
        use_edge_rail=use_edge_rail,
        thickness=thickness,
        depth=depth,
        use_outset=use_outset,
        use_select_inset=False,
        use_individual=True,
        use_interpolate=use_interpolate,
    )

    return extract_face_mask(mutates_obj)


@pf.tracer.primitive(mutates=["mutates_obj"])
def bisect(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    plane_co: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    plane_no: Tuple[float, float, float] = (1.0, 0.0, 0.0),
    use_fill: bool = False,
    clear_inner: bool = False,
    clear_outer: bool = False,
    threshold: float = 0.0001,
    flip: bool = False,
) -> None:
    """
    Cut geometry along a plane

    Based on bpy.ops.mesh.bisect

    TODO: add edge_mask ?

    NOTE: xstart, xend, ystart, yend are not supported as these relate to UI input, please manually specify the plane_c

    Args:
        mutates_obj: MeshObject to bisect
        face_mask: Boolean array selecting faces to bisect. If None, operates on entire mesh.
        plane_co: Location of the plane
        plane_no: Normal of the plane
    """
    execute_mesh_op(
        bpy.ops.mesh.bisect,
        mutates_obj,
        face_mask=face_mask,
        plane_co=plane_co,
        plane_no=plane_no,
        use_fill=use_fill,
        clear_inner=clear_inner,
        clear_outer=clear_outer,
        threshold=threshold,
        flip=flip,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def convex_hull(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    delete_unused: bool = True,
    use_existing_faces: bool = True,
    make_holes: bool = False,
    join_triangles: bool = True,
    face_threshold: float = 0.698132,
    shape_threshold: float = 0.698132,
    uvs: bool = False,
    vcols: bool = False,
    seam: bool = False,
    sharp: bool = False,
    materials: bool = False,
) -> None:
    """
    Enclose selected vertices in a convex hull

    Based on bpy.ops.mesh.convex_hull

    Args:
        vertex_mask: Boolean array selecting vertices for hull computation. If None, operates on entire mesh.
    """
    bpy.context.view_layer.objects.active = mutates_obj.item()
    execute_mesh_op(
        bpy.ops.mesh.convex_hull,
        mutates_obj,
        vertex_mask=vertex_mask,
        delete_unused=delete_unused,
        use_existing_faces=use_existing_faces,
        make_holes=make_holes,
        join_triangles=join_triangles,
        face_threshold=face_threshold,
        shape_threshold=shape_threshold,
        uvs=uvs,
        vcols=vcols,
        seam=seam,
        sharp=sharp,
        materials=materials,
    )


@dataclass
class BevelProperties:
    offset: float = 0.1
    offset_pct: float = 0.1
    offset_type: Literal["OFFSET", "WIDTH", "DEPTH", "PERCENT", "ABSOLUTE"] = "OFFSET"
    profile_type: Literal["SUPERELLIPSE", "CUSTOM"] = "SUPERELLIPSE"
    segments: int = 1
    profile: float = 0.5
    clamp_overlap: bool = False
    loop_slide: bool = True
    mark_seam: bool = False
    mark_sharp: bool = False
    material: int = -1
    harden_normals: bool = False
    face_strength_mode: Literal["NONE", "NEW", "AFFECTED", "ALL"] = "NONE"
    miter_outer: Literal["SHARP", "PATCH", "ARC"] = "SHARP"
    miter_inner: Literal["SHARP", "ARC"] = "SHARP"
    spread: float = 0.1
    vmesh_method: Literal["ADJ", "CUTOFF"] = "ADJ"


@pf.tracer.primitive(mutates=["mutates_obj"])
def bevel_vertices(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    **kwargs: Unpack[BevelProperties],
) -> None:
    """
    Cut into selected items at an angle to create bevel or chamfer

    Based on bpy.ops.mesh.bevel

    Args:
        vertex_mask: Boolean array selecting vertices to bevel. If None, operates on entire mesh.
    """
    bevel = BevelProperties(**kwargs)
    execute_mesh_op(
        bpy.ops.mesh.bevel,
        mutates_obj,
        vertex_mask=vertex_mask,
        affect="VERTICES",
        **asdict(bevel),
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def bevel_edges(
    mutates_obj: t.MeshObject,
    edge_mask: np.ndarray | None = None,
    **kwargs: Unpack[BevelProperties],
) -> None:
    """
    Cut into selected items at an angle to create bevel or chamfer

    Based on bpy.ops.mesh.bevel

    Args:
        edge_mask: Boolean array selecting edges to bevel. If None, operates on entire mesh.
    """
    bevel = BevelProperties(**kwargs)
    execute_mesh_op(
        bpy.ops.mesh.bevel,
        mutates_obj,
        edge_mask=edge_mask,
        affect="EDGES",
        **asdict(bevel),
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def select_loose(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    extend: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Select loose geometry.

    Based on bpy.ops.mesh.select_loose

    Returns:
        Tuple of (vertex_mask, edge_mask, face_mask) of the resulting selection.
    """
    execute_mesh_op(
        bpy.ops.mesh.select_loose,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        empty_mask_mode="execute",
        extend=extend,
    )
    return (
        extract_vertex_mask(mutates_obj),
        extract_edge_mask(mutates_obj),
        extract_face_mask(mutates_obj),
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def select_more(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    use_face_step: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Select more vertices, edges or faces connected to current selection.

    Based on bpy.ops.mesh.select_more

    Returns:
        Tuple of (vertex_mask, edge_mask, face_mask) of the resulting selection.
    """
    execute_mesh_op(
        bpy.ops.mesh.select_more,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        empty_mask_mode="execute",
        use_face_step=use_face_step,
    )
    return (
        extract_vertex_mask(mutates_obj),
        extract_edge_mask(mutates_obj),
        extract_face_mask(mutates_obj),
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def loop_multi_select(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    ring: bool = False,
) -> np.ndarray:
    """
    Select a loop of connected edges by connection type.

    Based on bpy.ops.mesh.loop_multi_select

    Args:
        ring: If True, select edge rings instead of edge loops.

    Returns:
        Boolean edge mask of the resulting selection.
    """
    execute_mesh_op(
        bpy.ops.mesh.loop_multi_select,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        empty_mask_mode="execute",
        ring=ring,
    )
    return extract_edge_mask(mutates_obj)


@pf.tracer.primitive(mutates=["mutates_obj"])
def fill(
    mutates_obj: t.MeshObject,
    edge_mask: np.ndarray | None = None,
    use_beauty: bool = True,
) -> None:
    """
    Fill a selected edge loop with faces

    Based on bpy.ops.mesh.fill

    Args:
        edge_mask: Boolean array selecting edge loop to fill.
    """
    execute_mesh_op(
        bpy.ops.mesh.fill,
        mutates_obj,
        edge_mask=edge_mask,
        use_beauty=use_beauty,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def poke(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    offset: float = 0.0,
    use_relative_offset: bool = False,
    center_mode: Literal["MEDIAN_WEIGHTED", "MEDIAN", "BOUNDS"] = "MEDIAN_WEIGHTED",
) -> None:
    """
    Split selected faces into individual triangles

    Based on bpy.ops.mesh.poke

    Args:
        face_mask: Boolean array selecting faces to poke.
    """
    execute_mesh_op(
        bpy.ops.mesh.poke,
        mutates_obj,
        face_mask=face_mask,
        offset=offset,
        use_relative_offset=use_relative_offset,
        center_mode=center_mode,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def flip_normals(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    only_clnors: bool = False,
) -> None:
    """
    Flip the direction of selected faces' normals

    Based on bpy.ops.mesh.flip_normals

    Args:
        face_mask: Boolean array selecting faces to flip normals. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.flip_normals,
        mutates_obj,
        face_mask=face_mask,
        only_clnors=only_clnors,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def extrude_faces_shrink_fatten(
    mutates_obj: t.MeshObject,
    use_normal_flip: bool = False,
    use_dissolve_ortho_edges: bool = False,
    mirror: bool = False,
    value: float = 0.0,
    use_even_offset: bool = False,
    snap: bool = False,
    use_accurate: bool = False,
    face_mask: np.ndarray | None = None,
    **proportional_edit_kwargs: Unpack[ProportionalEditProperties],
) -> None:
    """
    Extrude region and shrink/fatten

    Based on bpy.ops.mesh.extrude_region_shrink_fatten

    Args:
        face_mask: Boolean array selecting faces to extrude. If None, operates on entire mesh.
    """
    proportional_edit = ProportionalEditProperties(**proportional_edit_kwargs)
    execute_mesh_op(
        bpy.ops.mesh.extrude_region_shrink_fatten,
        mutates_obj,
        face_mask=face_mask,
        MESH_OT_extrude_region={
            "use_normal_flip": use_normal_flip,
            "use_dissolve_ortho_edges": use_dissolve_ortho_edges,
            "mirror": mirror,
        },
        TRANSFORM_OT_shrink_fatten={
            "value": value,
            "use_even_offset": use_even_offset,
            "mirror": mirror,
            "use_proportional_edit": proportional_edit.falloff is not None,
            "proportional_edit_falloff": proportional_edit.falloff or "SMOOTH",
            "proportional_size": proportional_edit.size,
            "use_proportional_connected": proportional_edit.connected,
            "use_proportional_projected": proportional_edit.projected,
            "snap": snap,
            "use_accurate": use_accurate,
        },
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def tris_convert_to_quads(
    mutates_obj: t.MeshObject,
    face_threshold: float = 0.698132,
    shape_threshold: float = 0.698132,
    uvs: bool = False,
    vcols: bool = False,
    seam: bool = False,
    sharp: bool = False,
    materials: bool = False,
    face_mask: np.ndarray | None = None,
) -> None:
    """
    Convert triangles to quads

    Based on bpy.ops.mesh.tris_convert_to_quads

    Args:
        face_mask: Boolean array selecting faces to convert. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.tris_convert_to_quads,
        mutates_obj,
        face_mask=face_mask,
        face_threshold=face_threshold,
        shape_threshold=shape_threshold,
        uvs=uvs,
        vcols=vcols,
        seam=seam,
        sharp=sharp,
        materials=materials,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def merge(
    mutates_obj: t.MeshObject,
    type: Literal["CENTER", "CURSOR", "COLLAPSE"] = "CENTER",
    uvs: bool = False,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
) -> None:
    """
    Merge selected vertices

    Based on bpy.ops.mesh.merge

    Args:
        vertex_mask: Boolean array selecting vertices to merge. At most one can be provided. If all are None, operates on entire mesh.
        edge_mask: Boolean array selecting edges to merge. At most one can be provided. If all are None, operates on entire mesh.
        face_mask: Boolean array selecting faces to merge. At most one can be provided. If all are None, operates on entire mesh.

    Note: Only one of vertex_mask, edge_mask, or face_mask should be provided.
    """
    execute_mesh_op(
        bpy.ops.mesh.merge,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        type=type,
        uvs=uvs,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def mark_sharp(
    mutates_obj: t.MeshObject,
    clear: bool = False,
    use_verts: bool = False,
    edge_mask: np.ndarray | None = None,
) -> None:
    """
    Mark selected edges as sharp

    Based on bpy.ops.mesh.mark_sharp

    Args:
        edge_mask: Boolean array selecting edges to mark/unmark as sharp. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.mark_sharp,
        mutates_obj,
        edge_mask=edge_mask,
        clear=clear,
        use_verts=use_verts,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def dissolve_limited(
    mutates_obj: t.MeshObject,
    angle_limit: float = 0.0872665,
    use_dissolve_boundaries: bool = False,
    delimit: set[Literal["NORMAL", "MATERIAL", "SEAM", "SHARP", "UV"]] = {"NORMAL"},
    edge_mask: np.ndarray | None = None,
) -> None:
    """
    Dissolve selected edges and faces limited by the angle of adjacent faces

    Based on bpy.ops.mesh.dissolve_limited

    Args:
        edge_mask: Boolean array selecting edges to dissolve. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.dissolve_limited,
        mutates_obj,
        angle_limit=angle_limit,
        use_dissolve_boundaries=use_dissolve_boundaries,
        delimit=delimit,
        edge_mask=edge_mask,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def extrude_vertices(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray,
    mirror: bool = False,
    value: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    orient_type: Literal[
        "GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR"
    ] = "GLOBAL",
    constraint_axis: Tuple[bool, bool, bool] = (False, False, False),
    **kwargs: Unpack[ProportionalEditProperties],
) -> None:
    """
    Extrude individual vertices and move

    Based on bpy.ops.mesh.extrude_vertices_move

    Args:
        vertex_mask: Boolean array selecting vertices to extrude. If None, operates on entire mesh.
    """
    proportional_edit = ProportionalEditProperties(**kwargs)

    execute_mesh_op(
        bpy.ops.mesh.extrude_vertices_move,
        mutates_obj,
        vertex_mask=vertex_mask,
        MESH_OT_extrude_verts_indiv={
            "mirror": mirror,
        },
        TRANSFORM_OT_translate={
            "value": value,
            "orient_type": orient_type,
            "constraint_axis": constraint_axis,
            "mirror": mirror,
            "use_proportional_edit": proportional_edit.falloff is not None,
            "proportional_edit_falloff": proportional_edit.falloff or "SMOOTH",
            "proportional_size": proportional_edit.size,
            "use_proportional_connected": proportional_edit.connected,
            "use_proportional_projected": proportional_edit.projected,
        },
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def fill_holes(
    mutates_obj: t.MeshObject,
    sides: int = 4,
) -> None:
    """
    Fill in holes (boundary edge loops)

    Based on bpy.ops.mesh.fill_holes
    """
    execute_mesh_op(
        bpy.ops.mesh.fill_holes,
        mutates_obj,
        sides=sides,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def spin(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    steps: int = 12,
    dupli: bool = False,
    angle: float = 1.5708,
    use_auto_merge: bool = True,
    use_normal_flip: bool = False,
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    axis: Tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> None:
    """
    Extrude selected vertices in a circle around the cursor in indicated viewport

    Based on bpy.ops.mesh.spin

    Args:
        vertex_mask: Boolean array selecting vertices to extrude in spin. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.spin,
        mutates_obj,
        steps=steps,
        dupli=dupli,
        angle=angle,
        use_auto_merge=use_auto_merge,
        use_normal_flip=use_normal_flip,
        center=center,
        axis=axis,
        vertex_mask=vertex_mask,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def vertices_smooth(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    factor: float = 0.5,
    repeat: int = 1,
    xaxis: bool = True,
    yaxis: bool = True,
    zaxis: bool = True,
) -> None:
    """
    Flatten angles of selected vertices

    Based on bpy.ops.mesh.vertices_smooth

    Args:
        vertex_mask: Boolean array selecting vertices to smooth. If None, operates on entire mesh.
    """
    execute_mesh_op(
        bpy.ops.mesh.vertices_smooth,
        mutates_obj,
        factor=factor,
        repeat=repeat,
        xaxis=xaxis,
        yaxis=yaxis,
        zaxis=zaxis,
        wait_for_input=False,
        vertex_mask=vertex_mask,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def split_nonplanar_faces(
    mutates_obj: t.MeshObject,
    face_mask: np.ndarray | None = None,
    angle_limit_rad: float = 0.0872665,
):
    """
    Split nonplanar faces into new faces
    """
    execute_mesh_op(
        bpy.ops.mesh.vert_connect_nonplanar,
        mutates_obj,
        face_mask=face_mask,
        angle_limit=angle_limit_rad,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def edges_select_sharp(
    mutates_obj: t.MeshObject,
    sharpness: float = 0.523599,
) -> np.ndarray:
    """
    Select all sharp enough edges

    Based on bpy.ops.mesh.edges_select_sharp
    """
    execute_mesh_op(
        bpy.ops.mesh.edges_select_sharp,
        mutates_obj,
        sharpness=sharpness,
        edge_mask=np.zeros(len(mutates_obj.item().data.edges), dtype=bool),
        empty_mask_mode="execute",
    )
    return extract_edge_mask(mutates_obj)


@pf.tracer.primitive(mutates=["mutates_obj"])
def select_nth(
    mutates_obj: t.MeshObject,
    domain: Literal["VERT", "EDGE", "FACE"] = "FACE",
    skip: int = 1,
    nth: int = 1,
    offset: int = 0,
) -> np.ndarray:
    """
    Deselect every Nth element starting from the active vertex, edge or face.

    Based on bpy.ops.mesh.select_nth

    Parameters:
        domain: Which element type to operate on.
        skip: Number of deselected elements in the repetitive sequence.
        nth: Number of selected elements in the repetitive sequence.
        offset: Offset from the starting point.

    Returns:
        Boolean mask of the selected elements after the operation.
    """
    if domain == "VERT":
        mask = np.ones(len(mutates_obj.item().data.vertices), dtype=bool)
        execute_mesh_op(
            bpy.ops.mesh.select_nth,
            mutates_obj,
            vertex_mask=mask,
            skip=skip,
            nth=nth,
            offset=offset,
        )
        return extract_vertex_mask(mutates_obj)
    elif domain == "EDGE":
        mask = np.ones(len(mutates_obj.item().data.edges), dtype=bool)
        execute_mesh_op(
            bpy.ops.mesh.select_nth,
            mutates_obj,
            edge_mask=mask,
            skip=skip,
            nth=nth,
            offset=offset,
        )
        return extract_edge_mask(mutates_obj)
    else:
        mask = np.ones(len(mutates_obj.item().data.polygons), dtype=bool)
        execute_mesh_op(
            bpy.ops.mesh.select_nth,
            mutates_obj,
            face_mask=mask,
            skip=skip,
            nth=nth,
            offset=offset,
        )
        return extract_face_mask(mutates_obj)


@pf.tracer.primitive(mutates=["mutates_obj"])
def edge_split(
    mutates_obj: t.MeshObject,
    edge_mask: np.ndarray | None = None,
    type: Literal["EDGE", "VERT"] = "EDGE",
):
    execute_mesh_op(
        bpy.ops.mesh.edge_split,
        mutates_obj,
        edge_mask=edge_mask,
        type=type,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def symmetrize(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    direction: Literal[
        "NEGATIVE_X",
        "POSITIVE_X",
        "NEGATIVE_Y",
        "POSITIVE_Y",
        "NEGATIVE_Z",
        "POSITIVE_Z",
    ] = "NEGATIVE_X",
    threshold: int | float | None = 0.001,
):
    execute_mesh_op(
        bpy.ops.mesh.symmetrize,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        direction=direction,
        threshold=threshold,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def subdivide_edgering(
    mutates_obj: t.MeshObject,
    edge_mask: np.ndarray | None = None,
    number_cuts: int = 10,
    interpolation: Literal["PATH", "SMOOTH", "SPHERE", "CREASE", "FIRE"] = "PATH",
    smoothness: float = 1.0,
    profile_shape_factor: float = 0.0,
    profile_shape: Literal["SMOOTH", "SPHERE"] = "SMOOTH",
):
    execute_mesh_op(
        bpy.ops.mesh.subdivide_edgering,
        mutates_obj,
        edge_mask=edge_mask,
        number_cuts=number_cuts,
        interpolation=interpolation,
        smoothness=smoothness,
        profile_shape_factor=profile_shape_factor,
        profile_shape=profile_shape,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def move(
    mutates_obj: t.MeshObject,
    value: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    orient_type: Literal[
        "GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR"
    ] = "GLOBAL",
    constraint_axis: Tuple[bool, bool, bool] = (False, False, False),
    mirror: bool = False,
    **proportional_edit_kwargs: Unpack[ProportionalEditProperties],
) -> None:
    """
    Move selected geometry

    Based on bpy.ops.transform.translate
    """
    proportional_edit = ProportionalEditProperties(**proportional_edit_kwargs)
    execute_mesh_op(
        bpy.ops.transform.translate,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        value=value,
        orient_type=orient_type,
        constraint_axis=constraint_axis,
        mirror=mirror,
        use_proportional_edit=proportional_edit.falloff is not None,
        proportional_edit_falloff=proportional_edit.falloff or "SMOOTH",
        proportional_size=proportional_edit.size,
        use_proportional_connected=proportional_edit.connected,
        use_proportional_projected=proportional_edit.projected,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def rotate(
    mutates_obj: t.MeshObject,
    value: float = 0.0,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    orient_axis: Literal["X", "Y", "Z"] = "Z",
    orient_type: Literal[
        "GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR"
    ] = "GLOBAL",
    constraint_axis: Tuple[bool, bool, bool] = (False, False, False),
    mirror: bool = False,
    **proportional_edit_kwargs: Unpack[ProportionalEditProperties],
) -> None:
    """
    Rotate selected geometry

    Based on bpy.ops.transform.rotate
    """
    proportional_edit = ProportionalEditProperties(**proportional_edit_kwargs)
    execute_mesh_op(
        bpy.ops.transform.rotate,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        value=value,
        orient_axis=orient_axis,
        orient_type=orient_type,
        constraint_axis=constraint_axis,
        mirror=mirror,
        use_proportional_edit=proportional_edit.falloff is not None,
        proportional_edit_falloff=proportional_edit.falloff or "SMOOTH",
        proportional_size=proportional_edit.size,
        use_proportional_connected=proportional_edit.connected,
        use_proportional_projected=proportional_edit.projected,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def resize(
    mutates_obj: t.MeshObject,
    value: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    orient_type: Literal[
        "GLOBAL", "LOCAL", "NORMAL", "GIMBAL", "VIEW", "CURSOR"
    ] = "GLOBAL",
    constraint_axis: Tuple[bool, bool, bool] = (False, False, False),
    mirror: bool = False,
    **proportional_edit_kwargs: Unpack[ProportionalEditProperties],
) -> None:
    """
    Resize selected geometry

    Based on bpy.ops.transform.resize
    """
    proportional_edit = ProportionalEditProperties(**proportional_edit_kwargs)
    execute_mesh_op(
        bpy.ops.transform.resize,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        value=value,
        orient_type=orient_type,
        constraint_axis=constraint_axis,
        mirror=mirror,
        use_proportional_edit=proportional_edit.falloff is not None,
        proportional_edit_falloff=proportional_edit.falloff or "SMOOTH",
        proportional_size=proportional_edit.size,
        use_proportional_connected=proportional_edit.connected,
        use_proportional_projected=proportional_edit.projected,
    )


@pf.tracer.primitive(mutates=["mutates_obj"])
def dissolve_verts(
    mutates_obj: t.MeshObject,
    vertex_mask: np.ndarray | None = None,
    edge_mask: np.ndarray | None = None,
    face_mask: np.ndarray | None = None,
    use_face_split: bool = False,
    use_boundary_tear: bool = False,
):
    execute_mesh_op(
        bpy.ops.mesh.dissolve_verts,
        mutates_obj,
        vertex_mask=vertex_mask,
        edge_mask=edge_mask,
        face_mask=face_mask,
        use_face_split=use_face_split,
        use_boundary_tear=use_boundary_tear,
    )
