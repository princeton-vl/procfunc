from pathlib import Path
import argparse
import logging
import imageio
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def visualize_task(task_name: str, start_img: Path, goal_img: Path, step_imgs: list[Path], out_path: Path, title: str = ""):
    """Create visualization with start, steps, and goal images."""
    n_steps = len(step_imgs)
    fig, axes = plt.subplots(1, n_steps + 2, figsize=(2 * (n_steps + 2), 2.25))
    fig.set_tight_layout(True)
    if title:
        fig.suptitle(title)

    for ax in axes:
        ax.axis("off")

    axes[0].imshow(imageio.imread(start_img))
    axes[0].set_title("Start")

    for i, img in enumerate(step_imgs):
        axes[i + 1].imshow(imageio.imread(img))
        axes[i + 1].set_title(f"Round {i}")

    axes[-1].imshow(imageio.imread(goal_img))
    axes[-1].set_title("Goal")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300)
    plt.close()
    logger.info(f"Saved {out_path}")


def find_render(folder: Path) -> Path | None:
    for name in ["render1.png", "render.png"]:
        if (p := folder / name).exists():
            return p
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("llm_results_path", type=Path)
    parser.add_argument("--bench_data", type=Path, required=True)
    parser.add_argument("--out_vis_path", type=Path, default=None)
    parser.add_argument("--description", type=str, default="")
    args = parser.parse_args()

    out_vis_path = args.out_vis_path or args.llm_results_path / "vis"

    for task_dir in sorted(args.llm_results_path.iterdir()):
        if not task_dir.is_dir():
            continue
        task_name = task_dir.name
        bench_task = args.bench_data / task_name
        if not bench_task.exists():
            continue

        start_img = find_render(bench_task / "renders" / "start")
        goal_img = find_render(bench_task / "renders" / "goal")
        if not goal_img:
            logger.warning(f"{task_name}: no goal render")
            continue

        # New format: round_00/, round_01/, ...
        if list(task_dir.glob("round_*")):
            rounds = sorted(task_dir.glob("round_*"))
            step_imgs = [find_render(r) for r in rounds]
            step_imgs = [p for p in step_imgs if p]
        # Old bgym format: instance0/*/best_of.png
        elif (task_dir / "instance0").exists():
            step_path = next((task_dir / "instance0").iterdir(), None)
            if step_path and (step_path / "best_of.png").exists():
                step_imgs = [step_path / "best_of.png"]
                start_img = start_img or (step_path / "init_render.png")
            else:
                step_imgs = []
        else:
            logger.warning(f"{task_name}: unknown format")
            continue

        if not step_imgs:
            logger.warning(f"{task_name}: no step renders found")
            continue

        visualize_task(
            task_name, start_img, goal_img, step_imgs,
            out_vis_path / f"{task_name}.png",
            title=f"{args.description} {task_name}" if args.description else task_name
        )

        
if __name__ == "__main__":
    main()