import functools
import tempfile
from collections.abc import Callable
from pathlib import Path

import bpy
import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes.util import bpy_node_info
from procfunc.util import pytree

AOV_NAME = "shader_eval"

# a binding to render, or a callable that hand-wires the native nodes it wraps
Source = pf.ProcNode | Callable[[bpy.types.NodeTree], bpy.types.NodeSocket]

EEVEE = "BLENDER_EEVEE_NEXT"
CYCLES = "CYCLES"

RESOLUTION = 16
COMPARE_RESOLUTION = 32
SAMPLES = 32
INTERIOR = (slice(2, 14), slice(2, 14))
# clear of the quad's triangulation diagonal, which wireframe draws
PROBE = (slice(9, 13), slice(3, 7))

UV_LAYER = "UVMap"
COLOR_LAYER = "Col"
FLOAT_LAYER = "myfloat"

PI = 3.14159265
HALF_PI = PI / 2

HAIR_ROOTS = (-0.6, -0.2, 0.2, 0.6)
HAIR_POINTS = 4
HAIR_RADIUS = 0.15

POINT_POSITIONS = [
    (-0.35, -0.35, 0),
    (0.35, -0.35, 0),
    (0.35, 0.35, 0),
    (-0.35, 0.35, 0),
]
POINT_RADIUS = 0.3

PARTICLE_COUNT = 8
PARTICLE_SIZE = 0.4
PARTICLE_LIFETIME = 100

PLANE_VERTS = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
CUBE_VERTS = [
    (-0.75, -0.75, -0.75),
    (0.75, -0.75, -0.75),
    (0.75, 0.75, -0.75),
    (-0.75, 0.75, -0.75),
    (-0.75, -0.75, 0.75),
    (0.75, -0.75, 0.75),
    (0.75, 0.75, 0.75),
    (-0.75, 0.75, 0.75),
]
CUBE_FACES = [
    (0, 3, 2, 1),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (1, 2, 6, 5),
    (2, 3, 7, 6),
    (3, 0, 4, 7),
]


def _nodegroup(node: pf.ProcNode) -> bpy.types.NodeTree:
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree(node.item()),
        name="shader_eval",
        metadata={"known_value_types": {}},
    )
    return pf.nodes.as_nodegroup(graph, bpy_node_info.NodeGroupType.SHADER)


def _group_socket(
    group_tree: bpy.types.NodeTree, tree: bpy.types.NodeTree
) -> bpy.types.NodeSocket:
    group = tree.nodes.new("ShaderNodeGroup")
    group.node_tree = group_tree
    return group.outputs[0]


def _source(tree: bpy.types.NodeTree, node: Source) -> bpy.types.NodeSocket:
    if callable(node):
        return node(tree)
    return _group_socket(_nodegroup(node), tree)


def _material(node: Source, slot: str) -> bpy.types.Material:
    material = bpy.data.materials.new("shader_eval")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()

    socket = _source(material.node_tree, node)
    output = nodes.new("ShaderNodeOutputMaterial")
    material.node_tree.links.new(socket, output.inputs[slot])
    return material


def _aov_material(node: Source) -> bpy.types.Material:
    material = bpy.data.materials.new("shader_eval")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()

    socket = _source(material.node_tree, node)
    aov = nodes.new("ShaderNodeOutputAOV")
    aov.aov_name = AOV_NAME
    material.node_tree.links.new(socket, aov.inputs["Color"])

    emission = nodes.new("ShaderNodeEmission")
    output = nodes.new("ShaderNodeOutputMaterial")
    emission.inputs["Color"].default_value = (0, 0, 0, 1)
    material.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def _emission_material(node: Source) -> bpy.types.Material:
    def emission(tree: bpy.types.NodeTree) -> bpy.types.NodeSocket:
        shader = tree.nodes.new("ShaderNodeEmission")
        tree.links.new(_source(tree, node), shader.inputs["Color"])
        return shader.outputs[0]

    return _material(emission, "Surface")


def _configure_aov(scene: bpy.types.Scene) -> None:
    active_scene = bpy.context.window.scene
    try:
        bpy.context.window.scene = scene
        aov = scene.view_layers[0].aovs.add()
        aov.name = AOV_NAME
        aov.type = "COLOR"

        scene.use_nodes = True
        nodes = scene.node_tree.nodes
        nodes.clear()
        render_layers = nodes.new("CompositorNodeRLayers")
        composite = nodes.new("CompositorNodeComposite")
        scene.node_tree.links.new(
            render_layers.outputs[AOV_NAME], composite.inputs["Image"]
        )
    finally:
        bpy.context.window.scene = active_scene


def _scene(
    engine: str,
    world: tuple[float, float, float] = (0, 0, 0),
    resolution: int = RESOLUTION,
) -> bpy.types.Scene:
    scene = bpy.data.scenes.new("shader_eval")

    camera_data = bpy.data.cameras.new("shader_eval")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 2
    camera = bpy.data.objects.new("shader_eval", camera_data)
    camera.location.z = 4
    scene.collection.objects.link(camera)
    scene.camera = camera

    light_data = bpy.data.lights.new("shader_eval", type="SUN")
    light_data.energy = 1.0
    light_data.angle = 0.0
    light = bpy.data.objects.new("shader_eval", light_data)
    light.location.z = 5
    scene.collection.objects.link(light)

    world_data = bpy.data.worlds.new("shader_eval")
    world_data.use_nodes = False
    world_data.color = world
    scene.world = world_data

    scene.render.engine = engine
    if engine == CYCLES:
        scene.cycles.device = "CPU"
        scene.cycles.samples = SAMPLES
        scene.cycles.use_denoising = False
        scene.cycles.seed = 0
        # a wider reconstruction filter would bleed neighbouring pixels into the probe
        scene.cycles.pixel_filter_type = "BOX"
        scene.cycles.filter_width = 1.0
    else:
        scene.eevee.taa_render_samples = 1
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    return scene


def probe_plane(scene: bpy.types.Scene) -> bpy.types.Object:
    # the UV, color and float attributes make geometry-context bindings observable
    mesh = bpy.data.meshes.new("shader_eval")
    mesh.from_pydata(PLANE_VERTS, [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name=UV_LAYER)
    for i, co in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = co

    colors = mesh.color_attributes.new(COLOR_LAYER, "FLOAT_COLOR", "POINT")
    for i, color in enumerate([(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1)]):
        colors.data[i].color = color

    values = mesh.attributes.new(FLOAT_LAYER, "FLOAT", "POINT")
    values.data.foreach_set("value", [0.0, 0.25, 0.5, 1.0])

    obj = bpy.data.objects.new("shader_eval", mesh)
    scene.collection.objects.link(obj)
    return obj


def render_scene(scene: bpy.types.Scene) -> np.ndarray:
    with bpy.context.temp_override(scene=scene), tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "shader.exr"
        scene.render.filepath = str(path.with_suffix(""))
        bpy.ops.render.render(scene=scene.name, write_still=True)
        image = bpy.data.images.load(str(path), check_existing=False)
        buf = np.empty(image.size[0] * image.size[1] * image.channels, dtype=np.float32)
        image.pixels.foreach_get(buf)
        arr = buf.reshape(image.size[1], image.size[0], image.channels).copy()
        bpy.data.images.remove(image)
    return arr[..., :3]


def render(node: Source, engine: str = CYCLES) -> np.ndarray:
    """Value output routed through an AOV, so it is read back unclamped."""
    scene = _scene(engine)
    _configure_aov(scene)
    probe_plane(scene).data.materials.append(_aov_material(node))
    return render_scene(scene)


def render_nodegroup(
    group_tree: bpy.types.NodeTree,
    engine: str = CYCLES,
    resolution: int = COMPARE_RESOLUTION,
) -> np.ndarray:
    """Render an existing group at finer resolution for spatial comparisons."""
    scene = _scene(engine, resolution=resolution)
    _configure_aov(scene)
    material = _aov_material(functools.partial(_group_socket, group_tree))
    probe_plane(scene).data.materials.append(material)
    return render_scene(scene)


def render_emission(node: Source, engine: str = CYCLES) -> np.ndarray:
    scene = _scene(engine)
    probe_plane(scene).data.materials.append(_emission_material(node))
    return render_scene(scene)


def render_shader(
    node: Source,
    world: tuple[float, float, float] = (0, 0, 0),
    engine: str = CYCLES,
) -> np.ndarray:
    scene = _scene(engine, world)
    probe_plane(scene).data.materials.append(_material(node, "Surface"))
    return render_scene(scene)


def render_backlit(node: Source) -> np.ndarray:
    """The sun moved below the plane, so only transmitted light reaches the camera."""
    scene = _scene(CYCLES)
    sun = next(obj for obj in scene.objects if obj.type == "LIGHT")
    sun.location.z = -5
    sun.rotation_euler = (PI, 0, 0)
    probe_plane(scene).data.materials.append(_material(node, "Surface"))
    return render_scene(scene)


def render_cube(
    node: Source, world: tuple[float, float, float] = (0.2, 0.2, 0.2)
) -> np.ndarray:
    """A tilted cube, so the shading of real edges and corners is visible."""
    scene = _scene(CYCLES, world)
    mesh = bpy.data.meshes.new("shader_eval_cube")
    mesh.from_pydata(CUBE_VERTS, [], CUBE_FACES)
    mesh.update()

    cube = bpy.data.objects.new("shader_eval_cube", mesh)
    cube.rotation_euler = (0.5, 0.6, 0.0)
    scene.collection.objects.link(cube)
    mesh.materials.append(_material(node, "Surface"))
    return render_scene(scene)


def render_volume(
    node: Source, world: tuple[float, float, float] = (0, 0, 0)
) -> np.ndarray:
    scene = _scene(CYCLES, world)
    mesh = bpy.data.meshes.new("shader_eval")
    mesh.from_pydata(CUBE_VERTS, [], CUBE_FACES)
    mesh.update()

    cube = bpy.data.objects.new("shader_eval", mesh)
    scene.collection.objects.link(cube)
    cube.data.materials.append(_material(node, "Volume"))
    return render_scene(scene)


def render_displacement(node: Source) -> np.ndarray:
    """True displacement is Cycles-only, and only moves the silhouette when the
    camera is oblique and the surface is subdivided finely enough to follow it."""
    scene = _scene(CYCLES)
    scene.camera.location = (0, -4, 1)
    scene.camera.rotation_euler = (1.2, 0, 0)

    plane = probe_plane(scene)
    subsurf = plane.modifiers.new("subsurf", "SUBSURF")
    subsurf.render_levels = 3

    material = _material(node, "Displacement")
    material.displacement_method = "DISPLACEMENT"
    tree = material.node_tree
    emission = tree.nodes.new("ShaderNodeEmission")
    tree.links.new(emission.outputs[0], tree.nodes["Material Output"].inputs["Surface"])
    plane.data.materials.append(material)
    return render_scene(scene)


def render_hair(node: Source, slot: str = "Surface") -> np.ndarray:
    """Four vertical strands filling the frame, lit and viewed along -Y so the
    hair BSDFs' forward-scattering lobes reach the camera."""
    scene = _scene(CYCLES)
    scene.camera.location = (0, -4, 0)
    scene.camera.rotation_euler = (HALF_PI, 0, 0)
    sun = next(obj for obj in scene.objects if obj.type == "LIGHT")
    sun.location = (0, -5, 0)
    sun.rotation_euler = (HALF_PI, 0, 0)

    curves = bpy.data.hair_curves.new("shader_eval")
    curves.add_curves([HAIR_POINTS] * len(HAIR_ROOTS))
    positions = []
    for x in HAIR_ROOTS:
        positions += [c for i in range(HAIR_POINTS) for c in (x, 0.0, -0.6 + i * 0.4)]
    curves.attributes["position"].data.foreach_set("vector", positions)
    radius = curves.attributes.new("radius", "FLOAT", "POINT")
    radius.data.foreach_set("value", [HAIR_RADIUS] * HAIR_POINTS * len(HAIR_ROOTS))

    obj = bpy.data.objects.new("hair", curves)
    scene.collection.objects.link(obj)
    curves.materials.append(_material(node, slot))
    return render_scene(scene)


def render_points(node: Source) -> np.ndarray:
    """A Mesh to Points modifier is the only route to a point cloud from Python;
    bpy.data.pointclouds offers no way to add points."""
    scene = _scene(CYCLES)
    mesh = bpy.data.meshes.new("shader_eval_points")
    mesh.from_pydata(POINT_POSITIONS, [], [])
    mesh.update()
    obj = bpy.data.objects.new("shader_eval_points", mesh)
    scene.collection.objects.link(obj)

    tree = bpy.data.node_groups.new("shader_eval_points", "GeometryNodeTree")
    tree.interface.new_socket(
        "Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    tree.interface.new_socket(
        "Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )
    group_input = tree.nodes.new("NodeGroupInput")
    group_output = tree.nodes.new("NodeGroupOutput")
    to_points = tree.nodes.new("GeometryNodeMeshToPoints")
    to_points.inputs["Radius"].default_value = POINT_RADIUS
    set_material = tree.nodes.new("GeometryNodeSetMaterial")
    set_material.inputs["Material"].default_value = _emission_material(node)
    tree.links.new(group_input.outputs[0], to_points.inputs["Mesh"])
    tree.links.new(to_points.outputs[0], set_material.inputs["Geometry"])
    tree.links.new(set_material.outputs[0], group_output.inputs[0])

    modifier = obj.modifiers.new("points", "NODES")
    modifier.node_group = tree
    return render_scene(scene)


def render_particles(node: Source, frame: int = 1) -> np.ndarray:
    """The probe plane emits cubes whose material reads the particle attributes."""
    scene = _scene(CYCLES)
    emitter = probe_plane(scene)

    mesh = bpy.data.meshes.new("shader_eval_instance")
    mesh.from_pydata(CUBE_VERTS, [], CUBE_FACES)
    mesh.update()
    mesh.materials.append(_emission_material(node))
    instance = bpy.data.objects.new("shader_eval_instance", mesh)
    instance.hide_render = True
    scene.collection.objects.link(instance)

    emitter.modifiers.new("particles", "PARTICLE_SYSTEM")
    settings = emitter.particle_systems[0].settings
    settings.count = PARTICLE_COUNT
    settings.frame_start = 1
    settings.frame_end = 1
    settings.lifetime = PARTICLE_LIFETIME
    settings.physics_type = "NO"
    settings.render_type = "OBJECT"
    settings.instance_object = instance
    settings.particle_size = PARTICLE_SIZE
    scene.frame_set(frame)
    return render_scene(scene)


def constant_vector(x: float, y: float, z: float) -> pf.ProcNode:
    """A literal vector wired into a texture node's Vector does not survive Cycles,
    which folds the constant subgraph away and then substitutes the generated
    coordinate for the input it now sees as unconnected. A 1x1 image lookup holds
    the same value and cannot be folded."""
    raw = bpy.data.images.new("shader_eval", 1, 1, alpha=False, float_buffer=True)
    raw.colorspace_settings.name = "Non-Color"
    raw.pixels.foreach_set((x, y, z, 1.0))
    raw.update()
    return pf.nodes.texture.image(
        pf.nodes.shader.coord().generated, pf.Image(raw), interpolation="Closest"
    ).color


def probe(frame: np.ndarray) -> np.ndarray:
    return frame[PROBE].reshape(-1, 3).mean(axis=0)


def uv_grid() -> np.ndarray:
    """The UV the probe plane presents at each pixel centre, for analytic
    comparison against anything that reads texture coordinates."""
    axis = (np.arange(RESOLUTION) + 0.5) / RESOLUTION
    u, v = np.meshgrid(axis, axis)
    return np.stack([u, v, np.zeros_like(u)], axis=-1).astype(np.float32)


def assert_value(
    frame: np.ndarray, expected: float | tuple[float, float, float]
) -> None:
    expected_arr = np.broadcast_to(np.asarray(expected, dtype=np.float32), (3,))
    np.testing.assert_allclose(probe(frame), expected_arr, atol=3e-4, rtol=1e-3)


def assert_image(actual: np.ndarray, expected: np.ndarray, atol: float = 1e-6) -> None:
    assert np.isfinite(expected).all()
    assert np.abs(expected).max() > 0
    np.testing.assert_allclose(actual, expected, atol=atol)


def assert_varies(frame: np.ndarray, threshold: float = 1e-3) -> None:
    assert frame[INTERIOR].std(axis=(0, 1)).max() > threshold


def assert_differs(a: np.ndarray, b: np.ndarray, threshold: float = 1e-4) -> None:
    assert np.abs(a - b).max() > threshold
