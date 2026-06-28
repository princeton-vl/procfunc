"""Transpile-and-execute round-trip gate (no rendering).

Modes:
  demo <blend>          scan every node-material in a blend, transpile each in
                        sequence, then execute each generated .py (materials are
                        self-contained). Prints per-material pass/fail.
  benchdata <dir>       for every <dir>/{material,geometry}*/blender_file_bgym_*
                        blend, transpile with the BlenderGym-pipeline flags and
                        execute the result against that same blend.
  execute_dir <dir>     execute the already-transpiled start.py/goal.py in a
                        regenerated bench_data_pf <dir> against their bgym blends
                        (validates execution of generate_benchdata_procfunc out).

Exits nonzero if any target fails. Driven by tests/integration_test/run.sh.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import bpy

from procfunc.transpiler.main import _transforms_map, transpile_targets


def _last_stderr(result):
    return (result.stderr.strip().splitlines() or ["<no stderr>"])[-1][:300]


def _execute(code_py, base_blend=None):
    # Clear to the base blend (objects need its datablocks) or an empty scene
    # (self-contained materials) so each run starts clean, then rebuild in-process.
    if base_blend is not None:
        bpy.ops.wm.open_mainfile(filepath=str(base_blend))
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        exec(  # noqa: S102
            compile(code_py.read_text(), str(code_py), "exec"), {"__name__": "__main__"}
        )
        return None
    except Exception as e:
        return f"{type(e).__name__}: {str(e).splitlines()[0]}"[:300]


def _transpile_cli(blend, out_py, task_type):
    cmd = [
        "procfunc",
        "transpile",
        str(blend),
        "--output",
        str(out_py),
        "--object_mode",
        "active",
        "--no_version_comments",
    ]
    if task_type == "geometry":
        cmd += ["--objects", "ACTIVE", "--include_object_materials", "0"]
    else:
        cmd += ["--objects", "Cube", "--include_object_materials", "1"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return None if result.returncode == 0 else _last_stderr(result)


def _collect(results, fails, prefix=""):
    for key, err in results:
        if err:
            fails[key] = err
        print(f"{prefix}{key}: {'FAIL ' + err if err else 'ok'}", flush=True)


def check_demo(blend, out_dir):
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    materials = [m for m in bpy.data.materials if m.use_nodes]
    assert materials, f"no node-materials found in {blend}"
    n = len(materials)
    print(f"scanning {n} node-materials in {blend}", flush=True)

    fails = {}
    code_paths = {}
    for i, material in enumerate(materials, 1):
        safe = re.sub(r"[^A-Za-z0-9_]", "_", material.name)
        code_py = out_dir / f"mat_{safe}.py"
        try:
            code = transpile_targets(
                [material], transforms=[], add_version_comment=False
            )
            code_py.write_text(code)
            code_paths[material.name] = code_py
            print(f"[{i}/{n}] transpile {material.name!r}: ok", flush=True)
        except Exception as e:
            msg = f"{type(e).__name__}: {str(e).splitlines()[0]}"[:300]
            fails[material.name] = f"transpile: {msg}"
            print(f"[{i}/{n}] transpile {material.name!r}: FAIL {msg}", flush=True)

    for i, (name, code_py) in enumerate(code_paths.items(), 1):
        err = _execute(code_py)
        if err:
            fails[name] = f"execute: {err}"
        print(
            f"[{i}/{len(code_paths)}] execute {name!r}: {'FAIL ' + err if err else 'ok'}",
            flush=True,
        )
    return n, fails


_CATEGORY_INFO = {
    "material": (lambda: bpy.data.materials, True),
    "object": (lambda: bpy.data.objects, False),
    "nodegroup": (lambda: bpy.data.node_groups, False),
}


def _default_spec():
    return [
        {"target_name": m.name, "category": "material"}
        for m in bpy.data.materials
        if m.use_nodes
    ]


def _resolve_blend_targets(spec):
    # spec: list of {target_name, category, object_mode?, transforms?}.
    # label -> (datablock | None, is_material, object_mode, transforms)
    targets = {}
    for entry in spec:
        name = entry["target_name"]
        category = entry["category"]
        collection, is_material = _CATEGORY_INFO[category]
        transforms = [_transforms_map[t] for t in entry.get("transforms", [])]
        targets[f"{category}:{name}"] = (
            collection().get(name),
            is_material,
            entry.get("object_mode", "active"),
            transforms,
        )
    return targets


def _check_one_blend_dir(blend_dir, out_dir):
    blend = blend_dir / "file.blend"
    info = blend_dir / "testcase_info.json"

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    spec = json.loads(info.read_text()) if info.exists() else _default_spec()
    targets = _resolve_blend_targets(spec)
    if not targets:
        return 0, {blend_dir.name: "no targets in testcase_info.json"}

    fails = {}
    to_execute = {}
    for label, (datablock, is_material, object_mode, transforms) in targets.items():
        key = f"{blend_dir.name}/{label}"
        if datablock is None:
            fails[key] = "transpile: target not found in blend"
            print(f"transpile {key}: FAIL not found", flush=True)
            continue
        code_py = out_dir / (re.sub(r"[^A-Za-z0-9_]", "_", key) + ".py")
        try:
            code = transpile_targets(
                [datablock],
                transforms=transforms,
                object_mode=object_mode,
                add_version_comment=False,
            )
            code_py.write_text(code)
            to_execute[key] = (code_py, None if is_material else blend)
            print(f"transpile {key}: ok", flush=True)
        except Exception as e:
            msg = f"{type(e).__name__}: {str(e).splitlines()[0]}"[:300]
            fails[key] = f"transpile: {msg}"
            print(f"transpile {key}: FAIL {msg}", flush=True)

    executed = (
        (key, _execute(code_py, base_blend=base))
        for key, (code_py, base) in to_execute.items()
    )
    executed = ((key, f"execute: {err}" if err else None) for key, err in executed)
    _collect(executed, fails)
    return len(targets), fails


def check_blends(blends_root, out_dir):
    """Transpile+execute each target listed in <name>/testcase_info.json per blend dir.

    Layout: <blends_root>/<name>/file.blend + testcase_info.json, a list of
    {"target_name", "category"} entries (category: material / object / nodegroup,
    with optional per-entry "object_mode" and "transforms"). A missing
    testcase_info.json defaults to every node-material. Each target is transpiled
    individually; materials execute standalone, objects/nodegroups against the blend.
    """
    blend_dirs = sorted(
        d for d in Path(blends_root).iterdir() if (d / "file.blend").exists()
    )
    assert blend_dirs, f"no <name>/file.blend dirs under {blends_root}"

    total = 0
    fails = {}
    for blend_dir in blend_dirs:
        count, dir_fails = _check_one_blend_dir(blend_dir, out_dir)
        total += count
        fails.update(dir_fails)
    return total, fails


def _bench_units(bench_root):
    units = []
    for task_dir in sorted(Path(bench_root).iterdir()):
        if task_dir.name.startswith("material"):
            task_type = "material"
        elif task_dir.name.startswith("geometry"):
            task_type = "geometry"
        else:
            continue
        units += [
            (task_dir.name, task_type, "start"),
            (task_dir.name, task_type, "goal"),
        ]
    return units


def _check_bench_unit(unit, bench_root, out_dir):
    name, task_type, which = unit
    blend = Path(bench_root) / name / f"blender_file_bgym_{which}.blend"
    key = f"{name}/{which}"
    if not blend.exists():
        return key, "transpile: missing blend"
    code_py = out_dir / f"{name}_{which}.py"
    err = _transpile_cli(blend, code_py, task_type)
    if err:
        return key, f"transpile: {err}"
    err = _execute(code_py, base_blend=blend)
    if err:
        return key, f"execute: {err}"
    return key, None


def check_benchdata(bench_root, out_dir):
    units = _bench_units(bench_root)
    assert units, f"no material/geometry task folders under {bench_root}"
    fails = {}
    results = (_check_bench_unit(u, bench_root, out_dir) for u in units)
    _collect(results, fails)
    return len(units), fails


def _check_execute_unit(unit, bench_root):
    name, _task_type, which = unit
    task_dir = Path(bench_root) / name
    code_py = task_dir / f"{which}.py"
    blend = task_dir / f"blender_file_bgym_{which}.blend"
    key = f"{name}/{which}"
    if not code_py.exists() or not blend.exists():
        return key, "missing code or blend"
    err = _execute(code_py, base_blend=blend)
    return key, err


def check_execute_dir(bench_root):
    units = _bench_units(bench_root)
    assert units, f"no material/geometry task folders under {bench_root}"
    fails = {}
    results = (_check_execute_unit(u, bench_root) for u in units)
    _collect(results, fails)
    return len(units), fails


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["demo", "blends", "benchdata", "execute_dir"])
    parser.add_argument(
        "target",
        help="demo: .blend; blends: transpile-blends dir; benchdata/execute_dir: bench_data dir",
    )
    parser.add_argument("--out", type=Path, default=Path("transpile_roundtrip_out"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if args.mode == "demo":
        total, fails = check_demo(args.target, args.out)
        unit = "materials"
    elif args.mode == "blends":
        total, fails = check_blends(args.target, args.out)
        unit = "targets"
    elif args.mode == "benchdata":
        total, fails = check_benchdata(args.target, args.out)
        unit = "task files"
    else:
        total, fails = check_execute_dir(args.target)
        unit = "task files"

    summary = {
        "mode": args.mode,
        "total": total,
        "passed": total - len(fails),
        "failed": len(fails),
        "failures": fails,
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n=== {args.mode}: {total - len(fails)}/{total} {unit} round-tripped ===")
    if fails:
        print(json.dumps(fails, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
