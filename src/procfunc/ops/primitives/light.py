from typing import Literal

import bpy
import numpy as np

from procfunc import types as t
from procfunc.tracer import primitive as tracer_primitive


@tracer_primitive
def point_lamp(
    energy: float = 10.0,
    color: tuple = (1.0, 1.0, 1.0),
    shadow_soft_size: float = 0.0,
    use_contact_shadow: bool = False,
    contact_shadow_distance: float = 0.2,
    contact_shadow_bias: float = 0.03,
    contact_shadow_thickness: float = 0.2,
) -> t.LightObject:
    bpy.ops.object.light_add(type="POINT")
    lamp = bpy.context.object

    lamp.data.energy = energy
    lamp.data.color = color
    lamp.data.shadow_soft_size = shadow_soft_size
    lamp.data.use_contact_shadow = use_contact_shadow
    lamp.data.contact_shadow_distance = contact_shadow_distance
    lamp.data.contact_shadow_bias = contact_shadow_bias
    lamp.data.contact_shadow_thickness = contact_shadow_thickness

    return t.LightObject(lamp)


@tracer_primitive
def sun_lamp(
    intensity: float = 1.0,
    color: tuple = (1.0, 1.0, 1.0),
    angle_deg: float = 0.526,
    use_contact_shadow: bool = False,
    contact_shadow_distance: float = 0.2,
    contact_shadow_bias: float = 0.03,
    contact_shadow_thickness: float = 0.2,
) -> t.LightObject:
    bpy.ops.object.light_add(type="SUN")
    lamp = bpy.context.object

    lamp.data.energy = intensity  # intentional - blender uses energy for this case
    lamp.data.color = color
    lamp.data.angle = np.deg2rad(angle_deg)
    lamp.data.use_contact_shadow = use_contact_shadow
    lamp.data.contact_shadow_distance = contact_shadow_distance
    lamp.data.contact_shadow_bias = contact_shadow_bias
    lamp.data.contact_shadow_thickness = contact_shadow_thickness

    return t.LightObject(lamp)


@tracer_primitive
def spot_lamp(
    energy: float = 10.0,
    color: tuple = (1.0, 1.0, 1.0),
    spot_size_deg: float = 45.0,
    spot_blend: float = 0.15,
    shadow_soft_size: float = 0.0,
    use_contact_shadow: bool = False,
    contact_shadow_distance: float = 0.2,
    contact_shadow_bias: float = 0.03,
    contact_shadow_thickness: float = 0.2,
) -> t.LightObject:
    bpy.ops.object.light_add(type="SPOT")
    lamp = bpy.context.object

    lamp.data.energy = energy
    lamp.data.color = color
    lamp.data.spot_size = np.deg2rad(spot_size_deg)
    lamp.data.spot_blend = spot_blend
    lamp.data.shadow_soft_size = shadow_soft_size
    lamp.data.use_contact_shadow = use_contact_shadow
    lamp.data.contact_shadow_distance = contact_shadow_distance
    lamp.data.contact_shadow_bias = contact_shadow_bias
    lamp.data.contact_shadow_thickness = contact_shadow_thickness

    return t.LightObject(lamp)


@tracer_primitive
def area_lamp(
    energy: float = 10.0,
    color: tuple = (1.0, 1.0, 1.0),
    shape: Literal["SQUARE", "RECTANGLE", "ELLIPSE", "DISK"] = "SQUARE",
    size_x: float = 1.0,
    size_y: float = 1.0,
    portal: bool = False,
    use_contact_shadow: bool = False,
    contact_shadow_distance: float = 0.2,
    contact_shadow_bias: float = 0.03,
    contact_shadow_thickness: float = 0.2,
) -> t.LightObject:
    bpy.ops.object.light_add(type="AREA")
    lamp = bpy.context.object

    lamp.data.energy = energy
    lamp.data.color = color
    lamp.data.shape = shape
    lamp.data.size = size_x
    if shape in ["RECTANGLE", "ELLIPSE"]:
        lamp.data.size_y = size_y
    lamp.data.cycles.is_portal = portal
    lamp.data.use_contact_shadow = use_contact_shadow
    lamp.data.contact_shadow_distance = contact_shadow_distance
    lamp.data.contact_shadow_bias = contact_shadow_bias
    lamp.data.contact_shadow_thickness = contact_shadow_thickness

    return t.LightObject(lamp)
