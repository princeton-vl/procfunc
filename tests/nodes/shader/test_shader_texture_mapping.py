import uuid

import bpy
import numpy as np
import pytest
import shader_eval

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.util.bpy_node_info import NodeGroupType
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo

ATOL = 2e-3

IMAGE_TEXTURE_NODES = ("ShaderNodeTexImage", "ShaderNodeTexEnvironment")

MAPPED_TEXTURE_NODES = [
    "ShaderNodeTexBrick",
    "ShaderNodeTexChecker",
    "ShaderNodeTexEnvironment",
    "ShaderNodeTexGradient",
    "ShaderNodeTexImage",
    "ShaderNodeTexMagic",
    "ShaderNodeTexNoise",
    "ShaderNodeTexVoronoi",
    "ShaderNodeTexWave",
]

# every field at once, chosen so that no texture node renders it as a no-op
EVERY_MAPPING_FIELD = {
    "vector_type": "TEXTURE",
    "translation": (0.1, 0.2, 0.3),
    "rotation": (0.3, 0.4, 0.5),
    "scale": (2.0, 3.0, 0.5),
    "mapping_x": "Y",
    "mapping_z": "X",
}


def texture_tree(
    bl_idname: str = "ShaderNodeTexMagic",
    link_object_coordinate: bool = False,
    **mapping,
) -> bpy.types.NodeTree:
    tree = bpy.data.node_groups.new(f"texmap_{uuid.uuid4().hex[:8]}", "ShaderNodeTree")
    tree.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    output = tree.nodes.new("NodeGroupOutput")
    node = tree.nodes.new(bl_idname)

    if bl_idname in IMAGE_TEXTURE_NODES:
        node.image = bpy.data.images.new(f"grid_{uuid.uuid4().hex[:8]}", 8, 8)
        node.image.generated_type = "COLOR_GRID"
    for field, value in mapping.items():
        setattr(node.texture_mapping, field, value)
    if link_object_coordinate:
        coord = tree.nodes.new("ShaderNodeTexCoord")
        tree.links.new(coord.outputs["Object"], node.inputs["Vector"])

    tree.links.new(node.outputs[0], output.inputs["Color"])
    return tree


def transpile_to_source(tree: bpy.types.NodeTree) -> str:
    graph, _ = parse_node_tree(tree, ParseMemo())
    return to_python(graph, toplevel_as_maincall=False)


def rebuild(tree: bpy.types.NodeTree) -> bpy.types.NodeTree:
    namespace: dict = {}
    exec(transpile_to_source(tree), namespace)  # noqa: S102
    functions = [
        value
        for value in namespace.values()
        if callable(value) and hasattr(value, "__wrapped__")
    ]
    assert len(functions) == 1
    graph = pf.nodes.function_to_compute_graph(functions[0])
    return as_nodegroup(graph, NodeGroupType.SHADER)


@pytest.fixture(scope="module")
def unmapped_magic() -> np.ndarray:
    return shader_eval.render_nodegroup(texture_tree())


def test_translation_survives_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(translation=(0.5, 0.25, 0.125))
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_rotation_survives_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(rotation=(0.3, 0.4, 0.5))
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_scale_survives_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(scale=(2.0, 3.0, 0.5))
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_point_vector_type_survives_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(
        vector_type="POINT", translation=(0.5, 0.25, 0.125), scale=(2.0, 3.0, 0.5)
    )
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    assert "pf.nodes.shader.mapping(" in transpile_to_source(tree)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_texture_vector_type_survives_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(
        vector_type="TEXTURE", translation=(0.5, 0.25, 0.125), scale=(2.0, 3.0, 0.5)
    )
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    assert "pf.nodes.shader.mapping_texture(" in transpile_to_source(tree)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_vector_vector_type_survives_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(
        vector_type="VECTOR", rotation=(0.3, 0.4, 0.5), scale=(2.0, 3.0, 0.5)
    )
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    assert "pf.nodes.shader.mapping_vector(" in transpile_to_source(tree)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_normal_vector_type_survives_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(
        vector_type="NORMAL", rotation=(0.3, 0.4, 0.5), scale=(2.0, 3.0, 0.5)
    )
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    assert "pf.nodes.shader.mapping_normal(" in transpile_to_source(tree)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_vector_vector_type_keeps_ignoring_translation(
    unmapped_magic: np.ndarray,
) -> None:
    tree = texture_tree(vector_type="VECTOR", translation=(0.5, 0.25, 0.125))
    source = transpile_to_source(tree)
    assert "location=" not in source
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(tree), unmapped_magic, atol=ATOL
    )
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), unmapped_magic, atol=ATOL
    )


def test_normal_vector_type_keeps_ignoring_translation(
    unmapped_magic: np.ndarray,
) -> None:
    tree = texture_tree(vector_type="NORMAL", translation=(0.5, 0.25, 0.125))
    original = shader_eval.render_nodegroup(tree)
    assert "location=" not in transpile_to_source(tree)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_reordered_axes_survive_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(mapping_x="Z", mapping_y="X", mapping_z="Y")
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_dropped_axes_survive_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(mapping_x="NONE", mapping_z="NONE")
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_duplicated_axis_survives_transpile(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(mapping_x="Y", mapping_y="Y", mapping_z="Y")
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, unmapped_magic, atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_axes_are_reordered_before_the_transform(unmapped_magic: np.ndarray) -> None:
    tree = texture_tree(mapping_x="Y", mapping_y="X", translation=(0.5, 0.0, 0.0))
    swapped_after = texture_tree(
        mapping_x="Y", mapping_y="X", translation=(0.0, 0.5, 0.0)
    )
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(
        original, shader_eval.render_nodegroup(swapped_after), atol=ATOL
    )
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


def test_linked_vector_is_mapped_before_reaching_the_texture() -> None:
    unmapped = texture_tree(link_object_coordinate=True)
    tree = texture_tree(link_object_coordinate=True, **EVERY_MAPPING_FIELD)
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, shader_eval.render_nodegroup(unmapped), atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


@pytest.mark.parametrize("bl_idname", MAPPED_TEXTURE_NODES)
def test_every_mapped_texture_node_survives_transpile(bl_idname: str) -> None:
    unmapped = texture_tree(bl_idname)
    tree = texture_tree(bl_idname, **EVERY_MAPPING_FIELD)
    original = shader_eval.render_nodegroup(tree)
    assert not np.allclose(original, shader_eval.render_nodegroup(unmapped), atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )
