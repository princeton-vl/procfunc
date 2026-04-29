import logging
from pathlib import Path

import bpy

from procfunc import types as t
from procfunc.util.log import Suppress

logger = logging.getLogger(__name__)


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
