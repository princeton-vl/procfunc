import logging
from numbers import Real
from typing import Any

import bpy
import numpy as np

from procfunc import compute_graph as cg
from procfunc import types as pt
from procfunc.nodes import func as pf_func
from procfunc.nodes import types as nt
from procfunc.nodes.util import bpy_node_info as bni

from .util import assign_default_value

logger = logging.getLogger(__name__)


def special_case_color_ramp(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    color_ramp = bl_node.color_ramp  # colorramp actually starts with 2 elements already
    color_ramp.interpolation = attrs.pop("interpolation", "LINEAR")
    color_ramp.color_mode = attrs.pop("color_mode", "RGB")
    color_ramp.hue_interpolation = attrs.pop("hue_interpolation", "NEAR")

    points = attrs.pop("points", None)
    if points is None:
        return

    while len(color_ramp.elements) < len(points):
        color_ramp.elements.new(0)

    # Set positions and colors for all elements
    for i, (position, color) in enumerate(points):
        if i < len(color_ramp.elements):
            color_ramp.elements[i].position = position
            if len(color) == 3:
                color_ramp.elements[i].color = (color[0], color[1], color[2], 1.0)
            else:
                color_ramp.elements[i].color = color


def special_case_float_curve(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    """Handle float curve nodes with points attribute."""
    points = attrs.pop("mapping", None)
    handle_type = attrs.pop("handle_type", "AUTO")
    handle_types = attrs.pop("handle_types", None)
    use_clip = attrs.pop("use_clip", True)
    bl_node.mapping.use_clip = use_clip

    if handle_types is not None and handle_type != "AUTO":
        raise ValueError(
            "handle_types cannot be combined with a non-default handle_type"
        )
    if handle_types is None and handle_type != "AUTO":
        point_count = (
            len(points) if points is not None else len(bl_node.mapping.curves[0].points)
        )
        handle_types = [handle_type] * point_count

    curves = None if points is None else [points]
    nested_handles = None if handle_types is None else [handle_types]
    _apply_curves(bl_node, curves, nested_handles)


def _apply_curves(
    bl_node: bpy.types.Node,
    curves: list[np.ndarray] | np.ndarray | None,
    handle_types: list[list[nt.HandleType]] | None = None,
) -> None:
    if curves is None and handle_types is None:
        return
    if curves is None:
        curves = [
            np.array([tuple(point.location) for point in curve.points])
            for curve in bl_node.mapping.curves
        ]

    # Accept either list[np.ndarray] or a single stacked ndarray of shape
    # (n_curves, n_points, 2); both iterate per-curve on the outer dim.
    if len(curves) != len(bl_node.mapping.curves):
        raise ValueError(
            f"{bl_node.bl_idname} expects {len(bl_node.mapping.curves)} curves, "
            f"got {len(curves)}"
        )
    if handle_types is None:
        handle_types = [["AUTO"] * len(curve_np) for curve_np in curves]
    if len(handle_types) != len(curves):
        raise ValueError(
            f"{bl_node.bl_idname} expects handles for {len(curves)} curves, "
            f"got {len(handle_types)}"
        )
    point_counts = [len(curve_np) for curve_np in curves]
    handle_counts = [len(curve_handles) for curve_handles in handle_types]
    if handle_counts != point_counts:
        raise ValueError(
            f"{bl_node.bl_idname} has {point_counts} points per curve "
            f"but {handle_counts} handles per curve"
        )
    for bl_curve, curve_np, curve_handles in zip(
        bl_node.mapping.curves, curves, handle_types, strict=True
    ):
        while len(bl_curve.points) < len(curve_np):
            bl_curve.points.new(0, 0)
        while len(bl_curve.points) > len(curve_np):
            bl_curve.points.remove(bl_curve.points[-1])
        for i, (x, y) in enumerate(curve_np):
            bl_curve.points[i].location = (x, y)
            bl_curve.points[i].handle_type = curve_handles[i]
    # Without update(), Blender keeps the default identity LUT and ignores
    # the points we just assigned during geo/shader node evaluation.
    bl_node.mapping.update()


def special_case_rgb_curves(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    """Handle RGB curve nodes with points attribute."""

    curves = attrs.pop("curves", None)
    handle_types = attrs.pop("handle_types", None)
    _apply_curves(bl_node, curves, handle_types)


def special_case_vector_curves(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    """Handle vector curve nodes with points attribute."""

    curves = attrs.pop("curves", None)
    handle_types = attrs.pop("handle_types", None)
    _apply_curves(bl_node, curves, handle_types)


def special_case_hue_correct(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    curves = attrs.pop("curves", None)
    handle_types = attrs.pop("handle_types", None)
    _apply_curves(bl_node, curves, handle_types)


IMAGE_USER_ATTRS = (
    "frame_duration",
    "frame_offset",
    "frame_start",
    "tile",
    "use_auto_refresh",
    "use_cyclic",
    "frame_current",
)


def special_case_image_user(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    """ShaderNodeTexImage and ShaderNodeTexEnvironment keep their sequence and UDIM
    settings on an ImageUser sub-struct rather than on the node itself."""

    image = attrs.pop("image", None)
    if image is not None:
        bl_node.image = image.item() if isinstance(image, pt.BlenderAsset) else image

    for name in IMAGE_USER_ATTRS:
        value = attrs.pop(name, None)
        if value is not None:
            setattr(bl_node.image_user, name, value)


def special_case_compositor_vector_curves(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    inputs: dict[str, Any],
    kwargs: dict[str, Any],
    **_kwargs,
):
    """CompositorNodeCurveVec has no Fac socket and always applies the curve
    fully, so `fac` is accepted only at its no-op value 1.0."""

    fac = inputs.get("Fac", 1.0)
    wired = isinstance(fac, (bpy.types.NodeSocket, bpy.types.NodeInternal))
    if wired or fac != 1.0:
        raise ValueError(
            f"CompositorNodeCurveVec has no Fac socket; fac={fac!r} cannot be "
            "honored (only the no-op 1.0). Synthesizing a mix node would be "
            "needed to support this."
        )
    inputs.pop("Fac", None)
    kwargs.pop("Fac", None)
    special_case_vector_curves(bl_node=bl_node, attrs=attrs)


def special_case_texture_mix_rgb(
    attrs: dict[str, Any],
    **_kwargs,
):
    """TextureNodeMixRGB has no clamp_factor attr and unconditionally clamps
    its factor to [0, 1] (verified via Texture.evaluate: factor 2.0 / -1.0
    behave as 1.0 / 0.0), so only clamp_factor=True is representable."""

    if not attrs.pop("clamp_factor", True):
        raise ValueError(
            "TextureNodeMixRGB always clamps its factor; clamp_factor=False "
            "cannot be honored. Synthesizing extra nodes would be needed to "
            "support this."
        )


def special_case_file_output(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    inputs: dict[str, Any],
    **_kwargs,
):
    assert bl_node.bl_idname == "CompositorNodeOutputFile"

    bl_node.file_slots.clear()
    for k in inputs.keys():
        if k == 0 or k in attrs:
            continue
        bl_node.file_slots.new(k)

    if file_format := attrs.pop("format", None):
        for k, v in file_format.items():
            setattr(bl_node.format, k, v)

    if slot_paths := attrs.pop("slot_paths", None):
        for k, v in slot_paths.items():
            bl_node.file_slots[k].path = v


def special_case_input(
    node: nt.ProcNode,
    node_tree: bpy.types.NodeTree,
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    raise NotImplementedError(f"{special_case_input.__name__} is not implemented")

    # TODO node is actually a cg.Node

    if node.type != nt.INPUT_NODE_TYPE:
        raise ValueError(
            f"{special_case_input.__name__} requires {nt.INPUT_NODE_TYPE!r}, got {node.type}"
        )

    socket_types: list[nt.SocketType] = attrs.pop("socket_types")
    defaults: list = attrs.pop("default_values")

    output_sockets = node._output_sockets()

    if output_sockets is None:
        raise ValueError(f"{node=} has no output sockets")

    for name, socket_type, default in zip(output_sockets, socket_types, defaults):
        if name in node_tree.interface.items_tree:
            raise ValueError(f"Socket {name} already exists in {node_tree.name}")
        soc = node_tree.interface.new_socket(
            name=name,
            in_out="INPUT",
            socket_type=socket_type.value,
        )
        data_type = nt.SOCKET_CLASS_TO_DATATYPE[socket_type.value]
        assign_default_value(soc, default, data_type)

        if name not in bl_node.outputs:
            raise ValueError(f"Failed to add {name=} {socket_type=} to {bl_node.name=}")


def special_case_map_range(
    attrs: dict[str, Any],
    kwargs: dict[str, Any],
    inputs: dict[str, Any],
    **_kwargs,
):
    if attrs["data_type"] == bni.NodeDataType.FLOAT_VECTOR.value:
        assert "Value" in inputs, inputs
        inputs["Vector"] = inputs.pop("Value")
        kwargs["Vector"] = kwargs.pop("Value")
        for name, value in inputs.items():
            if isinstance(value, Real):
                inputs[name] = (value, value, value)


def special_case_capture_attribute(
    bl_node: bpy.types.Node,
    inputs: dict[str, Any],
    kwargs: dict[str, Any],
    **_kwargs,
):
    for input_name, input_val in inputs.items():
        if input_name == "Geometry":
            continue

        kwargval = kwargs.get(input_name)
        if isinstance(kwargval, cg.Node) and (
            annot := kwargval.metadata.get("known_value_type")
        ):
            soc_type = bni.PYTHON_TYPE_TO_SOCKET_TYPE[annot]
            data_type = bni.SOCKET_CLASS_TO_DATATYPE[soc_type.value]
        elif isinstance(input_val, bpy.types.NodeSocket):
            data_type = bni.SOCKET_CLASS_TO_DATATYPE[input_val.bl_idname]
        elif (soc_type := bni.value_type_to_socket_type(type(input_val))) is not None:
            data_type = bni.SOCKET_CLASS_TO_DATATYPE[soc_type.value]
        else:
            raise ValueError(f"Could not determine data type for {input_val=}")

        data_type = (
            "VECTOR"  # NodeDataType uses FLOAT_VECTOR here but that seems incorrect for CaptureAttribute??
            if data_type == bni.NodeDataType.FLOAT_VECTOR
            else data_type.value
        )

        try:
            bl_node.capture_items.new(data_type, name=input_name)
        except Exception as e:
            raise ValueError(
                f"Could not add capture item {input_name=} {data_type} to {bl_node.name=}. "
                f"{bl_node.capture_items.keys()=}. {e=}"
            ) from e


def special_case_value_outputdefault(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    value = attrs.pop("value", None)
    if value is not None and hasattr(value, "__len__") and len(value) == 3:
        value = (*value, 1.0)
    bl_node.outputs[0].default_value = value


def special_case_input_constant(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    # FunctionNodeInput* store their constant on a node property (named per
    # CONSTANT_NODES), not on an output socket default like ShaderNodeValue/RGB.
    # Property-named attrs (e.g. from func.input_string) skip this and are
    # applied by the generic attr loop.
    if "value" not in attrs:
        return
    value = attrs.pop("value")
    if bl_node.bl_idname == "FunctionNodeInputColor" and len(value) == 3:
        value = (*value, 1.0)
    setattr(bl_node, bni.CONSTANT_NODES[bl_node.bl_idname], value)


def special_case_compare(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    inputs: dict[str, Any],
    kwargs: dict[str, Any],
    **_kwargs,
):
    for attr_key in ("data_type", "operation"):
        if attr_key in attrs:
            setattr(bl_node, attr_key, attrs[attr_key])

    epsilon_key = ("Epsilon", 0)
    if inputs.get(epsilon_key) != pf_func.COMPARE_EPSILON_DEFAULT:
        return

    epsilon_socket = next((s for s in bl_node.inputs if s.name == "Epsilon"), None)
    if epsilon_socket is not None and not epsilon_socket.enabled:
        inputs.pop(epsilon_key, None)
        kwargs.pop(epsilon_key, None)


def special_case_combine_xyz_constant(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    # A vector/rotation constant lowered to CombineXYZ outside geometry trees;
    # regular combine_xyz nodes carry no "value" attr and pass through untouched.
    if "value" not in attrs:
        return
    value = attrs.pop("value")
    for socket, component in zip(bl_node.inputs, value, strict=True):
        socket.default_value = float(component)


NODE_SPECIAL_CASES = {
    "ShaderNodeValToRGB": special_case_color_ramp,
    "CompositorNodeValToRGB": special_case_color_ramp,
    "ShaderNodeFloatCurve": special_case_float_curve,
    "ShaderNodeMapRange": special_case_map_range,
    "ShaderNodeRGBCurve": special_case_rgb_curves,
    "CompositorNodeCurveRGB": special_case_rgb_curves,
    "ShaderNodeVectorCurve": special_case_vector_curves,
    "CompositorNodeCurveVec": special_case_compositor_vector_curves,
    "CompositorNodeHueCorrect": special_case_hue_correct,
    "ShaderNodeTexImage": special_case_image_user,
    "ShaderNodeTexEnvironment": special_case_image_user,
    "TextureNodeMixRGB": special_case_texture_mix_rgb,
    "CompositorNodeOutputFile": special_case_file_output,
    nt.INPUT_NODE_TYPE: special_case_input,
    "GeometryNodeCaptureAttribute": special_case_capture_attribute,
    "ShaderNodeValue": special_case_value_outputdefault,
    "ShaderNodeRGB": special_case_value_outputdefault,
    "CompositorNodeValue": special_case_value_outputdefault,
    "CompositorNodeRGB": special_case_value_outputdefault,
    "FunctionNodeInputBool": special_case_input_constant,
    "FunctionNodeInputColor": special_case_input_constant,
    "FunctionNodeInputInt": special_case_input_constant,
    "FunctionNodeInputRotation": special_case_input_constant,
    "FunctionNodeInputString": special_case_input_constant,
    "FunctionNodeInputVector": special_case_input_constant,
    "FunctionNodeCompare": special_case_compare,
    "ShaderNodeCombineXYZ": special_case_combine_xyz_constant,
    "CompositorNodeCombineXYZ": special_case_combine_xyz_constant,
}
