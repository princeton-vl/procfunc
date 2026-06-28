import argparse
import json
import logging
import sys
from pathlib import Path

import imageio
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

HEADROOM_PX = 0.5  # band around each per-frame baseline before we flag a change

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("task_type", type=str, choices=["material", "geometry"])
    parser.add_argument("bench_data_bgym", type=Path)
    parser.add_argument("bench_data_pf", type=Path)
    parser.add_argument("out_vis_path", type=Path)
    parser.add_argument("--tasks", type=str, nargs='+', default=None)
    parser.add_argument(
        "--thresh",
        type=float,
        default=None,
        help="exit nonzero if any per-example mean abs pixel diff exceeds this (drives CI)",
    )
    parser.add_argument(
        "--thresh-json",
        type=Path,
        default=None,
        help="JSON {'tasks': {task: {start, goal}}} of per-frame baselines; "
        "diffs are gated to baseline +/- HEADROOM_PX instead of --thresh",
    )
    args = parser.parse_args()

    baselines = {}
    if args.thresh_json is not None:
        baselines = json.loads(args.thresh_json.read_text())["tasks"]

    args.out_vis_path.mkdir(parents=True, exist_ok=True)

    results = []  # (task_name, start_diff, goal_diff); diff is inf when renders missing

    for task_folder in sorted(args.bench_data_bgym.glob(f"{args.task_type}*")):

        task_name = task_folder.name

        if args.tasks is not None and task_name not in args.tasks:
            continue

        pf_task_folder = args.bench_data_pf / task_name
        assert pf_task_folder.exists(), pf_task_folder

        paths = [
            task_folder / "renders/start/render1.png",
            pf_task_folder / "renders/start/render1.png",
            task_folder / "renders/goal/render1.png",
            pf_task_folder / "renders/goal/render1.png",
        ]

        missing = [path for path in paths if not path.exists()]
        if missing:
            logger.warning(f"Task {task_name} has missing renders: {missing}")
            results.append((task_name, float("inf"), float("inf")))
            continue

        imgs = [imageio.imread(path) for path in paths]
        assert all(img.shape == imgs[0].shape for img in imgs), [img.shape for img in imgs]

        start_diff = np.abs(imgs[0].astype(float) - imgs[1].astype(float)).mean()
        goal_diff = np.abs(imgs[2].astype(float) - imgs[3].astype(float)).mean()
        results.append((task_name, start_diff, goal_diff))

        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        for i, (img, path) in enumerate(zip(imgs, paths)):
            ax = axes[i // 2, i % 2]
            ax.imshow(img)
            ax.set_title(path)
            ax.axis("off")

        fig.savefig(args.out_vis_path / f"{task_name}.png")
        plt.close()

    for task_name, start_diff, goal_diff in results:
        logger.info(f"{task_name:40s} start_diff {start_diff:.4f}  goal_diff {goal_diff:.4f}")

    if args.thresh is not None:
        regressions = []
        improvements = []
        for task_name, start_diff, goal_diff in results:
            base = baselines.get(task_name)
            for which, diff in (("start", start_diff), ("goal", goal_diff)):
                if base is None:
                    if diff > args.thresh:
                        regressions.append((task_name, which, diff, args.thresh))
                    continue
                if diff > base[which] + HEADROOM_PX:
                    regressions.append((task_name, which, diff, base[which] + HEADROOM_PX))
                elif diff < base[which] - HEADROOM_PX:
                    improvements.append((task_name, which, diff, base[which]))

        if improvements:
            logger.warning("=== diffs IMPROVED below baseline — inspect the render, then lower tasks.json ===")
        for task_name, which, diff, base_val in improvements:
            logger.warning(f"{task_name:40s} {which}_diff {diff:.4f} GOT BETTER (baseline {base_val:.4f})")

        for task_name, which, diff, ceiling in regressions:
            logger.error(f"{task_name:40s} {which}_diff {diff:.4f} exceeds ceiling {ceiling:.4f}")
        if regressions:
            sys.exit(f"{len(regressions)} render diffs exceed their ceilings")


if __name__ == "__main__":
    main()
