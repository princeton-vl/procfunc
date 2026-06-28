# 0.34.0

Interface changes:

- removed the material strict-mode checks for normal/bump inputs, implicit texture vectors, and IO nodes, along with their `ProcfuncContext` fields (`warn_mode_avoid_normal_bump`, `warn_mode_avoid_implicit_vector`, `warn_mode_avoid_io_nodes`) and env vars (`PROCFUNC_WARN_MODE_AVOID_NORMAL_BUMP`, `PROCFUNC_WARN_MODE_AVOID_IMPLICIT_VECTOR`, `PROCFUNC_WARN_MODE_AVOID_IO_NODES`)
- dropped the now-unused `is_infinigen_restricted` field and restriction-only `notes` from the node manifest
- `texture.noise` `offset` / `gain` now default to `None` and raise for noise types that don't support them (were `0.0` / `1.0` and applied unconditionally)
- `color.hex_color` dropped its unused `alpha` parameter
- removed `transform_nodetree` from `procfunc.compute_graph.__all__` (was exported but unimplemented)
- `math.vector_dot_product` / `math.vector_distance` are now annotated `ProcNode[float]` (were `ProcNode[Vector]`)
- texture nodes (`brick`, `checker`, `environment`, `gradient`, `ies`, `image`, `magic`, `point_density`, `wave`, …) now accept `vector=None` for blender's implicit coordinates (was required)
- `geo.mesh_to_points` `position` and `geo.scale_elements` `center` now default to `None`; `geo.instances_to_points` `position` accepts `None`
- `bpy_nocollide_data_name` now produces deterministic names (bare prefix, then an incrementing `_N` suffix on collision) instead of a random `uuid4` suffix; dropped its `retries` parameter

Fixed crashes:

- transpiled code that passes `None` to disconnect a geometry/shader socket no longer crashes the strict-`None` executor; one central predicate accepts `None` for any socket carrying no explicit value — multi-inputs, datablock pointers (Object/Collection/Material/Image), and hide-value implicit fields (Selection/Vector/Center/Position) — replacing the per-binding omit-on-`None` workarounds
- transpiling a Separate XYZ with a disconnected Vector emitted a `pf.nodes.func.constant` NameError; now emits `pf.nodes.math.constant`
- transpiling `vector_rotate` with a dropped default-valued Angle socket no longer re-injects `angle=None`
- assigning an `INT` socket default during execution now coerces the value to `int` (was unhandled)

Fixed wrong results:

- transpiler preserves `data_type` / `input_type` when no type-determining input is wired (was dropped unconditionally, breaking re-execution of `random_value` / `switch` / `sample_curve_length` / `blur_attribute`)

Other:

- removed dead commented-out `curve_handle_type_selection` / `viewer` bindings in `geo.py`
- corrected the `control.choice` docstring parameter names
- added an integration test suite (transpile round-trip + render pixel-diff) and a warnings-as-errors Sphinx docs job
- added ast-grep codemods (`scripts/update_greps/`) for migrating call sites across the 0.30 → 0.34 binding changes

# 0.33.2

Interface changes:

- `texture.voronoi_smooth_f1` now exposes `exponent` (Minkowski distance), matching `voronoi`

Fixed crashes:

- transpiling 1D `noise` / `voronoi` / `white_noise` now emits an explicit `vector=None` (the Vector socket is disabled in 1D); previously generated a call missing the required `vector`
- transpiling a dangling reroute (unconnected input, wired output) now resolves to its input socket default instead of raising; also fixes a `pf.nodes.func.constant` NameError in the Separate XYZ disconnected-input path
- `ops.attr.write_attribute` now handles the CORNER domain (was a `KeyError`) and broadcasts scalar values across it

Fixed wrong results:

- compute-graph subgraph deduplication now compares nodes structurally (node type, value, attr identity), so distinct nodes are no longer merged and identical subgraphs dedup correctly
- graph BFS marks nodes visited on enqueue, so a multi-parent node is reported once (was reported per parent)
- `transforms.extract_materials` tracks all callers in its parent map (previously missed some)
- nocollide datablock naming applies its prefix+uuid immediately, avoiding name collisions

Errors instead of silent misbehavior:

- `ops.attr.write_attribute` raises a clear cast hint for dtypes with no Blender attribute type (e.g. 64-bit int)
- `color.hsv_color` / `rgb_color` validate their arguments (require `hsv=`/`rgb=` or all components)

Other:

- multi-binding docstrings now name the target Blender node and mode
- fixed CLI docs argparse reference and README documentation link; refreshed the transpile example output

# 0.33.0

Interface changes:

- `texture.noise` / `voronoi` / `voronoi_distance` / `voronoi_smooth_f1` now require `vector`; pass `vector=None` to opt into blender's implicit coordinates (gated by `warn_mode_avoid_implicit_vector`)
- `shader.principled_bsdf` `normal` / `coat_normal` / `tangent` now default to `None` (previously always wired `Normal=(0,0,0)`)
- `compositor.mix_rgb` now accepts `clamp_result` (exposes the node's `use_clamp`, previously inexpressible)
- `procfunc.util.bpy_data.removing_new_datablocks` context manager bounds bpy.data growth (suitable for downstream test suites)
- removed `OperatorType.AND` / `OperatorType.OR` aliases; corrected `__all__` (`sample_collection`, `primitives`)
- trimmed internal-only `procfunc.tracer` exports (`Patcher`, `PATCHING_FLAG_ATTR`, `add_banned_module`, `add_wrap_target`, `RngSpawnResultProxy`); added `procfunc.compute_graph.__all__`; fixed `procfunc.transpiler.__all__` (`parse_node_tree`)
- module layout (breaks code importing internals): execute construction split into `construct_operator.py` / `construct_standard.py` with realization helpers in `nodes/execute/realize.py`; transpiler special-cases in `transpiler/parse_special_cases.py` and bpy-default coercion in `parse_default_values.py`; codegen value→source in `codegen/repr.py`; node infra (`bindings_util`, `bpy_node_info`, `node_function`) in `nodes/util/`; `control` and `cli` are now packages (console entrypoint unchanged)

Fixed crashes:

- `from procfunc.nodes import *` (nonexistent `to_material` in `__all__`)
- `'prefix*'` globs in the transpile CLI (inverted assert)
- `procfunc transpile --output print`
- `--add_line_comments` (`NameError` on every use)
- second execution of a scene-bound compositor graph (Render Layers / Cryptomatte)
- `transforms.extract_shader_vectors_as_inputs`, `infer_distribution_hypercube`, `distribution_to_mode`, `outlier_distribution`
- transpiling node groups with matrix or image interface sockets (`KeyError`)
- `@node_function` with a missing annotation now raises a clear error (was a bare `AttributeError`)
- `to_mesh_object_with_attributes()` with default `attributes=None`
- kwargs-form rng calls (`rng.uniform(low=..., high=...)`) in `distribution_to_mode` / `outlier_distribution`
- `transforms.colors_to_hsv_definition` on positional Color args
- `primitives.empty()` (asserted MESH on an EMPTY object) and boolean modifiers with `Collection` targets
- transpiling legacy `use_clamp` nodes (`TextureNodeMixRGB` / `ShaderNodeMixRGB` → `clamp_result`, `TextureNodeMath` → a `clamp()` wrap)
- compare with a non-default `epsilon` no longer binds the Epsilon socket when it is remapped to a Math node (operator dispatch `<`/`>`) or disabled (INT/STRING compares)

Fixed wrong results:

- codegen now emits valid Python for matrix constants and non-finite floats; matrices travel as numpy arrays and coerce back to `mathutils.Matrix` at execute time, lowering to `FunctionNodeCombineMatrix` where needed
- ambiguous tuple compares (`func.less_than((1,2,3), b)`) now resolve to FLOAT_VECTOR (was RGBA)
- `GetAttributeNode` / `ProceduralNode` instances now compare by value and are hashable (previously all compared equal and were unhashable)
- raw `rng.uniform(...)` calls are now recognized as distributions in transforms
- transpile no longer emits false values for unlinked implicit-field sockets (e.g. `extrude_mesh(offset=(0,0,0))`)
- top-level known value types are now recorded for codegen annotations
- `ops.mesh.transform` now interprets `rotation_euler` as Euler angles (was an exponential-map rotation vector)
- `random.clip_gaussian` now treats `low=0.0` / `high=0.0` as real bounds (were treated as unset)
- `infer_nodegroup_distributions` now keeps subgraphs with inferred distributions and drops all-dynamic ones (gate was inverted)
- `util.pytree` dict specs now snapshot their keys (a live `keys()` view corrupted `unflatten` when the source dict changed)
- transpile now preserves ColorRamp `color_mode` (HSV/HSL ramps had re-executed as RGB) and gains `hue_interpolation`; codegen renames keyword-named sockets (`Lambda` → `lambda`) instead of emitting `SyntaxError`
- boolean modifier `threshold` is now forwarded to the EXACT solver (was accepted but ignored)

Errors instead of silent misbehavior:

- mixed scalar+tuple operands and ambiguous length-4 tuples raise a clear `.astype` hint
- vector/color compares outside geometry trees raise instead of degrading to scalar Math COMPARE, including wired (non-literal) vector operands
- inputs/attrs a context's legacy node cannot honor raise per-node (e.g. `mix_rgb(clamp_factor=False)` in texture trees, compositor `vector_curve` with `fac != 1.0`)
- operator dispatch only reorders operands for known-commutative operators

Other:

- no root-logging reconfiguration at import time; CLI scopes verbosity to procfunc loggers
- `override_globals` / codegen printoptions restored on exception
- removed dead `is_multi_output` manifest column and dead scaffolding
- version defined once in `procfunc.__version__`; new tests pin multi-input order and matrix round-trips
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
