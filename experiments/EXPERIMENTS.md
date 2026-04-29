
# ProcFunc LLM/VLM Experiments

This code can be used to measure ProcFunc's performance on BlenderGym's material and geometry Parameter Editing tasks, aswell to measure performance on our non-standard From Scratch generation setting, which provides no starter code.

Note: Our contribution does not include experiments or code support for BlenderGym's lighting and placement tasks, even though these could in principle be represented as ProcFunc programs.

## Choose a ProcFunc version

These instructions are valid only for use with the `experiments` branch of ProcFunc. This branch will have no interface changes, but may have bugfixes in the experiment code itself (if necessary).

Using this experiment code with any other version of ProcFunc may produce invalid results, or may have signifcantly different LLM performance due to interface changes. If you use any version besides `experiments`, you should report the major version in your paper. e.g. "We used ProcFunc v0.30.0 for all experiments." 

We will not actively maintain the correctness of this experiment code on the `main` branch, but please make a Github Issue if you intend to contribute to this.

## Setup

### Installation

Experiment code is not included in our PyPi package, so you must install from source (including heavier dependencies e.g. torch):

```bash
git clone https://github.com/princeton-vl/procfunc.git
cd procfunc

git checkout experiments
uv venv
uv pip install -e .

cd experiments/
uv pip install -r requirements.txt
```

Install BlenderGym, BlenderGym's fork of Infinigen v1.2.5, and a headless Blender 3.6 with Infinigen's dependencies:
```bash
git clone https://github.com/richard-guyunqi/BlenderGym-Open blendergym
git clone git@github.com:richard-guyunqi/infinigen.git blendergym/infinigen
bash install_blendergym_bl36.sh
```
This installs Blender to `blender_3_6/` and uses `infinigen125_requirements.txt` (Infinigen's deps minus `bpy`) to avoid a bug with installing `bpy==3.6.0` into Blender's bundled Python.

### Download and generate parameter-editing task files

Download blendergym's original task files (downloads and unpacks 1.8GB from HuggingFace)
```bash
uv run python blendergym/generate_benchdata.py

mkdir outputs
mv bench_data outputs/bench_data
rm bench_data.zip
```

Generate the ProcFunc-API-equivalent of blendergym's bench_data. 
For every material/geometry task in Blendergym, this will execute it to a blenderfile, transpile to procfunc, then re-render the start/end images.
Default runtime ~20min on a GPU desktop. You can attempt `--num_workers 4` to process the tasks in paralell.
```bash
uv run python scripts/generate_benchdata_procfunc.py outputs/bench_data outputs/bench_data_pf --task_type material --blender_bgym_path ./blender_3_6.sh
uv run python scripts/generate_benchdata_procfunc.py outputs/bench_data outputs/bench_data_pf --task_type geometry --blender_bgym_path ./blender_3_6.sh
```

You can check visualize and check for render differences between Bgym/Infinigen1.2.5 vs Procfunc using the script below:
```bash
uv run python scripts/visualize_bgym_pf_start_goal.py material outputs/bench_data outputs/bench_data_pf outputs/visualize_bgym_pf_material
uv run python scripts/visualize_bgym_pf_start_goal.py geometry outputs/bench_data outputs/bench_data_pf outputs/visualize_bgym_pf_geometry
```

The procfunc start and end renders are not exact matches to the original BlenderGym renders. The main sources of error are (1) different random seeds for placement of geometry particles (e.g. grains of sugar in tasks geometry46-geometry50), and a difference subsurface shading model (e.g. geometry49) due to our using Blender4.2 vs Blender3.6. 
In both cases these are not major semantic differences and should not affect the difficulty of the task, since the required code edits do not change and the image differences do not obscure the edits needed.

### Generate BlenderGym From-Scratch Procedural Generation Files

Create our non-standard "from-scratch" startfiles, which replace the start.py files with an empty template.
```bash
cp -r outputs/bench_data outputs/bench_data_ifg_fromscratch
cp -r outputs/bench_data_pf outputs/bench_data_pf_fromscratch
find outputs/bench_data_ifg_fromscratch -name "start.py" -exec cp prompts/reference_code/ifg_fromscratch_starterfile.py {} \;
find outputs/bench_data_pf_fromscratch -name "start.py" -exec cp prompts/reference_code/pf_fromscratch_starterfile.py {} \;
```

### Re-generate in-context data:

VLMs attempting the From-Scratch task are provided with in-context documentation and finished material examples.
**Files for the `experiment` ProcFunc version are already provided in `prompts/reference_code/`**. 
However, you may re-generate using commands below, and especially should do so if using a later or nonstandard version of ProcFunc: 

Generate simple .txt reference files for ProcFunc and BlenderGym/Infinigen1.2.5's NodeWrangler interface:
```bash
uv run python scripts/create_procfunc_incontext_reference.py prompts/reference_code/pf_shader_interface.py ../src/procfunc/nodes/{math,shader}.py
uv run python scripts/create_procfunc_incontext_reference.py prompts/reference_code/pf_geo_interface.py ../src/procfunc/nodes/{math,func,shader,geo}.py
./blender_3_6.sh --background --python scripts/create_blender_nodes_interface.py -- prompts/reference_code/ifg_shader_nodes_interface.txt --node-types ShaderNode 
./blender_3_6.sh --background --python scripts/create_blender_nodes_interface.py -- prompts/reference_code/ifg_geo_nodes_interface.txt --node-types GeometryNode ShaderNode FunctionNode
```

Generate in-context material examples:
```bash
INCONTEXT_FILES="blendergym/system/blender_scripts/material_examples/infinigen_bone_example.py blendergym/system/blender_scripts/material_examples/infinigen_nose_example.py blendergym/system/blender_scripts/material_examples/infinigen_snakeplant_example.py blendergym/system/blender_scripts/material_examples/infinigen_tongue_example.py blendergym/system/blender_scripts/material_examples/infinigen_wood_example.py"

# infinigen examples (execute to concretify random values, then re-transpile to infinigen)
uv run python scripts/reexecute_ifg_examples.py prompts/reference_code/ifg_incontext_examples/ outputs/bench_data_pf_fromscratch/material1/blender_file.blend $INCONTEXT_FILES --blender_bgym_path ./blender_3_6.sh
cat prompts/reference_code/ifg_incontext_examples/*.py | grep -v import > prompts/reference_code/infinigenv1_incontext_examples.py

# procfunc examples
uv run python scripts/executable_materials_to_procfunc.py prompts/reference_code/pf_incontext_examples/ outputs/bench_data_pf_fromscratch/material1/blender_file.blend $INCONTEXT_FILES --blender_bgym_path ./blender_3_6.sh
cat prompts/reference_code/pf_incontext_examples/*.py | grep -v import > prompts/reference_code/pf_incontext_examples.py
```

### API Keys

**Option A**: Create a `credentials/` directory with text files (auto-discovered based on model prefix):
```bash
mkdir -p credentials
echo "your-openai-key-here" > credentials/openai_api.txt
echo "your-google-key-here" > credentials/gemini_api.txt
```

**Option B**: Set environment variables:
```bash
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
```

## Paper Experiments - ProcFunc Evaluation Harness

We provide each suite of experiments as a separate bash script in `commands/`. 
You can in theory each file directly, but we recommend copying individual lines and running them one at a time or in paralell.

Material Editing: [commands/material_editing.sh](commands/material_editing.sh)
Geometry Editing: [commands/geometry_editing.sh](commands/geometry_editing.sh)

Material From-Scratch: [commands/material_fromscratch.sh](commands/material_fromscratch.sh)
Geometry From-Scratch: [commands/geometry_fromscratch.sh](commands/geometry_fromscratch.sh)

You can easily modify the experiments by changing bash variables or --arguments, e.g. using new gemini-3.x or gpt-5.x models, or adding new prompt.txt files. 