"""Manifest-coverage sweep: every binding survives a strict transpile roundtrip.

Parametrizes over every (manifest row, node_group_type, mode) combination,
where a mode is one of the row's data_types or a Literal-typed parameter that
the native node exposes. Each case builds a minimal node group in that mode,
transpiles it, re-executes the generated source, and asserts the rebuilt node
still carries the mode. Every collected case runs; a mode that cannot be
applied, or that the roundtrip loses, is a failure.
"""

import ast
import inspect
import uuid
from typing import Literal, get_args, get_origin

import bpy
import pytest

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.execute.construct_standard import set_node_attribute
from procfunc.nodes.util.bindings_util import (
    CONTEXTUAL_NODE_MAPPING,
    resolve_contextual_node,
)
from procfunc.nodes.util.bpy_node_info import (
    DATATYPE_TO_SOCKET_CLASS,
    SOCKET_DTYPE_TO_DATATYPE,
    NodeDataType,
    NodeGroupType,
    SocketDType,
    SocketType,
)
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import (
    ParseMemo,
    _target_attrs,
    parse_standard_node,
)
from procfunc.util import manifest
from procfunc.util.manifest import filter_manifest

_GENERIC_ROUNDTRIP_EXCLUDED_BPY_NAMES = frozenset({"ShaderNodeScript"})

_NODES = filter_manifest(
    pf.nodes.NODES_MANIFEST,
    exclude={"name": ["LATER", "DECLINE", "TODO"]},
    require_nonempty=["bpy_name", "node_group_type", "name"],
)
_NODES = _NODES[
    ~_NODES["bpy_name"].isin(_GENERIC_ROUNDTRIP_EXCLUDED_BPY_NAMES)
].explode("node_group_type")

_BPY_NAME_TO_CONTEXTUAL = {
    ncr.node_type: ncr.contextual_node for ncr in CONTEXTUAL_NODE_MAPPING
}

_NESTED_MODE_PATHS = {
    "pf.nodes.color.color_ramp": {
        "mode": ("color_ramp", "color_mode"),
        "interpolation": ("color_ramp", "interpolation"),
        "hue_interpolation": ("color_ramp", "hue_interpolation"),
    }
}

_AXIS_ROTATION_TYPES = frozenset({"X_AXIS", "Y_AXIS", "Z_AXIS"})

# legacy MixRGB parses to mix_rgb, which binds ContextualNode.MIX_RGB
_LEGACY_REBUILD_BL_IDNAME = {"ShaderNodeMixRGB": "ShaderNodeMix"}


def _manifest_canonical_to_ndt(canonical: str) -> NodeDataType | None:
    # manifest data_types are lowercase short forms; resolve to the matching
    # NodeDataType (e.g. "bool" -> BOOLEAN, "vector" -> FLOAT_VECTOR)
    key = {"bool": "BOOLEAN", "str": "STRING"}.get(canonical.lower(), canonical.upper())
    matches = [m for m in NodeDataType if key in m.name.split("_")]
    exact = [m for m in matches if m.name == key]
    matches = exact or matches
    return matches[0] if len(matches) == 1 else None


def _resolve_data_type(node, canonical: str) -> str | None:
    prop = node.bl_rna.properties.get("data_type")
    if prop is None or prop.type != "ENUM":
        return None
    valid = {item.identifier for item in prop.enum_items}
    ndt = _manifest_canonical_to_ndt(canonical)
    if ndt is None:
        upper = canonical.upper()
        return upper if upper in valid else None
    # Try the NodeDataType identifier first; then any SocketDType identifier
    # that maps to the same NodeDataType (older nodes use those, e.g.
    # `VECTOR` for FLOAT_VECTOR, `FLOAT_COLOR` for RGBA).
    candidates: list[str] = [ndt.value]
    for sdt, mapped in SOCKET_DTYPE_TO_DATATYPE.items():
        if mapped is ndt and sdt.value not in candidates:
            candidates.append(sdt.value)
    return next((c for c in candidates if c in valid), None)


def _socket_iface_type(socket) -> str | None:
    """socket.type -> the interface NodeSocket* class name that can carry it."""
    # matrix / image / texture have no NodeDataType analogue, so they never
    # reach the SocketDType -> NodeDataType -> SocketType chain below
    direct = {
        "MATRIX": SocketType.MATRIX,
        "IMAGE": SocketType.IMAGE,
        "TEXTURE": SocketType.TEXTURE,
    }.get(socket.type)
    if direct is not None:
        return direct.value
    try:
        sdt = SocketDType(socket.type)
    except ValueError:
        return None
    stype = DATATYPE_TO_SOCKET_CLASS.get(SOCKET_DTYPE_TO_DATATYPE[sdt])
    return stype.value if stype else None


def _resolve_bl_idname(bpy_name: str, group_type: str) -> str:
    contextual = _BPY_NAME_TO_CONTEXTUAL.get(bpy_name)
    if contextual is None:
        return bpy_name
    return resolve_contextual_node(contextual, NodeGroupType(group_type)).node_type


def _ensure_io_nodes(tree):
    inp = next((n for n in tree.nodes if n.bl_idname == "NodeGroupInput"), None)
    out = next((n for n in tree.nodes if n.bl_idname == "NodeGroupOutput"), None)
    if inp is None:
        inp = tree.nodes.new("NodeGroupInput")
    if out is None:
        out = tree.nodes.new("NodeGroupOutput")
    return inp, out


def _wire_socket(tree, iface_node, node_socket, in_out: str) -> bool:
    iface_type = _socket_iface_type(node_socket)
    if iface_type is None:
        return False
    # the socket identifier, not its display name, so duplicates (e.g. Math's
    # two "Value" inputs) yield unique interface sockets. Some tree types
    # refuse certain interface socket types (Shader / NodeSocketString).
    try:
        iface = tree.interface.new_socket(
            name=node_socket.identifier, in_out=in_out, socket_type=iface_type
        )
    except (TypeError, RuntimeError):
        return False
    sockets = iface_node.outputs if in_out == "INPUT" else iface_node.inputs
    matching = next((s for s in sockets if s.identifier == iface.identifier), None)
    if matching is None:
        return False
    if in_out == "INPUT":
        tree.links.new(matching, node_socket)
    else:
        tree.links.new(node_socket, matching)
    return True


def _make_test_tree(group_type: str):
    """Create a node tree for the given group type and return (tree, cleanup).

    Compositor trees must live on a scene (CompositorNodeTree cannot be
    created via bpy.data.node_groups.new), so allocate a throwaway scene.
    """
    suffix = uuid.uuid4().hex[:8]
    if group_type == "CompositorNodeTree":
        scene = bpy.data.scenes.new(f"_pf_test_scene_{suffix}")
        scene.use_nodes = True
        scene.node_tree.nodes.clear()
        return scene.node_tree, lambda: bpy.data.scenes.remove(scene)
    tree = bpy.data.node_groups.new(f"_pf_test_{suffix}", group_type)
    return tree, lambda: bpy.data.node_groups.remove(tree)


def _row_func(row):
    return manifest.import_item_iterative(row.name.replace("pf.", "procfunc."))


def _literal_values(annotation) -> list[str]:
    if get_origin(annotation) is Literal:
        return [v for v in get_args(annotation) if isinstance(v, str)]
    nested = [a for a in get_args(annotation) if get_origin(a) is Literal]
    if len(nested) == 1:
        return [v for v in get_args(nested[0]) if isinstance(v, str)]
    return []


def _literal_params(func) -> list[tuple[str, list[str]]]:
    inner = getattr(func, "__wrapped__", func)
    result = []
    for param in inspect.signature(inner).parameters.values():
        if param.name in ("data_type", "input_type"):
            continue
        values = _literal_values(param.annotation)
        if values:
            result.append((param.name, values))
    return result


def _reverse_arg_names(row) -> dict[str, str]:
    if not isinstance(row.arg_names_map, dict):
        return {}
    return {v: k for k, v in row.arg_names_map.items() if isinstance(v, str)}


def _mode_path(row, param: str) -> tuple[str, ...]:
    nested = _NESTED_MODE_PATHS.get(row.name, {}).get(param)
    if nested is not None:
        return nested
    attr = _reverse_arg_names(row).get(param, param)
    return (attr,)


def _row_claims_literal(row, param: str) -> bool:
    path = _mode_path(row, param)
    if len(path) > 1:
        return True
    bl_idname = _resolve_bl_idname(row.bpy_name, row.node_group_type)
    node_type = getattr(bpy.types, bl_idname)
    return path[0] in node_type.bl_rna.properties


def _row_modes(row) -> list[tuple[str, str] | None]:
    modes: list[tuple[str, str] | None] = []
    if isinstance(row.data_types, list) and row.data_types:
        modes.extend(("data_type", dt) for dt in row.data_types)
    else:
        modes.append(None)
    for param, values in _literal_params(_row_func(row)):
        if not _row_claims_literal(row, param):
            continue
        modes.extend((param, value) for value in values)
    return modes


def _case_id(row, mode) -> str:
    suffix = "" if mode is None else f"__{mode[0]}__{mode[1]}"
    return f"{row.name}__{row.node_group_type}{suffix}"


_PARAMS = [
    (row, mode) for row in _NODES.itertuples(index=False) for mode in _row_modes(row)
]
_CASE_PARAMS = [pytest.param(r, m, id=_case_id(r, m)) for r, m in _PARAMS]


def _get_path(obj, path: tuple[str, ...]):
    for attr in path:
        obj = getattr(obj, attr)
    return obj


def _set_path(obj, path: tuple[str, ...], value):
    target = _get_path(obj, path[:-1]) if len(path) > 1 else obj
    set_node_attribute(target, path[-1], value)


def _apply_mode_args(node, row) -> list[tuple[str, ...]]:
    if not isinstance(row.bpy_mode_args, dict):
        return []
    # data_type first: other enum attrs' valid values can depend on it
    ordered = sorted(row.bpy_mode_args.items(), key=lambda kv: kv[0] != "data_type")
    for attr, value in ordered:
        set_node_attribute(node, attr, value)
    return [(attr,) for attr, _ in ordered]


def _apply_default_data_type(node, row) -> list[tuple[str, ...]]:
    if not (isinstance(row.data_types, list) and row.data_types):
        return []
    # a bpy_mode_args data_type selects the row's pf function; never override it
    if isinstance(row.bpy_mode_args, dict) and "data_type" in row.bpy_mode_args:
        return []
    chosen = _resolve_data_type(node, row.data_types[0])
    if chosen is None:
        return []
    set_node_attribute(node, "data_type", chosen)
    return [("data_type",)]


def _apply_mode(node, row, bl_idname: str, mode) -> list[tuple[str, ...]]:
    """Put `node` into `mode` and return the bpy attrs that now carry it."""
    attrs = _apply_mode_args(node, row)
    if mode is None:
        return attrs + _apply_default_data_type(node, row)
    param, value = mode
    if param == "data_type":
        chosen = _resolve_data_type(node, value)
        assert chosen is not None, f"{bl_idname} does not expose data_type {value!r}"
        set_node_attribute(node, "data_type", chosen)
        return [*attrs, ("data_type",)]
    attrs += _apply_default_data_type(node, row)
    if row.name == "pf.nodes.color.color_ramp" and param == "hue_interpolation":
        color_mode = _mode_path(row, "mode")
        _set_path(node, color_mode, "HSV")
        attrs.append(color_mode)
    path = _mode_path(row, param)
    _set_path(node, path, value)
    return [*attrs, path]


def _build_row_node(tree, row, bl_idname: str, mode, *, connect_inputs: bool):
    input_node, output_node = _ensure_io_nodes(tree)
    try:
        node = tree.nodes.new(bl_idname)
    except RuntimeError as e:
        raise AssertionError(
            f"cannot instantiate {bl_idname} in {row.node_group_type}: {e}"
        ) from None
    attrs = _apply_mode(node, row, bl_idname, mode)

    if connect_inputs:
        for socket in [s for s in node.inputs if s.enabled and s.name]:
            _wire_socket(tree, input_node, socket, "INPUT")

    wireable = [s for s in node.outputs if s.enabled and s.name]
    wired = sum(_wire_socket(tree, output_node, s, "OUTPUT") for s in wireable)
    assert wired or not wireable, (
        f"{bl_idname} in {row.node_group_type}: none of its outputs are wireable "
        "in isolation (e.g. every socket is an unsupported type)"
    )
    return node, attrs


def _assert_mode_preserved(nodegroups, expected: dict, bl_idname: str):
    if not expected:
        return
    rebuilt = [node for group in nodegroups for node in group.nodes]
    wanted = _LEGACY_REBUILD_BL_IDNAME.get(bl_idname, bl_idname)
    observed = []
    for node in [n for n in rebuilt if n.bl_idname == wanted]:
        try:
            observed.append({path: _get_path(node, path) for path in expected})
        except AttributeError:
            continue
    assert expected in observed, (
        f"rebuilt {bl_idname} lost its mode: expected={expected}, "
        f"observed={observed}, rebuilt={[node.bl_idname for node in rebuilt]}"
    )


def _assert_vector_rotate_normalized(nodegroups):
    rebuilt = [node for group in nodegroups for node in group.nodes]
    rotations = [node for node in rebuilt if node.bl_idname == "ShaderNodeVectorRotate"]
    assert any(node.rotation_type == "EULER_XYZ" for node in rotations)
    assert any(node.bl_idname == "ShaderNodeCombineXYZ" for node in rebuilt)


def _roundtrip(tree, row, node, attrs: list[tuple[str, ...]]):
    bl_idname = node.bl_idname
    expected = {path: _get_path(node, path) for path in attrs}
    source_rotation = getattr(node, "rotation_type", None)

    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    ast.parse(src)

    ns: dict = {}
    exec(src, ns)  # noqa: S102
    generated = [v for v in ns.values() if callable(v) and hasattr(v, "__wrapped__")]
    assert generated, f"no generated functions found for {bl_idname}"

    group_enum = NodeGroupType(row.node_group_type)
    nodegroups = [
        as_nodegroup(pf.nodes.function_to_compute_graph(fn), group_enum)
        for fn in generated
    ]
    if row.name == "pf.nodes.math.vector_rotate_euler" and source_rotation in (
        _AXIS_ROTATION_TYPES
    ):
        _assert_vector_rotate_normalized(nodegroups)
    else:
        _assert_mode_preserved(nodegroups, expected, bl_idname)


def _check_manifest_row(row, mode, *, connect_inputs: bool):
    bl_idname = _resolve_bl_idname(row.bpy_name, row.node_group_type)
    tree, cleanup = _make_test_tree(row.node_group_type)
    groups_before = set(bpy.data.node_groups)
    try:
        node, attrs = _build_row_node(
            tree, row, bl_idname, mode, connect_inputs=connect_inputs
        )
        _roundtrip(tree, row, node, attrs)
    except Exception as e:
        # string-only args, no chain: repr of freed bpy references segfaults
        raise AssertionError(f"{type(e).__name__}: {e}") from None
    finally:
        cleanup()
        # remove node groups as_nodegroup constructed here to bound memory growth
        for group in set(bpy.data.node_groups) - groups_before:
            bpy.data.node_groups.remove(group)


@pytest.mark.parametrize(("row", "mode"), _CASE_PARAMS)
def test_manifest_row_transpiles(row, mode):
    _check_manifest_row(row, mode, connect_inputs=True)


@pytest.mark.parametrize(("row", "mode"), _CASE_PARAMS)
def test_manifest_row_transpiles_defaults(row, mode):
    _check_manifest_row(row, mode, connect_inputs=False)


def test_sweep_covers_literal_params():
    literal = [m for _, m in _PARAMS if m is not None and m[0] != "data_type"]
    assert len(literal) > 500, (
        f"literal-param sweep collected only {len(literal)} modes"
    )


def test_compositor_map_range_does_not_claim_interpolation():
    compositor_modes = [
        mode for row, mode in _PARAMS if row.bpy_name == "CompositorNodeMapRange"
    ]
    assert not any(
        mode is not None and mode[0] == "interpolation_type"
        for mode in compositor_modes
    )


@pytest.mark.parametrize(
    "name", ["pf.nodes.geo.sample_nearest", "pf.nodes.compositor.viewer"]
)
def test_manifest_row_does_not_claim_false_data_types(name):
    rows = [row for row in _NODES.itertuples(index=False) if row.name == name]
    assert rows
    assert all(not isinstance(row.data_types, list) for row in rows)


def test_color_ramp_hue_uses_nested_mode_paths():
    row = next(
        row
        for row in _NODES.itertuples(index=False)
        if row.name == "pf.nodes.color.color_ramp"
        and row.node_group_type == "ShaderNodeTree"
    )
    tree, cleanup = _make_test_tree(row.node_group_type)
    try:
        node, paths = _build_row_node(
            tree,
            row,
            _resolve_bl_idname(row.bpy_name, row.node_group_type),
            ("hue_interpolation", "CW"),
            connect_inputs=False,
        )
        assert paths == [
            ("color_ramp", "color_mode"),
            ("color_ramp", "hue_interpolation"),
        ]
        assert node.color_ramp.color_mode == "HSV"
        assert node.color_ramp.hue_interpolation == "CW"
    finally:
        cleanup()


def test_shader_script_uses_exact_low_level_coverage():
    assert _GENERIC_ROUNDTRIP_EXCLUDED_BPY_NAMES == frozenset({"ShaderNodeScript"})
    assert all(row.bpy_name != "ShaderNodeScript" for row, _ in _PARAMS)

    tree, cleanup = _make_test_tree("ShaderNodeTree")
    try:
        node = tree.nodes.new("ShaderNodeScript")
        for mode in ("INTERNAL", "EXTERNAL"):
            set_node_attribute(node, "mode", mode)
            assert _target_attrs(node)["mode"] == mode
            parsed = parse_standard_node(tree, node, ParseMemo())
            assert parsed.func is pf.nodes.shader.script
            assert parsed.kwargs.get("mode", "INTERNAL") == mode
    finally:
        cleanup()
