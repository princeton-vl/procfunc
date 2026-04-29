import bpy

from procfunc import types as t


def perspective_camera(
    focal_length_mm: float = 50.0,
    clip_start: float = 0.1,
    clip_end: float = 1000.0,
    sensor_width_mm: float = 36.0,
    sensor_height_mm: float | None = None,
) -> t.CameraObject:
    bpy.ops.object.camera_add()
    camera = bpy.context.object

    camera.data.lens = focal_length_mm
    camera.data.clip_start = clip_start
    camera.data.clip_end = clip_end
    camera.data.sensor_width = sensor_width_mm
    if sensor_height_mm is None:
        resx = bpy.context.scene.render.resolution_x
        resy = bpy.context.scene.render.resolution_y
        ratio = resx / resy
        # assert ratio.is_integer(), (ratio, resx, resy)
        camera.data.sensor_height = sensor_width_mm * ratio
    else:
        camera.data.sensor_height = sensor_height_mm

    return t.CameraObject(camera)


def orthographic_camera(
    scale: float = 1.0,
    clip_start: float = 0.1,
    clip_end: float = 1000.0,
) -> t.CameraObject:
    bpy.ops.object.camera_add()
    camera = bpy.context.object

    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    camera.data.clip_start = clip_start
    camera.data.clip_end = clip_end

    return t.CameraObject(camera)
