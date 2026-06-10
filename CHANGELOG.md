# 0.32.0

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
