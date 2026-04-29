# Simple LLM inference experiments using scripts/run_llm_inference.py
# Run from experiments/ folder

METHOD="uv run --quiet python scripts/run_llm_inference.py --task_type material --workers 6 --max_renders 2"

BGYM="--backend bgym --blender_path ./blender_3_6.sh --render_script blendergym/system/blender_base/pipeline_render_script.py"

PF_PARAMEDIT="--backend pf --bench_data outputs/bench_data_pf --prompt_file prompts/material_simple/pf_paramedit.txt --rounds 4 "
BGYM_PARAMEDIT="--backend bgym --bench_data outputs/bench_data --prompt_file prompts/material_simple/ifg_paramedit.txt $BGYM --rounds 4"

#dryrun
$METHOD $PF_PARAMEDIT --model dryrun --output_dir outputs/exp_pf_paramedit_dryrun

# PF paramedit
$METHOD $PF_PARAMEDIT --model gemini-2.5-flash --output_dir outputs/exp_pf_paramedit_gemini-2.5-flash/0/
$METHOD $PF_PARAMEDIT --model gemini-2.5-pro   --output_dir outputs/exp_pf_paramedit_gemini-2.5-pro/0
$METHOD $PF_PARAMEDIT --model gpt-5-mini       --output_dir outputs/exp_pf_paramedit_gpt-5-mini/0
$METHOD $PF_PARAMEDIT --model gpt-5.2          --output_dir outputs/exp_pf_paramedit_gpt-5.2/0

# IFG paramedit
$METHOD $BGYM_PARAMEDIT --model gemini-2.5-flash --output_dir outputs/exp_ifg_paramedit_gemini-2.5-flash/0
$METHOD $BGYM_PARAMEDIT --model gemini-2.5-pro   --output_dir outputs/exp_ifg_paramedit_gemini-2.5-pro/0
$METHOD $BGYM_PARAMEDIT --model gpt-5-mini       --output_dir outputs/exp_ifg_paramedit_gpt-5-mini/0
$METHOD $BGYM_PARAMEDIT --model gpt-5.2          --output_dir outputs/exp_ifg_paramedit_gpt-5.2/0

## EVAL COMMANDS

uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_pf_paramedit_gemini-2.5-flash/* --bench_data outputs/bench_data_pf
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_ifg_paramedit_gemini-2.5-flash/* --bench_data outputs/bench_data
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_pf_paramedit_gemini-2.5-pro/* --bench_data outputs/bench_data_pf
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_ifg_paramedit_gemini-2.5-pro/* --bench_data outputs/bench_data
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_pf_paramedit_gpt-5-mini/0 --bench_data outputs/bench_data_pf
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_pf_paramedit_gpt-5.2/0 --bench_data outputs/bench_data_pf
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_ifg_paramedit_gpt-5-mini/0 --bench_data outputs/bench_data
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_ifg_paramedit_gpt-5.2/0 --bench_data outputs/bench_data

for f in outputs/*paramedit*/0/overall_scores.tsv; do echo "$f"; cat "$f"; echo; echo; done > outputs/tab1_paramedit.tsv