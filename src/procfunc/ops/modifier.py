from typing import Literal, Tuple

from procfunc import types as t
from procfunc.tracer import primitive

from ._util import modify


def subdivide_surface(
    levels: int = 2,
    _skip_apply: bool = False,
    """
    Apply subdivision surface modifier.

    We disallow render_levels since this function is automatically executed & fully "applied"
    """
        "SUBSURF",
        levels=levels,
        render_levels=levels,
        _skip_apply=_skip_apply,


def solidify(
    thickness: float = 0.01,
    """Apply solidify modifier."""
        "SOLIDIFY",
        thickness=thickness,
        offset=offset,


def bevel(
    width: float = 0.01,
    segments: int = 1,
    """Apply bevel modifier."""
    return modify(mutates_obj, "BEVEL", width=width, segments=segments)


def _boolean(
    target: t.MeshObject | t.Collection,
    operation: Literal["DIFFERENCE", "INTERSECT", "UNION"],
    threshold: float = 1e-6,
    fast: bool = True,
    hole_tolerant: bool = False,
    self_intersect: bool = False,
    if isinstance(target, t.Collection):
        target_kwargs = {
            "collection": target,
            "operand_type": "COLLECTION",
    elif isinstance(target, t.MeshObject):
        target_kwargs = {
            "object": target,
            "operand_type": "OBJECT",
    else:
        raise ValueError(f"Invalid target type: {type(target)}")

        "BOOLEAN",
        operation=operation,
        solver="FAST" if fast else "EXACT",
        use_hole_tolerant=hole_tolerant,
        use_self=self_intersect,
        **target_kwargs,


@primitive(mutates=["mutates_obj"])
def boolean_difference(
    mutates_obj: t.MeshObject,
    target: t.MeshObject | t.Collection,
    threshold: float = 1e-6,
    fast: bool = True,
    hole_tolerant: bool = False,
    self_intersect: bool = False,
):
    """Apply boolean difference modifier."""
    return _boolean(
        target,
        operation="DIFFERENCE",
        fast=fast,
        hole_tolerant=hole_tolerant,
        self_intersect=self_intersect,


@primitive(mutates=["mutates_obj"])
def boolean_intersect(
    mutates_obj: t.MeshObject,
    target: t.MeshObject | t.Collection,
    threshold: float = 1e-6,
    fast: bool = True,
    hole_tolerant: bool = False,
    self_intersect: bool = False,
):
    """Apply boolean intersect modifier."""
    return _boolean(
        mutates_obj,
        target,
        operation="INTERSECT",
        fast=fast,
        hole_tolerant=hole_tolerant,
        self_intersect=self_intersect,


@primitive(mutates=["mutates_obj"])
def boolean_union(
    mutates_obj: t.MeshObject,
    target: t.MeshObject,
    threshold: float = 1e-6,
    fast: bool = True,
    hole_tolerant: bool = False,
    self_intersect: bool = False,
):
    """Apply boolean union modifier."""
    return _boolean(
        mutates_obj,
        target,
        operation="UNION",
        fast=fast,
        hole_tolerant=hole_tolerant,
        self_intersect=self_intersect,
    )


@primitive(mutates=["mutates_obj"])
def mirror(
    mutates_obj: t.MeshObject,
    use_axis: Tuple[bool, bool, bool] = (True, False, False),
    use_bisect_axis: Tuple[bool, bool, bool] = (False, False, False),
    use_bisect_flip_axis: Tuple[bool, bool, bool] = (False, False, False),
    merge_threshold: float = 0.0,
):
    """
    Apply mirror modifier.

    TODO: May also be applicable to t.CurveObject
    """
        mutates_obj,
        "MIRROR",
        use_axis=use_axis,
        use_bisect_axis=use_bisect_axis,
        use_bisect_flip_axis=use_bisect_flip_axis,
        use_mirror_merge=merge_threshold > 0,
        merge_threshold=merge_threshold,
    )


@primitive(mutates=["mutates_obj"])
def array(
    mutates_obj: t.MeshObject,
    count: int = 2,
    merge_threshold: float = 0.0,
):
    """Apply array modifier."""
    if relative_offset_displace is not None and constant_offset_displace is not None:
        raise ValueError(
            "Cannot specify both relative_offset_displace and constant_offset_displace"
        )
        }
        }
    return modify(
        mutates_obj,
        "ARRAY",
        count=count,
        merge_threshold=merge_threshold,
        use_merge_vertices=merge_threshold > 0,
    )


@primitive(mutates=["mutates_obj"])
def decimate_collapse(
    mutates_obj: t.MeshObject,
    ratio: float = 0.5,
    #    decimate_type: Literal["COLLAPSE", "UNSUBDIV", "DISSOLVE"] = "COLLAPSE",
):
    """
    Apply decimate modifier.

    TODO: we will add other modes e.g. DISSOLVE and UNSUBDIV at a later date if proven necessary
    """
    return modify(
        mutates_obj,
        "DECIMATE",
        ratio=ratio,
        decimate_type="COLLAPSE",
    )


@primitive(mutates=["mutates_obj"])
def smooth(
    mutates_obj: t.MeshObject,
    iterations: int = 1,
    factor: float = 0.5,
):
    """Apply smooth modifier."""
    return modify(
        mutates_obj,
        "SMOOTH",
        iterations=iterations,
        factor=factor,
    )


@primitive(mutates=["mutates_obj"])
def wireframe(
    mutates_obj: t.MeshObject,
    thickness: float = 0.01,
    use_boundary: bool = True,
    use_replace: bool = False,
):
    """Apply wireframe modifier."""
    return modify(
        mutates_obj,
        "WIREFRAME",
        thickness=thickness,
        use_boundary=use_boundary,
        use_replace=use_replace,
    )


@primitive(mutates=["mutates_obj"])
def triangulate(
    mutates_obj: t.MeshObject,
    quad_method: Literal[
        "BEAUTY", "FIXED", "FIXED_ALTERNATIVE", "SHORTEST_DIAGONAL", "LONGEST_DIAGONAL"
    ] = "BEAUTY",
    ngon_method: Literal["BEAUTY", "CLIP"] = "BEAUTY",
    min_vertices=4,
):
    """Apply triangulate modifier."""
    return modify(
        mutates_obj,
        "TRIANGULATE",
        quad_method=quad_method,
        ngon_method=ngon_method,
        min_vertices=min_vertices,
    )


@primitive(mutates=["mutates_obj"])
def remesh_voxel(
    mutates_obj: t.MeshObject,
    voxel_size: float = 0.1,
):
    """
    Apply remesh modifier.

    TODO: we will add other modes e.g. BLOCKS and SMOOTH at a later date if proven necessary
    """
    return modify(
        mutates_obj,
    )


@primitive(mutates=["mutates_obj"])
    mutates_obj: t.MeshObject,
):
    return modify(
        mutates_obj,
        threshold=threshold,
    )


@primitive(mutates=["mutates_obj"])
    mutates_obj: t.MeshObject,
    threshold: float = 1.0,
):
    return modify(
        mutates_obj,
        threshold=threshold,
    )


@primitive(mutates=["mutates_obj"])
    mutates_obj: t.MeshObject,
    threshold: float = 1.0,
):
    return modify(
        mutates_obj,
        threshold=threshold,
    )


@primitive(mutates=["mutates_obj"])
def skin(
    mutates_obj: t.MeshObject,
    use_smooth_shade: bool = True,
):
    """Apply skin modifier."""
    return modify(mutates_obj, "SKIN", use_smooth_shade=use_smooth_shade)


@primitive(mutates=["mutates_obj"])
def screw(
    mutates_obj: t.MeshObject,
    angle: float = 6.28318,  # 2*pi radians = 360 degrees
    iterations: int = 1,
    screw_offset: float = 0,
):
    """Apply screw modifier."""
    return modify(
        mutates_obj,
        "SCREW",
        angle=angle,
        iterations=iterations,
        screw_offset=screw_offset,
    )


@primitive(mutates=["mutates_obj"])
def weld(
    mutates_obj: t.MeshObject,
    merge_threshold: float = 0.001,
    mode: Literal["ALL", "CONNECTED"] = "ALL",
):
    """Apply weld modifier."""
    return modify(
        mutates_obj,
        "WELD",
        merge_threshold=merge_threshold,
        mode=mode,
    )


@primitive(mutates=["mutates_obj"])
def corrective_smooth(
    mutates_obj: t.MeshObject,
    iterations: int = 1,
    smooth_type: Literal["SIMPLE", "LENGTH_WEIGHTED"] = "SIMPLE",
):
    """Apply corrective smooth modifier."""
    return modify(
        mutates_obj,
        "CORRECTIVE_SMOOTH",
        iterations=iterations,
        smooth_type=smooth_type,
    )


@primitive(mutates=["mutates_obj"])
def edge_split(
    mutates_obj: t.MeshObject,
    use_edge_angle: bool = True,
    split_angle: float = 0.523599,
):
    """Apply edge split modifier."""
    return modify(
        mutates_obj,
        "EDGE_SPLIT",
        use_edge_angle=use_edge_angle,
        split_angle=split_angle,
    )


@primitive(mutates=["mutates_obj"])
    mutates_obj: t.MeshObject,
):
    return modify(
        mutates_obj,
    )


@primitive(mutates=["mutates_obj"])
def shrinkwrap(
    mutates_obj: t.MeshObject,
    target: t.MeshObject,
    # wrap_method: Literal["NEAREST_SURFACEPOINT", "NEAREST_VERTEX", "PROJECT", "TARGET_PROJECT"] = "NEAREST_SURFACEPOINT",
):
    """Apply shrinkwrap modifier."""
    return modify(
        mutates_obj,
        "SHRINKWRAP",
        target=target,
        wrap_method="NEAREST_SURFACEPOINT",
    )


@primitive(mutates=["mutates_obj"])
def displacement(
    mutates_obj: t.MeshObject,
    texture: t.Texture | None = None,
    strength: float = 1.0,
    direction: Literal[
        "X", "Y", "Z", "NORMAL", "CUSTOM_NORMAL", "RGB_TO_XYZ"
    ] = "NORMAL",
    space: Literal["LOCAL", "GLOBAL"] = "LOCAL",
    texture_coords: Literal["LOCAL", "GLOBAL", "OBJECT", "UV"] = "LOCAL",
):
    """Apply displacement modifier."""
    kwargs = {}
    if texture_coords == "OBJECT" and texture_coords_object is not None:
        kwargs["texture_coords_object"] = texture_coords_object

    return modify(
        mutates_obj,
        "DISPLACE",
        texture=texture,
        strength=strength,
        **kwargs,
    )


@primitive(mutates=["mutates_obj"])
def laplacian_smooth(
    mutates_obj: t.MeshObject,
    iterations: int = 1,
    lambda_factor: float = 1.0,
    lambda_border: float = 1.0,
):
    """Apply Laplacian smooth modifier."""
    return modify(
        mutates_obj,
        "LAPLACIANSMOOTH",
        iterations=iterations,
        lambda_factor=lambda_factor,
        lambda_border=lambda_border,
    )


'''
@primitive(mutates=["mutates_obj"])
def collision(
    mutates_obj: t.MeshObject,
):
    """Apply collision modifier."""
    return _modify(mutates_obj, "COLLISION")
'''

__all__ = [
    "array",
    "bevel",
    "boolean_difference",
    "boolean_intersect",
    "boolean_union",
    "corrective_smooth",
    "decimate_collapse",
    "displacement",
    "edge_split",
    "laplacian_smooth",
    "mirror",
    "remesh_voxel",
    "screw",
    "shrinkwrap",
    "skin",
    "smooth",
    "solidify",
    "subdivide_surface",
    "triangulate",
    "weld",
    "wireframe",
]
