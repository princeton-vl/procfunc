# Adapted from the 2025-10-29 version of blendergym's `pipeline_render_script.py`
# file originally sourced from blendergym's huggingface data download .zip
# https://huggingface.co/datasets/richard-guyunqi/BG_bench_data/tree/refs%2Fpr%2F2

import argparse
import sys
from pathlib import Path

import bpy

import procfunc as pf
from procfunc.util.teardown import skip_teardown_on_exit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("code_path", type=Path)
    parser.add_argument("rendering_dir", type=Path)
    parser.add_argument("--base_blendfile_path", type=Path, default=None)

    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    else:
        args = parser.parse_args()

    assert args.code_path.exists(), args.code_path
    assert args.code_path.suffix == ".py", args.code_path

    args.rendering_dir.mkdir(parents=True, exist_ok=True)

    if args.base_blendfile_path is not None:
        assert args.base_blendfile_path.exists(), args.base_blendfile_path
        assert args.base_blendfile_path.suffix == ".blend", args.base_blendfile_path
        bpy.ops.wm.open_mainfile(filepath=str(args.base_blendfile_path))

    code = args.code_path.read_text()

    code = code.strip().removeprefix("gpt_raw:")

    original_active_object = bpy.context.active_object
    if original_active_object:
        original_matrix_world = original_active_object.matrix_world.copy()
    original_mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    is_geometry = "geometry" in str(args.code_path)
    if is_geometry and original_active_object:
        mods_to_remove = [m.name for m in original_active_object.modifiers]
        for mod_name in mods_to_remove:
            original_active_object.modifiers.remove(original_active_object.modifiers[mod_name])

    ns = {"__name__": "__main__"}
    exec(compile(code, str(args.code_path), 'exec'), ns)

    is_material = "material" in str(args.code_path)
    if is_material == is_geometry:
        raise ValueError(f"Unhandled task name: {args.code_path} had {is_material=} {is_geometry=}")

    if is_material:

        if "shader" not in ns:
            raise ValueError(
                "Material script failed to produce `shader` variable "
                "- the implementation must assign this variable to be the final function call result"
            )
        shader = ns["shader"]
        if not isinstance(shader, pf.Material):
            raise ValueError(f"Material script produced `shader` variable of type {type(shader)} - expected `pf.Material`")

        assert isinstance(shader, pf.Material), type(shader)

        obj = bpy.data.objects["Cube"]
        while len(obj.data.materials) > 0:
            bpy.ops.object.material_slot_remove()
        obj = pf.MeshObject(obj)

        sockets = {
            k: getattr(shader, k) 
            for k in ["surface", "displacement", "volume"] 
            if hasattr(shader, k)
        }
        pf.ops.object.set_material(obj, **sockets)
    elif is_geometry:
        all_mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        new_mesh_objects = [obj for obj in all_mesh_objects if obj not in original_mesh_objects]

        if original_active_object:
            original_active_object.hide_render = True
            original_active_object.hide_viewport = True

        for obj in new_mesh_objects[:-1]:
            obj.hide_render = True
            obj.hide_viewport = True

        if new_mesh_objects and original_active_object:
            final_obj = new_mesh_objects[-1]
            final_obj.matrix_world = original_matrix_world
    else:
        raise ValueError(f"Unhandled task name: {args.code_path} had {is_material=} {is_geometry=}")

    scene_blend_path = str(args.rendering_dir / "scene.blend")
    print(f"Saving scene blend to {scene_blend_path}")
    bpy.ops.wm.save_mainfile(filepath=scene_blend_path)

    cam_to_filename = [('Camera', 'render.png')] + [
        (f'Camera{i}', f'render{i}.png') for i in range(1, 6)
    ]
    for cam_name, filename in cam_to_filename:
        if cam_name in bpy.data.objects:
            pf.ops.file.render(
                args.rendering_dir / filename,
                camera=cam_name,
                samples=512,
            )


if __name__ == "__main__":
    with skip_teardown_on_exit(): # prevents Blender from segfaulting (exit code 139) on normal shutdown
        main()