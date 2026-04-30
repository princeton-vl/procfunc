import bpy
import numpy as np

import procfunc as pf


def test_to_material_basic():
    """Test to_material with a simple principled BSDF shader."""
    # Create a simple material shader
    bsdf = pf.nodes.shader.principled_bsdf(
        base_color=(0.8, 0.2, 0.1, 1.0), metallic=0.0, roughness=0.5
    )

    # Convert to material
    material = pf.Material(surface=bsdf)

    # Verify material was created
    assert material.item().use_nodes is True
    assert material.item().name in bpy.data.materials

    # Verify node tree structure
    nodes = material.item().node_tree.nodes
    assert "Material Output" in nodes
    assert any("Group" in node.name for node in nodes)


def test_to_material_with_texture():
    """Test to_material with texture nodes."""
    # Create a texture-based material
    coord = pf.nodes.shader.coord()
    noise = pf.nodes.shader.noise(
        vector=coord.generated, scale=5.0, detail=2.0, roughness=0.5
    )

    bsdf = pf.nodes.shader.principled_bsdf(base_color=noise.color, roughness=noise.fac)

    # Convert to material
    material = pf.Material(surface=bsdf)

    assert material.item().use_nodes is True


def test_to_environment_basic():
    """Test to_environment with a simple background shader."""
    # Create a simple environment shader
    background = pf.nodes.shader.background(color=(0.05, 0.1, 0.3, 1.0), strength=1.0)

    # Convert to environment
    world = pf.nodes.to_environment(surface=background)

    # Verify world was created/modified
    assert world is not None
    assert world.item().use_nodes is True
    assert bpy.context.scene.world == world.item()

    # Verify node tree structure
    nodes = world.item().node_tree.nodes
    assert len(nodes) > 0
    # Should have a ShaderNodeGroup instance and ShaderNodeOutputWorld
    assert any(node.type == "GROUP" for node in nodes)
    assert any(node.type == "OUTPUT_WORLD" for node in nodes)


def test_to_environment_with_sky():
    """Test to_environment with sky texture."""
    # Create sky-based environment
    sky = pf.nodes.shader.sky(sky_type="NISHITA", sun_elevation=0.5, sun_rotation=0.0)

    background = pf.nodes.shader.background(color=sky, strength=1.0)

    # Convert to environment
    world = pf.nodes.to_environment(surface=background)

    assert world is not None
    assert world.item().use_nodes is True


def test_to_compositor_basic():
    """Test to_compositor with simple compositor nodes."""
    # Create simple compositor setup
    render_layers = pf.nodes.compositor.render_layers()

    # Add some color correction
    bright_contrast = pf.nodes.compositor.bright_contrast(
        image=render_layers.image, bright=0.1, contrast=0.1
    )

    composite = pf.nodes.compositor.composite(image=bright_contrast)

    # Convert to compositor
    pf.nodes.to_compositor(results={"image": composite})

    # Verify compositor was set up
    assert bpy.context.scene.use_nodes is True
    assert bpy.context.scene.node_tree is not None

    # Verify nodes exist
    nodes = bpy.context.scene.node_tree.nodes
    assert len(nodes) > 0


def test_material_with_displacement():
    """Test material creation with displacement."""
    # Create material with displacement
    coord = pf.nodes.shader.coord()
    noise = pf.nodes.shader.noise(vector=coord.generated, scale=2.0)

    bsdf = pf.nodes.shader.principled_bsdf(base_color=(0.8, 0.8, 0.8, 1.0))

    displacement = pf.nodes.shader.displacement(
        height=noise.fac, midlevel=0.5, scale=0.1
    )

    material = pf.Material(surface=bsdf, displacement=displacement)

    assert material.item().use_nodes is True


def test_material_with_volume():
    """Test material creation with volume shader."""
    # Create material with volume
    bsdf = pf.nodes.shader.principled_bsdf(base_color=(0.8, 0.8, 0.8, 1.0))

    volume = pf.nodes.shader.volume_principled(color=(1.0, 1.0, 1.0, 1.0), density=0.1)

    material = pf.Material(surface=bsdf, volume=volume)

    assert material.item().use_nodes is True


def test_environment_with_volume():
    """Test environment creation with volume."""

    background = pf.nodes.shader.background(color=(0.1, 0.2, 0.4, 1.0), strength=1.0)
    volume = pf.nodes.shader.volume_principled(color=(0.8, 0.9, 1.0, 1.0), density=0.01)

    world = pf.nodes.to_environment(surface=background, volume=volume)

    assert world is not None
    assert world.item().use_nodes is True


def test_multiple_outputs_compositor():
    """Test compositor with multiple output nodes."""
    render_layers = pf.nodes.compositor.render_layers()

    # Create multiple outputs
    composite = pf.nodes.compositor.composite(image=render_layers.image)

    viewer = pf.nodes.compositor.viewer(image=render_layers.image)

    # Convert to compositor with multiple outputs
    pf.nodes.to_compositor(results={"image": composite, "viewer": viewer})

    assert bpy.context.scene.use_nodes is True
    nodes = bpy.context.scene.node_tree.nodes
    assert len(nodes) >= 2  # At least render layers and one output


def test_complex_shader_network():
    """Test complex shader network with multiple node types."""
    # Create a complex shader with multiple textures and mixing
    coord = pf.nodes.shader.coord()
    mapping = pf.nodes.shader.mapping(vector=coord.generated, scale=(2.0, 2.0, 2.0))

    noise1 = pf.nodes.shader.noise(vector=mapping, scale=5.0)

    noise2 = pf.nodes.shader.noise(vector=mapping, scale=10.0, roughness=0.3)

    mix_color = pf.nodes.func.mix_rgb(factor=0.5, a=noise1.color, b=noise2.color)

    bsdf = pf.nodes.shader.principled_bsdf(
        base_color=mix_color, roughness=noise1.fac, metallic=0.0
    )

    material = pf.Material(surface=bsdf)

    assert material.item().use_nodes is True


@pf.nodes.node_function
def _translate_for_test(
    geo: pf.ProcNode[pf.MeshObject], offset: pf.ProcNode[pf.Vector] = (0, 0, 1)
) -> pf.ProcNode:
    return pf.nodes.geo.set_position(geo, offset=offset)


def test_node_function_meshobject_geometry_input():
    """MeshObject passed to a node_function geometry param should implicitly go through object_info,
    not collection_info."""

    cube = pf.ops.primitives.mesh_cube(size=1.0)
    result = pf.nodes.to_mesh_object(_translate_for_test(cube))

    assert result is not None
    assert result.item().type == "MESH"


def test_object_info_accepts_curve_object():
    """object_info should accept any Object subclass (e.g. CurveObject), not only MeshObject.

    Regression test: assign_default_value previously only auto-unwrapped MeshObject,
    causing CurveObject to be passed as a wrapper to NodeSocketObject.default_value
    and raising "expected a Object type, not CurveObject"."""

    curve = pf.nodes.to_curve_object(
        geometry=pf.nodes.geo.curve_circle(radius=1.0, resolution=8)
    )
    assert isinstance(curve, pf.CurveObject)

    geo = pf.nodes.geo.object_info(curve).geometry
    result = pf.nodes.to_curve_object(geometry=geo)

    assert result is not None
    assert result.item().type == "CURVE"


def test_set_material_unwraps_material_wrapper():
    """assign_default_value should unwrap a pf.Material via .item() when assigning
    to a NodeSocketMaterial, so that bpy receives a bpy.types.Material."""

    bsdf = pf.nodes.shader.principled_bsdf(
        base_color=(0.1, 0.5, 0.8, 1.0), roughness=0.4
    )
    material = pf.Material(surface=bsdf)
    assert isinstance(material, pf.Material)

    cube = pf.nodes.geo.mesh_cube(size=(1, 1, 1)).mesh
    cube_with_mat = pf.nodes.geo.set_material(geometry=cube, material=material)
    obj = pf.nodes.to_mesh_object(geometry=cube_with_mat)

    assert obj is not None
    assert obj.item().type == "MESH"


def test_collection_info_unwraps_collection_wrapper():
    """assign_default_value should unwrap a pf.Collection via .item() when assigning
    to a NodeSocketCollection, so that bpy receives a bpy.types.Collection."""

    cube_obj = pf.nodes.to_mesh_object(pf.nodes.geo.mesh_cube(size=(1, 1, 1)).mesh)
    col = pf.Collection([cube_obj], name="test_unwrap_collection")
    assert isinstance(col, pf.Collection)

    instances = pf.nodes.geo.collection_info(collection=col)
    realized = pf.nodes.geo.realize_instances(instances)
    result = pf.nodes.to_mesh_object(geometry=realized)

    assert result is not None
    assert result.item().type == "MESH"


def test_to_object_basic():
    cube = pf.nodes.geo.mesh_cube(size=(2, 2, 2))
    obj = pf.nodes.to_mesh_object(geometry=cube.mesh)

    assert obj is not None
    assert obj.item().type == "MESH"
    assert obj.item().name in bpy.data.objects

    assert np.abs(np.array(obj.item().dimensions) - 2).max() < 1e-6


def test_to_object_curve_as_mesh():
    curve = pf.nodes.geo.curve_circle(radius=1.0, resolution=10)
    curve = pf.nodes.to_curve_object(geometry=curve)

    assert curve is not None
    assert curve.item().type == "CURVE"
    assert len(curve.item().data.splines[0].points) == 10


def test_to_objects_multi():
    """Test to_object with multiple output nodes."""
    cube1 = pf.nodes.geo.mesh_cube(size=(2, 2, 2))
    cube2 = pf.nodes.geo.mesh_cube(size=(1, 1, 1))

    objs = pf.nodes.to_objects_multi(
        geometries={"cube1": cube1.mesh, "cube2": cube2.mesh}
    )
    assert np.abs(np.array(objs["cube1"].item().dimensions) - 2).max() < 1e-6
    assert np.abs(np.array(objs["cube2"].item().dimensions) - 1).max() < 1e-6


def test_to_aliases():
    """Test to_aliases with instanced geometry."""
    # Create actual objects for instancing
    cube_geo = pf.nodes.geo.mesh_cube(size=(1, 1, 1))
    cube_obj = pf.nodes.to_mesh_object(cube_geo.mesh)

    cylinder_geo = pf.nodes.geo.mesh_cylinder(radius=0.5, depth=1.0)
    cylinder_obj = pf.nodes.to_mesh_object(cylinder_geo.mesh)

    # Create a collection with these objects
    col = pf.types.Collection([cube_obj, cylinder_obj], name="instance_collection")

    # Now use collection_info to get instances
    collection_info = pf.nodes.geo.collection_info(
        collection=col, separate_children=True, reset_children=True
    )

    points = pf.nodes.geo.mesh_line(
        start_location=(0, 0, 0),
        offset=(2, 0, 0),
        count=4,
    )

    idx = pf.nodes.geo.input_index()
    instance_idx = pf.nodes.math.modulo(idx, 2)

    instances = pf.nodes.geo.instance_on_points(
        points=points,
        instance=collection_info,
        pick_instance=True,
        instance_index=instance_idx,
    )

    aliases = pf.nodes.to_aliases(geometry=instances)

    assert len(aliases) == 4

    # Check all objects are valid meshes
    for alias in aliases:
        obj = alias.item()
        assert obj.type == "MESH"
        assert obj.name in bpy.data.objects

    # Check positions - should be at x=0,2,4,6
    positions_x = sorted([a.item().location.x for a in aliases])
    expected_positions = [0.0, 2.0, 4.0, 6.0]
    for actual, expected in zip(positions_x, expected_positions):
        assert np.abs(actual - expected) < 0.01

    # Check that we have exactly 2 unique mesh datas (cube and cylinder)
    unique_meshes = {a.item().data for a in aliases}
    assert len(unique_meshes) == 2

    # Check that each unique mesh has exactly 2 instances
    for mesh in unique_meshes:
        instances_of_this_mesh = [a for a in aliases if a.item().data == mesh]
        assert len(instances_of_this_mesh) == 2


"""
def test_func_as_nodegroup():
    def func(
        x: pf.MeshObject, offset: pf.Vector = (0, 0, 0), offset_scale: float = 1.0
    ):
        geo = pf.nodes.geo.object_info(x)
        geo = pf.nodes.geo.extrude_mesh(geo, offset_scale=offset_scale)
        geo = pf.nodes.geo.transform(geo, translation=offset)
        out = pf.nodes.output(geometry=geo)
        return out

    nodefunc = pf.nodes.nodegroup.from_function(func, pf.nodes.NodeGroupType.GEOMETRY)
    nodegroup = pf.nodes.as_nodegroup(nodefunc(), pf.nodes.NodeGroupType.GEOMETRY)
    items = [x for x in nodegroup.interface.items_tree.values() if x.in_out == "INPUT"]

    assert len(items) == 3

    assert items[0].socket_type == pf.nodes.SocketType.OBJECT.value
    assert items[1].socket_type == pf.nodes.SocketType.VECTOR.value
    assert items[2].socket_type == pf.nodes.SocketType.FLOAT.value
"""
