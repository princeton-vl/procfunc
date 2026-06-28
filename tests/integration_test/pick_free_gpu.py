"""Print comma-separated ids of N free GPUs (nvidia-smi memory heuristic).

A GPU counts as free when its used memory is under GPU_MEM_USED_MAX_MB.
Waits/retries if not enough are free. Usage:
  CUDA_VISIBLE_DEVICES=$(python pick_free_gpu.py [n])
"""

import os
import subprocess
import sys
import time


def free_gpu_ids(used_max_mb):
    out = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,memory.used",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    ids = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        idx, used_mb = (p.strip() for p in line.split(","))
        if int(used_mb) < used_max_mb:
            ids.append(idx)
    return ids


def main():
    want = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    used_max_mb = int(os.environ.get("GPU_MEM_USED_MAX_MB", "10000"))
    sleep_seconds = int(os.environ.get("GPU_WAIT_SLEEP_SECONDS", "60"))
    max_retries = int(os.environ.get("GPU_WAIT_MAX_RETRIES", "20"))

    for _ in range(max_retries):
        free = free_gpu_ids(used_max_mb)
        if len(free) >= want:
            print(",".join(free[:want]))
            return
        time.sleep(sleep_seconds)
    sys.exit(
        f"No {want} free GPU(s) (<{used_max_mb}MB used) after {max_retries} retries"
    )


if __name__ == "__main__":
    main()
