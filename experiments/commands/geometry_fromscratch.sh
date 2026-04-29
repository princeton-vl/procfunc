# Simple LLM inference experiments for geometry nodes using scripts/run_llm_inference.py
# Run from experiments/ folder

METHOD="uv run --quiet python scripts/run_llm_inference.py --task_type geometry --workers 6 --max_renders 2"

BGYM="--backend bgym --blender_path ./blender_3_6.sh --render_script blendergym/system/blender_base/pipeline_render_script.py"

PF_PARAMEDIT="--backend pf --bench_data outputs/bench_data_pf --prompt_file prompts/geo_simple/pf_paramedit.txt --rounds 4 "
BGYM_PARAMEDIT="--backend bgym --bench_data outputs/bench_data --prompt_file prompts/geo_simple/ifg_paramedit.txt $BGYM --rounds 4"
PF_FROMSCRATCH="--backend pf --bench_data outputs/bench_data_pf_fromscratch --prompt_file prompts/geo_simple/pf_fromscratch.txt --rounds 8"
BGYM_FROMSCRATCH="--backend bgym --bench_data outputs/bench_data_ifg_fromscratch --prompt_file prompts/geo_simple/ifg_fromscratch.txt $BGYM --rounds 8"

#dryrun
$METHOD $PF_PARAMEDIT --model dryrun --output_dir outputs/exp_geo_pf_paramedit_dryrun

# PF paramedit
$METHOD $PF_PARAMEDIT --model gemini-2.5-flash --output_dir outputs/exp_geo_pf_paramedit_gemini-2.5-flash/0/
$METHOD $PF_PARAMEDIT --model gemini-2.5-pro   --output_dir outputs/exp_geo_pf_paramedit_gemini-2.5-pro/0
$METHOD $PF_PARAMEDIT --model gpt-5-mini       --output_dir outputs/exp_geo_pf_paramedit_gpt-5-mini/0
$METHOD $PF_PARAMEDIT --model gpt-5.2          --output_dir outputs/exp_geo_pf_paramedit_gpt-5.2/0
$METHOD $PF_PARAMEDIT --model gemini-3-flash-preview --output_dir outputs/exp_geo_pf_paramedit_gemini-3-flash/0/
$METHOD $PF_PARAMEDIT --model gemini-3-pro-preview --output_dir outputs/exp_geo_pf_paramedit_gemini-3-pro/0/ --workers 4

# IFG paramedit
$METHOD $BGYM_PARAMEDIT --model gemini-2.5-flash --output_dir outputs/exp_geo_ifg_paramedit_gemini-2.5-flash/0
$METHOD $BGYM_PARAMEDIT --model gemini-2.5-pro   --output_dir outputs/exp_geo_ifg_paramedit_gemini-2.5-pro/0
$METHOD $BGYM_PARAMEDIT --model gpt-5-mini       --output_dir outputs/exp_geo_ifg_paramedit_gpt-5-mini/0
$METHOD $BGYM_PARAMEDIT --model gpt-5.2          --output_dir outputs/exp_geo_ifg_paramedit_gpt-5.2/0
$METHOD $BGYM_PARAMEDIT --model gemini-3-flash-preview --output_dir outputs/exp_geo_ifg_paramedit_gemini-3-flash/0
$METHOD $BGYM_PARAMEDIT --model gemini-3-pro-preview   --output_dir outputs/exp_geo_ifg_paramedit_gemini-3-pro/0 --workers 4

# PF fromscratch
$METHOD $PF_FROMSCRATCH --model gemini-2.5-pro   --output_dir outputs/exp_geo_pf_fromscratch_gemini-2.5-pro_nodocs/0
$METHOD $PF_FROMSCRATCH --model gemini-2.5-pro   --output_dir outputs/exp_geo_pf_fromscratch_gemini-2.5-pro/0 --reference_file prompts/reference_code/pf_geo_interface.py --examples_file prompts/reference_code/pf_geo_incontext_examples.py

# IFG fromscratch
$METHOD $BGYM_FROMSCRATCH --model gemini-2.5-pro   --output_dir outputs/exp_geo_ifg_fromscratch_gemini-2.5-pro_nodocs/0
$METHOD $BGYM_FROMSCRATCH --model gemini-2.5-pro   --output_dir outputs/exp_geo_ifg_fromscratch_gemini-2.5-pro/0 --reference_file prompts/reference_code/ifg_geo_nodes_interface.txt --examples_file prompts/reference_code/ifg_geo_incontext_examples.py

## EVAL COMMANDS

uv run python scripts/evaluate_results.py outputs/exp_geo_pf_paramedit_gemini-2.5-flash/* --bench_data outputs/bench_data_pf
uv run python scripts/evaluate_results.py outputs/exp_geo_ifg_paramedit_gemini-2.5-flash/* --bench_data outputs/bench_data
uv run python scripts/evaluate_results.py outputs/exp_geo_pf_paramedit_gemini-2.5-pro/* --bench_data outputs/bench_data_pf
uv run python scripts/evaluate_results.py outputs/exp_geo_ifg_paramedit_gemini-2.5-pro/* --bench_data outputs/bench_data
uv run python scripts/evaluate_results.py outputs/exp_geo_pf_paramedit_gpt-5-mini/* --bench_data outputs/bench_data_pf
uv run python scripts/evaluate_results.py outputs/exp_geo_ifg_paramedit_gpt-5-mini/* --bench_data outputs/bench_data
uv run python scripts/evaluate_results.py outputs/exp_geo_pf_paramedit_gpt-5.2/* --bench_data outputs/bench_data_pf
uv run python scripts/evaluate_results.py outputs/exp_geo_ifg_paramedit_gpt-5.2/* --bench_data outputs/bench_data

for f in outputs/*geo*paramedit*/0/overall_scores.tsv; do echo "$f"; cat "$f"; echo; echo; done > outputs/tab1_geo_paramedit.tsv

uv run python scripts/evaluate_results.py outputs/exp_geo_pf_fromscratch_gemini-2.5-pro_nodocs/* --bench_data outputs/bench_data_pf_fromscratch
uv run python scripts/evaluate_results.py outputs/exp_geo_ifg_fromscratch_gemini-2.5-pro_nodocs/* --bench_data outputs/bench_data_ifg_fromscratch
uv run python scripts/evaluate_results.py outputs/exp_geo_pf_fromscratch_gemini-2.5-pro/* --bench_data outputs/bench_data_pf_fromscratch
uv run python scripts/evaluate_results.py outputs/exp_geo_ifg_fromscratch_gemini-2.5-pro/* --bench_data outputs/bench_data_ifg_fromscratch

for f in outputs/*geo*fromscratch*/0/overall_scores.tsv; do echo "$f"; cat "$f"; echo; echo; done > outputs/tab2_geo_fromscratch.tsv