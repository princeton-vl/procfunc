# 0.36.0

Interface changes:

- importing ProcFunc disables Blender's global undo; `procfunc.ops` disables it again before every operator call in case loading factory settings restores it
- `texture.image` and `texture.environment` gain the seven ImageUser arguments listed below; all default to Blender's own values, so existing calls are unaffected
- `pf.nodes.func.rotate_euler` no longer takes `rotation_type`; the AXIS_ANGLE form is the new `rotate_euler_axis_angle(rotation, axis, angle, space)`, with `rotation_type` pinned via the manifest (was one function whose AXIS_ANGLE mode was unusable — it had no axis/angle kwargs and fed the Rotate By default into a socket that mode disables)
- `shader.subsurface_scattering` split into `subsurface_scattering_burley` / `subsurface_scattering_random_walk` / `subsurface_scattering_random_walk_skin`, each exposing only the sockets its falloff supports (the combined binding fed defaults into disabled sockets)
- `shader.principled_hair_bsdf` split by model into `principled_hair_bsdf_chiang` / `principled_hair_bsdf_huang`, adding the previously-missing melanin, absorption, and Huang-model sockets; each function derives COLOR / ABSORPTION / MELANIN parametrization from the provided color arguments and rejects mixed parametrizations
- `shader.mapping` now pins POINT; TEXTURE, VECTOR, and NORMAL are `mapping_texture`, `mapping_vector`, and `mapping_normal`, with directional functions omitting the disabled Location socket
- `texture.sky` is replaced by `sky_texture_nishita`, `sky_texture_hosek_wilkie`, and `sky_texture_preetham`; each exposes only its model's controls, and Nishita accepts `vector` only with `sun_disc=False`
- `compositor.color_balance` now pins LIFT_GAMMA_GAIN and exposes only lift, gamma, and gain; OFFSET_POWER_SLOPE is the separate `color_balance_slope_offset_power`
- `sky_texture_nishita` uses `None` sentinels for sun elevation, intensity, rotation, and size; only explicit intensity and size require `sun_disc=True`, while elevation and rotation are preserved with either disc setting and omitted values resolve to Blender's defaults
- `geo.mesh_to_volume` and `geo.points_to_volume` take `voxel_amount` or `voxel_size` and derive `resolution_mode` from whichever is given (was a `resolution_mode` enum with no `voxel_size` argument at all, so VOXEL_SIZE fed the voxel amount into a socket that mode disables)
- `geo.distribute_points_in_grid` and `geo.distribute_points_in_volume` take `density`/`seed` or `spacing`/`threshold` and derive `mode` from whichever group is given (was a `mode` enum with no `spacing`/`threshold` arguments, so DENSITY_GRID fed density and seed into disabled sockets)
- `geo.mesh_line_from_endpoints` takes `count` or `resolution` and derives `count_mode` from whichever is given (was a `count_mode` enum with no `resolution` argument, so RESOLUTION fed the count into a disabled socket)
- passing arguments from both modes to any of the above raises `ValueError`, and passing neither keeps the Blender default mode and its default values
- `geo.mesh_cone` and `geo.mesh_cylinder` default `fill_segments` to None and reject it when `fill_type='NONE'`, which has no fill segments to set (was fed into a disabled socket)
- `geo.sample_curve` no longer takes `mode`; length-based sampling is the existing `geo.sample_curve_length` (was a mode argument that fed Factor into the socket LENGTH disables)
- `geo.mesh_line` no longer takes `count_mode`, which its OFFSET mode ignores
- `texture.wave` accepts `bands_direction` 'DIAGONAL' instead of 'SPHERICAL', which Blender only accepts on `rings_direction`
- `compositor.image` types `layer` and `view` as `str`, since their valid values come from the assigned image datablock at runtime rather than a fixed set
- `geo.volume_to_mesh` takes `voxel_amount` or `voxel_size` and derives `resolution_mode` from whichever is given; passing neither keeps the GRID default
- `geo.string_to_curves` takes `text_box_height` for SCALE_TO_FIT and TRUNCATE overflow and rejects it for OVERFLOW, where Blender disables that socket
- `math.map_range` spells its stepped interpolation `STEPPED` instead of `STEPPED_LINEAR`, which Blender rejects
- `math.map_range` takes `steps` for STEPPED interpolation and rejects it in the other modes, where Blender disables that socket (the argument was missing entirely, so no STEPPED node could transpile)
- `texture.voronoi` and `texture.voronoi_smooth_f1` return `position=None` in 1D, which has no Position socket, and expose `w` in 1D as well as 4D (its 1D W output was unreachable)
- `math.float_curve` gains a per-point `handle_types` list alongside its broadcast `handle_type`, and `math.vector_curve`, `color.rgb_curve`, and `compositor.rgb_curve` gain a per-curve `handle_types`
- `compositor.hue_correct` takes `curves` and per-point `handle_types` for its hue, saturation and value curves, and transpile emits them (they were dropped entirely, so every transpiled node rebuilt with default curves)

Fixed behavior:

- `control.choice` resolves the selected branch below `RANDOM_CONTROL` and retains its RNG while tracing callable alternatives, so generated code preserves the requested random-control granularity
- `@node_function` calls expand into their underlying primitives at `PRIMITIVES` without constructing `ProcNode` values inside the trace graph
- primitive code generation emits integer addition and subtraction, floor division, unary operators, native equality, and `ProcNode` / union type values correctly
- curve nodes remove points beyond the ones given rather than leaving the node's remaining defaults in place
- `func.axes_to_rotation` retains its public X/Y defaults while the transpiler emits Blender's native Z/X defaults explicitly, so native nodes rebuild with the same axes
- `geo.string_to_curves` exposes the `remainder` string output for TRUNCATE overflow and returns `None` for modes where Blender has no such socket
- transpiling a `ShaderNodeTex*` node in a shader tree whose `texture_mapping` is not the identity transform now rebuilds it as the Combine XYZ and Mapping nodes it is equivalent to, in front of the texture, instead of silently dropping it and changing how the graph renders
- the `use_min`/`use_max` clamp, which EEVEE applies and Cycles ignores, and any `texture_mapping` on `ShaderNodeTexSky`, which has no Vector input to map, have no such equivalent and now raise; set `context.globals.warn_mode_transpile_dropped_attrs` (or `PROCFUNC_WARN_MODE_TRANSPILE_DROPPED_ATTRS`) to `warn` or `ignore` to transpile anyway
- `color_mapping`, the legacy `mapping` projection of `texture_mapping`, and any `texture_mapping` in a geometry node tree are dropped silently, since nothing evaluates them
- float, vector, and RGB curve nodes keep each point's handle type through transpile (non-AUTO handles were logged as a warning and dropped, so the rebuilt curve had a different shape)
- `GeometryNodeIndexSwitch` gets a transpiler handler that drops its `index_switch_items` collection, which restates the numbered input sockets
- `GeometryNodeRaycast` and `CompositorNodePremulKey` transpile their `mapping` enum, which a global skip list had been pinning to `INTERPOLATED` and `STRAIGHT_TO_PREMUL` regardless of the source node
- `texture.image` and `texture.environment` take the node's ImageUser settings as plain `frame_current` / `frame_duration` / `frame_offset` / `frame_start` / `tile` / `use_auto_refresh` / `use_cyclic` arguments, matching `compositor.image`, instead of dropping them on transpile

Fixed crashes:

- the manifest splits attr renames into their own `attr_names_map` column, applied to bpy attrs only while `arg_names_map` applies to sockets only, so a node whose attr and socket share a name transpiles instead of crashing (`FunctionNodeAxesToRotation` raised `keys overlap` for every non-default primary/secondary axis)

# 0.35.1

Interface changes:

- per-node definition metadata is recorded only when the context's `record_node_definitions` is set (or `PROCFUNC_RECORD_NODE_DEFINITIONS=1`), so node-instantiation errors carry file/line context only when it is enabled (was always, and the stack walk dominated build time in node-heavy callers)
- `texture.sky` accepts an optional `vector` input for PREETHAM and HOSEK_WILKIE skies; omitting it preserves Blender's implicit direction

Fixed crashes:

- transpiling a geometry-nodes modifier with one geometry output plus extra attribute outputs calls `to_mesh_object_with_attributes` with the geometry positional and the attributes under `attributes=` (was flat kwargs, which did not match the signature)

Other:

- entrypoints exiting through `skip_teardown_on_exit` save coverage data before `os._exit`, so running one under `coverage` records the executed lines instead of discarding them
- CI runs for every pull request, quarantines fresh dependency releases in the compatibility job, and gained lowest-supported-version unit tests

# 0.35.0

Interface changes:

- material construction builds the shader graph directly into the material's node tree, dropping the redundant top-level wrapper node group (nested node groups are unaffected)
- `@node_function` calls are captured as a single leaf call when tracing at `NODEGROUPS` or coarser — including the default `GENERATORS` level — instead of being inlined into the traced graph

Fixed crashes:

- transpiling a material whose Displacement output is unconnected emits a zero vector instead of `None`, so downstream arithmetic on `material.displacement` no longer crashes
- the transpiler decides whether to inject a `vector` argument from the graph's actual inputs (was: any graph whose name starts with `material_`, which passed `vector=` to materials that have no such input)
- `ndarray` arithmetic against a `Proxy` defers to the `Proxy` operator instead of probing it as an array, which fabricated a bogus `__array_struct__` through `__getattr__`

Fixed wrong results:

- codegen parenthesizes folded operator expressions by parsing them, so subscripts, method-call targets, comparisons and unary/power expressions are grouped correctly (was a whitespace heuristic)
- epsilon-tolerant equality transpiles to a named `func.equal` / `func.not_equal` call unless every operand is an exact dtype, rather than folding to Python `==` / `!=`, whose exact semantics differ from Blender's Compare node
- every rng-consuming distribution in `random.py` is a tracer primitive, so tracing at `GENERATORS` bakes it to a constant instead of emitting a live call against an unseeded generator
- `MOD` transpiles to a named `math.modulo` call rather than Python `%`, whose floored semantics differ from Blender's truncated MODULO
- the transpiler emits an output getattr whenever the bound function returns a `NamedTuple`, even when the source node leaves only one output socket active (the socket count alone underdetected this)
- generated function signatures keep an input socket default of `None` (was dropped, changing the emitted argument order and defaults)
- `to_light` declares that it mutates its `light` argument, so its shader assignment survives trace codegen
- `is_zero_displacement` recognizes zero displacement written as a `math.constant` call or a contextual vector node, not just a bare constant, so the drop-dead-displacement optimization applies to transpiled materials
- generated `NamedTuple` field types fall back to the tuple's own annotations before `Any`

Errors instead of silent misbehavior:

- `build_bpy_material` raises `TypeError` when `surface` / `displacement` / `volume` is neither a `ProcNode` nor `None`

Other:

- generated docs strip the boilerplate docstrings Python synthesizes for `NamedTuple` members

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
