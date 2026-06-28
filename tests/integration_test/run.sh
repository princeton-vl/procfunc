#!/usr/bin/env bash
# Transpile round-trip + dual render pixel-diff gate. See README.md.
# Usage: run.sh <data_dir> [out_dir]
# Env: TASKS (subset or "all"), THRESH_BGYM (4.0), THRESH_PF (0.5), CUDA_VISIBLE_DEVICES.

set -euo pipefail

DATA="${1:?usage: run.sh <data_dir> [out_dir]}"
OUT="${2:-./integration_out}"

THRESH_BGYM="${THRESH_BGYM:-4.0}"
THRESH_PF="${THRESH_PF:-0.5}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
mkdir -p "$OUT"

# Single source of truth for the task list + per-frame Gate A baselines.
# Lives with the staged dataset (render-derived), not in the repo.
TASKS_JSON="$DATA/tasks.json"
DEFAULT_TASKS="$(uv run python -c "import json,sys; print(' '.join(json.load(open(sys.argv[1]))['tasks']))" "$TASKS_JSON")"
TASKS="${TASKS:-$DEFAULT_TASKS}"

TASKARG=()
if [ "$TASKS" != "all" ]; then
  TASKARG=(--tasks $TASKS)
fi

echo "=== Transpile-blend round-trip (transpile + execute, no render) ==="
uv run python "$HERE/transpile_roundtrip_check.py" \
  blends "$DATA/transpile-blends" --out "$OUT/blends"

# F401/F841 ignored: import preamble + intermediates.
echo "=== Lint generated code (ruff) ==="
uv run ruff check --isolated --select E9,F --ignore F401,F841 "$OUT/blends"

if [ -z "${CUDA_VISIBLE_DEVICES:-}" ]; then
  export CUDA_VISIBLE_DEVICES="$(uv run python "$HERE/pick_free_gpu.py" 1)"
fi
echo "=== Using GPU(s): $CUDA_VISIBLE_DEVICES ==="

cd "$REPO/experiments"
ln -sfn "$DATA/bl36env/blendergym" blendergym

echo "=== Regenerate bench_data from base (execute + transpile + render) ==="
for tt in material geometry; do
  uv run python scripts/generate_benchdata_procfunc.py \
    "$DATA/bench_data" "$OUT/bench_data_pf" \
    --task_type "$tt" --overwrite --num_workers 4 \
    --blender_bgym_path "$DATA/bl36env/blender_3_6.sh" \
    "${TASKARG[@]}"
done

echo "=== Gate A: vs blendergym 3.6 reference (thresh $THRESH_BGYM, per-task ceilings) ==="
for tt in material geometry; do
  uv run python scripts/visualize_bgym_pf_start_goal.py \
    "$tt" "$DATA/bench_data" "$OUT/bench_data_pf" \
    "$OUT/vis_bgym_$tt" --thresh "$THRESH_BGYM" \
    --thresh-json "$TASKS_JSON" "${TASKARG[@]}"
done

echo "=== Gate B: vs frozen experiments-branch pf reference (thresh $THRESH_PF) ==="
for tt in material geometry; do
  uv run python scripts/visualize_bgym_pf_start_goal.py \
    "$tt" "$DATA/pf_reference_experiments" "$OUT/bench_data_pf" \
    "$OUT/vis_pf_$tt" --thresh "$THRESH_PF" "${TASKARG[@]}"
done
