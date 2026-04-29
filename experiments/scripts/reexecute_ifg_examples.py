import argparse
import shutil
import subprocess
from pathlib import Path

from generate_benchdata_procfunc import (
    execute_blendergym_infinigen_script,
    preprocess_blendergym_task,
)

TRANSPILE_IFG_SCRIPT = Path(__file__).parent / "transpile_blend_to_ifg.py"


def transpile_blend_to_ifg(blend_path: Path, output_path: Path, blender_bgym_path: Path):
    blender_install_path = blender_bgym_path.resolve()
    blendergym_root = Path("blendergym").absolute()
    path_append_script = (
        blendergym_root / "infinigen/infinigen/tools/blendscript_path_append.py"
    )

    cmd = [
        str(blender_install_path),
        "-noaudio", "--background",
        str(blend_path.absolute()),
        "--python", str(path_append_script.absolute()),
        "--python", str(TRANSPILE_IFG_SCRIPT.absolute()),
        "--", str(output_path.absolute()),
    ]
    print(" ".join(cmd))
    subprocess.check_call(cmd)
    assert output_path.exists(), f"Infinigen transpiler succeeded but output missing: {output_path}"


def main():
    parser = argparse.ArgumentParser(
        description="Execute Infinigen scripts in Blender 3.6 to concretify random values, "
        "then re-transpile the .blend back to Infinigen code."
    )
    parser.add_argument("output_folder", type=Path)
    parser.add_argument("base_blender_file", type=Path)
    parser.add_argument("input_files", type=Path, nargs="+")
    parser.add_argument("--task_type", type=str, choices=["material", "geometry"], default="material")
    parser.add_argument("--blender_bgym_path", type=Path, default=Path("blender_3_6.sh"))
    args = parser.parse_args()

    args.output_folder.mkdir(parents=True, exist_ok=True)

    for input_file in args.input_files:
        script_copy = args.output_folder / input_file.name.replace(".py", "_ORIG.py")
        blend_new = args.output_folder / input_file.name.replace(".py", ".blend")
        script_final = args.output_folder / input_file.name

        print(f"Processing {input_file} -> {script_final}")

        shutil.copy(input_file, script_copy)
        shutil.copy(args.base_blender_file, blend_new)
        preprocess_blendergym_task(script_copy, blend_new, args.task_type)
        execute_blendergym_infinigen_script(blend_new, script_copy, args.blender_bgym_path)

        transpile_blend_to_ifg(blend_new, script_final, args.blender_bgym_path)

        script_copy.unlink()
        blend_new.unlink()
        blend1 = blend_new.with_suffix(".blend1")
        if blend1.exists():
            blend1.unlink()


if __name__ == "__main__":
    main()
