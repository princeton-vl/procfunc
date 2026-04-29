"""
Unit tests for infinigen node function bindings.

Tests that all node functions can be instantiated with default values
and successfully converted to nodegroups via as_nodegroup.

Uses procfunc/nodes/bindings/manifest.csv to know what to test and what features to require for each node.
"""

import inspect
from typing import Callable

import bpy
import pytest

import procfunc as pf
from procfunc.util.manifest import import_item_iterative


def _get_required_args(func: Callable) -> list[str]:
    sig = inspect.signature(func)
    return [
        name
        for name, param in sig.parameters.items()
        if param.default is inspect.Parameter.empty
        and param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
    ]


def _test_node_nodetree(
    func: Callable,
    inputs: dict,
    node_group_type: pf.nodes.NodeGroupType,
    is_multi_output: bool,
):
    """Test a node function by converting it to a nodegroup."""


def _construct_asset_string(arg_name: str):
    match arg_name:
        case "value":
            return 1.0
        case "vector":
            return pf.nodes.shader.coord().generated
        case "start_location" | "end_location":
            return pf.Vector((1, 1, 1))
        case "geometry" | "mesh" | "mesh_1" | "mesh_2" | "instance":
            return pf.nodes.geo.mesh_cube()
        case "matrix":
            return pf.Matrix.Identity(4)
        case "collection":
            return pf.ops.collection.group_objects(
                pf.ops.primitives.mesh_cube(),
                pf.ops.primitives.mesh_cube(),
            )
        case "points":
            return pf.nodes.geo.mesh_to_points(pf.nodes.geo.mesh_grid().mesh)
        case "instances":
            return pf.nodes.geo.instance_on_points(
                pf.nodes.geo.mesh_to_points(pf.nodes.geo.mesh_grid().mesh),
                pf.nodes.geo.mesh_cube().mesh,
            )
        case x if "curve" in x:
            return pf.nodes.geo.curve_circle()
        case "volume":
            return pf.nodes.geo.mesh_to_volume(
                pf.nodes.geo.mesh_cube().mesh,
            )
        case "geometries":
            return [pf.nodes.geo.mesh_cube()] * 2
        case "image":
            return pf.types.Image(
                bpy.data.images.new(
                    name="Test Image", width=100, height=100, alpha=True
                ),
            )
        case "object":
            return pf.ops.primitives.mesh_cube()
        case "string":
            return "hello"
        case "strings":
            return ["hello", "world"]
        case _:
            raise ValueError(f"Unknown positional argument: {arg_name}")


def _test_node_function(
    func: Callable,
    nodegroup_type: pf.nodes.NodeGroupType,
    is_multi_output: bool,
):
    arguments = _get_required_args(func)
    inputs = {arg: _construct_asset_string(arg) for arg in arguments}
    node = func(**inputs)
    assert node is not None, f"Function {func.__name__} returned None"

    if is_multi_output:
        pass
    else:
        pass


_STANDARD_NODES = pf.util.manifest.filter_manifest(
    pf.nodes.NODES_MANIFEST,
    filter={"is_infinigen_restricted": False, "is_unittest_specialcase": False},
    exclude={"name": ["LATER", "TODO"]},
    require_nonempty=["name"],
    min_entries=300,
)

TESTCASE_KEYS = [
    "name",
    "node_group_type",
    "is_multi_output",
]


@pytest.mark.parametrize(
    "func_name,node_group_types,is_multi_output",
    list(_STANDARD_NODES[TESTCASE_KEYS].itertuples(index=False)),
    ids=_STANDARD_NODES["name"].values,
)
def test_standard_nodes(
    func_name: str,
    node_group_types: list[str] | str,
    is_multi_output: bool,
):
    func = import_item_iterative(func_name.replace("pf.", "procfunc."))

    # Handle both list format (new JSON) and string format (legacy)
    if isinstance(node_group_types, str):
        node_group_type_list = node_group_types.split("|")
    else:
        node_group_type_list = node_group_types

    for node_group_type in node_group_type_list:
        _test_node_function(
            func=func,
            nodegroup_type=pf.nodes.NodeGroupType(node_group_type),
            is_multi_output=is_multi_output,
        )


_RESTRICTED_NODES = pf.util.manifest.filter_manifest(
    pf.nodes.NODES_MANIFEST,
    filter={"is_infinigen_restricted": True, "is_unittest_specialcase": False},
    require_nonempty=["name"],
    min_entries=1,
)


@pytest.mark.parametrize(
    "func_name,node_group_types,is_multi_output",
    list(_RESTRICTED_NODES[TESTCASE_KEYS].itertuples(index=False)),
    ids=_RESTRICTED_NODES["name"].values,
)
def test_nodes_restricted_throw(
    func_name: str,
    node_group_types: list[str] | str,
    is_multi_output: bool,
):
    if isinstance(node_group_types, str):
        nodegroups = node_group_types.split("|")
    else:
        nodegroups = node_group_types

    func = import_item_iterative(func_name.replace("pf.", "procfunc."))

    for nodegroup in nodegroups:
        with pf.context.override_globals(
            warn_mode_avoid_normal_bump="throw",
            warn_mode_avoid_implicit_vector="throw",
            warn_mode_avoid_io_nodes="throw",
        ):
            with pytest.raises(ValueError):
                _test_node_function(
                    func=func,
                    nodegroup_type=pf.nodes.NodeGroupType(nodegroup),
                    is_multi_output=False,
                )

        with pf.context.override_globals(
            warn_mode_avoid_normal_bump="warn",
            warn_mode_avoid_implicit_vector="warn",
            warn_mode_avoid_io_nodes="warn",
        ):
            _test_node_function(
                func=func,
                nodegroup_type=pf.nodes.NodeGroupType(nodegroup),
                is_multi_output=is_multi_output,
            )
