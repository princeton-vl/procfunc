import logging
from typing import Any

import bpy

from procfunc import compute_graph as cg
from procfunc.nodes import bpy_node_info as bni
from procfunc.nodes import types as nt

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
    if handle_type != "AUTO":
        raise NotImplementedError(
            f"handle_type={handle_type!r} is not yet supported, only 'AUTO' is implemented"
        )
    use_clip = attrs.pop("use_clip", True)
    bl_node.mapping.use_clip = use_clip

    if points is None:
        return

    curve = bl_node.mapping.curves[0]

    # Add new points if needed (starts with 2 by default)
    if len(points) > 2:
        for _ in range(len(points) - 2):
            curve.points.new(0, 0)

    # Set positions for all points
    for i, (x, y) in enumerate(points):
        if i < len(curve.points):
            curve.points[i].location = (x, y)


def special_case_rgb_curves(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    """Handle RGB curve nodes with points attribute."""

    curves = attrs.pop("curves", None)
    if curves is None:
        return

    for bl_curve, curve_np in zip(bl_node.mapping.curves, curves):
        while len(bl_curve.points) < len(curve_np):
            bl_curve.points.new(0, 0)

        for i, (x, y) in enumerate(curve_np):
            bl_curve.points[i].location = (x, y)


def special_case_vector_curves(
    bl_node: bpy.types.Node,
    attrs: dict[str, Any],
    **_kwargs,
):
    """Handle vector curve nodes with points attribute."""

    curves = attrs.pop("curves", None)
    if curves is None:
        return

    for bl_curve, curve_np in zip(bl_node.mapping.curves, curves):
        while len(bl_curve.points) < len(curve_np):
            bl_curve.points.new(0, 0)

        for i, (x, y) in enumerate(curve_np):
            bl_curve.points[i].location = (x, y)


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
        elif type(input_val) in bni.PYTHON_TYPE_TO_SOCKET_TYPE:
            soc_type = bni.PYTHON_TYPE_TO_SOCKET_TYPE[type(input_val)]
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


NODE_SPECIAL_CASES = {
    "ShaderNodeValToRGB": special_case_color_ramp,
    "ShaderNodeFloatCurve": special_case_float_curve,
    "ShaderNodeMapRange": special_case_map_range,
    "ShaderNodeRGBCurve": special_case_rgb_curves,
    "ShaderNodeVectorCurve": special_case_vector_curves,
    "CompositorNodeOutputFile": special_case_file_output,
    nt.INPUT_NODE_TYPE: special_case_input,
    "GeometryNodeCaptureAttribute": special_case_capture_attribute,
    "ShaderNodeValue": special_case_value_outputdefault,
    "ShaderNodeRGB": special_case_value_outputdefault,
}
