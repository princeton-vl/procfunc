from typing import Literal

import bpy
import numpy as np

from procfunc import types as t

SplineType = Literal["POLY", "BEZIER", "NURBS"]


def curve_circle(radius: float = 1.0):
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius)
    return t.CurveObject(bpy.context.active_object)


def curve_bezier():
    bpy.ops.curve.primitive_bezier_curve_add()
    return t.CurveObject(bpy.context.active_object)


def _add_spline(
    curve_data: bpy.types.Curve,
    points: list[t.Vector] | np.ndarray,
    spline_type: SplineType = "POLY",
) -> None:
    """Add a single spline with the given points to *curve_data*."""
    spline = curve_data.splines.new(spline_type)
    assert len(points) > 0, "There should be at least one point"
    spline.points.add(len(points) - 1)
    for i, coord in enumerate(points):
        spline.points[i].co = (*coord, 1)


def curve_line(
    points: list[t.Vector] | np.ndarray,
    dimensions="3D",
    resolution_u=12,
    spline_type: SplineType = "POLY",
) -> t.CurveObject:
    """Create a curve object containing a single spline through *points*."""
    if dimensions != "3D":
        raise NotImplementedError(
            f"dimensions={dimensions!r} is not yet supported, only '3D' is implemented"
        )
    if resolution_u != 12:
        raise NotImplementedError(
            f"resolution_u={resolution_u!r} is not yet supported, only 12 is implemented"
        )
    curve = bpy.data.curves.new(curve_line.__name__, type="CURVE")
    _add_spline(curve, points, spline_type)
    obj = bpy.data.objects.new(curve_line.__name__, curve)
    bpy.context.scene.collection.objects.link(obj)
    return t.CurveObject(obj)


def curve_splines(
    splines: list[list[t.Vector] | np.ndarray],
    spline_type: SplineType = "POLY",
) -> t.CurveObject:
    """Create a curve object containing multiple splines.

    Args:
        splines: List of point lists, one per spline.
        spline_type: Spline interpolation type for all splines.
    """
    curve = bpy.data.curves.new(curve_splines.__name__, type="CURVE")
    for points in splines:
        _add_spline(curve, points, spline_type)
    obj = bpy.data.objects.new(curve_splines.__name__, curve)
    bpy.context.scene.collection.objects.link(obj)
    return t.CurveObject(obj)
