"""
Math and Vector Math Node bindings for Blender
"""

from typing import Literal

from procfunc import types as pt
from procfunc.nodes import types as nt


def clamp(
    value: nt.SocketOrVal[float] = 1.0,
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
    value_2: nt.SocketOrVal[float] = None,
    operation: str = "ADD",
) -> nt.ProcNode[float]:
    """
    Uses a Math Shader Node.

    Procfunc does NOT support the inline clamp option - use pf.nodes.math.clamp() on the output instead.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/math.html
    """

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeMath",
        inputs={("Value", 0): a, ("Value", 1): b, ("Value", 2): value_2},
        attrs={
            "operation": operation,
            "use_clamp": False,  # not supported by procfunc
        },
    )


# Basic Math Operations
def add(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="ADD")


def subtract(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="SUBTRACT")


def multiply(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="MULTIPLY")


def multiply_add(
    a: nt.SocketOrVal[float] = 0.5,
    b: nt.SocketOrVal[float] = 0.5,
    addend: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    return _math(a, b, addend, operation="MULTIPLY_ADD")


def divide(
    numerator: nt.SocketOrVal[float] = 0.5, denominator: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(numerator, denominator, operation="DIVIDE")


def power(
    base: nt.SocketOrVal[float] = 0.5, exponent: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(base, exponent, operation="POWER")


def logarithm(
    value: nt.SocketOrVal[float] = 0.5, base: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(value, base, operation="LOGARITHM")


def sqrt(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="SQRT")


def inverse_sqrt(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="INVERSE_SQRT")


def absolute(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="ABSOLUTE")


def exponent(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="EXPONENT")


# Comparison Operations
def minimum(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="MINIMUM")


def maximum(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="MAXIMUM")


def less_than(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="LESS_THAN")


def greater_than(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="GREATER_THAN")


def sign(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="SIGN")


def compare(
    a: nt.SocketOrVal[float] = 0.5,
    b: nt.SocketOrVal[float] = 0.5,
    epsilon: nt.SocketOrVal[float] = 0.001,
) -> nt.ProcNode[float]:
    return _math(a, b, epsilon, operation="COMPARE")


def smooth_minimum(
    a: nt.SocketOrVal[float] = 0.5,
    b: nt.SocketOrVal[float] = 0.5,
    distance: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    return _math(a, b, distance, operation="SMOOTH_MIN")


def smooth_maximum(
    a: nt.SocketOrVal[float] = 0.5,
    b: nt.SocketOrVal[float] = 0.5,
    distance: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    return _math(a, b, distance, operation="SMOOTH_MAX")


def round(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="ROUND")


def floor(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="FLOOR")


def ceil(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="CEIL")


def truncate(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="TRUNC")


def fraction(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="FRACT")


def modulo(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="MODULO")


def floor_mod(
    a: nt.SocketOrVal[float] = 0.5, b: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(a, b, operation="FLOORED_MODULO")


def wrap(
    value: nt.SocketOrVal[float] = 0.5,
    max_val: nt.SocketOrVal[float] = 1.0,
    min_val: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[float]:
    return _math(value, max_val, min_val, operation="WRAP")


def snap(
    value: nt.SocketOrVal[float] = 0.5, increment: nt.SocketOrVal[float] = 1.0
) -> nt.ProcNode[float]:
    return _math(value, increment, operation="SNAP")


def pingpong(
    value: nt.SocketOrVal[float] = 0.5, scale: nt.SocketOrVal[float] = 1.0
) -> nt.ProcNode[float]:
    return _math(value, scale, operation="PINGPONG")


# Trigonometric Operations
def sin(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="SINE")


def cos(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="COSINE")


def tan(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="TANGENT")


def asin(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="ARCSINE")


def acos(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="ARCCOSINE")


def atan(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="ARCTANGENT")


def atan2(
    y: nt.SocketOrVal[float] = 0.5, x: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode[float]:
    return _math(y, x, operation="ARCTAN2")


def sinh(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="SINH")


def cosh(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="COSH")


def tanh(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="TANH")


# Conversion Operations
def deg_to_rad(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="RADIANS")


def rad_to_deg(value: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode[float]:
    return _math(value, operation="DEGREES")


# Vector Math Operations
def vector_add(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    """Add two vectors."""

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "ADD"},
    )


def vector_subtract(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "SUBTRACT"},
    )


def vector_multiply(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "MULTIPLY"},
    )


def vector_multiply_add(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    addend: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        attrs={"operation": "MULTIPLY_ADD"},
        inputs={("Vector", 0): a, ("Vector", 1): b, ("Vector", 2): addend},
    )


def vector_divide(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "DIVIDE"},
    )


def vector_cross_product(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "CROSS_PRODUCT"},
    )


def vector_project(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    onto: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[float]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector, ("Vector", 1): onto},
        attrs={"operation": "PROJECT"},
    )


def vector_reflect(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    normal: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): normal},
        attrs={"operation": "REFLECT"},
    )


def vector_refract(
    incident: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    normal: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    ior: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): incident, ("Vector", 1): normal, ("Scale", 2): ior},
        attrs={"operation": "REFRACT"},
    )


def vector_faceforward(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    surface: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    normal: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
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
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "DOT_PRODUCT"},
    )


def vector_distance(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "DISTANCE"},
    )


def vector_length(vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0)) -> nt.ProcNode[float]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "LENGTH"},
    )


def vector_scale(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0), scale: nt.SocketOrVal[float] = 1.0
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector, ("Scale", 0): scale},
        attrs={"operation": "SCALE"},
    )


def vector_normalize(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "NORMALIZE"},
    )


def vector_wrap(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    max_val: nt.SocketOrVal[pt.Vector] = (1, 1, 1),
    min_val: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector, ("Vector", 1): max_val, ("Vector", 2): min_val},
        attrs={"operation": "WRAP"},
    )


def vector_snap(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (1, 1, 1),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "SNAP"},
    )


def vector_floor(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "FLOOR"},
    )


def vector_ceil(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "CEIL"},
    )


def vector_modulo(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (1, 1, 1),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "MODULO"},
    )


def vector_fraction(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "FRACTION"},
    )


def vector_round(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "ROUND"},
    )


def vector_truncate(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "TRUNC"},
    )


def vector_absolute(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "ABSOLUTE"},
    )


def vector_minimum(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "MINIMUM"},
    )


def vector_maximum(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): a, ("Vector", 1): b},
        attrs={"operation": "MAXIMUM"},
    )


def vector_sine(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "SINE"},
    )


def vector_cosine(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "COSINE"},
    )


def vector_tangent(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorMath",
        inputs={("Vector", 0): vector},
        attrs={"operation": "TANGENT"},
    )


def vector_rotate_axis_angle(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    center: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    axis: nt.SocketOrVal[pt.Vector] = (0, 0, 1),
    angle: nt.SocketOrVal[float] = 0.0,
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
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    center: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    invert: bool = False,
) -> nt.ProcNode[pt.Vector]:
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorRotate",
        inputs={"Vector": vector, "Center": center, "Rotation": rotation},
        attrs={"invert": invert, "rotation_type": "EULER_XYZ"},
    )


# NOTE: mode XYZ have been dropped. transpiler specialcases will map these back to vector_rotate_euler calls.


def vector_transform(
    vector: nt.SocketOrVal[pt.Vector] = (0.5, 0.5, 0.5),
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
