import pandas as pd
import pytest

import procfunc as pf
from procfunc.nodes.util import bindings_util
from procfunc.nodes.util.bindings_util import ContextualNode, NodeContextResolution
from procfunc.nodes.util.bpy_node_info import NodeGroupType
from procfunc.nodes.util.bpy_versioning import bpy_version, unsupported_message
from procfunc.transpiler import bpy_to_computegraph
from procfunc.util import manifest

_OLD_ROW = {
    "bpy_name": "ExampleNode",
    "name": "pf.nodes.old",
    "bpy_mode_args": None,
    "bpy_version_min_max": [[3, 6], [4, 4]],
}

_NEW_ROW = {
    "bpy_name": "ExampleNode",
    "name": "pf.nodes.new",
    "bpy_mode_args": None,
    "bpy_version_min_max": [[4, 5], [5, 2]],
}


def _versioned_rows() -> pd.DataFrame:
    return pd.DataFrame([_OLD_ROW, _NEW_ROW])


def test_filter_manifest_by_bpy_version_keeps_matching_rows() -> None:
    rows = _versioned_rows()

    old = manifest.filter_manifest_by_bpy_version(rows, (4, 2))
    new = manifest.filter_manifest_by_bpy_version(rows, (5, 2))

    assert old.iloc[0]["name"] == "pf.nodes.old"
    assert new.iloc[0]["name"] == "pf.nodes.new"


def test_filter_manifest_without_version_column_is_identity() -> None:
    rows = pd.DataFrame([{"bpy_name": "ExampleNode", "name": "pf.nodes.only"}])

    filtered = manifest.filter_manifest_by_bpy_version(rows, (4, 2))

    assert filtered.equals(rows)


def test_find_manifest_func_uses_preloaded_version_rows() -> None:
    rows = _versioned_rows()
    old_rows = manifest.filter_manifest_by_bpy_version(rows, (4, 2)).set_index(
        "bpy_name"
    )
    new_rows = manifest.filter_manifest_by_bpy_version(rows, (5, 2)).set_index(
        "bpy_name"
    )

    old = bpy_to_computegraph._find_manifest_func("ExampleNode", {}, old_rows)
    new = bpy_to_computegraph._find_manifest_func("ExampleNode", {}, new_rows)

    assert old["name"] == "pf.nodes.old"
    assert new["name"] == "pf.nodes.new"


def test_loaded_manifest_keeps_every_row_for_running_bpy() -> None:
    unfiltered = pd.read_json(pf.nodes.NODES_MANIFEST_PATH)
    filtered = manifest.filter_manifest_by_bpy_version(unfiltered, bpy_version())

    assert len(pf.nodes.NODES_MANIFEST) == len(filtered)


def test_contextual_resolution_honours_version_bounds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old = NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="OldMath",
        before_version=(5, 2),
    )
    new = NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="NewMath",
        from_version=(5, 2),
    )
    monkeypatch.setattr(bindings_util, "CONTEXTUAL_NODE_MAPPING", [old, new])

    resolve = bindings_util.resolve_contextual_node
    group = NodeGroupType.COMPOSITOR

    assert resolve(ContextualNode.MATH, group, (4, 2)).node_type == "OldMath"
    assert resolve(ContextualNode.MATH, group, (5, 2)).node_type == "NewMath"


def test_bpy_version_rejects_unsupported_versions() -> None:
    with pytest.raises(ValueError, match="Unsupported bpy"):
        bpy_version((2, 93))


def test_unsupported_message_names_required_range() -> None:
    message = unsupported_message("Example node", since=(4, 5))

    assert "Example node requires bpy 4.5 or newer" in message
