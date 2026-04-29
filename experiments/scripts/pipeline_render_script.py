# Adapted from the 2025-10-29 version of blendergym's `pipeline_render_script.py`
# file originally sourced from blendergym's huggingface data download .zip
# https://huggingface.co/datasets/richard-guyunqi/BG_bench_data/tree/refs%2Fpr%2F2

import argparse
import sys
import time
from pathlib import Path

import bpy

import procfunc as pf
from procfunc.util.teardown import skip_teardown_on_exit


def configure_render_device():
    # Enable GPU rendering

    for i in range(10):
        try:
            bpy.context.scene.render.engine = 'CYCLES'
            break
        except Exception as e:
            print(f"Error setting render engine {i}: {e}")
            time.sleep(1)
    else:
        raise RuntimeError("Failed to set render engine to CYCLES after 10 attempts")

    # Try device types in order of preference
    cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
    device_type_priority = ['OPTIX', 'CUDA', 'METAL', 'HIP', 'CPU']  # NONE = CPU

    for device_type in device_type_priority:
        try:
            cycles_prefs.compute_device_type = device_type
            cycles_prefs.get_devices()
            break
        except Exception:
            continue
    else:
        raise RuntimeError(
            f"No supported Cycles compute device found of types {device_type_priority}, available devices: {cycles_prefs.devices}"
        )

    for device in cycles_prefs.devices:
        device.use = (device.type == device_type)
    bpy.context.scene.cycles.device = 'CPU' if device_type == 'CPU' else 'GPU'

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

    configure_render_device()
    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    bpy.context.scene.cycles.samples = 512
    bpy.context.scene.render.image_settings.color_mode = 'RGB'

    # Render from camera1
    if 'Camera' in bpy.data.objects:
        bpy.context.scene.camera = bpy.data.objects['Camera']
        bpy.context.scene.render.image_settings.file_format = 'PNG'

        render_path = args.rendering_dir / 'render.png'
        bpy.context.scene.render.filepath = str(render_path)
        bpy.ops.render.render(write_still=True)
        assert render_path.exists(), render_path
        assert render_path.is_file(), render_path

    # Render from camera1
    if 'Camera1' in bpy.data.objects:
        bpy.context.scene.camera = bpy.data.objects['Camera1']
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = str(args.rendering_dir / 'render1.png')
        bpy.ops.render.render(write_still=True)

    # Render from camera2
    if 'Camera2' in bpy.data.objects:
        bpy.context.scene.camera = bpy.data.objects['Camera2']
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = str(args.rendering_dir / 'render2.png')
        bpy.ops.render.render(write_still=True)

    for extra_cam in ['Camera3', 'Camera4', 'Camera5']:
        if extra_cam in bpy.data.objects:
            bpy.context.scene.camera = bpy.data.objects[extra_cam]
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = str(args.rendering_dir / f'render{extra_cam[-1]}.png')
            bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    with skip_teardown_on_exit(): # prevents Blender from segfaulting (exit code 139) on normal shutdown
        main()