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

_MAPPING_FUNCTIONS = {
    "POINT": "mapping",
    "TEXTURE": "mapping_texture",
    "VECTOR": "mapping_vector",
    "NORMAL": "mapping_normal",
}


def _native_tree(vector_type: str) -> bpy.types.NodeTree:
    tree = bpy.data.node_groups.new("_native_mapping", "ShaderNodeTree")
    tree.interface.new_socket("Vector", in_out="OUTPUT", socket_type="NodeSocketVector")
    output = tree.nodes.new("NodeGroupOutput")
    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.vector_type = vector_type
    mapping.inputs["Rotation"].default_value = (0.1, 0.2, 0.3)
    mapping.inputs["Scale"].default_value = (2.0, 3.0, 4.0)
    if vector_type in ("POINT", "TEXTURE"):
        mapping.inputs["Location"].default_value = (1.0, 2.0, 3.0)
    tree.links.new(mapping.outputs["Vector"], output.inputs["Vector"])
    return tree


def _transpile(tree: bpy.types.NodeTree) -> str:
    graph, _ = parse_node_tree(tree, ParseMemo())
    source = to_python(graph, toplevel_as_maincall=False)
    ast.parse(source)
    return source


def _mapping_call_name(source: str) -> str:
    names = [
        node.func.attr
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr.startswith("mapping")
    ]
    assert len(names) == 1
    return names[0]


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
    tree = as_nodegroup(graph, NodeGroupType.SHADER)
    nodes = [node for node in tree.nodes if node.bl_idname == "ShaderNodeMapping"]
    assert len(nodes) == 1
    return nodes[0]


@pytest.mark.parametrize(("vector_type", "function_name"), _MAPPING_FUNCTIONS.items())
def test_mapping_mode_round_trips(vector_type: str, function_name: str) -> None:
    source = _transpile(_native_tree(vector_type))
    assert _mapping_call_name(source) == function_name
    assert "vector_type=" not in source

    rebuilt = _rebuild(source)
    assert rebuilt.vector_type == vector_type


@pytest.mark.parametrize(
    ("function_name", "has_location"),
    [
        ("mapping", True),
        ("mapping_texture", True),
        ("mapping_vector", False),
        ("mapping_normal", False),
    ],
)
def test_mapping_mode_signature_matches_sockets(
    function_name: str, has_location: bool
) -> None:
    signature = inspect.signature(getattr(pf.nodes.shader, function_name))
    assert ("location" in signature.parameters) is has_location
    assert "vector_type" not in signature.parameters


def test_mapping_preserves_point_signature() -> None:
    signature = inspect.signature(pf.nodes.shader.mapping)
    assert list(signature.parameters) == ["vector", "location", "rotation", "scale"]
    assert signature.parameters["vector"].default == (0, 0, 0)
    assert signature.parameters["location"].default == (0, 0, 0)
    assert signature.parameters["rotation"].default == (0, 0, 0)
    assert signature.parameters["scale"].default == (1, 1, 1)
