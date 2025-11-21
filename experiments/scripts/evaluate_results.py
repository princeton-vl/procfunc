"""Evaluate experiment results by comparing renders to goal images."""

import argparse
import json
import logging
import re
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

# Cost per million tokens (input, output, thinking) in USD
COST_PER_MILLION = {
    # OpenAI
    "gpt-4o": (2.50, 10.00, 10.00),
    "gpt-4o-mini": (0.15, 0.60, 0.60),
    "gpt-4.1": (2.00, 8.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60, 1.60),
    "gpt-5": (1.25, 10.00, 10.00),
    "gpt-5-mini": (0.25, 2.00, 2.00),
    "gpt-5.1": (1.25, 10.00, 10.00),
    "gpt-5.2": (1.75, 14.00, 14.00),
    # Google Gemini
    "gemini-2.5-flash": (0.30, 2.50, 2.50),
    "gemini-2.5-pro": (1.25, 10.00, 10.00),
    "gemini-3-flash-preview": (0.50, 3.00, 3.00),
    "gemini-3-flash": (0.50, 3.00, 3.00),
    "gemini-3-pro-preview": (2.00, 12.00, 12.00),
    "gemini-3-pro": (2.00, 12.00, 12.00),
}


def extract_model_from_path(folder: str) -> str | None:
    """Extract model name from folder path like 'exp_pf_paramedit_gemini-2.5-pro/0'."""
    for model in sorted(COST_PER_MILLION.keys(), key=len, reverse=True):
        if model in folder:
            return model
    return None


def extract_backend_from_path(folder: str) -> str:
    """Extract backend from folder path like 'exp_pf_paramedit_gemini-2.5-pro/0'."""
    if "_pf_" in folder:
        return "procfunc"
    elif "_ifg_" in folder or "_bgym_" in folder:
        return "infinigen"
    return ""


def calculate_cost(tokens: dict, model: str | None) -> float | None:
    """Calculate USD cost from token counts and model name."""
    if not model or model not in COST_PER_MILLION:
        return None
    input_cost, output_cost, thinking_cost = COST_PER_MILLION[model]
    prompt_tokens = tokens.get("prompt_tokens", 0)
    cached_tokens = tokens.get("cached_tokens", 0)
    completion_tokens = tokens.get("completion_tokens", 0)
    thinking_tokens = tokens.get("thinking_tokens", 0)
    uncached_input = prompt_tokens - cached_tokens
    cached_input_cost = input_cost * 0.5
    return (uncached_input * input_cost + cached_tokens * cached_input_cost + completion_tokens * output_cost + thinking_tokens * thinking_cost) / 1_000_000


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


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
        features = model.get_image_features(**inputs)
    features = features / features.norm(dim=-1, keepdim=True)
    similarity = (features[0] @ features[1]).item()
    return similarity


def photometric_loss(img1: Image.Image, img2: Image.Image) -> float:
    """Compute MSE between two images (RGB only, normalized to 0-1)."""
    import numpy as np

    img1 = img1.convert("RGB").resize(img2.size)
    arr1 = np.array(img1, dtype=np.float32) / 255.0
    arr2 = np.array(img2.convert("RGB"), dtype=np.float32) / 255.0
    mse = np.mean((arr1 - arr2) ** 2)
    return float(mse)


def find_render(folder: Path) -> Path | None:
    for name in ["render1.png", "render.png"]:
        path = folder / name
        if path.exists():
            return path
    return None


def evaluate_task(task_folder: Path, bench_data_folder: Path, model, processor, device) -> dict | None:
    """Evaluate a single task folder. Returns scores dict or None if no renders."""
    # Find goal render
    goal_path = find_render(bench_data_folder / "renders" / "goal")
    if not goal_path:
        logger.warning(f"{task_folder.name}: no goal render found")
        return None

    goal_img = Image.open(goal_path)

    # Find all round folders
    round_folders = sorted(task_folder.glob("round_*"))
    if not round_folders:
        logger.warning(f"{task_folder.name}: no round_* folders found")
        return None

    rounds = {}
    best_round = None
    best_n_clip = float("inf")

    for folder in round_folders:
        render_path = find_render(folder)
        if not render_path:
            render_path = find_render(bench_data_folder / "renders" / "start")

        render_img = Image.open(render_path)

        sim = clip_similarity(model, processor, device, render_img, goal_img)
        n_clip = 1 - sim
        pl = photometric_loss(render_img, goal_img)

        rounds[folder.name] = {"n_clip": round(n_clip, 4), "pl": round(pl, 4)}

        if n_clip < best_n_clip:
            best_n_clip = n_clip
            best_round = folder.name

    if not rounds:
        logger.warning(f"{task_folder.name}: no renders found")
        return None

    final_round = max(rounds.keys())

    return {
        "n_rounds": len(rounds),
        "rounds": rounds,
        "best": {"round": best_round, "n_clip": round(best_n_clip, 4)},
        "final": {"round": final_round, **rounds[final_round]},
    }


def validate_experiment(exp_folder: Path):
    """Validate experiment completeness. Raises ValueError if incomplete."""
    tasks = [d.name for d in exp_folder.iterdir() if d.is_dir() and d.name != "vis"]
    if not tasks:
        raise ValueError(f"No task folders found in {exp_folder}")

    task_rounds = {t: {r.name for r in (exp_folder / t).glob("round_*")} for t in tasks}
    all_rounds = set.union(*task_rounds.values()) if any(task_rounds.values()) else set()
    if mismatched := {t: all_rounds - r for t, r in task_rounds.items() if r != all_rounds}:
        raise ValueError(f"Missing rounds: {mismatched}")


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


METRIC_COLUMNS = ["Source", "PL*10^2", "NCLIP*10^2", "Crash %", "Tokens", "Cost", "Characters"]


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
    model = extract_model_from_path(folder)
    cost = calculate_cost(tokens, model)
    crash_pct = round((1 - agg["success_rate"]) * 100, 1) if agg["success_rate"] is not None else None
    base_folder = str(Path(folder).parent) + "/" if suffix else folder
    source = f"{base_folder} ({suffix})" if suffix else folder
    return {
        "Source": source,
        "PL*10^2": round(agg["final_pl"] * 100, 2),
        "NCLIP*10^2": round(agg["final_n_clip"] * 100, 2),
        "Crash %": f"{crash_pct}%" if crash_pct is not None else None,
        "Tokens": f"{format_num(input_tokens)}/{format_num(output_tokens)}",
        "Cost": f"${cost:.2f}" if cost is not None else None,
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
    best_n_clips, best_pls, final_n_clips, final_pls = [], [], [], []

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
        "tokens": tokens,
        "code_stats": code_stats,
    }
    return {"folder": str(exp_folder), "aggregate": aggregate, "tasks": all_results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_folders", type=Path, nargs="+", help="Path(s) to experiment output folder(s)")
    parser.add_argument("--bench_data", type=Path, required=True, help="Path to benchmark data with goal renders")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON path (default: first folder/overall_scores.json)")
    parser.add_argument("--skip-validation", action="store_true", help="Skip validation that all tasks have same rounds")
    args = parser.parse_args()

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

    averaged = {
        "n_runs": n_runs,
        "success_rate": round(total_successful / total_rounds, 4) if total_rounds else 0,
        "successful_renders": total_successful,
        "total_rounds": total_rounds,
        "best_n_clip": round(sum(r["aggregate"]["best_n_clip"] for r in runs) / n_runs, 4),
        "best_pl": round(sum(r["aggregate"]["best_pl"] for r in runs) / n_runs, 4),
        "final_n_clip": round(sum(r["aggregate"]["final_n_clip"] for r in runs) / n_runs, 4),
        "final_pl": round(sum(r["aggregate"]["final_pl"] for r in runs) / n_runs, 4),
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
