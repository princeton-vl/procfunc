# ProcFunc: Function-Oriented Abstractions for Procedural 3D Generation in Python

[**Documentation**](#documentation)
| [**Research Paper**](#paper)
| [**Documentation**](#paper)
| [**Transpiling**](#transpile-a-blender-file-to-procfunc-code)
| [**Experiments**](#experiments)
| [**Contributing**](#contributing)

This repository contains only the Primitives API, Transpiler and Tracer from our research paper.

The pre-made procedural generators are coming soon as part of [infinigen](https://github.com/princeton-vl/infinigen).

### Installation

Use [uv](https://docs.astral.sh/uv/getting-started/installation/) or your favorite package manager to install procfunc via pip:
```bash
uv pip install procfunc
```

Note: ProcFunc depends on `bpy==4.2.0` which then requires Python==3.11.x. Other version are not yet supported.

Since we have not yet reached [semver 1.0.0](https://semver.org/) we have not yet finalized procfunc's interface. 
In the meantime, each 0.X.0 may introduce interface changes. Please pin `uv add procfunc<0.XX` where X is the current version.

### Usage

See [procfunc.readthedocs.io](https://procfunc.readthedocs.io) for available functions

Please create Github Issues for any bugs or  unclear interfaces!

##### Transpile a blender file to ProcFunc code

<p float="left">
  <img src="examples/transpile_simple_chair/blender_screenshot.png" height="200" />
  <img src="examples/transpile_simple_chair/code_screenshot.png" height="200" />
</p>

Convert a Blender geometry node tree into procfunc Python code by downloading our example blend and executing the transpiler:
```bash
wget https://raw.githubusercontent.com/princeton-vl/procfunc/main/examples/transpile_simple_chair/simple_chair.blend
uv run python -m procfunc.transpiler.main simple_chair.blend --node_trees simple_chair --output transpiled_code.py
```

See the expected output in [`examples/transpile_simple_chair/transpiled_code.py`](examples/transpile_simple_chair/transpiled_code.py).
To use the code, you can add `pf.ops.file.save_blend("test.blend")` to the end of it, then open the generated blender file.
You can also open and edit the blender geonodes prior to transpiling in order to generate different procfunc code.

### Paper

If you find procfunc useful, please cite our paper:
```
@misc{raistrick2026procfunc,
      title={ProcFunc: Function-Oriented Abstractions for Procedural 3D Generation in Python}, 
      author={Alexander Raistrick and Karhan Kayan and Jack Nugent and David Yan and Lingjie Mei and Meenal Parakh and Hongyu Wen and Dylan Li and Yiming Zuo and Erich Liang and Jia Deng},
      year={2026},
      eprint={2604.26943},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2604.26943}, 
}
```

### Experiments

See [experiments/EXPERIMENTS.md](experiments/EXPERIMENTS.md)

NOTE: experiments are only intended to be correct when using the `experiments` branch, which will not see major updates.

### Contributing

Please create an issue for any proposed features to discuss them before implementing.

##### Developer Installation
```bash
git clone git@github.com:princeton-vl/procfunc.git
cd procfunc
uv venv
uv pip install -e ".[dev]"
```

##### Tools

```bash
uv run ruff format
uv run ruff check --fix
uv run pytest
make docs
```

##### Todos / Sharp Edges

Add optional support for bpy==4.x and 5.x and maybe 3.6, all under the same procfunc interface. 

pf.ops is missing some blender functions and arguments, especially returning "selection" masks for some cases. 

Assets like pf.MeshObject and pf.Material are not currently cleaned up upon going out of scope 
