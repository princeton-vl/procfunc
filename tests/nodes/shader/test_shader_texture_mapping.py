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
pytestmark = pytest.mark.render

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
    link_vector: bool = True,
    **mapping,
) -> bpy.types.NodeTree:
    tree = bpy.data.node_groups.new(f"texmap_{uuid.uuid4().hex[:8]}", "ShaderNodeTree")
    tree.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    output = tree.nodes.new("NodeGroupOutput")
    node = tree.nodes.new(bl_idname)

    if bl_idname in IMAGE_TEXTURE_NODES:
        # noise rather than a grid, so that a mapping which lands the whole plane
        # inside one texel still renders something the comparison can see
        node.image = bpy.data.images.new(
            f"noise_{uuid.uuid4().hex[:8]}", 64, 64, alpha=False, float_buffer=True
        )
        node.image.colorspace_settings.name = "Non-Color"
        node.image.pixels.foreach_set(
            np.random.default_rng(0).random(64 * 64 * 4, dtype=np.float32)
        )
    for field, value in mapping.items():
        setattr(node.texture_mapping, field, value)
    if link_vector:
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


@pytest.mark.parametrize(
    "mapping",
    [
        pytest.param({"translation": (0.5, 0.25, 0.125)}, id="translation"),
        pytest.param({"rotation": (0.3, 0.4, 0.5)}, id="rotation"),
        pytest.param({"scale": (2.0, 3.0, 0.5)}, id="scale"),
        pytest.param(
            {
                "vector_type": "POINT",
                "translation": (0.5, 0.25, 0.125),
                "scale": (2.0, 3.0, 0.5),
            },
            id="point",
        ),
        pytest.param(
            {
                "vector_type": "TEXTURE",
                "translation": (0.5, 0.25, 0.125),
                "scale": (2.0, 3.0, 0.5),
            },
            id="texture",
        ),
        pytest.param(
            {
                "vector_type": "VECTOR",
                "rotation": (0.3, 0.4, 0.5),
                "scale": (2.0, 3.0, 0.5),
            },
            id="vector",
        ),
        pytest.param(
            {
                "vector_type": "NORMAL",
                "rotation": (0.3, 0.4, 0.5),
                "scale": (2.0, 3.0, 0.5),
            },
            id="normal",
        ),
        pytest.param(
            {"mapping_x": "Z", "mapping_y": "X", "mapping_z": "Y"}, id="reordered-axes"
        ),
        pytest.param({"mapping_x": "NONE", "mapping_z": "NONE"}, id="dropped-axes"),
        pytest.param(
            {"mapping_x": "Y", "mapping_y": "Y", "mapping_z": "Y"}, id="duplicated-axis"
        ),
    ],
)
def test_mapping_survives_transpile(mapping: dict) -> None:
    tree = texture_tree(**mapping)
    original = shader_eval.render_nodegroup(tree)
    unmapped = shader_eval.render_nodegroup(texture_tree())
    assert not np.allclose(original, unmapped, atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


@pytest.mark.parametrize("vector_type", ["VECTOR", "NORMAL"])
def test_direction_mapping_ignores_translation(vector_type: str) -> None:
    mapping = {"vector_type": vector_type, "scale": (2.0, 3.0, 0.5)}
    tree = texture_tree(**mapping, translation=(0.5, 0.25, 0.125))
    unmapped = shader_eval.render_nodegroup(texture_tree(**mapping))
    assert "location=" not in transpile_to_source(tree)
    np.testing.assert_allclose(shader_eval.render_nodegroup(tree), unmapped, atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), unmapped, atol=ATOL
    )


def test_axes_are_reordered_before_the_transform() -> None:
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


def test_unlinked_vector_maps_the_implicit_coordinate() -> None:
    tree = texture_tree(link_vector=False, **EVERY_MAPPING_FIELD)
    unmapped = texture_tree(link_vector=False)
    original = shader_eval.render_nodegroup(tree)
    assert "coord = pf.nodes.shader.coord()" in transpile_to_source(tree)
    assert "coord.generated" in transpile_to_source(tree)
    assert not np.allclose(original, shader_eval.render_nodegroup(unmapped), atol=ATOL)
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree)), original, atol=ATOL
    )


@pytest.mark.parametrize("link_vector", [True, False])
@pytest.mark.parametrize("bl_idname", MAPPED_TEXTURE_NODES)
@pytest.mark.parametrize("engine", [shader_eval.CYCLES, shader_eval.EEVEE])
def test_every_mapped_texture_node_survives_transpile(
    bl_idname: str, link_vector: bool, engine: str
) -> None:
    tree = texture_tree(bl_idname, link_vector, **EVERY_MAPPING_FIELD)
    unmapped = texture_tree(bl_idname, link_vector)
    original = shader_eval.render_nodegroup(tree, engine=engine)
    assert not np.allclose(
        original, shader_eval.render_nodegroup(unmapped, engine=engine), atol=ATOL
    )
    np.testing.assert_allclose(
        shader_eval.render_nodegroup(rebuild(tree), engine=engine), original, atol=ATOL
    )
