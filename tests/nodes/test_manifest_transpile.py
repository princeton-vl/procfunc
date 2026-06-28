"""Manifest-coverage smoke test: every binding survives transpile end-to-end.

Parametrizes over every (manifest_row, node_group_type) pair, builds a minimal
node group exercising the row, runs the transpiler, and ast.parses the source.
"""

import ast
import uuid

import bpy
import pytest

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.util.bindings_util import CONTEXTUAL_NODE_MAPPING
from procfunc.nodes.util.bpy_node_info import (
    DATATYPE_TO_SOCKET_CLASS,
    SOCKET_DTYPE_TO_DATATYPE,
    NodeDataType,
    NodeGroupType,
    SocketDType,
    SocketType,
)
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo
from procfunc.util.manifest import filter_manifest

_NODES = filter_manifest(
    pf.nodes.NODES_MANIFEST,
    exclude={"name": ["LATER", "DECLINE", "TODO"]},
    require_nonempty=["bpy_name", "node_group_type", "name"],
).explode("node_group_type")

_BPY_NAME_TO_CONTEXTUAL = {
    ncr.node_type: ncr.contextual_node for ncr in CONTEXTUAL_NODE_MAPPING
}

# Manifest data_types canonical names are lowercase short forms; resolve to the
# matching NodeDataType (e.g. "bool" → BOOLEAN, "vector" → FLOAT_VECTOR).
_MANIFEST_CANONICAL_ALIASES = {"bool": "BOOLEAN", "str": "STRING"}


def _manifest_canonical_to_ndt(canonical: str) -> NodeDataType | None:
    key = _MANIFEST_CANONICAL_ALIASES.get(canonical.lower(), canonical.upper())
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


# socket.type → interface NodeSocket* class name. Derived via the
# SocketDType → NodeDataType → SocketType chain in bpy_node_info; matrix /
# image / texture sockets have no NodeDataType analogue and fall back to a
# direct SocketType lookup.
_DTYPE_TO_SOCKET_TYPE_FALLBACK = {
    "MATRIX": SocketType.MATRIX,
    "IMAGE": SocketType.IMAGE,
    "TEXTURE": SocketType.TEXTURE,
}


def _socket_iface_type(socket) -> str | None:
    fallback = _DTYPE_TO_SOCKET_TYPE_FALLBACK.get(socket.type)
    if fallback is not None:
        return fallback.value
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
    ng = NodeGroupType(group_type)
    for ncr in CONTEXTUAL_NODE_MAPPING:
        if ncr.contextual_node == contextual and ncr.node_group_type == ng:
            return ncr.node_type
    return bpy_name


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
    # use the wrapped-node socket identifier so duplicate display names
    # (e.g. Math's two "Value" inputs) yield unique interface socket names.
    # Some tree types (Shader) refuse certain interface socket types
    # (NodeSocketString); treat that as "can't wire" and let the test fall
    # through.
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
    Other group types use a regular node group.
    """
    suffix = uuid.uuid4().hex[:8]
    if group_type == "CompositorNodeTree":
        scene = bpy.data.scenes.new(f"_pf_test_scene_{suffix}")
        scene.use_nodes = True
        scene.node_tree.nodes.clear()
        return scene.node_tree, lambda: bpy.data.scenes.remove(scene)
    tree = bpy.data.node_groups.new(f"_pf_test_{suffix}", group_type)
    return tree, lambda: bpy.data.node_groups.remove(tree)


_PARAMS = list(_NODES.itertuples(index=False))
_IDS = [f"{r.name}__{r.node_group_type}" for r in _PARAMS]


def _check_manifest_row(row, *, connect_inputs: bool):
    group_type = row.node_group_type
    bl_idname = _resolve_bl_idname(row.bpy_name, group_type)

    tree, cleanup = _make_test_tree(group_type)
    groups_before = set(bpy.data.node_groups)
    try:
        input_node, output_node = _ensure_io_nodes(tree)

        try:
            node = tree.nodes.new(bl_idname)
        except RuntimeError as e:
            pytest.fail(f"Failed to instantiate {bl_idname} in {group_type}: {e}")

        if isinstance(row.bpy_mode_args, dict):
            # data_type must be applied before other enum attrs whose valid
            # values depend on it (e.g. FunctionNodeCompare.operation: BRIGHTER
            # is only available once data_type is RGBA).
            ordered = sorted(
                row.bpy_mode_args.items(), key=lambda kv: kv[0] != "data_type"
            )
            for attr, val in ordered:
                assert hasattr(node, attr), (
                    f"manifest row {row.name}: bpy_mode_args key {attr!r} does "
                    f"not exist on {bl_idname}"
                )
                setattr(node, attr, val)

        if isinstance(row.data_types, list) and row.data_types:
            chosen = _resolve_data_type(node, row.data_types[0])
            if chosen is not None:
                node.data_type = chosen

        if connect_inputs:
            for socket in node.inputs:
                if not socket.enabled or not socket.name:
                    continue
                _wire_socket(tree, input_node, socket, "INPUT")

        wireable = [s for s in node.outputs if s.enabled and s.name]
        wired_outputs = 0
        for socket in wireable:
            if _wire_socket(tree, output_node, socket, "OUTPUT"):
                wired_outputs += 1

        # Sink-style nodes (no outputs at all) are valid: parse_node_tree will
        # walk back from the empty NodeGroupOutput and emit a graph with no
        # outputs. Only skip when the row exposes outputs but none are wireable.
        if wireable and wired_outputs == 0:
            pytest.skip(
                f"{bl_idname} in {group_type}: no outputs are wireable in "
                "isolated test (e.g. all sockets are unsupported types)."
            )

        memo = ParseMemo()
        graph, _ = parse_node_tree(tree, memo)
        src = to_python(graph, toplevel_as_maincall=False)
        ast.parse(src)

        ns: dict = {}
        exec(src, ns)  # noqa: S102

        # Actually construct the generated node trees on real bpy data: each
        # generated function is a @node_function whose graph we realize via
        # as_nodegroup. Sink rows generate empty `pass` bodies, which realize
        # to an input-only group (presence-only, but still exercised).
        group_enum = NodeGroupType(group_type)
        generated = [
            v for v in ns.values() if callable(v) and hasattr(v, "__wrapped__")
        ]
        assert generated, f"no generated functions found for {bl_idname}"
        for fn in generated:
            subgraph = pf.nodes.function_to_compute_graph(fn)
            as_nodegroup(subgraph, group_enum)
    finally:
        cleanup()
        # as_nodegroup creates node groups (scene-bound rows reuse the active
        # scene's tree); remove those constructed here to bound memory growth.
        for ng in set(bpy.data.node_groups) - groups_before:
            bpy.data.node_groups.remove(ng)


@pytest.mark.parametrize("row", _PARAMS, ids=_IDS)
def test_manifest_row_transpiles(row):
    _check_manifest_row(row, connect_inputs=True)


@pytest.mark.parametrize("row", _PARAMS, ids=_IDS)
def test_manifest_row_transpiles_defaults(row):
    _check_manifest_row(row, connect_inputs=False)
