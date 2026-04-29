"""Evaluate experiment results by comparing renders to goal images."""

import argparse
import json
import logging
import re
from pathlib import Path

import bpy
import numpy as np
import pandas as pd
import torch
from PIL import Image
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor

from procfunc.util.log import Suppress

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def extract_backend_from_path(folder: str) -> str:
    """Extract backend from folder path like 'exp_pf_paramedit_gemini-2.5-pro/0'."""
    if "_pf_" in folder:
        return "procfunc"
    elif "_ifg_" in folder or "_bgym_" in folder:
        return "infinigen"
    return ""


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def subsample_points(pts: np.ndarray, max_points: int, name: str) -> np.ndarray:
    if len(pts) > max_points:
        logger.warning(f"{name} has {len(pts)} points, subsampling to {max_points}")
        indices = np.random.choice(len(pts), max_points, replace=False)
        return pts[indices]
    return pts


def chamfer_distance(points1: np.ndarray, points2: np.ndarray, max_points: int = 10000) -> float:
    """Compute chamfer distance between two point clouds."""
    if len(points1) == 0:
        raise ValueError("points1 is empty")
    if len(points2) == 0:
        raise ValueError("points2 is empty")

    points1 = subsample_points(points1, max_points, "points1")
    points2 = subsample_points(points2, max_points, "points2")

    def min_distances(src: np.ndarray, tgt: np.ndarray, chunk_size: int = 5000) -> np.ndarray:
        min_dists = np.full(len(src), np.inf)
        for i in range(0, len(src), chunk_size):
            src_chunk = src[i:i + chunk_size]
            diff = src_chunk[:, None, :] - tgt[None, :, :]
            sq_dists = np.sum(diff**2, axis=-1)
            min_dists[i:i + chunk_size] = np.sqrt(sq_dists.min(axis=1))
        return min_dists

    return float(min_distances(points1, points2).mean() + min_distances(points2, points1).mean())


def get_active_object_vertices(max_verts: int = 100000) -> np.ndarray:
    """Get world-space vertices from the active object (with modifiers and instances realized)."""
    obj = bpy.context.active_object
    if obj is None or obj.type != "MESH":
        return np.zeros((0, 3))

    depsgraph = bpy.context.evaluated_depsgraph_get()
    all_verts = []

    for obj_inst in depsgraph.object_instances:
        if not (obj_inst.parent and obj_inst.parent.original == obj):
            continue
        inst_obj = obj_inst.object
        if inst_obj.type != "MESH":
            continue
        mesh = inst_obj.to_mesh()
        if mesh and len(mesh.vertices) > 0:
            matrix = obj_inst.matrix_world
            all_verts.append(np.array([matrix @ v.co for v in mesh.vertices]))
            inst_obj.to_mesh_clear()

    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    if mesh and len(mesh.vertices) > 0:
        all_verts.append(np.array([obj.matrix_world @ v.co for v in mesh.vertices]))
    obj_eval.to_mesh_clear()

    if not all_verts:
        return np.zeros((0, 3))
    pts = np.concatenate(all_verts, axis=0)
    if len(pts) > max_verts:
        pts = pts[np.random.choice(len(pts), max_verts, replace=False)]
    return pts


def load_blend_get_vertices(blend_path: Path) -> np.ndarray:
    """Load .blend and get active object vertices."""
    with Suppress():
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    return get_active_object_vertices()


def load_goal_vertices(bench_data_folder: Path) -> np.ndarray:
    """Load goal geometry vertices from pre-built .blend file."""
    candidates = [
        bench_data_folder / "goal_scene.blend",
        bench_data_folder / "blender_file_bgym_goal.blend",
    ]
    goal_blend = next((p for p in candidates if p.exists()), None)
    if goal_blend is None:
        raise FileNotFoundError(
            f"No goal blend found in {bench_data_folder}. "
            f"Tried: {[p.name for p in candidates]}"
        )

    verts = load_blend_get_vertices(goal_blend)
    if len(verts) == 0:
        raise ValueError(f"No vertices found in goal for {bench_data_folder}")
    return verts


def compute_chamfer_for_geometry_task(
    task_folder: Path, bench_data_folder: Path
) -> float:
    """Compute chamfer distance between last successful round and goal for geometry tasks."""
    candidates = [r / "scene.blend" for r in sorted(task_folder.glob("round_*"), reverse=True)]
    start_blend = bench_data_folder / "start_scene.blend"
    if not start_blend.exists():
        start_blend = bench_data_folder / "blender_file_bgym_start.blend"
    candidates.append(start_blend)

    for blend in candidates:
        if not blend.exists():
            continue
        verts = load_blend_get_vertices(blend)
        if len(verts) == 0:
            continue
        verts_goal = load_goal_vertices(bench_data_folder)
        cd = chamfer_distance(verts, verts_goal)
        with Suppress():
            bpy.ops.wm.read_homefile(use_empty=True)
        return cd

    raise ValueError(f"No valid geometry found in {task_folder} or start blend at {start_blend}")


def load_clip_model():
    device = get_device()
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    try:
        from transformers import CLIPImageProcessorFast
        processor = CLIPImageProcessorFast.from_pretrained("openai/clip-vit-base-patch32")
    except ImportError:
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.eval()
    return model, processor, device


def clip_similarity(model, processor, device, img1: Image.Image, img2: Image.Image) -> float:
    """Compute CLIP cosine similarity between two images."""
    inputs = processor(images=[img1, img2], return_tensors="pt").to(device)
    with torch.no_grad():
        output = model.get_image_features(**inputs)
        features = output.pooler_output if hasattr(output, "pooler_output") else output
    features = features / features.norm(dim=-1, keepdim=True)
    similarity = (features[0] @ features[1]).item()
    return similarity


def photometric_loss(img1: Image.Image, img2: Image.Image) -> float:
    """Compute MSE between two images (RGB only, normalized to 0-1)."""
    img1 = img1.convert("RGB").resize(img2.size)
    arr1 = np.array(img1, dtype=np.float32) / 255.0
    arr2 = np.array(img2.convert("RGB"), dtype=np.float32) / 255.0
    mse = np.mean((arr1 - arr2) ** 2)
    return float(mse)


def find_render(folder: Path) -> Path | None:
    render_path = folder / "render.png"
    numbered = sorted(folder.glob("render[0-9]*.png"))
    if numbered:
        if len(numbered) == 1:
            return numbered[0]
        return concat_images(numbered, render_path)
    return render_path if render_path.exists() else None


def concat_images(paths: list[Path], output_path: Path) -> Path:
    if len(paths) == 1:
        return paths[0]
    images = [Image.open(p) for p in paths]
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    merged = Image.new("RGB", (total_width, max_height))
    x_offset = 0
    for img in images:
        merged.paste(img, (x_offset, 0))
        x_offset += img.width
    merged.save(output_path)
    return output_path


def evaluate_renders(result_folder: Path, goal_folder: Path, model, processor, device) -> tuple[float, float]:
    """Score each numbered render pair and average. Falls back to render.png if no numbered renders."""
    goal_renders = sorted(goal_folder.glob("render[0-9]*.png"))
    result_renders = sorted(result_folder.glob("render[0-9]*.png"))
    if goal_renders and result_renders:
        assert set(p.name for p in goal_renders) == set(p.name for p in result_renders), (
            f"View mismatch: goal={[p.name for p in goal_renders]} result={[p.name for p in result_renders]}"
        )
        clips, pls = [], []
        for g, r in zip(goal_renders, result_renders):
            clips.append(1 - clip_similarity(model, processor, device, Image.open(r), Image.open(g)))
            pls.append(photometric_loss(Image.open(r), Image.open(g)))
        return sum(clips) / len(clips), sum(pls) / len(pls)
    goal_path = find_render(goal_folder)
    result_path = find_render(result_folder)
    if not goal_path or not result_path:
        raise FileNotFoundError(f"Missing renders: goal={goal_path} result={result_path}")
    goal_img, result_img = Image.open(goal_path), Image.open(result_path)
    return 1 - clip_similarity(model, processor, device, result_img, goal_img), photometric_loss(result_img, goal_img)


def evaluate_task(task_folder: Path, bench_data_folder: Path, model, processor, device) -> dict | None:
    """Evaluate a single task folder. Returns scores dict or None if no renders."""
    goal_folder = bench_data_folder / "renders" / "goal"
    if not find_render(goal_folder):
        logger.warning(f"{task_folder.name}: no goal render found")
        return None

    round_folders = sorted(task_folder.glob("round_*"))
    if not round_folders:
        logger.warning(f"{task_folder.name}: no round_* folders found")
        return None

    rounds = {}
    best_round = None
    best_n_clip = float("inf")

    for folder in round_folders:
        result_folder = folder
        if not find_render(folder):
            result_folder = bench_data_folder / "renders" / "start"

        n_clip, pl = evaluate_renders(result_folder, goal_folder, model, processor, device)

        rounds[folder.name] = {"n_clip": round(n_clip, 4), "pl": round(pl, 4)}

        if n_clip < best_n_clip:
            best_n_clip = n_clip
            best_round = folder.name

    if not rounds:
        logger.warning(f"{task_folder.name}: no renders found")
        return None

    final_round = max(rounds.keys())

    result = {
        "n_rounds": len(rounds),
        "rounds": rounds,
        "best": {"round": best_round, "n_clip": round(best_n_clip, 4)},
        "final": {"round": final_round, **rounds[final_round]},
    }

    is_geometry = task_folder.name.startswith("geometry")
    if is_geometry:
        try:
            cd = compute_chamfer_for_geometry_task(task_folder, bench_data_folder)
            result["final"]["chamfer"] = round(cd, 6)
        except (FileNotFoundError, ValueError) as e:
            logger.warning(f"{task_folder.name}: chamfer failed: {e}")

    return result


def validate_experiment(exp_folder: Path):
    """Validate experiment completeness. Raises ValueError if incomplete."""
    if not exp_folder.exists():
        raise ValueError(f"Experiment folder does not exist: {exp_folder}")

    tasks = [d.name for d in exp_folder.iterdir() if d.is_dir() and d.name != "vis"]
    if not tasks:
        raise ValueError(f"No task folders found in {exp_folder}")

    task_rounds = {t: {r.name for r in (exp_folder / t).glob("round_*")} for t in tasks}
    all_rounds = set.union(*task_rounds.values()) if any(task_rounds.values()) else set()
    if mismatched := {t: all_rounds - r for t, r in task_rounds.items() if r != all_rounds}:
        incomplete_tasks = sorted(mismatched.keys())
        msg = f"Incomplete experiment: {exp_folder}\n"
        msg += f"  Expected rounds: {sorted(all_rounds)}\n"
        msg += f"  Tasks with missing rounds ({len(incomplete_tasks)}):\n"
        for task in incomplete_tasks[:5]:
            msg += f"    - {task}: missing {sorted(mismatched[task])}\n"
        if len(incomplete_tasks) > 5:
            msg += f"    ... and {len(incomplete_tasks) - 5} more tasks\n"
        msg += "  Use --skip-validation to run anyway"
        raise ValueError(msg)


def count_tokens_from_log(exp_folder: Path) -> dict:
    """Sum token counts from log.txt file."""
    log_path = exp_folder / "log.txt"
    if not log_path.exists():
        return {}

    text = log_path.read_text()
    tokens = {}
    for token_type in ["PROMPT_TOKENS", "COMPLETION_TOKENS", "TOTAL_TOKENS", "CACHED_TOKENS", "THINKING_TOKENS"]:
        matches = re.findall(rf"\[{token_type}\]: (\d+)", text)
        if matches:
            tokens[token_type.lower()] = sum(int(m) for m in matches)
    return tokens


def count_renders(exp_folder: Path) -> tuple[int, int]:
    """Count (successful_renders, total_rounds) across all tasks."""
    successful = 0
    total = 0
    for task_folder in exp_folder.iterdir():
        if not task_folder.is_dir() or task_folder.name == "vis":
            continue
        for round_folder in task_folder.glob("round_*"):
            total += 1
            if find_render(round_folder):
                successful += 1
    return successful, total


def count_code_stats(exp_folder: Path) -> dict:
    """Count code chars/lines: total across all rounds, and final round only."""
    total_chars = 0
    total_lines = 0
    final_chars = 0
    final_lines = 0

    for task_folder in exp_folder.iterdir():
        if not task_folder.is_dir() or task_folder.name == "vis":
            continue
        round_folders = sorted(task_folder.glob("round_*"))
        for i, round_folder in enumerate(round_folders):
            code_path = round_folder / "code.py"
            if code_path.exists():
                content = code_path.read_text()
                chars = len(content)
                lines = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
                total_chars += chars
                total_lines += lines
                if i == len(round_folders) - 1:  # final round
                    final_chars += chars
                    final_lines += lines

    return {
        "total_chars": total_chars,
        "total_lines": total_lines,
        "final_chars": final_chars,
        "final_lines": final_lines,
    }


METRIC_COLUMNS = ["Source", "PL*10^2", "NCLIP*10^2", "CD", "Crash %", "Tokens", "Characters"]


def format_num(n: int | float) -> str:
    """Format number with K/M/B suffix."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


def extract_metrics(agg: dict, folder: str = "", suffix: str = "") -> dict:
    """Extract metrics dict from aggregate results."""
    tokens = agg.get("tokens", {})
    input_tokens = tokens.get("prompt_tokens", 0)
    output_tokens = tokens.get("completion_tokens", 0)
    crash_pct = round((1 - agg["success_rate"]) * 100, 1) if agg["success_rate"] is not None else None
    base_folder = str(Path(folder).parent) + "/" if suffix else folder
    source = f"{base_folder} ({suffix})" if suffix else folder
    cd = agg.get("final_chamfer")
    return {
        "Source": source,
        "PL*10^2": round(agg["final_pl"] * 100, 2),
        "NCLIP*10^2": round(agg["final_n_clip"] * 100, 2),
        "CD": round(cd, 4) if cd is not None else None,
        "Crash %": f"{crash_pct}%" if crash_pct is not None else None,
        "Tokens": f"{format_num(input_tokens)}/{format_num(output_tokens)}",
        "Characters": agg["code_stats"]["total_chars"],
    }


def create_results_dataframe(runs: list, averaged: dict) -> pd.DataFrame:
    """Create DataFrame with one row per run plus average and average± rows."""
    folder = runs[0]["folder"] if runs else ""
    base_folder = str(Path(folder).parent) + "/"

    rows = [extract_metrics(r["aggregate"], r["folder"]) for r in runs]
    avg_row = extract_metrics(averaged, folder, "AVERAGE")
    rows.append(avg_row)

    if len(runs) > 1:
        pm_cols = ["PL*10^2", "NCLIP*10^2"]
        run_rows = rows[:-1]

        avg_pm_row = dict(avg_row)
        avg_pm_row["Source"] = f"{base_folder} (AVERAGE±)"
        for col in pm_cols:
            values = [r[col] for r in run_rows if r[col] is not None]
            if values:
                avg_val = avg_row[col]
                err_val = round((max(values) - min(values)) / 2, 4)
                avg_pm_row[col] = f"{avg_val}±{err_val}"
        rows.append(avg_pm_row)

    df = pd.DataFrame(rows, columns=METRIC_COLUMNS)
    return df


def format_tsv_justified(df: pd.DataFrame) -> str:
    """Format DataFrame as justified TSV string."""
    cols = df.columns.tolist()
    str_df = df.astype(str).replace("None", "")
    widths = {col: max(len(col), str_df[col].str.len().max()) for col in cols}
    lines = ["\t".join(col.ljust(widths[col]) for col in cols)]
    for _, row in str_df.iterrows():
        lines.append("\t".join(str(row[col]).ljust(widths[col]) for col in cols))
    return "\n".join(lines)


def evaluate_experiment(exp_folder: Path, bench_data: Path, model, processor, device) -> dict:
    """Evaluate a single experiment folder, return results dict."""
    task_folders = sorted([f for f in exp_folder.iterdir() if f.is_dir() and f.name != "vis"])
    all_results = {}
    best_n_clips, best_pls, final_n_clips, final_pls, final_chamfers = [], [], [], [], []

    for task_folder in tqdm(task_folders, desc=exp_folder.name):
        bench_data_folder = bench_data / task_folder.name
        if not bench_data_folder.exists():
            continue
        result = evaluate_task(task_folder, bench_data_folder, model, processor, device)
        if result is None:
            continue
        all_results[task_folder.name] = result
        task_folder.joinpath("scores.json").write_text(json.dumps(result, indent=2))
        best_n_clips.append(result["best"]["n_clip"])
        best_pls.append(result["rounds"][result["best"]["round"]]["pl"])
        final_n_clips.append(result["final"]["n_clip"])
        final_pls.append(result["final"]["pl"])
        if "chamfer" in result["final"]:
            final_chamfers.append(result["final"]["chamfer"])

    n = len(all_results)
    successful_renders, total_rounds = count_renders(exp_folder)
    tokens = count_tokens_from_log(exp_folder)
    code_stats = count_code_stats(exp_folder)

    aggregate = {
        "n_tasks": len(task_folders),
        "n_evaluated": n,
        "success_rate": round(successful_renders / total_rounds, 4) if total_rounds else 0,
        "successful_renders": successful_renders,
        "total_rounds": total_rounds,
        "best_n_clip": round(sum(best_n_clips) / n, 4) if n else 0,
        "best_pl": round(sum(best_pls) / n, 4) if n else 0,
        "final_n_clip": round(sum(final_n_clips) / n, 4) if n else 0,
        "final_pl": round(sum(final_pls) / n, 4) if n else 0,
        "final_chamfer": round(sum(final_chamfers) / len(final_chamfers), 6) if final_chamfers else None,
        "tokens": tokens,
        "code_stats": code_stats,
    }
    return {"folder": str(exp_folder), "aggregate": aggregate, "tasks": all_results}


def main():
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_folders", type=Path, nargs="+", help="Path(s) to experiment output folder(s)")
    parser.add_argument("--bench_data", type=Path, required=True, help="Path to benchmark data with goal renders")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON path (default: first folder/overall_scores.json)")
    parser.add_argument("--skip-validation", action="store_true", help="Skip validation that all tasks have same rounds")

    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None
    args = parser.parse_args(argv)

    if not args.skip_validation:
        for folder in args.experiment_folders:
            validate_experiment(folder)

    logger.info("Loading CLIP model...")
    model, processor, device = load_clip_model()
    logger.info(f"Using device: {device}")

    runs = []
    for folder in args.experiment_folders:
        runs.append(evaluate_experiment(folder, args.bench_data, model, processor, device))

    # Average across runs
    n_runs = len(runs)
    total_successful = sum(r["aggregate"]["successful_renders"] for r in runs)
    total_rounds = sum(r["aggregate"]["total_rounds"] for r in runs)
    avg_tokens = {}
    for r in runs:
        for k, v in r["aggregate"].get("tokens", {}).items():
            avg_tokens[k] = avg_tokens.get(k, 0) + v
    avg_tokens = {k: v / n_runs for k, v in avg_tokens.items()}
    avg_code_stats = {}
    for r in runs:
        for k, v in r["aggregate"].get("code_stats", {}).items():
            avg_code_stats[k] = avg_code_stats.get(k, 0) + v
    avg_code_stats = {k: v / n_runs for k, v in avg_code_stats.items()}

    chamfer_values = [r["aggregate"]["final_chamfer"] for r in runs if r["aggregate"].get("final_chamfer") is not None]
    avg_chamfer = round(sum(chamfer_values) / len(chamfer_values), 6) if chamfer_values else None

    averaged = {
        "n_runs": n_runs,
        "success_rate": round(total_successful / total_rounds, 4) if total_rounds else 0,
        "successful_renders": total_successful,
        "total_rounds": total_rounds,
        "best_n_clip": round(sum(r["aggregate"]["best_n_clip"] for r in runs) / n_runs, 4),
        "best_pl": round(sum(r["aggregate"]["best_pl"] for r in runs) / n_runs, 4),
        "final_n_clip": round(sum(r["aggregate"]["final_n_clip"] for r in runs) / n_runs, 4),
        "final_pl": round(sum(r["aggregate"]["final_pl"] for r in runs) / n_runs, 4),
        "final_chamfer": avg_chamfer,
        "tokens": avg_tokens,
        "code_stats": avg_code_stats,
    }

    overall = {"averaged": averaged, "runs": runs}
    output_path = args.output or args.experiment_folders[0] / "overall_scores.json"
    output_path.write_text(json.dumps(overall, indent=2))

    df = create_results_dataframe(runs, averaged)
    tsv_path = output_path.with_suffix(".tsv")
    tsv_path.write_text(format_tsv_justified(df))

    logger.info(f"Saved: {output_path}")
    logger.info(f"Saved: {tsv_path}")


if __name__ == "__main__":
    main()
