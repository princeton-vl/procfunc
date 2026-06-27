import logging
from typing import Callable

import bpy
import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes.util import bpy_node_info
from procfunc.transpiler.parse_default_values import normalize_default_value

logger = logging.getLogger(__name__)


def handle_specialcase_math(_node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    if cg_node.kwargs.pop("use_clamp", False):
        # our math funcs wont support inline clamp, so we add an extra node when needed
        cg_node = cg.FunctionCallNode(
            func=pf.nodes.math.clamp, args=(cg_node,), kwargs={}
        )
    return cg_node


def handle_specialcase_color_ramp(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    cg_node.kwargs.pop("color_ramp", None)
    cg_node.kwargs["interpolation"] = node.color_ramp.interpolation
    if node.color_ramp.color_mode != "RGB":
        cg_node.kwargs["mode"] = node.color_ramp.color_mode
        if node.color_ramp.hue_interpolation != "NEAR":
            cg_node.kwargs["hue_interpolation"] = node.color_ramp.hue_interpolation
    cg_node.kwargs["points"] = [
        (round(point.position, 3), tuple(round(x, 3) for x in point.color))
        for point in node.color_ramp.elements
    ]
    return cg_node


def handle_specialcase_value(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    cg_node.kwargs["value"] = normalize_default_value(
        node.outputs[0].default_value, node.outputs[0].type
    )
    return cg_node


def handle_specialcase_input_value(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    attr_name = bpy_node_info.CONSTANT_NODES[node.bl_idname]
    cg_node.kwargs.clear()
    cg_node.kwargs["value"] = normalize_default_value(
        getattr(node, attr_name), node.outputs[0].type
    )
    return cg_node


_ANGLE_ABSENT = object()


def handle_specialcase_vector_rotate(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    angle = cg_node.kwargs.pop("angle", _ANGLE_ABSENT)
    axis_angle = 0.0 if angle is _ANGLE_ABSENT else angle

    match node.rotation_type:
        case "X_AXIS":
            cg_node.kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.math.combine_xyz, args=(axis_angle, 0, 0), kwargs={}
            )
        case "Y_AXIS":
            cg_node.kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.math.combine_xyz, args=(0, axis_angle, 0), kwargs={}
            )
        case "Z_AXIS":
            cg_node.kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.math.combine_xyz, args=(0, 0, axis_angle), kwargs={}
            )
        case "AXIS_ANGLE":
            if angle is not _ANGLE_ABSENT:
                cg_node.kwargs["angle"] = angle
        case "EULER_XYZ":
            pass  # Euler-vector rotation, no Angle socket
        case _:
            raise ValueError(f"Unknown rotation type {node.rotation_type}")

    return cg_node


def handle_specialcase_1d_texture(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    dims = getattr(node, "noise_dimensions", None) or getattr(
        node, "voronoi_dimensions", None
    )
    if dims == "1D":
        cg_node.kwargs["vector"] = None
    return cg_node


SINGLE_CURVE_NODES = {"ShaderNodeFloatCurve"}


def handle_specialcase_curve(node: bpy.types.Node, cg_node: cg.Node) -> cg.Node:
    cg_node.kwargs.pop("mapping", None)

    def _repr_point(point):
        return tuple(round(p, 4) for p in point.location)

    curves = [
        np.array([_repr_point(point) for point in curve.points])
        for curve in node.mapping.curves
    ]
    if node.bl_idname in SINGLE_CURVE_NODES:
        cg_node.kwargs["curve"] = curves[0]
    else:
        cg_node.kwargs["curves"] = curves

    invalid_handle = next(
        (
            point.handle_type
            for point in node.mapping.curves[0].points
            if point.handle_type != "AUTO"
        ),
        None,
    )
    if invalid_handle:
        logger.warning(
            f"{node.name=} had curve handle {invalid_handle=}, currently only AUTO is supported. "
            "Please use a different handle, or contact the developers to add support for it"
        )

    return cg_node


SPECIAL_CASE_NODES: Callable[[bpy.types.Node, cg.Node], cg.Node] = {
    "ShaderNodeMath": handle_specialcase_math,
    "CompositorNodeMath": handle_specialcase_math,
    "TextureNodeMath": handle_specialcase_math,
    "ShaderNodeValToRGB": handle_specialcase_color_ramp,
    "CompositorNodeValToRGB": handle_specialcase_color_ramp,
    "ShaderNodeVectorRotate": handle_specialcase_vector_rotate,
    # 1D noise/voronoi need an explicit vector=None (Vector socket is disabled)
    "ShaderNodeTexNoise": handle_specialcase_1d_texture,
    "ShaderNodeTexVoronoi": handle_specialcase_1d_texture,
    "ShaderNodeTexWhiteNoise": handle_specialcase_1d_texture,
    # curves share handler
    "ShaderNodeFloatCurve": handle_specialcase_curve,
    "ShaderNodeRGBCurve": handle_specialcase_curve,
    "CompositorNodeCurveRGB": handle_specialcase_curve,
    "ShaderNodeVectorCurve": handle_specialcase_curve,
    "CompositorNodeCurveVec": handle_specialcase_curve,
    # values with .outputs[0].default_value can share handler
    "ShaderNodeValue": handle_specialcase_value,
    "ShaderNodeRGB": handle_specialcase_value,
    "CompositorNodeValue": handle_specialcase_value,
    "CompositorNodeRGB": handle_specialcase_value,
    # FunctionNodeInput* store the constant on a node property, not a socket
    "FunctionNodeInputInt": handle_specialcase_input_value,
    "FunctionNodeInputVector": handle_specialcase_input_value,
    "FunctionNodeInputColor": handle_specialcase_input_value,
    "FunctionNodeInputBool": handle_specialcase_input_value,
    "FunctionNodeInputRotation": handle_specialcase_input_value,
    "FunctionNodeInputString": handle_specialcase_input_value,
}
