"""
Math and Vector Math Node bindings for Blender.

Also hosts general-purpose value/vector utilities (mix, map_range,
combine/separate xyz, curves, constant) that work
across shader and geometry trees - they live here rather than in shader.py
or func.py to avoid implying they are specific to those contexts.
"""

from typing import Any, Literal, NamedTuple, TypeVar

import numpy as np

from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import ContextualNode, RuntimeResolveDataType
from procfunc.nodes.bpy_node_info import NodeDataType


def clamp(
    value: nt.SocketOrVal[float],
    min: nt.SocketOrVal[float] = 0.0,
    max: nt.SocketOrVal[float] = 1.0,
    clamp_type: Literal["MINMAX", "RANGE"] = "MINMAX",
) -> nt.ProcNode[float]:
    """
    Uses a Clamp Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/clamp.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeClamp",
        inputs={"Value": value, "Min": min, "Max": max},
        attrs={"clamp_type": clamp_type},
    )


# Math Nodes


def _math(
    a: nt.SocketOrVal[float] = None,
    b: nt.SocketOrVal[float] = None,
    c: nt.SocketOrVal[float] = None,
    operation: str = "ADD",
) -> nt.ProcNode[float]:
    """
    Uses a Math Shader Node.

    Procfunc does NOT support the inline clamp option - use pf.nodes.math.clamp() on the output instead.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/math.html
    """

    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.MATH.value,
        inputs={("Value", 0): a, ("Value", 1): b, ("Value", 2): c},
        attrs={
            "operation": operation,
            "use_clamp": False,  # not supported by procfunc
        },
    )


# Basic Math Operations
def add(a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(a, b, operation="ADD")


def subtract(a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(a, b, operation="SUBTRACT")


def multiply(a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(a, b, operation="MULTIPLY")


def multiply_add(
    a: nt.SocketOrVal[float],
    b: nt.SocketOrVal[float],
    addend: nt.SocketOrVal[float],
) -> nt.ProcNode[float]:
    return _math(a, b, addend, operation="MULTIPLY_ADD")


def divide(
    numerator: nt.SocketOrVal[float], denominator: nt.SocketOrVal[float]
) -> nt.ProcNode[float]:
    return _math(numerator, denominator, operation="DIVIDE")


def power(
    base: nt.SocketOrVal[float], exponent: nt.SocketOrVal[float]
) -> nt.ProcNode[float]:
    return _math(base, exponent, operation="POWER")


def logarithm(
    value: nt.SocketOrVal[float], base: nt.SocketOrVal[float]
) -> nt.ProcNode[float]:
    return _math(value, base, operation="LOGARITHM")


def sqrt(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="SQRT")


def inverse_sqrt(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="INVERSE_SQRT")


def absolute(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="ABSOLUTE")


def exponent(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="EXPONENT")


# Comparison Operations
def minimum(a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(a, b, operation="MINIMUM")


def maximum(a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(a, b, operation="MAXIMUM")


def less_than(a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(a, b, operation="LESS_THAN")


def greater_than(
    a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]
) -> nt.ProcNode[float]:
    return _math(a, b, operation="GREATER_THAN")


def sign(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="SIGN")


def compare(
    a: nt.SocketOrVal[float],
    b: nt.SocketOrVal[float],
    epsilon: nt.SocketOrVal[float] = 0.001,
) -> nt.ProcNode[float]:
    return _math(a, b, epsilon, operation="COMPARE")


def smooth_minimum(
    a: nt.SocketOrVal[float],
    b: nt.SocketOrVal[float],
    distance: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    return _math(a, b, distance, operation="SMOOTH_MIN")


def smooth_maximum(
    a: nt.SocketOrVal[float],
    b: nt.SocketOrVal[float],
    distance: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    return _math(a, b, distance, operation="SMOOTH_MAX")


def round(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="ROUND")


def floor(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="FLOOR")


def ceil(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="CEIL")


def truncate(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="TRUNC")


def fraction(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="FRACT")


def modulo(a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(a, b, operation="MODULO")


def floor_mod(a: nt.SocketOrVal[float], b: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(a, b, operation="FLOORED_MODULO")


def wrap(
    value: nt.SocketOrVal[float],
    max_val: nt.SocketOrVal[float] = 1.0,
    min_val: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    return _math(value, max_val, min_val, operation="WRAP")


def snap(
    value: nt.SocketOrVal[float], increment: nt.SocketOrVal[float] = 1.0
) -> nt.ProcNode[float]:
    return _math(value, increment, operation="SNAP")


def pingpong(
    value: nt.SocketOrVal[float], scale: nt.SocketOrVal[float] = 1.0
) -> nt.ProcNode[float]:
    return _math(value, scale, operation="PINGPONG")


# Trigonometric Operations
def sin(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="SINE")


def cos(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="COSINE")


def tan(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="TANGENT")


def asin(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="ARCSINE")


def acos(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="ARCCOSINE")


def atan(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="ARCTANGENT")


def atan2(y: nt.SocketOrVal[float], x: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(y, x, operation="ARCTAN2")


def sinh(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="SINH")


def cosh(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="COSH")


def tanh(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="TANH")


# Conversion Operations
def deg_to_rad(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="RADIANS")


def rad_to_deg(value: nt.SocketOrVal[float]) -> nt.ProcNode[float]:
    return _math(value, operation="DEGREES")


# Vector Math Operations
def vector_add(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    """Add two vectors."""

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "ADD"},
    )


def vector_subtract(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "SUBTRACT"},
    )


def vector_multiply(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "MULTIPLY"},
    )


def vector_multiply_add(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
    addend: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        attrs={"operation": "MULTIPLY_ADD"},
        inputs={("Vector", 0): a, ("Vector", 1): b, ("Vector", 2): addend},
    )


def vector_divide(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "DIVIDE"},
    )


def vector_cross_product(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "CROSS_PRODUCT"},
    )


def vector_project(
    vector: nt.SocketOrVal[pt.Vector],
    onto: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[float]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector, ("Vector", 1): onto},
        attrs={"operation": "PROJECT"},
    )


def vector_reflect(
    a: nt.SocketOrVal[pt.Vector],
    normal: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): normal},
        attrs={"operation": "REFLECT"},
    )


def vector_refract(
    incident: nt.SocketOrVal[pt.Vector],
    normal: nt.SocketOrVal[pt.Vector],
    ior: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): incident, ("Vector", 1): normal, ("Scale", 2): ior},
        attrs={"operation": "REFRACT"},
    )


def vector_faceforward(
    vector: nt.SocketOrVal[pt.Vector],
    surface: nt.SocketOrVal[pt.Vector],
    normal: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={
            ("Vector", 0): vector,
            ("Vector", 1): surface,
            ("Vector", 2): normal,
        },
        attrs={"operation": "FACEFORWARD"},
    )


def vector_dot_product(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "DOT_PRODUCT"},
    )


def vector_distance(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "DISTANCE"},
    )


def vector_length(vector: nt.SocketOrVal[pt.Vector]) -> nt.ProcNode[float]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "LENGTH"},
    )


def vector_scale(
    vector: nt.SocketOrVal[pt.Vector], scale: nt.SocketOrVal[float]
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector, ("Scale", 0): scale},
        attrs={"operation": "SCALE"},
    )


def vector_normalize(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "NORMALIZE"},
    )


def vector_wrap(
    vector: nt.SocketOrVal[pt.Vector],
    max_val: nt.SocketOrVal[pt.Vector],
    min_val: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector, ("Vector", 1): max_val, ("Vector", 2): min_val},
        attrs={"operation": "WRAP"},
    )


def vector_snap(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "SNAP"},
    )


def vector_floor(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "FLOOR"},
    )


def vector_ceil(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "CEIL"},
    )


def vector_modulo(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "MODULO"},
    )


def vector_fraction(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "FRACTION"},
    )


def vector_round(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "ROUND"},
    )


def vector_truncate(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "TRUNC"},
    )


def vector_absolute(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "ABSOLUTE"},
    )


def vector_minimum(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "MINIMUM"},
    )


def vector_maximum(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "MAXIMUM"},
    )


def vector_sine(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "SINE"},
    )


def vector_cosine(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "COSINE"},
    )


def vector_tangent(
    vector: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "TANGENT"},
    )


def vector_rotate_axis_angle(
    vector: nt.SocketOrVal[pt.Vector],
    center: nt.SocketOrVal[pt.Vector],
    axis: nt.SocketOrVal[pt.Vector],
    angle: nt.SocketOrVal[float],
    invert: bool = False,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a VectorRotate Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/vector_rotate.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorRotate",
        inputs={"Vector": vector, "Center": center, "Axis": axis, "Angle": angle},
        attrs={"invert": invert, "rotation_type": "AXIS_ANGLE"},
    )


def vector_rotate_euler(
    vector: nt.SocketOrVal[pt.Vector],
    center: nt.SocketOrVal[pt.Vector],
    rotation: nt.SocketOrVal[pt.Vector],
    invert: bool = False,
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorRotate",
        inputs={"Vector": vector, "Center": center, "Rotation": rotation},
        attrs={"invert": invert, "rotation_type": "EULER_XYZ"},
    )


# NOTE: mode XYZ have been dropped. transpiler specialcases will map these back to vector_rotate_euler calls.


def vector_transform(
    vector: nt.SocketOrVal[pt.Vector],
    convert_from: Literal["WORLD", "OBJECT", "CAMERA"] = "WORLD",
    convert_to: Literal["WORLD", "OBJECT", "CAMERA"] = "OBJECT",
    vector_type: Literal["POINT", "VECTOR", "NORMAL"] = "VECTOR",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a VectorTransform Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/transform.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorTransform",
        inputs={"Vector": vector},
        attrs={
            "convert_from": convert_from,
            "convert_to": convert_to,
            "vector_type": vector_type,
        },
    )


# ---- Constants / inputs ----------------------------------------------------

TConstant = TypeVar("TConstant", int, float, bool, pt.Vector, pt.Euler, pt.Color)


def constant(
    value: TConstant,
) -> nt.ProcNode[TConstant]:
    """
    Replaces all nodes which just store a constant
    e.g. ShaderNodeValue, ShaderNodeRGB, FunctionNodeInput*, etc
    """
    if isinstance(value, (float, int)):
        return nt.ProcNode.from_nodetype(
            node_type="ShaderNodeValue", inputs={}, attrs={"value": value}
        )
    elif isinstance(value, (pt.Vector, pt.Euler, tuple)):
        x, y, z = value
        return combine_xyz(x=float(x), y=float(y), z=float(z))
    elif isinstance(value, bool):
        return nt.ProcNode.from_nodetype(
            node_type="FunctionNodeBoolean", inputs={}, attrs={"boolean": value}
        )
    elif isinstance(value, pt.Color):
        return nt.ProcNode.from_nodetype(
            node_type="ShaderNodeRGB", inputs={}, attrs={"value": value}
        )
    elif isinstance(value, str):
        return nt.ProcNode.from_nodetype(
            node_type="FunctionNodeInputString", inputs={}, attrs={"value": value}
        )
    else:
        raise ValueError(f"Unsupported constant type: {type(value)}")


# ---- Mix -------------------------------------------------------------------

TMix = TypeVar(
    "TMix",
    nt.SocketOrVal[float],
    nt.SocketOrVal[pt.Vector],
    nt.SocketOrVal[pt.Color],
)


def mix(
    a: TMix,
    b: TMix,
    factor: nt.SocketOrVal[float],
    clamp_factor: bool = True,
    factor_mode: Literal["UNIFORM", "NON_UNIFORM"] = "UNIFORM",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TMix]:
    """
    Uses MixNode to mix float, vector, or color fields with a plain MIX blend.

    For colors, prefer mix_rgb when you need a non-MIX blend mode or clamp_result;
    this function hardcodes blend_type="MIX" and clamp_result=False.
    """

    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.RGBA, NodeDataType.FLOAT, NodeDataType.FLOAT_VECTOR],
            ["A", "B"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeMix",
        inputs={"A": a, "B": b, "Factor": factor},
        attrs={
            "blend_type": "MIX",
            "clamp_factor": clamp_factor,
            "clamp_result": False,
            "factor_mode": factor_mode,
            "data_type": data_type,
        },
    )


# ---- Curves ----------------------------------------------------------------


def float_curve(
    factor: nt.SocketOrVal[float],
    value: nt.SocketOrVal[float],
    curve: np.ndarray | None = None,
    handle_type: str = "AUTO",
    use_clip: bool = True,
) -> nt.ProcNode[float]:
    """
    Uses a FloatCurve Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/float_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeFloatCurve",
        inputs={"Factor": factor, "Value": value},
        attrs={"mapping": curve, "handle_type": handle_type, "use_clip": use_clip},
    )


def vector_curve(
    fac: nt.SocketOrVal[float],
    vector: nt.SocketOrVal[pt.Vector],
    curves: np.ndarray | None = None,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a VectorCurve Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/curves.html
    """
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.VECTOR_CURVE.value,
        inputs={"Fac": fac, "Vector": vector},
        attrs={"curves": curves},
    )


# ---- Combine / Separate ------------------------------------


def combine_xyz(
    x: nt.SocketOrVal[float] = 0.0,
    y: nt.SocketOrVal[float] = 0.0,
    z: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a CombineXYZ Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/combine_xyz.html
    """
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMBINE_XYZ.value,
        inputs={"X": x, "Y": y, "Z": z},
        attrs={},
    )


class SeparateXyzResult(NamedTuple):
    x: nt.ProcNode[float]
    y: nt.ProcNode[float]
    z: nt.ProcNode[float]


def separate_xyz(vector: nt.SocketOrVal[pt.Vector]) -> SeparateXyzResult:
    """
    Uses a SeparateXYZ Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/separate_xyz.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeSeparateXYZ",
        inputs={"Vector": vector},
        attrs={},
    )
    return SeparateXyzResult(
        node._output_socket("x"), node._output_socket("y"), node._output_socket("z")
    )


# ---- MapRange --------------------------------------------------------------


TInterpolationType = Literal["LINEAR", "STEPPED_LINEAR", "SMOOTHSTEP", "SMOOTHERSTEP"]


def map_range(
    value: nt.SocketOrVal[float],
    from_max: nt.SocketOrVal[float] = 1.0,
    from_min: nt.SocketOrVal[float] = 0.0,
    to_max: nt.SocketOrVal[float] = 1.0,
    to_min: nt.SocketOrVal[float] = 0.0,
    clamp: bool = True,
    interpolation_type: TInterpolationType = "LINEAR",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode:
    """
    Uses a MapRange Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/map_range.html
    """

    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.FLOAT, NodeDataType.FLOAT_VECTOR],
            ["From Max", "From Min", "To Max", "To Min", "Value"],
        )

    # interpolation_type / data_type only exist on ShaderNodeMapRange. The
    # wrapper omits interpolation_type at default so a compositor call with
    # all defaults doesn't trip _set_node_attribute. RuntimeResolveDataType
    # is dropped at construct time when the target lacks the attr; an
    # explicit NodeDataType in compositor context will reach setattr and
    # raise naturally.
    attrs: dict[str, Any] = {"clamp": clamp, "data_type": data_type}
    if interpolation_type != "LINEAR":
        attrs["interpolation_type"] = interpolation_type

    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.MAP_RANGE.value,
        inputs={
            "From Max": from_max,
            "From Min": from_min,
            "To Max": to_max,
            "To Min": to_min,
            "Value": value,
        },
        attrs=attrs,
    )
