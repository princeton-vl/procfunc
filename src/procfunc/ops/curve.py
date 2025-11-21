import bpy

import procfunc as pf
from procfunc import types as t


@pf.tracer.primitive(mutates=["mutates_obj"])
def subdivide(
    mutates_obj: t.CurveObject,
    number_cuts: int = 1,
) -> None:
    """
    Based on bpy.ops.curve.subdivide
    Subdivide selected segments
    """
    bpy.context.view_layer.objects.active = mutates_obj.item()
    bpy.ops.curve.subdivide(number_cuts=number_cuts)
