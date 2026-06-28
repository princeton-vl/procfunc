# procfunc migration codemods

ast-grep rule packs that rewrite the mechanical renames for each procfunc version bump. One file per bump: `to_0.31.yml` (0.30→0.31), `to_0.32.yml` (0.31→0.32), `to_0.33.yml` (0.32→0.33), `to_0.34.yml` (0.33→0.34).

## Run

Install ast-grep (tested on 0.39.9):

```bash
brew install ast-grep        # or: cargo install ast-grep
```

Use the `ast-grep` command, **not** `sg` — on macOS `sg` is the built-in setgroup binary, not ast-grep. Apply one bump at a time, in order, from the repo root. The last argument is the code to scan; `-r` names the rule file:

```bash
ast-grep scan -r scripts/update_greps/to_0.31.yml    src/ tests/   # dry run: prints the diff, changes nothing
ast-grep scan -r scripts/update_greps/to_0.31.yml -U src/ tests/   # apply: rewrites the files in place
ruff format src/ tests/                                            # an inserted/removed kwarg can collapse a wrapped call
```

Read the dry-run diff before you pass `-U`, and run on a clean git tree so you can revert. After a bump applies, set the new pin in `pyproject.toml` (e.g. `procfunc>=0.31,<0.32`), run your tests, and commit before the next file. Don't skip versions.

Each file's header comment says what it rewrites. Every file mixes auto-fix rules (`fix:`) with **locate-only** rules (no `fix:`) that flag the context-dependent edits below — those show up in the dry-run as matches with no diff; hand-edit them. `to_0.34.yml` is locate-only apart from the `hex_color` alpha drop.

## Edit by hand

- **→0.31** — `geo.fillet_curve` (drop `mode=`), `shader.vector_math` (→ `math.vector_multiply`/`vector_multiply_add`/…), `compositor.combine_color` (→ `color.combine_rgb` + optional `compositor.set_alpha`), and `geo.distribute_points_on_faces` (→ `..._poisson`, `density=`→`density_factor=`) all split by call shape — the locate rules flag every site. `separate_color` auto-rewrites to `separate_rgb` (the old default); if you used `mode="HSV"/"HSL"`, change to `separate_hsv`/`separate_hsl` by hand. Also removed: `pf.nodes.misc`, `geo.viewer`, the compositor math/color aliases; primary inputs now required on `geo.transform`, `math.mix`, and the other functions that lost placeholder defaults.
- **→0.32** — multi-output nodes return NamedTuples, so consume the field (`mesh_boolean(...).mesh`); `mesh_boolean`/`curve_arc`/`curve_circle` split per operation (the `mesh_boolean` locate rule flags both); `None` now errors on a value socket.
- **→0.33** — `principled_bsdf` `normal`/`coat_normal`/`tangent` default to `None`; `OperatorType.AND`/`OR` removed; internal module paths moved (only if you import procfunc internals).
- **→0.34** — the strict-mode checks moved to downstream consumers. Delete the `warn_mode_avoid_normal_bump`/`_implicit_vector`/`_io_nodes` context fields and the `PROCFUNC_WARN_MODE_AVOID_*` env vars (keep `warn_mode_empty_geonodes`). `hex_color`'s `alpha` arg is dropped automatically. Review `texture.noise` calls passing `offset=`/`gain=` (now default `None` and raise for noise types that don't support them) and any `from procfunc.compute_graph import transform_nodetree`. Dropping `normal=(0.0, 0.0, 0.0)` from `diffuse_bsdf`/`anisotropic_bsdf` is optional cleanup (the input still works when provided) — `to_0.34.yml` finds those sites.

## What each rewrite looks like

- **0.31** — `pf.nodes.shader.voronoi_distance(...)` → `pf.nodes.texture.voronoi_distance(...)`; `geo.mesh_boolean(mesh_1=, mesh_2=)` → `(a=, b=)`; `compositor.mix_rgb(image_0=, image_1=)` → `(a=, b=)`.
- **0.32** — `color.mix_rgb(a, b)` → `color.mix_rgb(factor=0.5, a, b)`; `color.hue_saturation(color)` → `color.hue_saturation(fac=1.0, color)`.
- **0.33** — `texture.noise(scale=...)` → `texture.noise(vector=None, scale=...)`.
- **0.34** — `color.hex_color(h, alpha=...)` → `color.hex_color(h)`; optional cleanup `shader.diffuse_bsdf(color=c, normal=(0.0, 0.0, 0.0))` → `shader.diffuse_bsdf(color=c)`.
