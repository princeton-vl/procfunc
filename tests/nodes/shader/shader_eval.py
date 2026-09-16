import tempfile
from pathlib import Path

import bpy
import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes.util import bpy_node_info
from procfunc.util import pytree

AOV_NAME = "shader_eval"


def _nodegroup(node: pf.ProcNode) -> bpy.types.NodeTree:
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree(node.item()),
        name="shader_eval",
        metadata={"known_value_types": {}},
    )
    return pf.nodes.as_nodegroup(graph, bpy_node_info.NodeGroupType.SHADER)


def _material(tree: bpy.types.NodeTree) -> bpy.types.Material:
    material = bpy.data.materials.new("shader_eval")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()

    group = nodes.new("ShaderNodeGroup")
    group.node_tree = tree
    aov = nodes.new("ShaderNodeOutputAOV")
    aov.aov_name = AOV_NAME
    material.node_tree.links.new(group.outputs[0], aov.inputs["Color"])

    emission = nodes.new("ShaderNodeEmission")
    output = nodes.new("ShaderNodeOutputMaterial")
    emission.inputs["Color"].default_value = (0, 0, 0, 1)
    material.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


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


def _scene(material: bpy.types.Material) -> bpy.types.Scene:
    scene = bpy.data.scenes.new("shader_eval")

    mesh = bpy.data.meshes.new("shader_eval")
    mesh.from_pydata(
        [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)],
        [],
        [(0, 1, 2, 3)],
    )
    plane = bpy.data.objects.new("shader_eval", mesh)
    mesh.materials.append(material)
    scene.collection.objects.link(plane)

    camera_data = bpy.data.cameras.new("shader_eval")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 2
    camera = bpy.data.objects.new("shader_eval", camera_data)
    camera.location.z = 1
    scene.collection.objects.link(camera)
    scene.camera = camera

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 1
    scene.render.resolution_x = 4
    scene.render.resolution_y = 4
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    _configure_aov(scene)
    return scene


def render_nodegroup(tree: bpy.types.NodeTree) -> np.ndarray:
    """Every pixel of the plane, as (height, width, rgb). Compare two node groups
    with this rather than with render(), whose single sample is too weak to
    notice most of the ways a texture coordinate can be wrong."""
    scene = _scene(_material(tree))
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "shader.exr"
        scene.render.filepath = str(path.with_suffix(""))
        bpy.ops.render.render(scene=scene.name, write_still=True)
        image = bpy.data.images.load(str(path), check_existing=False)
        buf = np.empty(image.size[0] * image.size[1] * image.channels, dtype=np.float32)
        image.pixels.foreach_get(buf)
        arr = buf.reshape(image.size[1], image.size[0], image.channels).copy()
        bpy.data.images.remove(image)
    return arr[..., :3]


def render(node: pf.ProcNode) -> np.ndarray:
    # (2, 1) sits off the plane's triangulation diagonal, which wireframe draws
    return render_nodegroup(_nodegroup(node))[2, 1]


def assert_value(
    value: np.ndarray, expected: float | tuple[float, float, float]
) -> None:
    expected_arr = np.broadcast_to(np.asarray(expected, dtype=np.float32), (3,))
    np.testing.assert_allclose(value, expected_arr, atol=3e-4, rtol=1e-3)
