import uuid

import bpy
import pytest

from procfunc import context
from procfunc.codegen import to_python
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo
from procfunc.transpiler.parse_special_cases import (
    IMPLICIT_TEXTURE_COORDINATES,
    SPECIAL_CASE_NODES,
    handle_specialcase_1d_texture,
    handle_specialcase_image_texture,
    handle_specialcase_sky,
    handle_specialcase_texture_mapping,
)

MAPPED_TEXTURE_NODES = [
    "ShaderNodeTexBrick",
    "ShaderNodeTexChecker",
    "ShaderNodeTexEnvironment",
    "ShaderNodeTexGradient",
    "ShaderNodeTexImage",
    "ShaderNodeTexMagic",
    "ShaderNodeTexNoise",
    "ShaderNodeTexSky",
    "ShaderNodeTexVoronoi",
    "ShaderNodeTexWave",
]

CLAMP_FIELDS = [
    ("use_min", True),
    ("use_max", True),
]


def shader_tree(bl_idname: str, **mapping) -> tuple[bpy.types.NodeTree, bpy.types.Node]:
    tree = bpy.data.node_groups.new(f"texmap_{uuid.uuid4().hex[:8]}", "ShaderNodeTree")
    tree.interface.new_socket("Color", in_out="OUTPUT", socket_type="NodeSocketColor")
    output = tree.nodes.new("NodeGroupOutput")
    node = tree.nodes.new(bl_idname)
    for field, value in mapping.items():
        setattr(node.texture_mapping, field, value)
    tree.links.new(node.outputs[0], output.inputs["Color"])
    return tree, node


def geometry_tree(**mapping) -> bpy.types.NodeTree:
    tree = bpy.data.node_groups.new(
        f"texmap_{uuid.uuid4().hex[:8]}", "GeometryNodeTree"
    )
    tree.interface.new_socket("Value", in_out="OUTPUT", socket_type="NodeSocketFloat")
    output = tree.nodes.new("NodeGroupOutput")
    node = tree.nodes.new("ShaderNodeTexNoise")
    for field, value in mapping.items():
        setattr(node.texture_mapping, field, value)
    position = tree.nodes.new("GeometryNodeInputPosition")
    tree.links.new(position.outputs[0], node.inputs["Vector"])
    tree.links.new(node.outputs["Fac"], output.inputs["Value"])
    return tree


def transpile(tree: bpy.types.NodeTree) -> str:
    graph, _ = parse_node_tree(tree, ParseMemo())
    return to_python(graph, toplevel_as_maincall=False)


def evaluate_geometry_value(tree: bpy.types.NodeTree) -> float:
    mesh = bpy.data.meshes.new("texmap")
    mesh.from_pydata([(0.25, 0.5, 0.75)], [], [])
    obj = bpy.data.objects.new("texmap", mesh)
    bpy.context.scene.collection.objects.link(obj)

    host = bpy.data.node_groups.new(f"host_{uuid.uuid4().hex[:8]}", "GeometryNodeTree")
    host.interface.new_socket(
        "Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    host.interface.new_socket(
        "Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )
    group_input = host.nodes.new("NodeGroupInput")
    group_output = host.nodes.new("NodeGroupOutput")
    store = host.nodes.new("GeometryNodeStoreNamedAttribute")
    store.data_type = "FLOAT"
    store.inputs["Name"].default_value = "texmap"
    called = host.nodes.new("GeometryNodeGroup")
    called.node_tree = tree
    host.links.new(group_input.outputs[0], store.inputs["Geometry"])
    host.links.new(called.outputs[0], store.inputs["Value"])
    host.links.new(store.outputs["Geometry"], group_output.inputs[0])

    modifier = obj.modifiers.new("texmap", "NODES")
    modifier.node_group = host
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return evaluated.data.attributes["texmap"].data[0].value


@pytest.mark.parametrize("bl_idname", MAPPED_TEXTURE_NODES)
def test_identity_texture_mapping_emits_nothing(bl_idname: str) -> None:
    source = transpile(shader_tree(bl_idname)[0])
    assert "texture_mapping" not in source
    assert "color_mapping" not in source
    assert "pf.nodes.shader.mapping" not in source


def test_color_mapping_is_dropped_without_complaint() -> None:
    tree, node = shader_tree("ShaderNodeTexChecker")
    node.color_mapping.brightness = 0.5
    node.color_mapping.saturation = 2.0
    node.color_mapping.use_color_ramp = True
    source = transpile(tree)
    assert "color_mapping" not in source
    assert "pf.nodes.shader.mapping" not in source


def test_legacy_projection_field_is_dropped_without_complaint() -> None:
    source = transpile(shader_tree("ShaderNodeTexChecker", mapping="SPHERE")[0])
    assert "pf.nodes.shader.mapping" not in source


def test_translation_emits_a_point_mapping_node() -> None:
    source = transpile(
        shader_tree("ShaderNodeTexChecker", translation=(0.5, 0.25, 0.125))[0]
    )
    assert "pf.nodes.shader.mapping(" in source
    assert "location=(0.5, 0.25, 0.125)" in source


def test_rotation_and_scale_emit_a_point_mapping_node() -> None:
    source = transpile(
        shader_tree(
            "ShaderNodeTexChecker", rotation=(0.25, 0.5, 0.75), scale=(2.0, 3.0, 0.5)
        )[0]
    )
    assert "rotation=(0.25, 0.5, 0.75)" in source
    assert "scale=(2.0, 3.0, 0.5)" in source


def test_texture_vector_type_emits_mapping_texture() -> None:
    source = transpile(
        shader_tree(
            "ShaderNodeTexChecker", vector_type="TEXTURE", translation=(0.5, 0.0, 0.0)
        )[0]
    )
    assert "pf.nodes.shader.mapping_texture(" in source
    assert "location=(0.5, 0.0, 0.0)" in source


def test_vector_vector_type_emits_mapping_vector_without_location() -> None:
    source = transpile(
        shader_tree(
            "ShaderNodeTexChecker", vector_type="VECTOR", translation=(0.5, 0.0, 0.0)
        )[0]
    )
    assert "pf.nodes.shader.mapping_vector(" in source
    assert "location=" not in source


def test_normal_vector_type_emits_mapping_normal_without_location() -> None:
    source = transpile(
        shader_tree(
            "ShaderNodeTexChecker", vector_type="NORMAL", translation=(0.5, 0.0, 0.0)
        )[0]
    )
    assert "pf.nodes.shader.mapping_normal(" in source
    assert "location=" not in source


def test_reordered_axes_emit_a_combine_xyz_before_the_mapping() -> None:
    source = transpile(
        shader_tree(
            "ShaderNodeTexChecker", mapping_x="Z", mapping_y="X", mapping_z="Y"
        )[0]
    )
    assert (
        "pf.nodes.math.combine_xyz(coord.generated.z, coord.generated.x, coord.generated.y)"
        in source
    )


def test_dropped_axis_becomes_a_literal_zero() -> None:
    source = transpile(shader_tree("ShaderNodeTexChecker", mapping_y="NONE")[0])
    assert (
        "pf.nodes.math.combine_xyz(coord.generated.x, 0.0, coord.generated.z)" in source
    )


def test_unlinked_vector_maps_the_generated_coordinate() -> None:
    source = transpile(shader_tree("ShaderNodeTexChecker", scale=(2.0, 2.0, 2.0))[0])
    assert "coord = pf.nodes.shader.coord()" in source
    assert "vector=coord.generated" in source


def test_image_texture_maps_the_uv_coordinate() -> None:
    source = transpile(shader_tree("ShaderNodeTexImage", scale=(2.0, 2.0, 2.0))[0])
    assert "vector=coord.uv" in source


def test_environment_texture_maps_the_position_coordinate() -> None:
    source = transpile(
        shader_tree("ShaderNodeTexEnvironment", scale=(2.0, 2.0, 2.0))[0]
    )
    assert "pf.nodes.shader.geometry()" in source
    assert ".position" in source


def test_linked_vector_is_mapped_instead_of_a_coordinate_node() -> None:
    tree, node = shader_tree("ShaderNodeTexChecker", scale=(2.0, 2.0, 2.0))
    combine = tree.nodes.new("ShaderNodeCombineXYZ")
    combine.inputs[0].default_value = 0.25
    tree.links.new(combine.outputs[0], node.inputs["Vector"])
    source = transpile(tree)
    assert "pf.nodes.shader.coord()" not in source
    assert "mapping_vector = pf.nodes.math.combine_xyz(0.25)" in source
    assert "pf.nodes.shader.mapping(vector=mapping_vector" in source
    assert "vector=mapping," in source


def test_geometry_nodes_ignore_a_non_identity_texture_mapping() -> None:
    unmapped = evaluate_geometry_value(geometry_tree())
    mapped_tree = geometry_tree(scale=(3.0, 3.0, 3.0), translation=(1.0, 2.0, 3.0))
    assert evaluate_geometry_value(mapped_tree) == unmapped
    assert "pf.nodes.shader.mapping" not in transpile(mapped_tree)


def test_compositor_has_no_texture_mapping_nodes() -> None:
    tree = bpy.data.node_groups.new(
        f"comp_{uuid.uuid4().hex[:8]}", "CompositorNodeTree"
    )
    for bl_idname in MAPPED_TEXTURE_NODES:
        with pytest.raises(RuntimeError):
            tree.nodes.new(bl_idname)


@pytest.mark.parametrize(
    ("bl_idname", "dimensions_attr"),
    [
        ("ShaderNodeTexNoise", "noise_dimensions"),
        ("ShaderNodeTexVoronoi", "voronoi_dimensions"),
    ],
)
def test_one_dimensional_textures_drop_the_mapping(
    bl_idname: str, dimensions_attr: str
) -> None:
    tree, node = shader_tree(bl_idname, scale=(2.0, 2.0, 2.0))
    setattr(node, dimensions_attr, "1D")
    source = transpile(tree)
    assert "pf.nodes.shader.mapping" not in source
    assert "vector=None" in source


@pytest.mark.parametrize(
    ("bl_idname", "dimensions_attr"),
    [
        ("ShaderNodeTexNoise", "noise_dimensions"),
        ("ShaderNodeTexVoronoi", "voronoi_dimensions"),
    ],
)
def test_higher_dimensional_textures_keep_the_mapping(
    bl_idname: str, dimensions_attr: str
) -> None:
    tree, node = shader_tree(bl_idname, scale=(2.0, 2.0, 2.0))
    setattr(node, dimensions_attr, "4D")
    assert "pf.nodes.shader.mapping(" in transpile(tree)


@pytest.mark.parametrize(
    ("sky_type", "sun_disc"),
    [("PREETHAM", True), ("HOSEK_WILKIE", True), ("NISHITA", False)],
)
def test_sky_texture_maps_enabled_vector(sky_type: str, sun_disc: bool) -> None:
    tree, node = shader_tree("ShaderNodeTexSky", scale=(2.0, 2.0, 2.0))
    node.sky_type = sky_type
    node.sun_disc = sun_disc
    source = transpile(tree)
    assert "coord = pf.nodes.shader.coord()" in source
    assert "pf.nodes.shader.mapping(" in source
    assert "vector=coord.generated" in source


def test_sky_texture_without_vector_rejects_mapping() -> None:
    tree, node = shader_tree("ShaderNodeTexSky", scale=(2.0, 2.0, 2.0))
    node.sky_type = "NISHITA"
    node.sun_disc = True
    assert "Vector" not in node.inputs
    with pytest.raises(ValueError, match="non-identity texture_mapping"):
        transpile(tree)


@pytest.mark.parametrize(("field", "value"), CLAMP_FIELDS)
def test_clamped_texture_mapping_throws(field: str, value: bool) -> None:
    tree, node = shader_tree("ShaderNodeTexChecker")
    setattr(node.texture_mapping, field, value)
    with pytest.raises(ValueError, match="texture_mapping clamp"):
        transpile(tree)


def test_clamp_bounds_alone_do_not_throw() -> None:
    tree, node = shader_tree("ShaderNodeTexChecker")
    node.texture_mapping.min = (0.2, 0.2, 0.2)
    node.texture_mapping.max = (0.4, 0.4, 0.4)
    assert "pf.nodes.shader.mapping" not in transpile(tree)


def test_warn_mode_transpiles_the_clamp_anyway(
    caplog: pytest.LogCaptureFixture,
) -> None:
    tree, node = shader_tree("ShaderNodeTexChecker", scale=(2.0, 2.0, 2.0))
    node.texture_mapping.use_min = True
    with context.override_globals(warn_mode_transpile_dropped_attrs="warn"):
        with caplog.at_level("WARNING"):
            source = transpile(tree)
    assert "texture_mapping clamp" in caplog.text
    assert "pf.nodes.shader.mapping(" in source


def test_ignore_mode_is_silent(caplog: pytest.LogCaptureFixture) -> None:
    tree, node = shader_tree("ShaderNodeTexChecker")
    node.texture_mapping.use_min = True
    with context.override_globals(warn_mode_transpile_dropped_attrs="ignore"):
        with caplog.at_level("WARNING"):
            transpile(tree)
    assert "texture_mapping clamp" not in caplog.text


def test_every_mapped_node_knows_its_implicit_coordinate() -> None:
    mapped = {
        bl_idname
        for bl_idname, handler in SPECIAL_CASE_NODES.items()
        if handler
        in (
            handle_specialcase_texture_mapping,
            handle_specialcase_1d_texture,
            handle_specialcase_image_texture,
            handle_specialcase_sky,
        )
    }
    assert mapped - {"ShaderNodeTexWhiteNoise"} == set(IMPLICIT_TEXTURE_COORDINATES)


def test_white_noise_has_no_texture_mapping() -> None:
    tree, node = shader_tree("ShaderNodeTexWhiteNoise")
    assert not hasattr(node, "texture_mapping")
    transpile(tree)
