import ast
import inspect

import bpy
import pytest

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.util.bpy_node_info import NodeGroupType
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo

_AXES = ("X", "Y", "Z")
_PF_DEFAULTS = {"primary_axis": "X", "secondary_axis": "Y"}


def _native_tree(primary_axis: str, secondary_axis: str) -> bpy.types.NodeTree:
    tree = bpy.data.node_groups.new("_native_axes_to_rotation", "GeometryNodeTree")
    tree.interface.new_socket(
        "Rotation", in_out="OUTPUT", socket_type="NodeSocketRotation"
    )
    output = tree.nodes.new("NodeGroupOutput")
    axes = tree.nodes.new("FunctionNodeAxesToRotation")
    axes.primary_axis = primary_axis
    axes.secondary_axis = secondary_axis
    tree.links.new(axes.outputs["Rotation"], output.inputs["Rotation"])
    return tree


def _transpile(tree: bpy.types.NodeTree) -> str:
    graph, _ = parse_node_tree(tree, ParseMemo())
    source = to_python(graph, toplevel_as_maincall=False)
    ast.parse(source)
    return source


def _axis_kwargs(source: str) -> dict[str, str]:
    calls = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "axes_to_rotation"
    ]
    assert len(calls) == 1
    return {
        keyword.arg: ast.literal_eval(keyword.value)
        for keyword in calls[0].keywords
        if keyword.arg in _PF_DEFAULTS
    }


def _rebuild(source: str) -> bpy.types.Node:
    namespace: dict = {}
    exec(source, namespace)  # noqa: S102
    functions = [
        value
        for value in namespace.values()
        if callable(value) and hasattr(value, "__wrapped__")
    ]
    assert len(functions) == 1
    graph = pf.nodes.function_to_compute_graph(functions[0])
    tree = as_nodegroup(graph, NodeGroupType.GEOMETRY)
    nodes = [
        node for node in tree.nodes if node.bl_idname == "FunctionNodeAxesToRotation"
    ]
    assert len(nodes) == 1
    return nodes[0]


def test_axes_to_rotation_signature_preserves_public_defaults() -> None:
    signature = inspect.signature(pf.nodes.func.axes_to_rotation)
    assert signature.parameters["primary_axis"].default == "X"
    assert signature.parameters["secondary_axis"].default == "Y"


@pytest.mark.parametrize("primary_axis", _AXES)
@pytest.mark.parametrize("secondary_axis", _AXES)
def test_axes_to_rotation_axis_pair_round_trips(
    primary_axis: str, secondary_axis: str
) -> None:
    source = _transpile(_native_tree(primary_axis, secondary_axis))
    expected_kwargs = {
        name: value
        for name, value in {
            "primary_axis": primary_axis,
            "secondary_axis": secondary_axis,
        }.items()
        if value != _PF_DEFAULTS[name]
    }
    assert _axis_kwargs(source) == expected_kwargs

    rebuilt = _rebuild(source)
    assert rebuilt.primary_axis == primary_axis
    assert rebuilt.secondary_axis == secondary_axis
