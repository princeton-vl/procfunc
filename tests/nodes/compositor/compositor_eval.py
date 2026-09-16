"""Execute a procfunc compositor tree on dummy input images and read the
resulting pixels back as a numpy array, so compositor bindings can be asserted
on the values they actually compute rather than on the node tree they build.

The compositor only runs during a render, and the Viewer Node image is not
populated in background mode, so `composite_render` renders the scene to a
32-bit OpenEXR and loads that file back. EXR skips the view transform, making
the round trip exact for a passthrough tree.

Arrays are in top-down row order (``arr[0]`` is the top row), the opposite of
bpy's bottom-up image buffers; input and output are flipped consistently, so
axis-sensitive nodes such as ``flip`` and ``translate`` keep their meaning.
"""

import tempfile
import typing
from pathlib import Path

import bpy
import numpy as np

import procfunc as pf


def solid(width: int, height: int, rgba: tuple) -> np.ndarray:
    """An image of one repeated RGBA value."""
    arr = np.empty((height, width, 4), dtype=np.float32)
    arr[...] = np.asarray(rgba, dtype=np.float32)
    return arr


def halves(
    width: int, height: int, left: tuple, right: tuple, axis: str = "x"
) -> np.ndarray:
    """A step edge, for nodes whose effect only shows up across a discontinuity."""
    arr = np.empty((height, width, 4), dtype=np.float32)
    arr[...] = np.asarray(left, dtype=np.float32)
    if axis == "x":
        arr[:, width // 2 :] = np.asarray(right, dtype=np.float32)
    else:
        arr[height // 2 :, :] = np.asarray(right, dtype=np.float32)
    return arr


def ramp(width: int, height: int, low: float, high: float) -> np.ndarray:
    """A horizontal luminance ramp with opaque alpha."""
    row = np.linspace(low, high, width, dtype=np.float32)
    arr = np.empty((height, width, 4), dtype=np.float32)
    arr[..., :3] = row[None, :, None]
    arr[..., 3] = 1.0
    return arr


def image_datablock(name: str, arr: np.ndarray) -> bpy.types.Image:
    """A float RGBA image datablock holding `arr` verbatim, unaffected by color
    management, for use as `pf.nodes.compositor.image(image=...)`."""
    arr = np.ascontiguousarray(np.asarray(arr, dtype=np.float32))
    height, width, _ = arr.shape
    img = bpy.data.images.new(name, width, height, alpha=True, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(np.flipud(arr).ravel())
    img.update()
    return img


def image_node(name: str, arr: np.ndarray):
    """An Image compositor node sourcing `arr`, returning its (image, alpha)."""
    return pf.nodes.compositor.image(image=image_datablock(name, arr))


def movie_clip_datablock(path: Path) -> bpy.types.MovieClip:
    frame = bpy.data.images.new(path.stem, 2, 2, alpha=True)
    frame.filepath_raw = str(path)
    frame.file_format = "PNG"
    frame.save()
    return bpy.data.movieclips.load(str(path))


def ensure_camera(scene: bpy.types.Scene) -> None:
    data = bpy.data.cameras.new("compositor_eval")
    camera = bpy.data.objects.new("compositor_eval", data)
    scene.collection.objects.link(camera)
    scene.camera = camera


def build_compositor(value: typing.Any) -> bpy.types.Scene:
    scene = bpy.data.scenes.new("compositor_eval")
    with bpy.context.temp_override(scene=scene):
        pf.nodes.to_compositor(results={"result": value})
    return scene


def render_scene(scene: bpy.types.Scene, size: tuple = (8, 8)) -> np.ndarray:
    """Render `scene` through its compositor and return the resulting
    (height, width, 4) float array in top-down row order."""
    width, height = size
    ensure_camera(scene)
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.color_mode = "RGBA"

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "composite.exr"
        scene.render.filepath = str(path.with_suffix(""))
        bpy.ops.render.render(write_still=True, scene=scene.name)
        out = bpy.data.images.load(str(path), check_existing=False)
        buf = np.empty(out.size[0] * out.size[1] * out.channels, dtype=np.float32)
        out.pixels.foreach_get(buf)
        arr = buf.reshape(out.size[1], out.size[0], out.channels).copy()
        bpy.data.images.remove(out)
    return np.flipud(arr).copy()


def composite_render(color, size: tuple = (8, 8), alpha=None) -> np.ndarray:
    node = pf.nodes.compositor.composite(image=color, alpha=alpha)
    return render_scene(build_compositor(node), size)


def realized_node(value: typing.Any, bl_idname: str) -> bpy.types.Node:
    """Realize a binding to inspect its Blender inputs and properties."""
    scene = build_compositor(value)
    assert scene.node_tree is not None
    nodes = [node for node in scene.node_tree.nodes if node.bl_idname == bl_idname]
    assert len(nodes) == 1
    return nodes[0]


def composite_source(value: typing.Any) -> tuple[str, str]:
    """Where the composite input comes from, for the outputs that render as
    zero until a movie clip or texture datablock supplies them."""
    result = pf.nodes.compositor.composite(image=value)
    node = realized_node(result, "CompositorNodeComposite")
    link = node.inputs["Image"].links[0]
    return link.from_node.bl_idname, link.from_socket.name


def assert_uniform(arr: np.ndarray, rgba: tuple, tol: float = 1e-4) -> None:
    """Assert every pixel of `arr` equals `rgba`."""
    expected = np.asarray(rgba, dtype=np.float32)
    worst = np.abs(arr - expected).max()
    assert worst <= tol, f"not uniform {rgba}: worst={worst}, corner={arr[0, 0]}"
