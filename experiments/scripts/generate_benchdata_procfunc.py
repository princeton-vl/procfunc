import argparse
import logging
import shutil
import subprocess
from multiprocessing import Pool
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

PIPELINE_RENDER_SCRIPT = Path(__file__).parent/"pipeline_render_script.py"
if not PIPELINE_RENDER_SCRIPT.exists():
    raise FileNotFoundError(
        f"Expected to find render script from blendergym at {PIPELINE_RENDER_SCRIPT}"
    )


def transpile_v1_to_v2(input_path: Path, output_path: Path, fn_name: str):
    # used when you have CODE as input, not a blender file
    # cant use this currently since we need to use a blenderfile intermediary to autoconvert 3.6->4.2

    cmd = (
        ["python", "infinigen/scripts/transpile_v1_to_v2.py"]
        + [str(input_path) + ":" + fn_name]
        + [str(output_path) + ":" + fn_name]
        # + ["--infinigen_v1_path", "blendergym/infinigen"]
        + ["--debug"]
    )
    print(" ".join(cmd))
    subprocess.check_call(cmd)

def strip_comment_lines(code_path: Path):
    lines = code_path.read_text().splitlines()
    lines = [line for line in lines if not line.lstrip().startswith("#")]
    code_path.write_text("\n".join(lines))

def postprocess_transpiled_procfunc(code_path: Path):
    code_lines = code_path.read_text().splitlines()
    func_def_idx = [
        (i, line.removeprefix("def ").split("(")[0]) 
        for i, line in enumerate(code_lines) if line.startswith("def ")
    ]
    *nodegroups, impl, boilerplate = func_def_idx

    # remove boilerplate (material funcs neednt have code about creating the cube / applying material)
    assert boilerplate[1].startswith("object_"), (nodegroups, impl, boilerplate)
    lines = code_lines[:boilerplate[0]] 

    mat_func_name = impl[1]
    lines.append(f"shader = {mat_func_name}()")
    code_path.write_text("\n".join(lines))

def transpile_blendergym_task_blendfile(blend_path: Path, code_path: Path, task_type: Literal["material", "geometry"]):
    if task_type == "geometry":
        objects_arg = "ACTIVE"
    else:
        objects_arg = "Cube"

    cmd = (
        "uv run --no-sync python -m procfunc.transpiler.main".split()
        + [str(blend_path)]
        + ["--objects", objects_arg]
        + ["--output", str(code_path)]
        + ["--object_mode", "active"]
        + ["--no_version_comments"]
    )

    if task_type == "geometry":
        cmd += ["--transforms", "extract_materials"]
    else:
        cmd += ["--include_object_materials"]

    print(" ".join(cmd))
    subprocess.check_call(cmd)
    assert code_path.exists(), f"Transpiler succeeded but output missing: {code_path}"

def render_procfunc_file(blend_path: Path, code_path: Path, output_render_path: Path):

    cmd = (
        "uv run --no-sync python".split()
        + [str(PIPELINE_RENDER_SCRIPT)]
        + [str(code_path)]
        + [str(output_render_path)]
        + ["--base_blendfile_path", str(blend_path)]
    )
    print(" ".join(cmd))
    subprocess.check_call(cmd)

    render_files = list(output_render_path.glob("render*.png"))
    assert len(render_files) > 0, f"No render files created in {output_render_path}"


def execute_blendergym_infinigen_script(blend_path: Path, script_path: Path, blender_bgym_path: Path):
    blendergym_root = Path("blendergym").absolute()
    assert blendergym_root.exists(), blendergym_root

    path_append_script = (
        blendergym_root / "infinigen/infinigen/tools/blendscript_path_append.py"
    )
    assert path_append_script.exists(), path_append_script

    blender_install_path = blender_bgym_path.resolve()
    if not blender_install_path.exists():
        raise ValueError(f"Blender binary not found at {blender_install_path}")

    cmd = (
        [str(blender_install_path)]
        + ["-noaudio", "--background"]
        + [str(blend_path.absolute())]
        + ["--python", str(path_append_script.absolute())]
        + ["--python", str(script_path.absolute())]
    )
    print(" ".join(cmd))
    subprocess.check_call(cmd)


def preprocess_blendergym_task(script_path: Path, out_blend_path: Path, task_type: Literal["material", "geometry"]):
    text = script_path.read_text()

    # latest versions of infinigen no longer have this import, and none/few of the blendergym tasks actually use it
    # text = text.replace("from infinigen.core.util.color import color_category\n", "")

    if task_type == "material":
        text = text.replace(
            "apply(bpy.context.active_object)", "apply(bpy.data.objects['Cube'])"
        )
        text = text.replace(
            "\napply(material_obj)", "\napply(bpy.data.objects['Cube'])"
        )

    text += (
        f"\nbpy.ops.wm.save_as_mainfile(filepath={str(out_blend_path.absolute())!r})"
    )
    script_path.write_text(text)


def process_task(
    input_task_folder: Path,
    out_task_folder: Path,
    task_type: Literal["material", "geometry"],
    blender_bgym_path: Path = Path("./blender_3_6.sh"),
):
    print("\n\n")
    print("-" * 60)
    print(f"TASK {input_task_folder.name}: {input_task_folder} -> {out_task_folder}")
    print("-" * 60)

    shutil.copytree(input_task_folder / "renders", out_task_folder / "renders_old")

    out_blend = out_task_folder / "blender_file.blend"
    shutil.copy(input_task_folder / "blender_file.blend", out_blend)

    out_start_old = out_task_folder / "start_old.py"
    out_goal_old = out_task_folder / "goal_old.py"
    shutil.copy(input_task_folder / "start.py", out_start_old)
    shutil.copy(input_task_folder / "goal.py", out_goal_old)

    # create a bl3.6 blend file using blendergym's infinigen 1.2.5 fork
    bgym_start_blend = out_task_folder / "blender_file_bgym_start.blend"
    bgym_goal_blend = out_task_folder / "blender_file_bgym_goal.blend"
    preprocess_blendergym_task(out_start_old, bgym_start_blend, task_type)
    preprocess_blendergym_task(out_goal_old, bgym_goal_blend, task_type)
    execute_blendergym_infinigen_script(out_blend, out_start_old, blender_bgym_path)
    execute_blendergym_infinigen_script(out_blend, out_goal_old, blender_bgym_path)

    # convert from bl3.6 blendfile to bl4.2 procfunc code
    out_start_new = out_task_folder / "start.py"
    out_goal_new = out_task_folder / "goal.py"
    transpile_blendergym_task_blendfile(bgym_start_blend, out_start_new, task_type)
    transpile_blendergym_task_blendfile(bgym_goal_blend, out_goal_new, task_type)

    if task_type == "material":
        postprocess_transpiled_procfunc(out_start_new)
        postprocess_transpiled_procfunc(out_goal_new)

    strip_comment_lines(out_start_new)
    strip_comment_lines(out_goal_new)

    # sanitycheck we didnt get trivial / no targets files
    len_start_new = len(out_start_new.read_text().splitlines())
    len_goal_new = len(out_goal_new.read_text().splitlines())
    assert len_start_new > 15, len_start_new
    assert len_goal_new > 15, len_goal_new

    if task_type == "geometry":
        render_procfunc_file(bgym_start_blend, out_start_new, out_task_folder / "renders" / "start")
        render_procfunc_file(bgym_goal_blend, out_goal_new, out_task_folder / "renders" / "goal")
    else:
        render_procfunc_file(out_blend, out_start_new, out_task_folder / "renders" / "start")
        render_procfunc_file(out_blend, out_goal_new, out_task_folder / "renders" / "goal")


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_folder", type=Path)
    parser.add_argument("output_folder", type=Path)
    parser.add_argument(
        "--task_type", type=str, choices=["geometry", "material"], required=True
    )
    parser.add_argument("--blender_bgym_path", type=Path, default=Path("./blender_3_6.sh"),
        help="Path to Blender 3.6 binary installed by install_blendergym_bl36.sh")
    parser.add_argument("--tasks", type=str, nargs="+", default=None)
    parser.add_argument("--num_workers", type=int, default=1)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip_existing", action="store_true")

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    tasks = list(args.input_folder.glob(f"{args.task_type}*"))
    if len(tasks) == 0:
        raise ValueError(f"No {args.task_type} tasks found in {args.input_folder}")

    pool = Pool(args.num_workers) if args.num_workers > 1 else None
    results = []  # Store async results to check for errors

    for input_task_folder in sorted(tasks):

        taskname = input_task_folder.name
        if args.tasks is not None and taskname not in args.tasks:
            continue

        out_task_folder = args.output_folder / taskname
        if out_task_folder.exists():
            if args.overwrite:
                assert not args.skip_existing, "Cannot use both --overwrite and --skip_existing"
                shutil.rmtree(out_task_folder)
            elif args.skip_existing:
                continue
            else:
                raise ValueError(f"Output task folder {out_task_folder} already exists and --overwrite and --skip_existing are not set")

        out_task_folder.mkdir(parents=True, exist_ok=False)

        if args.num_workers > 1:
            assert pool is not None, pool
            result = pool.apply_async(
                process_task, (input_task_folder, out_task_folder, args.task_type, args.blender_bgym_path)
            )
            results.append((taskname, result))
        else:
            process_task(input_task_folder, out_task_folder, args.task_type, args.blender_bgym_path)

    if pool is not None:
        pool.close()
        pool.join()

        # Check all results for exceptions
        for taskname, result in results:
            try:
                result.get()  # This raises if the worker raised
            except Exception as e:
                raise RuntimeError(f"Task {taskname} failed") from e


if __name__ == "__main__":
    main()
