import inspect
import logging
from typing import Any, Callable

import bpy
import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes.util import bpy_node_info
from procfunc.transpiler.parse_attrs import generic_attrs
from procfunc.transpiler.parse_default_values import normalize_default_value

logger = logging.getLogger(__name__)


def build_call(
    node: bpy.types.Node,
    func: Callable,
    kwargs: dict[str, Any],
) -> cg.FunctionCallNode:
    signature = inspect.signature(func)
    has_var_keyword = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values()
    )
    excess_kwargs = set(kwargs.keys()) - set(signature.parameters.keys())
    if excess_kwargs and not has_var_keyword:
        node_mode = getattr(node, "mode", None)
        node_operation = getattr(node, "operation", None)
        node_data_type = getattr(node, "data_type", None)
        raise ValueError(
            f"Codegen would attempt to call {func.__name__=} with {excess_kwargs} "
            f"but these attributes do not exist in the procfunc signature, which had {list(signature.parameters.keys())} "
            f"source node had {node.bl_idname} {node.inputs.keys()=} {node_mode=} {node_operation=} {node_data_type=} "
            "Please contact the developers."
        )
    return cg.FunctionCallNode(func=func, args=(), kwargs=kwargs)


def handle_specialcase_math(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    kwargs = {**generic_attrs(node_tree, node, attrs, func, func_spec), **inputs}
    use_clamp = kwargs.pop("use_clamp", False)
    cg_node = build_call(node, func, kwargs)
    if use_clamp:
        # our math funcs wont support inline clamp, so we add an extra node when needed
        cg_node = cg.FunctionCallNode(
            func=pf.nodes.math.clamp, args=(cg_node,), kwargs={}
        )
    return cg_node


def handle_specialcase_color_ramp(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    kwargs = dict(inputs)
    kwargs["interpolation"] = node.color_ramp.interpolation
    if node.color_ramp.color_mode != "RGB":
        kwargs["mode"] = node.color_ramp.color_mode
        if node.color_ramp.hue_interpolation != "NEAR":
            kwargs["hue_interpolation"] = node.color_ramp.hue_interpolation
    kwargs["points"] = [
        (round(point.position, 3), tuple(round(x, 3) for x in point.color))
        for point in node.color_ramp.elements
    ]
    return build_call(node, func, kwargs)


def handle_specialcase_value(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    kwargs = {**generic_attrs(node_tree, node, attrs, func, func_spec), **inputs}
    kwargs["value"] = normalize_default_value(
        node.outputs[0].default_value, node.outputs[0].type
    )
    return build_call(node, func, kwargs)


def handle_specialcase_input_value(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    attr_name = bpy_node_info.CONSTANT_NODES[node.bl_idname]
    value = normalize_default_value(getattr(node, attr_name), node.outputs[0].type)
    return build_call(node, func, {"value": value})


_ANGLE_ABSENT = object()


def handle_specialcase_vector_rotate(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    kwargs = {**generic_attrs(node_tree, node, attrs, func, func_spec), **inputs}
    angle = kwargs.pop("angle", _ANGLE_ABSENT)
    axis_angle = 0.0 if angle is _ANGLE_ABSENT else angle

    match node.rotation_type:
        case "X_AXIS":
            kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.math.combine_xyz, args=(axis_angle, 0, 0), kwargs={}
            )
        case "Y_AXIS":
            kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.math.combine_xyz, args=(0, axis_angle, 0), kwargs={}
            )
        case "Z_AXIS":
            kwargs["rotation"] = cg.FunctionCallNode(
                pf.nodes.math.combine_xyz, args=(0, 0, axis_angle), kwargs={}
            )
        case "AXIS_ANGLE":
            if angle is not _ANGLE_ABSENT:
                kwargs["angle"] = angle
        case "EULER_XYZ":
            pass  # Euler-vector rotation, no Angle socket
        case _:
            raise ValueError(f"Unknown rotation type {node.rotation_type}")

    return build_call(node, func, kwargs)


def handle_specialcase_1d_texture(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    kwargs = {**generic_attrs(node_tree, node, attrs, func, func_spec), **inputs}
    dims = getattr(node, "noise_dimensions", None) or getattr(
        node, "voronoi_dimensions", None
    )
    if dims == "1D":
        kwargs["vector"] = None
    return build_call(node, func, kwargs)


def handle_specialcase_sky(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    kwargs = {**generic_attrs(node_tree, node, attrs, func, func_spec), **inputs}
    if node.sky_type == "NISHITA" and not node.sun_disc:
        for name in ("sun_elevation", "sun_intensity", "sun_rotation", "sun_size"):
            kwargs.pop(name, None)
    return build_call(node, func, kwargs)


SINGLE_CURVE_NODES = {"ShaderNodeFloatCurve"}


def handle_specialcase_curve(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    kwargs = dict(inputs)

    def _repr_point(point):
        return tuple(round(p, 4) for p in point.location)

    curves = [
        np.array([_repr_point(point) for point in curve.points])
        for curve in node.mapping.curves
    ]
    if node.bl_idname in SINGLE_CURVE_NODES:
        kwargs["curve"] = curves[0]
    else:
        kwargs["curves"] = curves

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

    return build_call(node, func, kwargs)


SpecialCaseHandler = Callable[
    [
        bpy.types.NodeTree,
        bpy.types.Node,
        Callable,
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
    ],
    cg.Node,
]

SPECIAL_CASE_NODES: dict[str, SpecialCaseHandler] = {
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
    "ShaderNodeTexSky": handle_specialcase_sky,
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
