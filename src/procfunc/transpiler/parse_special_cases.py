import inspect
import logging
from typing import Any, Callable

import bpy
import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc import context
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


TEXTURE_MAPPING_ATTRS = ("texture_mapping", "color_mapping")

# the TexMapping fields procfunc rebuilds as nodes; `mapping` is legacy and dead
TEXTURE_MAPPING_DEFAULTS = {
    "vector_type": "POINT",
    "translation": (0.0, 0.0, 0.0),
    "rotation": (0.0, 0.0, 0.0),
    "scale": (1.0, 1.0, 1.0),
    "mapping_x": "X",
    "mapping_y": "Y",
    "mapping_z": "Z",
}

# EEVEE clamps the mapped coordinate to these, Cycles ignores them, so no chain
# of nodes reproduces the original in both engines
TEXTURE_MAPPING_CLAMP_DEFAULTS = {"use_min": False, "use_max": False}

# what Blender substitutes into an unlinked Vector, which the mapping applies to
IMPLICIT_TEXTURE_COORDINATES = {
    "ShaderNodeTexBrick": ("coord", "generated"),
    "ShaderNodeTexChecker": ("coord", "generated"),
    "ShaderNodeTexGradient": ("coord", "generated"),
    "ShaderNodeTexMagic": ("coord", "generated"),
    "ShaderNodeTexNoise": ("coord", "generated"),
    "ShaderNodeTexVoronoi": ("coord", "generated"),
    "ShaderNodeTexWave": ("coord", "generated"),
    "ShaderNodeTexImage": ("coord", "uv"),
    "ShaderNodeTexEnvironment": ("geometry", "position"),
}

MAPPING_FUNCTION_NAMES = {
    "POINT": "mapping",
    "TEXTURE": "mapping_texture",
    "VECTOR": "mapping_vector",
    "NORMAL": "mapping_normal",
}


def changed_mapping_fields(
    mapping: bpy.types.TexMapping, defaults: dict[str, Any]
) -> list[str]:
    changed = []
    for attr, default in defaults.items():
        value = getattr(mapping, attr)
        if isinstance(default, (str, bool)) and value != default:
            changed.append(f"{attr}={value!r}")
        elif not isinstance(default, (str, bool)) and not np.allclose(value, default):
            changed.append(f"{attr}={tuple(value)}")
    return changed


def report_dropped_attrs(message: str) -> None:
    mode = context.globals.warn_mode_transpile_dropped_attrs
    if mode == "throw":
        raise ValueError(message)
    if mode == "warn":
        logger.warning(message)


def texture_mapping_vector(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    vector: Any,
) -> Any:
    """ShaderNodeTex* fold an affine transform of the texture coordinate into the
    node itself. procfunc has no field for it, so it becomes the Combine XYZ and
    Mapping nodes it is equivalent to, in front of the texture. Only shader trees
    evaluate texture_mapping at all; geometry nodes ignore it."""
    mapping = getattr(node, "texture_mapping", None)
    if mapping is None or node_tree.bl_idname != "ShaderNodeTree":
        return vector

    clamped = changed_mapping_fields(mapping, TEXTURE_MAPPING_CLAMP_DEFAULTS)
    if clamped:
        report_dropped_attrs(
            f"{node.name!r} ({node.bl_idname}) has a texture_mapping clamp "
            f"({', '.join(clamped)}) which EEVEE applies and Cycles ignores, so "
            "procfunc has no equivalent to emit and the transpiled graph will "
            "render differently under EEVEE. Replace it with explicit Minimum and "
            "Maximum nodes on the Vector input, or set context.globals."
            "warn_mode_transpile_dropped_attrs to 'warn' to transpile it anyway."
        )

    if not changed_mapping_fields(mapping, TEXTURE_MAPPING_DEFAULTS):
        return vector

    if vector is None:
        source, attribute = IMPLICIT_TEXTURE_COORDINATES[node.bl_idname]
        vector = cg.GetAttributeNode(
            source=cg.FunctionCallNode(
                func=getattr(pf.nodes.shader, source), args=(), kwargs={}
            ),
            attribute_name=attribute,
        )

    axes = (mapping.mapping_x, mapping.mapping_y, mapping.mapping_z)
    if axes != ("X", "Y", "Z"):
        components = [
            0.0
            if axis == "NONE"
            else cg.GetAttributeNode(source=vector, attribute_name=axis.lower())
            for axis in axes
        ]
        vector = cg.FunctionCallNode(
            func=pf.nodes.math.combine_xyz, args=tuple(components), kwargs={}
        )

    kwargs = {
        "vector": vector,
        "rotation": tuple(mapping.rotation),
        "scale": tuple(mapping.scale),
    }
    if mapping.vector_type in ("POINT", "TEXTURE"):
        kwargs["location"] = tuple(mapping.translation)
    func = getattr(pf.nodes.shader, MAPPING_FUNCTION_NAMES[mapping.vector_type])
    return cg.FunctionCallNode(func=func, args=(), kwargs=kwargs)


def handle_specialcase_texture_mapping(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    attrs = {k: v for k, v in attrs.items() if k not in TEXTURE_MAPPING_ATTRS}
    kwargs = {**generic_attrs(node_tree, node, attrs, func, func_spec), **inputs}
    kwargs["vector"] = texture_mapping_vector(node_tree, node, kwargs.get("vector"))
    return build_call(node, func, kwargs)


def handle_specialcase_1d_texture(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    attrs = {k: v for k, v in attrs.items() if k not in TEXTURE_MAPPING_ATTRS}
    kwargs = {**generic_attrs(node_tree, node, attrs, func, func_spec), **inputs}
    dims = getattr(node, "noise_dimensions", None) or getattr(
        node, "voronoi_dimensions", None
    )
    if dims == "1D":
        # the Vector socket is disabled, so nothing reads texture_mapping
        kwargs["vector"] = None
    else:
        kwargs["vector"] = texture_mapping_vector(node_tree, node, kwargs.get("vector"))
    return build_call(node, func, kwargs)


def handle_specialcase_sky(
    node_tree: bpy.types.NodeTree,
    node: bpy.types.Node,
    func: Callable,
    func_spec: dict[str, Any],
    inputs: dict[str, Any],
    attrs: dict[str, Any],
) -> cg.Node:
    changed = changed_mapping_fields(
        node.texture_mapping, TEXTURE_MAPPING_DEFAULTS
    ) + changed_mapping_fields(node.texture_mapping, TEXTURE_MAPPING_CLAMP_DEFAULTS)
    if changed and node_tree.bl_idname == "ShaderNodeTree":
        report_dropped_attrs(
            f"{node.name!r} ({node.bl_idname}) has a non-identity texture_mapping "
            f"({', '.join(changed)}), and unlike every other texture node the sky "
            "has no Vector input for procfunc to put an equivalent Mapping node "
            "in front of, so the transpiled graph will render differently. Set "
            "context.globals.warn_mode_transpile_dropped_attrs to 'warn' to "
            "transpile it anyway."
        )
    attrs = {k: v for k, v in attrs.items() if k not in TEXTURE_MAPPING_ATTRS}
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
    # nishita skies also drop the sun attrs the binding cannot reach
    "ShaderNodeTexSky": handle_specialcase_sky,
    # every other ShaderNodeTex* carrying texture_mapping and color_mapping
    "ShaderNodeTexBrick": handle_specialcase_texture_mapping,
    "ShaderNodeTexChecker": handle_specialcase_texture_mapping,
    "ShaderNodeTexEnvironment": handle_specialcase_texture_mapping,
    "ShaderNodeTexGradient": handle_specialcase_texture_mapping,
    "ShaderNodeTexImage": handle_specialcase_texture_mapping,
    "ShaderNodeTexMagic": handle_specialcase_texture_mapping,
    "ShaderNodeTexWave": handle_specialcase_texture_mapping,
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
