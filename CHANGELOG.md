# 0.32.1

Bugfix release from a full pre-release review of 0.32.0, plus a follow-up repo-wide audit. See PR #109 for repros and details.

Breaking signature fixes:

- `texture.noise` / `voronoi` / `voronoi_distance` / `voronoi_smooth_f1`: `vector` is now a required argument; pass `vector=None` explicitly to opt into blender's implicit coordinates (gated by `warn_mode_avoid_implicit_vector`). The old guards silently dropped explicit constant vectors (noise pinned default calls to a constant `(0,0,0)`) and rejected wired vectors.
- `shader.principled_bsdf`: `normal` / `coat_normal` / `tangent` default to `None`; the avoid-normal gate fired on every call (including all-defaults) and always wired `Normal=(0,0,0)`

Fixed crashes:

- `from procfunc.nodes import *` (nonexistent `to_material` in `__all__`)
- `'prefix*'` globs in the transpile CLI (inverted assert)
- `procfunc transpile --output print`
- `--add_line_comments` (`NameError` on every use)
- second execution of a scene-bound compositor graph (Render Layers / Cryptomatte)
- `transforms.extract_shader_vectors_as_inputs`, `infer_distribution_hypercube`, `distribution_to_mode`, `outlier_distribution`
- transpiling node groups with matrix or image interface sockets (`KeyError`)
- `@node_function` missing-annotation errors raised their own `AttributeError`
- `to_mesh_object_with_attributes()` with default `attributes=None`
- kwargs-form rng calls (`rng.uniform(low=..., high=...)`) in `distribution_to_mode` / `outlier_distribution`; `normal` params now read numpy's `loc`/`scale`
- `transforms.colors_to_hsv_definition` on positional Color args
- `primitives.empty()` (asserted MESH on an EMPTY object) and boolean modifiers with `Collection` targets
- transpiling legacy `use_clamp` nodes (`TextureNodeMixRGB` / `ShaderNodeMixRGB` → `clamp_result`, `TextureNodeMath` → a `clamp()` wrap)

Fixed wrong results:

- codegen emitted invalid Python for matrix constants and bare `inf`/`nan`; matrices now travel as numpy arrays and coerce back to `mathutils.Matrix` at execute time, lowering to `FunctionNodeCombineMatrix` where needed
- ambiguous tuple compares (`func.less_than((1,2,3), b)`) resolved to RGBA instead of FLOAT_VECTOR
- `GetAttributeNode` / `ProceduralNode` instances all compared equal and were unhashable
- raw `rng.uniform(...)` calls were never recognized as distributions in transforms
- transpile emitted false values for unlinked implicit-field sockets (e.g. `extrude_mesh(offset=(0,0,0))`)
- top-level known value types were silently never recorded for codegen annotations
- `ops.mesh.transform` interpreted `rotation_euler` as an exponential-map rotation vector, not Euler angles
- `random.clip_gaussian` treated `low=0.0` / `high=0.0` as unset
- `infer_nodegroup_distributions` dropped subgraphs with inferred distributions and kept all-dynamic ones (inverted gate)
- `util.pytree` dict specs held a live `keys()` view; mutating the source dict after `flatten` corrupted `unflatten`
- transpile dropped ColorRamp `color_mode`, so HSV/HSL ramps re-executed as RGB (`color_ramp` also gained `hue_interpolation`); codegen emitted SyntaxError code for keyword-named sockets (`Lambda` → `lambda`)
- boolean modifier `threshold` was accepted but never forwarded to the EXACT solver

Errors instead of silent misbehavior:

- mixed scalar+tuple operands and ambiguous length-4 tuples raise a clear `.astype` hint
- vector/color compares outside geometry trees raise instead of degrading to scalar Math COMPARE, including wired (non-literal) vector operands
- inputs/attrs a context's legacy node cannot honor raise per-node (e.g. `mix_rgb(clamp_factor=False)` in texture trees, compositor `vector_curve` with `fac != 1.0`)
- operator dispatch only reorders operands for known-commutative operators

Other:

- no root-logging reconfiguration at import time; CLI scopes verbosity to procfunc loggers
- `override_globals` / codegen printoptions restored on exception
- `__all__` fixes (`sample_collection`, `primitives`); removed dead `is_multi_output` manifest column, `OperatorType.AND/OR` aliases, and dead scaffolding
- version defined once in `procfunc.__version__`; new tests pin multi-input order and matrix round-trips
- new `procfunc.util.bpy_data.removing_new_datablocks` context manager bounds bpy.data growth (used as the test suite cleanup; suitable for downstream suites)
- `compositor.mix_rgb` gained `clamp_result` (the node's `use_clamp` was previously inexpressible)
- `requires-python` pinned to `>=3.11,<3.12` (bpy 4.2.0 is cp311-only)

# 0.32.0

Breaking changes:

- multi-output bindings now return NamedTuples (16 compositor, 3 shader, 3 geo bindings); `shader.coord` gained `reflection` (unpack arity)
- `math.vector_curve` reordered to `(vector, fac=1.0)`; `func.random_value` no longer auto-resolves RGBA
- `color.mix_rgb` requires `factor, a, b`; `color.hue_saturation` requires `color, fac` (reordered)

Additional Python operator bindings:
- comparison `== != < > <= >=` on floats (geometry, shader, and compositor graphs) and integers (geometry)
- string equality `==` / `!=`
- unary `-x` on floats and vectors
- `vector * scalar`
- `+` `-` `*` on colors

Split more functions into per-mode / per-operation bindings:

- `curve_arc` → `curve_arc` (radius) + `curve_arc_from_points`
- `curve_circle` → `curve_circle` (radius) + `curve_circle_from_points`
- `curve_quadrilateral` → `curve_quadrilateral` (rectangle) + `curve_quadrilateral_parallelogram` / `_trapezoid` / `_kite` / `_points`
- `mesh_boolean` → `mesh_boolean` (difference) + `mesh_boolean_union` + `mesh_boolean_intersect`
- `vector_compare_elementwise` → `vector_elementwise_equal` / `_not_equal` / `_less_than` / `_less_equal` / `_greater_than` / `_greater_equal`
- `compare_color` → `color_equal` / `_not_equal` / `_brighter` / `_darker`

Other additions and changes:

- attribute, sample, field, and switch / index_switch nodes accept vector, color, rotation, and matrix data types
- `curve_set_handles` `mode` is a `set[str]` (default `{"LEFT", "RIGHT"}`)
- image inputs accept a `pt.Image` datablock or `None` (to disconnect)
- passing `None` to a value socket now errors; `None` is allowed only on geometry/shader inputs, where it disconnects them. Primary inputs (`mix_shader`, `set_material`, boolean operands, …) are now required.
- removed `pf.nodes.compositor.value` / `pf.nodes.compositor.rgb` (use `pf.nodes.math.constant`)

Bugfixes:

- `func.equal` / `func.not_equal` correctly expose `epsilon` (default 0.001)
- `mesh_boolean` returns an `intersecting_edges` output (with `mesh`) only when `solver="EXACT"`
- transpile sanitizes generated Python identifiers — characters other than letters, digits, and underscores are replaced with underscores — and omits unlinked geometry-modifier outputs
- inline comparison operators (`==` `!=` `<=` `>=`) dropped their constant operand — `x == 1` was built as `x == x` (operand-binding collision on `FunctionNodeCompare`)
- `vector_rotate_axis_angle` (transpiled `AXIS_ANGLE` vector rotate) dropped its angle, leaving no rotation
- multi-input socket links (`join_geometry`, `mesh_boolean`) were built in reversed order, flipping join/winding and reversing boolean operands
- float socket values were rounded to 8 decimal places in codegen, destroying small magnitudes (e.g. a ~5.96e-08 curve coordinate → 6e-08) and perturbing `EXACT` mesh booleans; now emitted as exact float32 round-trips, making transpiled assets vertex-for-vertex identical to the source where they previously diverged

# 0.31.0 (develop → main)

## Moves

- `procfunc.transpiler.codegen` moved to `procfunc.codegen`.
- `combine_xyz`, `separate_xyz`, `constant`, `float_curve`, `map_range`, `mix` moved from `pf.nodes.func` to `pf.nodes.math`.
- `mix_rgb`, `rgb_curve`, `separate_color` moved from `pf.nodes.func` to `pf.nodes.color`.
- `voronoi`, `voronoi_distance`, `voronoi_smooth_f1`, `voronoi_n_spheres_distance`, `checker`, `gradient`, `image`, `noise`, `sky`, `white_noise` moved from `pf.nodes.shader` to `pf.nodes.texture`.
- `color_ramp`, `blackbody`, `bright_contrast`, `gamma`, `hue_saturation`, `rgb_to_bw`, `invert` moved from `pf.nodes.shader` to `pf.nodes.color`.
- Compositor math/color aliases (`math`, `val_to_rgb`, `curve_vec`, `combine_xyz`, `curve_rgb`, `map_range`) dropped; the shared `math.*` / `color.*` bindings now dispatch into the compositor tree via `ContextualNode`.

## Splits

- `pf.nodes.color.separate_color` split into `separate_rgb`, `separate_hsv`, `separate_hsl`.
- `pf.nodes.geo.fillet_curve(mode=…)` split into `fillet_curve_poly` and `fillet_curve_bezier`.

## Removed

- `pf.nodes.shader.value`, `pf.nodes.color.rgb` — use `pf.nodes.math.constant`.
- `pf.nodes.geo.viewer` and the entire `pf.nodes.misc` namespace.
- `pf.nodes.compositor.combine_color` — use `color.combine_rgb` (+ optional `compositor.set_alpha`).

## Positional args unified to `a, b[, c, d]`

- `compositor.alpha_over`, `compositor.diff_matte`, `compositor.mix_rgb`, `compositor.split`.
- `func.matrix_multiply`, `func.index_switch`.
- `geo.mesh_boolean`, `geo.sdf_grid_boolean`.
- `math._math` (`value_2` → `c`).
- `shader.add_shader`.
- Special cases: `compositor.z_combine` uses `image_a, z_a, image_b, z_b`; `compositor.cryptomatte` uses `crypto_00, crypto_01, crypto_02`.

## Placeholder defaults removed (primary inputs now required)

- `geo`: `transform`, `curve_line`, `curve_line_from_direction`, `mesh_line`, `points`, `mesh_to_points`, `rotate_instances`, `scale_elements`, `sample_curve`.
- `math`: `float_curve`, `mix`, `vector_rotate_euler`, `vector_rotate_axis_angle`.
- `color`: `rgb_curve`.
- `func`: `align_euler_to_vector`.

## Other

- RGBA defaults now transpile as bare tuples (alpha preserved); float rounding moved into codegen; warning emitted on dropped alpha.
- Added `pf.ops.file.render` with platform-portable color-management defaults.
- Added HSV/HSL wrappers for `ShaderNodeSeparateColor` (#65).
