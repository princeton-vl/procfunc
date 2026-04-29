import argparse
import logging
from pathlib import Path

import imageio
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("task_type", type=str, choices=["material", "geometry"])
    parser.add_argument("bench_data_bgym", type=Path)
    parser.add_argument("bench_data_pf", type=Path)
    parser.add_argument("out_vis_path", type=Path)
    parser.add_argument("--tasks", type=str, nargs='+', default=None)
    args = parser.parse_args()

    args.out_vis_path.mkdir(parents=True, exist_ok=True)

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
            continue

        imgs = [imageio.imread(path) for path in paths]
        assert all(img.shape == imgs[0].shape for img in imgs), [img.shape for img in imgs]

        start_diff = np.abs(imgs[0].astype(float) - imgs[1].astype(float)).mean()
        goal_diff = np.abs(imgs[2].astype(float) - imgs[3].astype(float)).mean()
        logger.info(f"{task_name:40s} start_diff {start_diff:.4f}  {paths[0]}  {paths[1]}")
        logger.info(f"{task_name:40s} goal_diff  {goal_diff:.4f}  {paths[2]}  {paths[3]}")

        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        for i, (img, path) in enumerate(zip(imgs, paths)):
            ax = axes[i // 2, i % 2]
            ax.imshow(img)
            ax.set_title(path)
            ax.axis("off")

        fig.savefig(args.out_vis_path / f"{task_name}.png")
        plt.close()



if __name__ == "__main__":
    main()
