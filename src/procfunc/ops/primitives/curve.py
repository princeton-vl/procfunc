
import bpy
import numpy as np

from procfunc import types as t



def curve_circle(radius: float = 1.0):
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius)
    return t.CurveObject(bpy.context.active_object)


def curve_bezier():
    bpy.ops.curve.primitive_bezier_curve_add()
    return t.CurveObject(bpy.context.active_object)




    if dimensions != "3D":
        raise NotImplementedError(
            f"dimensions={dimensions!r} is not yet supported, only '3D' is implemented"
        )
    if resolution_u != 12:
        raise NotImplementedError(
            f"resolution_u={resolution_u!r} is not yet supported, only 12 is implemented"
        )



