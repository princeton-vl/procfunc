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

comp = pf.nodes.compositor

_MODES = [
    (
        "LIFT_GAMMA_GAIN",
        "color_balance",
        {
            "gain": (1.1, 1.2, 1.3),
            "gamma": (0.8, 0.9, 1.0),
            "lift": (0.1, 0.2, 0.3),
        },
    ),
    (
        "OFFSET_POWER_SLOPE",
        "color_balance_slope_offset_power",
        {
            "offset": (0.2, 0.3, 0.4),
            "offset_basis": 0.1,
            "power": (0.7, 0.8, 0.9),
            "slope": (1.2, 1.3, 1.4),
        },
    ),
]


def _native_tree(method: str, attrs: dict) -> bpy.types.NodeTree:
    scene = bpy.data.scenes.new(f"_native_color_balance_{method}")
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    output = tree.nodes.new("NodeGroupOutput")
    color_balance = tree.nodes.new("CompositorNodeColorBalance")
    color_balance.correction_method = method
    for name, value in attrs.items():
        setattr(color_balance, name, value)
    tree.links.new(color_balance.outputs["Image"], output.inputs["Image"])
    return tree


def _transpile(tree: bpy.types.NodeTree) -> str:
    graph, _ = parse_node_tree(tree, ParseMemo())
    source = to_python(graph, toplevel_as_maincall=False)
    ast.parse(source)
    return source


def _realize(source: str) -> bpy.types.Node:
    namespace: dict = {}
    exec(source, namespace)  # noqa: S102
    functions = [
        value
        for value in namespace.values()
        if callable(value) and hasattr(value, "__wrapped__")
    ]
    assert len(functions) == 1
    graph = pf.nodes.function_to_compute_graph(functions[0])
    tree = as_nodegroup(graph, NodeGroupType.COMPOSITOR)
    nodes = [
        node for node in tree.nodes if node.bl_idname == "CompositorNodeColorBalance"
    ]
    assert len(nodes) == 1
    return nodes[0]


@pytest.mark.parametrize(
    ("method", "function_name", "attrs"),
    _MODES,
    ids=["lift_gamma_gain", "slope_offset_power"],
)
def test_color_balance_mode_round_trips(
    method: str, function_name: str, attrs: dict
) -> None:
    source = _transpile(_native_tree(method, attrs))
    assert f"compositor.{function_name}(" in source
    assert "correction_method=" not in source

    rebuilt = _realize(source)
    assert rebuilt.correction_method == method
    for name, value in attrs.items():
        actual = getattr(rebuilt, name)
        if isinstance(value, tuple):
            actual = tuple(actual)
        assert actual == pytest.approx(value)


@pytest.mark.parametrize(
    ("method", "function_name", "attrs"),
    _MODES,
    ids=["lift_gamma_gain", "slope_offset_power"],
)
def test_color_balance_mode_builds_only_active_attributes(
    method: str, function_name: str, attrs: dict
) -> None:
    result = getattr(comp, function_name)(**attrs)
    assert result.item().attrs == {"correction_method": method, **attrs}


@pytest.mark.parametrize(
    ("function_name", "parameters"),
    [
        (
            "color_balance",
            ["fac", "image", "gain", "gamma", "lift"],
        ),
        (
            "color_balance_slope_offset_power",
            ["fac", "image", "offset", "offset_basis", "power", "slope"],
        ),
    ],
)
def test_color_balance_mode_signatures(
    function_name: str, parameters: list[str]
) -> None:
    signature = inspect.signature(getattr(comp, function_name))
    assert list(signature.parameters) == parameters
    assert "correction_method" not in signature.parameters
