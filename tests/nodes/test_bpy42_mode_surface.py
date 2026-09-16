import inspect
from collections.abc import Callable
from typing import get_args

import bpy
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


def test_curve_handle_type_annotation_matches_bpy() -> None:
    annotation = (
        inspect.signature(math.float_curve).parameters["handle_type"].annotation
    )
    enum_items = bpy.types.CurveMapPoint.bl_rna.properties["handle_type"].enum_items
    assert get_args(annotation) == tuple(item.identifier for item in enum_items)


@pytest.mark.parametrize("fn", _DOMAIN_FUNCTIONS)
def test_geometry_domain_annotations_match_bpy42(fn: Callable) -> None:
    annotation = inspect.signature(fn).parameters["domain"].annotation
    assert "LAYER" not in get_args(annotation)


@pf.nodes.node_function
def _scalar_stepped_map_range() -> pf.ProcNode[float]:
    return math.map_range(0.25, interpolation_type="STEPPED")


@pf.nodes.node_function
def _vector_map_range() -> pf.ProcNode:
    return math.map_range(
        (0.25, 0.5, 0.75),
        from_max=(1.0, 1.0, 1.0),
        from_min=(0.0, 0.0, 0.0),
        to_max=(0.5, 0.6, 0.7),
        to_min=(0.1, 0.2, 0.3),
    )


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
        "manifest_data_types": ["float", "vector"],
        "runtime_data_types": [
            pf.nodes.NodeDataType.FLOAT,
            pf.nodes.NodeDataType.FLOAT_VECTOR,
        ],
        "native_state": ("FLOAT", "STEPPED"),
    }


def test_map_range_constructs_bpy42_vector_mode() -> None:
    graph = pf.nodes.function_to_compute_graph(_vector_map_range)
    group = pf.nodes.as_nodegroup(graph, pf.nodes.NodeGroupType.SHADER)
    native = next(n for n in group.nodes if n.bl_idname == "ShaderNodeMapRange")

    assert native.data_type == "FLOAT_VECTOR"
    assert tuple(native.inputs["Vector"].default_value) == pytest.approx(
        (0.25, 0.5, 0.75)
    )


@pf.nodes.node_function
def _stepped_map_range_steps() -> pf.ProcNode[float]:
    return math.map_range(0.25, interpolation_type="STEPPED", steps=7.0)


def test_map_range_steps_is_wired_only_for_stepped() -> None:
    graph = pf.nodes.function_to_compute_graph(_stepped_map_range_steps)
    group = pf.nodes.as_nodegroup(graph, pf.nodes.NodeGroupType.SHADER)
    native = next(n for n in group.nodes if n.bl_idname == "ShaderNodeMapRange")
    assert native.inputs["Steps"].default_value == pytest.approx(7.0)

    with pytest.raises(ValueError):
        math.map_range(0.25, steps=7.0)
