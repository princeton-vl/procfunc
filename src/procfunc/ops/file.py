import logging
import tempfile
import time
from pathlib import Path

import bpy
import numpy as np

from procfunc import types as t
from procfunc.util.log import Suppress

logger = logging.getLogger(__name__)


_SUFFIX_TO_FORMAT = {
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".bmp": "BMP",
    ".tga": "TARGA",
    ".tif": "TIFF",
    ".tiff": "TIFF",
    ".exr": "OPEN_EXR",
    ".hdr": "HDR",
    ".webp": "WEBP",
}

_DEVICE_PRIORITY = ["OPTIX", "CUDA", "METAL", "HIP", "CPU"]


def load_blend(input_path: Path | str):
    if isinstance(input_path, Path):
        input_path = str(input_path)

    bpy.ops.wm.open_mainfile(filepath=input_path)


def save_blend(
    output_path: Path | str,
    autopack: bool = False,
):
    logger.info(f"Saving blend to {output_path}")

    if isinstance(output_path, Path):
        output_path = str(output_path)

    with Suppress():
        if autopack:
            bpy.ops.file.autopack_toggle()
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        if autopack:
            bpy.ops.file.autopack_toggle()

    return output_path


def import_mesh(path: Path, **kwargs):
    ext = path.suffix.lower()

    funcs = {
        ".obj": bpy.ops.wm.obj_import,
        ".fbx": bpy.ops.import_scene.fbx,
        ".stl": bpy.ops.import_mesh.stl,
        ".ply": bpy.ops.wm.ply_import,
        ".usdc": bpy.ops.wm.usd_import,
    }

    if ext not in funcs:
        raise ValueError(
            f"{import_mesh.__name__} does not yet support extension {ext}, please contact the developer"
        )

    funcs[ext](filepath=str(path), **kwargs)

    if len(bpy.context.selected_objects) > 1 if ext != "usdc" else 2:
        logger.warning(
            f"Warning: {ext.upper()} Import produced {len(bpy.context.selected_objects)} objects, "
            f"but only the first is returned by import_obj"
        )
    if ext != "usdc":
        return bpy.context.selected_objects[0]
    else:
        return next(o for o in bpy.context.selected_objects if o.type != "EMPTY")


def save_mesh(
    output_path: Path,
    objects: list[t.Object | t.Object] | None = None,
    **kwargs,
) -> Path:
    funcs = {
        ".obj": bpy.ops.wm.obj_export,
        ".fbx": bpy.ops.export_scene.fbx,
        ".stl": bpy.ops.export_mesh.stl,
        ".ply": bpy.ops.wm.ply_export,
        ".usdc": bpy.ops.wm.usd_export,
    }

    if output_path.suffix not in funcs:
        raise ValueError(
            f"{save_mesh.__name__} does not yet support extension {output_path.suffix}, "
            " please contact the developer"
        )

    if objects is not None:
        for obj in bpy.data.objects:
            obj.select_set(False)
        for obj in objects:
            if isinstance(obj, t.Object):
                obj = obj.item()
            obj.select_set(True)
    use_selection = objects is not None

    match output_path.suffix:
        case ".obj":
            bpy.ops.wm.obj_export(
                filepath=str(output_path),
                export_selected_objects=use_selection,
                **kwargs,
            )
        case ".fbx":
            bpy.ops.export_scene.fbx(
                filepath=str(output_path), use_selection=use_selection, **kwargs
            )
        case ".stl":
            bpy.ops.export_mesh.stl(
                filepath=str(output_path), use_selection=use_selection, **kwargs
            )
        case ".ply":
            bpy.ops.wm.ply_export(
                filepath=str(output_path),
                export_selected_objects=use_selection,
                **kwargs,
            )
        case ".usdc":
            bpy.ops.wm.usd_export(
                filepath=str(output_path), selected_objects_only=use_selection, **kwargs
            )
        case _:
            raise ValueError(f"Unknown extension {output_path.suffix}")

    if not output_path.exists():
        raise FileNotFoundError(f"Failed to save mesh to {output_path}")

    return output_path


def _configure_render_device(engine: str, device: str) -> None:
    scene = bpy.context.scene

    for i in range(10):
        try:
            scene.render.engine = engine
            break
        except Exception as e:
            logger.warning(f"Error setting render engine {i}: {e}")
            time.sleep(1)
    else:
        raise RuntimeError(f"Failed to set render engine to {engine} after 10 attempts")

    if engine != "CYCLES":
        return

    cycles_prefs = bpy.context.preferences.addons["cycles"].preferences

    if device == "CPU":
        cycles_prefs.compute_device_type = "NONE"
        scene.cycles.device = "CPU"
        return

    candidates = _DEVICE_PRIORITY if device == "AUTO" else [device, "CPU"]
    for device_type in candidates:
        try:
            cycles_prefs.compute_device_type = device_type
            cycles_prefs.get_devices()
            break
        except Exception:
            continue
    else:
        raise RuntimeError(
            f"No supported Cycles compute device of types {candidates}, "
            f"available devices: {cycles_prefs.devices}"
        )

    for d in cycles_prefs.devices:
        d.use = d.type == device_type
    scene.cycles.device = "CPU" if device_type == "CPU" else "GPU"


def _load_png_rgb(path: Path) -> np.ndarray:
    img = bpy.data.images.load(str(path), check_existing=False)
    try:
        w, h = img.size
        channels = img.channels
        pixels = np.asarray(img.pixels[:], dtype=np.float32).reshape(h, w, channels)
        pixels = pixels[::-1]  # bpy stores bottom-up
        rgb = pixels[..., :3] if channels >= 3 else pixels
        return np.clip(rgb * 255.0, 0, 255).astype(np.uint8)
    finally:
        bpy.data.images.remove(img)


def render(
    path: Path | str | None = None,
    *,
    camera: "str | bpy.types.Object | None" = None,
    engine: str = "CYCLES",
    device: str = "AUTO",
    samples: int = 128,
    resolution: int | tuple[int, int] = 512,
    color_mode: str = "RGB",
    file_format: str | None = None,
    view_transform: str = "Filmic",
    look: str = "None",
    exposure: float = 0.0,
    gamma: float = 1.0,
    display_device: str = "sRGB",
) -> Path | np.ndarray:
    """Render the active scene with platform-portable defaults.

    If ``path`` is None, render to a tempdir and return an ``(H, W, 3)`` uint8
    ndarray. Otherwise write to ``path`` (file_format inferred from suffix if
    not given) and return the resolved Path.
    """
    scene = bpy.context.scene

    _configure_render_device(engine, device)

    if camera is not None:
        cam_obj = bpy.data.objects[camera] if isinstance(camera, str) else camera
        scene.camera = cam_obj
    if scene.camera is None:
        raise RuntimeError("No camera set on scene and no `camera` argument given")

    if isinstance(resolution, int):
        res_x = res_y = resolution
    else:
        res_x, res_y = resolution
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y

    if engine == "CYCLES":
        scene.cycles.samples = samples

    scene.render.image_settings.color_mode = color_mode

    scene.view_settings.view_transform = view_transform
    scene.view_settings.look = look
    scene.view_settings.exposure = exposure
    scene.view_settings.gamma = gamma
    scene.display_settings.display_device = display_device

    return_array = path is None
    if return_array:
        tmp = tempfile.TemporaryDirectory(prefix="pf-render-")
        out_path = Path(tmp.name) / "render.png"
        scene.render.image_settings.file_format = "PNG"
    else:
        out_path = Path(path)
        suffix = out_path.suffix.lower()
        if file_format is None:
            file_format = _SUFFIX_TO_FORMAT.get(suffix, "PNG")
        scene.render.image_settings.file_format = file_format
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = None

    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)

    if return_array:
        try:
            arr = _load_png_rgb(out_path)
        finally:
            tmp.cleanup()
        return arr

    if not out_path.exists():
        raise FileNotFoundError(f"Render did not produce {out_path}")
    return out_path
