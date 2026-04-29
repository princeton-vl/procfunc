import argparse
import shutil
from pathlib import Path

from generate_benchdata_procfunc import (
    execute_blendergym_infinigen_script,
    postprocess_transpiled_procfunc,
    preprocess_blendergym_task,
    transpile_blendergym_task_blendfile,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_folder", type=Path)
    parser.add_argument("base_blender_file", type=Path)
    parser.add_argument("input_files", type=Path, nargs="+")
    parser.add_argument("--task_type", type=str, choices=["material", "geometry"], default="material")
    parser.add_argument("--blender_bgym_path", type=Path, default=Path("blender_3_6.sh"),
        help="Path to Blender 3.6 binary installed by install_blendergym_bl36.sh")
    args = parser.parse_args()

    args.output_folder.mkdir(parents=True, exist_ok=True)

    for input_file in args.input_files:

        script_copy = args.output_folder / input_file.name.replace(".py", "_ORIG.py")
        blend_new = args.output_folder / input_file.name.replace(".py", ".blend")
        script_final = args.output_folder / input_file.name

        print(f"Processing {input_file} to {script_final}")

        shutil.copy(input_file, script_copy)
        shutil.copy(args.base_blender_file, blend_new)
        preprocess_blendergym_task(script_copy, blend_new, args.task_type)
        execute_blendergym_infinigen_script(blend_new, script_copy, args.blender_bgym_path)

        transpile_blendergym_task_blendfile(blend_new, script_final, args.task_type)
        postprocess_transpiled_procfunc(script_final)

        script_copy.unlink()
        blend_new.unlink()
        blend1 = blend_new.with_suffix(".blend1")
        if blend1.exists():
            blend1.unlink()

if __name__ == "__main__":
    main()
