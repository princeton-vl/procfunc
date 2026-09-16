import inspect
from collections.abc import Callable
from typing import get_args

import pytest

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes import geo, math

_DOMAIN_FUNCTIONS = [
    geo.accumulate_field,
    geo.attribute_statistic,
    geo.capture_attribute,
    geo.delete_geometry,
    geo.field_at_index,
    geo.field_on_domain,
    geo.sample_index,
    geo.separate_geometry,
    geo.split_to_instances,
    geo.store_named_attribute,
]


@pytest.mark.parametrize("fn", _DOMAIN_FUNCTIONS)
def test_geometry_domain_annotations_match_bpy42(fn: Callable) -> None:
    annotation = inspect.signature(fn).parameters["domain"].annotation
    assert "LAYER" not in get_args(annotation)


@pf.nodes.node_function
def _scalar_stepped_map_range() -> pf.ProcNode[float]:
    return math.map_range(0.25, interpolation_type="STEPPED")


def test_map_range_advertises_and_constructs_bpy42_modes() -> None:
    graph = pf.nodes.function_to_compute_graph(_scalar_stepped_map_range)
    group = pf.nodes.as_nodegroup(graph, pf.nodes.NodeGroupType.SHADER)
    native = next(n for n in group.nodes if n.bl_idname == "ShaderNodeMapRange")

    proc_node = math.map_range(0.25).item()
    assert isinstance(proc_node, cg.ProceduralNode)
    resolver = proc_node.attrs["data_type"]

    rows = pf.nodes.NODES_MANIFEST
    row = rows[
        (rows["name"] == "pf.nodes.math.map_range")
        & (rows["bpy_name"] == "ShaderNodeMapRange")
    ].iloc[0]
    annotation = (
        inspect.signature(math.map_range).parameters["interpolation_type"].annotation
    )

    assert {
        "literal_modes": get_args(annotation),
        "manifest_data_types": row["data_types"],
        "runtime_data_types": resolver.data_types,
        "native_state": (native.data_type, native.interpolation_type),
    } == {
        "literal_modes": ("LINEAR", "STEPPED", "SMOOTHSTEP", "SMOOTHERSTEP"),
        "manifest_data_types": ["float"],
        "runtime_data_types": [pf.nodes.NodeDataType.FLOAT],
        "native_state": ("FLOAT", "STEPPED"),
    }
