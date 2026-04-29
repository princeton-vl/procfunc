# Simple LLM inference experiments using scripts/run_llm_inference.py
# Run from experiments/ folder

METHOD="uv run --quiet python scripts/run_llm_inference.py --task_type material --workers 6 --max_renders 2"

BGYM="--backend bgym --blender_path ./blender_3_6.sh --render_script blendergym/system/blender_base/pipeline_render_script.py"

PF_FROMSCRATCH="--backend pf --bench_data outputs/bench_data_pf_fromscratch --prompt_file prompts/material_simple/pf_fromscratch.txt --rounds 8"
BGYM_FROMSCRATCH="--backend bgym --bench_data outputs/bench_data_ifg_fromscratch --prompt_file prompts/material_simple/ifg_fromscratch.txt $BGYM --rounds 8"
PF_DOCS="--reference_file prompts/reference_code/pf_shader_interface.py --examples_file prompts/reference_code/pf_incontext_examples.py"
BGYM_DOCS="--reference_file prompts/reference_code/ifg_shader_nodes_interface.txt --examples_file prompts/reference_code/infinigenv1_incontext_examples.py"

#dryrun
$METHOD $PF_FROMSCRATCH --model dryrun --output_dir outputs/exp_pf_fromscratch_dryrun

# PF fromscratch
$METHOD $PF_FROMSCRATCH --model gemini-2.5-pro   --output_dir outputs/exp_pf_fromscratch_gemini-2.5-pro_nodocs/0
$METHOD $PF_FROMSCRATCH --model gemini-2.5-pro   --output_dir outputs/exp_pf_fromscratch_gemini-2.5-pro/0 $PF_DOCS
$METHOD $PF_FROMSCRATCH --model gpt-5.2          --output_dir outputs/exp_pf_fromscratch_gpt-5.2/0 $PF_DOCS

# IFG fromscratch
$METHOD $BGYM_FROMSCRATCH --model gemini-2.5-pro   --output_dir outputs/exp_ifg_fromscratch_gemini-2.5-pro_nodocs/0
$METHOD $BGYM_FROMSCRATCH --model gemini-2.5-pro   --output_dir outputs/exp_ifg_fromscratch_gemini-2.5-pro/0 $BGYM_DOCS
$METHOD $BGYM_FROMSCRATCH --model gpt-5.2          --output_dir outputs/exp_ifg_fromscratch_gpt-5.2/0 $BGYM_DOCS

## EVAL COMMANDS
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_pf_fromscratch_gemini-2.5-pro_nodocs/* --bench_data outputs/bench_data_pf
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_ifg_fromscratch_gemini-2.5-pro_nodocs/* --bench_data outputs/bench_data
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_pf_fromscratch_gemini-2.5-pro/* --bench_data outputs/bench_data_pf
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_ifg_fromscratch_gemini-2.5-pro/* --bench_data outputs/bench_data
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_ifg_fromscratch_gpt-5-mini/0 --bench_data outputs/bench_data
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_pf_fromscratch_gpt-5-mini/0 --bench_data outputs/bench_data_pf
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_ifg_fromscratch_gpt-5.2/0 --bench_data outputs/bench_data
uv run python /home/araistrick/projects/procfunc/experiments/scripts/evaluate_results.py outputs/exp_pf_fromscratch_gpt-5.2/0 --bench_data outputs/bench_data_pf

for f in outputs/*fromscratch*/0/overall_scores.tsv; do echo "$f"; cat "$f"; echo; echo; done > outputs/tab2_fromscratch.tsv
