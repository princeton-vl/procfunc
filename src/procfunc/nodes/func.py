"""
Auto-generated Function Node bindings for Blender
"""

import logging
from typing import Any, Literal, NamedTuple, TypeVar

import numpy as np

from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import (
    ContextualNode,
    RuntimeResolveDataType,
    raise_io_error,
)
from procfunc.nodes.bpy_node_info import NodeDataType

logger = logging.getLogger(__name__)

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


def align_euler_to_vector(
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    factor: nt.SocketOrVal[float] = 1.0,
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 1),
    axis: Literal["X", "Y", "Z"] = "X",
    pivot_axis: Literal["AUTO", "X", "Y", "Z"] = "AUTO",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a AlignEulerToVector Function Node.

    See: http://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/align_euler_to_vector.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeAlignEulerToVector",
        inputs={"Rotation": rotation, "Factor": factor, "Vector": vector},
        attrs={"axis": axis, "pivot_axis": pivot_axis},
    )


def align_rotation_to_vector(
    rotation: Any = (0, 0, 0),
    factor: nt.SocketOrVal[float] = 1.0,
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 1),
    axis: Literal["X", "Y", "Z"] = "Z",
    pivot_axis: Literal["AUTO", "X", "Y", "Z"] = "AUTO",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a AlignRotationToVector Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/align_rotation_to_vector.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeAlignRotationToVector",
        inputs={"Rotation": rotation, "Factor": factor, "Vector": vector},
        attrs={"axis": axis, "pivot_axis": pivot_axis},
    )


def axes_to_rotation(
    primary_axis_vector: nt.SocketOrVal[pt.Vector] = (0, 0, 1),
    secondary_axis_vector: nt.SocketOrVal[pt.Vector] = (1, 0, 0),
    primary_axis: Literal["X", "Y", "Z"] = "X",
    secondary_axis: Literal["X", "Y", "Z"] = "Y",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a AxesToRotation Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/axis_to_rotation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeAxesToRotation",
        inputs={
            "Primary Axis": primary_axis_vector,
            "Secondary Axis": secondary_axis_vector,
        },
        attrs={"primary_axis": primary_axis, "secondary_axis": secondary_axis},
    )


def axis_angle_to_rotation(
    axis: nt.SocketOrVal[pt.Vector] = (0, 0, 1), angle: nt.SocketOrVal[float] = 0.0
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a AxisAngleToRotation Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/axis_angle_to_rotation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeAxisAngleToRotation",
        inputs={"Axis": axis, "Angle": angle},
        attrs={},
    )


def boolean_or(
    a: nt.SocketOrVal[bool] = False,
    b: nt.SocketOrVal[bool] = False,
) -> nt.ProcNode[bool]:
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeBooleanMath",
        inputs={("Boolean", 0): a, ("Boolean", 1): b},
        attrs={"operation": "OR"},
    )


def boolean_and(
    a: nt.SocketOrVal[bool] = False,
    b: nt.SocketOrVal[bool] = False,
) -> nt.ProcNode[bool]:
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeBooleanMath",
        inputs={("Boolean", 0): a, ("Boolean", 1): b},
        attrs={"operation": "AND"},
    )


def boolean_xor(
    a: nt.SocketOrVal[bool] = False,
    b: nt.SocketOrVal[bool] = False,
) -> nt.ProcNode[bool]:
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeBooleanMath",
        inputs={("Boolean", 0): a, ("Boolean", 1): b},
        attrs={"operation": "XOR"},
    )


def boolean_not(
    a: nt.SocketOrVal[bool] = False,
) -> nt.ProcNode[bool]:
    """
    Uses a BooleanNot Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/math/boolean_math.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeBooleanMath",
        inputs={("Boolean", 0): a},
        attrs={"operation": "NOT"},
    )


def combine_matrix(
    column_1_row_1: nt.SocketOrVal[float] = 1.0,
    column_1_row_2: nt.SocketOrVal[float] = 0.0,
    column_1_row_3: nt.SocketOrVal[float] = 0.0,
    column_1_row_4: nt.SocketOrVal[float] = 0.0,
    column_2_row_1: nt.SocketOrVal[float] = 0.0,
    column_2_row_2: nt.SocketOrVal[float] = 1.0,
    column_2_row_3: nt.SocketOrVal[float] = 0.0,
    column_2_row_4: nt.SocketOrVal[float] = 0.0,
    column_3_row_1: nt.SocketOrVal[float] = 0.0,
    column_3_row_2: nt.SocketOrVal[float] = 0.0,
    column_3_row_3: nt.SocketOrVal[float] = 1.0,
    column_3_row_4: nt.SocketOrVal[float] = 0.0,
    column_4_row_1: nt.SocketOrVal[float] = 0.0,
    column_4_row_2: nt.SocketOrVal[float] = 0.0,
    column_4_row_3: nt.SocketOrVal[float] = 0.0,
    column_4_row_4: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode[pt.Matrix]:
    """
    Uses a CombineMatrix Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/combine_matrix.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeCombineMatrix",
        inputs={
            "Column 1 Row 1": column_1_row_1,
            "Column 1 Row 2": column_1_row_2,
            "Column 1 Row 3": column_1_row_3,
            "Column 1 Row 4": column_1_row_4,
            "Column 2 Row 1": column_2_row_1,
            "Column 2 Row 2": column_2_row_2,
            "Column 2 Row 3": column_2_row_3,
            "Column 2 Row 4": column_2_row_4,
            "Column 3 Row 1": column_3_row_1,
            "Column 3 Row 2": column_3_row_2,
            "Column 3 Row 3": column_3_row_3,
            "Column 3 Row 4": column_3_row_4,
            "Column 4 Row 1": column_4_row_1,
            "Column 4 Row 2": column_4_row_2,
            "Column 4 Row 3": column_4_row_3,
            "Column 4 Row 4": column_4_row_4,
        },
        attrs={},
    )


def combine_transform(
    translation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    rotation: Any = (0, 0, 0),
    scale: nt.SocketOrVal[pt.Vector] = (1, 1, 1),
) -> nt.ProcNode[pt.Matrix]:
    """
    Uses a CombineTransform Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/combine_transform.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeCombineTransform",
        inputs={"Translation": translation, "Rotation": rotation, "Scale": scale},
        attrs={},
    )


TCompare = TypeVar(
    "TCompare",
    nt.SocketOrVal[int],
    nt.SocketOrVal[pt.Color],
    nt.SocketOrVal[str],
    nt.SocketOrVal[float],
    nt.SocketOrVal[pt.Vector],
)

TCompareOperation = Literal[
    "LESS_THAN", "LESS_EQUAL", "GREATER_THAN", "GREATER_EQUAL", "EQUAL", "NOT_EQUAL"
]


def _compare(
    a: TCompare = None,
    b: TCompare = None,
    epsilon: nt.SocketOrVal[float] | None = None,
    operation: TCompareOperation = "EQUAL",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[bool]:
    """
    Uses a Compare Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/math/compare.html
    """

    # TODO merge with math.less_than etc

    if data_type is None:
        data_type = RuntimeResolveDataType(
            [
                NodeDataType.INT,
                NodeDataType.FLOAT,
                NodeDataType.RGBA,
                NodeDataType.STRING,
                NodeDataType.FLOAT_VECTOR,
            ],
            ["A", "B"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeCompare",
        inputs={"A": a, "B": b, "Epsilon": epsilon},
        attrs={
            "operation": operation,
            "data_type": data_type,
        },
    )


TCompareNumeric = TypeVar("TCompareNumeric", nt.SocketOrVal[int], nt.SocketOrVal[float])


def less_than(
    a: TCompareNumeric = None,
    b: TCompareNumeric = None,
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="LESS_THAN")


def less_equal(
    a: TCompareNumeric = None,
    b: TCompareNumeric = None,
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="LESS_EQUAL")


def greater_than(
    a: TCompareNumeric = None,
    b: TCompareNumeric = None,
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="GREATER_THAN")


def greater_equal(
    a: TCompareNumeric = None,
    b: TCompareNumeric = None,
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="GREATER_EQUAL")


TCompareEqual = TypeVar(
    "TCompareEqual",
    nt.SocketOrVal[int],
    nt.SocketOrVal[float],
)


def equal(
    a: TCompareEqual = None,
    b: TCompareEqual = None,
    epsilon: nt.SocketOrVal[float] | None = None,
) -> nt.ProcNode[bool]:
    return _compare(a, b, epsilon, operation="EQUAL")


def not_equal(
    a: TCompareEqual = None,
    b: TCompareEqual = None,
    epsilon: nt.SocketOrVal[float] | None = None,
) -> nt.ProcNode[bool]:
    return _compare(a, b, epsilon, operation="NOT_EQUAL")


def vector_compare_elementwise(
    a: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    b: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    epsilon: nt.SocketOrVal[float] = 0.001,
    operation: TCompareOperation = "EQUAL",
) -> nt.ProcNode[bool]:
    # TODO merge with math.less_than etc

    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeCompare",
        inputs={"A": a, "B": b, "Epsilon": epsilon},
        attrs={
            "operation": operation,
            "data_type": NodeDataType.FLOAT_VECTOR,
            "mode": "ELEMENT_WISE",
        },
    )


def compare_color(
    a: nt.SocketOrVal[pt.Color],
    b: nt.SocketOrVal[pt.Color],
    operation: Literal["EQUAL", "NOT_EQUAL", "BRIGHTER", "DARKER"],
    epsilon: nt.SocketOrVal[float] = 0.001,
) -> nt.ProcNode[bool]:
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeCompare",
        inputs={"A": a, "B": b, "Epsilon": epsilon},
        attrs={"operation": operation},
    )


def euler_to_rotation(
    euler: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a EulerToRotation Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/euler_to_rotation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeEulerToRotation",
        inputs={"Euler": euler},
        attrs={},
    )


def float_to_int(
    float: nt.SocketOrVal[float] = 0.0,
    rounding_mode: Literal["ROUND", "FLOOR", "CEILING", "TRUNCATE"] = "ROUND",
) -> nt.ProcNode[int]:
    """
    Uses a FloatToInt Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/math/float_to_integer.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeFloatToInt",
        inputs={"Float": float},
        attrs={"rounding_mode": rounding_mode},
    )


'''
def input_bool(boolean: bool = False) -> t.ProcNode[bool]:
    """
    Uses a InputBool Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/boolean.html
    """

    raise_io_error("input_bool", logger=logger)

    return t.ProcNode.from_nodetype(
        node_type="FunctionNodeInputBool",
        inputs={},
        attrs={"boolean": boolean},
    )


def input_color(value: tuple = (0.5, 0.5, 0.5, 1.0)) -> t.ProcNode[pt.Color]:
    """
    Uses a InputColor Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/color.html
    """

    raise_io_error("input_color", logger=logger)

    return t.ProcNode.from_nodetype(
        node_type="FunctionNodeInputColor",
        inputs={},
        attrs={"value": value},
    )


def input_int(integer: int = 0) -> t.ProcNode[int]:
    """
    Uses a InputInt Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/integer.html
    """

    raise_io_error("input_int", logger=logger)

    return t.ProcNode.from_nodetype(
        node_type="FunctionNodeInputInt",
        inputs={},
        attrs={"integer": integer},
    )


def input_rotation(rotation_euler: tuple = (0.0, 0.0, 0.0)) -> t.ProcNode[pt.Vector]:
    """
    Uses a InputRotation Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/rotation.html
    """

    raise_io_error("input_rotation", logger=logger)

    return t.ProcNode.from_nodetype(
        node_type="FunctionNodeInputRotation",
        inputs={},
        attrs={"rotation_euler": rotation_euler},
    )
'''


class InputSpecialCharactersResult(NamedTuple):
    line_break: nt.ProcNode[str]
    tab: nt.ProcNode[str]


def input_special_characters() -> InputSpecialCharactersResult:
    """
    Uses a InputSpecialCharacters Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/text/special_characters.html
    """

    raise_io_error("input_special_characters", logger=logger)

    node = nt.ProcNode.from_nodetype(
        node_type="FunctionNodeInputSpecialCharacters",
        inputs={},
        attrs={},
    )
    return InputSpecialCharactersResult(
        node._output_socket("line_break"), node._output_socket("tab")
    )


def input_string(string: str = "") -> nt.ProcNode[str]:
    """
    Uses a InputString Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/string.html
    """

    raise_io_error("input_string", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeInputString",
        inputs={},
        attrs={"string": string},
    )


def input_vector(vector: tuple = (0.0, 0.0, 0.0)) -> nt.ProcNode[pt.Vector]:
    """
    Uses a InputVector Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/vector.html
    """

    raise_io_error("input_vector", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeInputVector",
        inputs={},
        attrs={"vector": vector},
    )


class InvertMatrixResult(NamedTuple):
    matrix: nt.ProcNode[pt.Matrix]
    invertible: nt.ProcNode[bool]


def invert_matrix(matrix: nt.SocketOrVal[pt.Matrix] = None) -> InvertMatrixResult:
    """
    Uses a InvertMatrix Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/invert_matrix.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="FunctionNodeInvertMatrix",
        inputs={"Matrix": matrix},
        attrs={},
    )
    return InvertMatrixResult(
        node._output_socket("matrix"), node._output_socket("invertible")
    )


def invert_rotation(
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a InvertRotation Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/invert_rotation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeInvertRotation",
        inputs={"Rotation": rotation},
        attrs={},
    )


def matrix_multiply(
    matrix_0: nt.SocketOrVal[pt.Matrix] = None,
    matrix_1: nt.SocketOrVal[pt.Matrix] = None,
) -> nt.ProcNode[pt.Matrix]:
    """
    Uses a MatrixMultiply Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/multiply_matrices.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeMatrixMultiply",
        inputs={("Matrix", 0): matrix_0, ("Matrix", 1): matrix_1},
        attrs={},
    )


def project_point(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    transform: nt.SocketOrVal[pt.Matrix] = None,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a ProjectPoint Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/project_point.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeProjectPoint",
        inputs={"Vector": vector, "Transform": transform},
        attrs={},
    )


def quaternion_to_rotation(
    w: nt.SocketOrVal[float] = 1.0,
    x: nt.SocketOrVal[float] = 0.0,
    y: nt.SocketOrVal[float] = 0.0,
    z: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a QuaternionToRotation Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/quaternion_to_rotation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeQuaternionToRotation",
        inputs={"W": w, "X": x, "Y": y, "Z": z},
        attrs={},
    )


TRandomValue = TypeVar("TRandomValue", int, float, pt.Vector, pt.Color)


def random_value(
    min: nt.SocketOrVal[TRandomValue] = 0.0,
    max: nt.SocketOrVal[TRandomValue] = 1.0,
    id: nt.SocketOrVal[int] = 0,
    seed: nt.SocketOrVal[int] = 0,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TRandomValue]:
    """
    Uses a RandomValue Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/random_value.html
    """

    if data_type is None:
        data_type = RuntimeResolveDataType(
            [
                NodeDataType.INT,
                NodeDataType.FLOAT,
                NodeDataType.FLOAT_VECTOR,
                NodeDataType.RGBA,
            ],
            ["Min", "Max"],
        )

    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeRandomValue",
        inputs={
            "ID": id,
            "Max": max,
            "Min": min,
            "Seed": seed,
        },
        attrs={"data_type": data_type},
    )


def random_boolean(
    probability: nt.SocketOrVal[float] = 0.5,
    id: nt.SocketOrVal[int] = 0,
    seed: nt.SocketOrVal[int] = 0,
) -> nt.ProcNode[bool]:
    """
    Uses a RandomBoolean Function Node.
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeRandomValue",
        inputs={"ID": id, "Probability": probability, "Seed": seed},
        attrs={"data_type": NodeDataType.BOOLEAN},
    )


def replace_string(
    string: nt.SocketOrVal[str] = "",
    find: nt.SocketOrVal[str] = "",
    replace: nt.SocketOrVal[str] = "",
) -> nt.ProcNode[str]:
    """
    Uses a ReplaceString Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/text/replace_string.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeReplaceString",
        inputs={"String": string, "Find": find, "Replace": replace},
        attrs={},
    )


def rotate_euler(
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    rotate_by: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    rotation_type: Literal["EULER", "AXIS_ANGLE"] = "EULER",
    space: Literal["OBJECT", "LOCAL"] = "OBJECT",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a RotateEuler Function Node.

    See: http://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/rotate_euler.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeRotateEuler",
        inputs={"Rotation": rotation, "Rotate By": rotate_by},
        attrs={"rotation_type": rotation_type, "space": space},
    )


def rotate_rotation(
    rotation: Any = (0, 0, 0),
    rotate_by: Any = (0, 0, 0),
    rotation_space: Literal["GLOBAL", "LOCAL"] = "GLOBAL",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a RotateRotation Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/rotate_rotation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeRotateRotation",
        inputs={"Rotation": rotation, "Rotate By": rotate_by},
        attrs={"rotation_space": rotation_space},
    )


def rotate_vector(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0), rotation: Any = (0, 0, 0)
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a RotateVector Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/rotate_vector.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeRotateVector",
        inputs={"Vector": vector, "Rotation": rotation},
        attrs={},
    )


class RotationToAxisAngleResult(NamedTuple):
    axis: nt.ProcNode[pt.Vector]
    angle: nt.ProcNode[float]


def rotation_to_axis_angle(
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> RotationToAxisAngleResult:
    """
    Uses a RotationToAxisAngle Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/axis_angle_to_rotation.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="FunctionNodeRotationToAxisAngle",
        inputs={"Rotation": rotation},
        attrs={},
    )
    return RotationToAxisAngleResult(
        node._output_socket("axis"), node._output_socket("angle")
    )


def rotation_to_euler(
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a RotationToEuler Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/rotation_to_euler.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeRotationToEuler",
        inputs={"Rotation": rotation},
        attrs={},
    )


class RotationToQuaternionResult(NamedTuple):
    w: nt.ProcNode[float]
    x: nt.ProcNode[float]
    y: nt.ProcNode[float]
    z: nt.ProcNode[float]


def rotation_to_quaternion(
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> RotationToQuaternionResult:
    """
    Uses a RotationToQuaternion Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/rotation/rotation_to_quaternion.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="FunctionNodeRotationToQuaternion",
        inputs={"Rotation": rotation},
        attrs={},
    )
    return RotationToQuaternionResult(
        node._output_socket("w"),
        node._output_socket("x"),
        node._output_socket("y"),
        node._output_socket("z"),
    )


class SeparateColorResult(NamedTuple):
    red: nt.ProcNode[float]
    green: nt.ProcNode[float]
    blue: nt.ProcNode[float]
    alpha: nt.ProcNode[float]


def separate_color(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
    ycc_mode: Literal["ITUBT601", "ITUBT709", "JFIF"] = "ITUBT709",
) -> SeparateColorResult:
    """
    Uses a SeparateColor Function Node.

    Context mapping:
    - Shader: ShaderNodeSeparateColor (input: Color, outputs: red/green/blue, mode: RGB only)
    - Compositor: CompositorNodeSeparateColor (input: Image, outputs: red/green/blue/alpha, modes: RGB/HSV/HSL/YCC/YUV, ycc_mode param)
    - Texture: TextureNodeSeparateColor (input: Color, modes: RGB/HSV/HSL)
    - Function: FunctionNodeSeparateColor (input: Color, outputs: red/green/blue/alpha)

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/color/separate_color.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type=ContextualNode.SEPARATE_COLOR.value,
        inputs={"Color": color},
        attrs={"mode": mode},
    )
    return SeparateColorResult(
        red=res._output_socket("red"),
        green=res._output_socket("green"),
        blue=res._output_socket("blue"),
        alpha=res._output_socket("alpha"),
    )


"""
def separate_matrix(matrix: t.SocketOrVal[pt.Matrix] = None) -> t.ProcNode[pt.Matrix]:
 
    return t.ProcNode.from_nodetype(
        node_type="FunctionNodeSeparateMatrix",
        inputs={"Matrix": matrix},
        attrs={},
            "column_1_row_1",
            "column_1_row_2",
            "column_1_row_3",
            "column_1_row_4",
            "column_2_row_1",
            "column_2_row_2",
            "column_2_row_3",
            "column_2_row_4",
            "column_3_row_1",
            "column_3_row_2",
            "column_3_row_3",
            "column_3_row_4",
            "column_4_row_1",
            "column_4_row_2",
            "column_4_row_3",
            "column_4_row_4",
        ],
    )
"""


class SeparateTransformResult(NamedTuple):
    translation: nt.ProcNode[pt.Vector]
    rotation: nt.ProcNode[pt.Vector]
    scale: nt.ProcNode[pt.Vector]


def separate_transform(
    transform: nt.SocketOrVal[pt.Matrix] = None,
) -> SeparateTransformResult:
    """
    Uses a SeparateTransform Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/separate_transform.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="FunctionNodeSeparateTransform",
        inputs={"Transform": transform},
        attrs={},
    )
    return SeparateTransformResult(
        node._output_socket("translation"),
        node._output_socket("rotation"),
        node._output_socket("scale"),
    )


def slice_string(
    string: nt.SocketOrVal[str] = "",
    position: nt.SocketOrVal[int] = 0,
    length: nt.SocketOrVal[int] = 10,
) -> nt.ProcNode[str]:
    """
    Uses a SliceString Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/text/slice_string.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeSliceString",
        inputs={"String": string, "Position": position, "Length": length},
        attrs={},
    )


def string_length(string: nt.SocketOrVal[str] = "") -> nt.ProcNode[int]:
    """
    Uses a StringLength Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/text/string_length.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeStringLength",
        inputs={"String": string},
        attrs={},
    )


def transform_direction(
    direction: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    transform: nt.SocketOrVal[pt.Matrix] = None,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a TransformDirection Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/transform_direction.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeTransformDirection",
        inputs={"Direction": direction, "Transform": transform},
        attrs={},
    )


def transform_point(
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    transform: nt.SocketOrVal[pt.Matrix] = None,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a TransformPoint Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/transform_point.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeTransformPoint",
        inputs={"Vector": vector, "Transform": transform},
        attrs={},
    )


def transpose_matrix(
    matrix: nt.SocketOrVal[pt.Matrix] = None,
) -> nt.ProcNode[pt.Matrix]:
    """
    Uses a TransposeMatrix Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/transpose_matrix.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeTransposeMatrix",
        inputs={"Matrix": matrix},
        attrs={},
    )


def value_to_string(
    value: nt.SocketOrVal[float] = 0.0, decimals: nt.SocketOrVal[int] = 0
) -> nt.ProcNode[str]:
    """
    Uses a ValueToString Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/text/value_to_string.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeValueToString",
        inputs={"Value": value, "Decimals": decimals},
        attrs={},
    )


TMix = TypeVar("TMix", nt.SocketOrVal[float], nt.SocketOrVal[pt.Vector])


def mix(
    a: TMix | None = None,
    b: TMix | None = None,
    factor: nt.SocketOrVal[float] = 0.5,
    clamp_factor: bool = True,
    factor_mode: Literal["UNIFORM", "NON_UNIFORM"] = "UNIFORM",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TMix]:
    """
    Uses MixNode to mix float or vector fields

    NOTE: procfunc forces all colors to be mixed via mix_rgb, since setting this function
    to type Color adds extra args & exactly matches the interface of mix_rgb

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


TColorMixType = Literal[
    "MIX",
    "DARKEN",
    "MULTIPLY",
    "BURN",
    "LIGHTEN",
    "SCREEN",
    "DODGE",
    "ADD",
    "OVERLAY",
    "SOFT_LIGHT",
    "LINEAR_LIGHT",
    "DIFFERENCE",
    "EXCLUSION",
    "SUBTRACT",
    "DIVIDE",
    "HUE",
    "SATURATION",
    "COLOR",
    "VALUE",
]


def mix_rgb(
    factor: nt.SocketOrVal[float] = 0.5,
    a: nt.SocketOrVal[pt.Color] = (0.5, 0.5, 0.5, 1),
    b: nt.SocketOrVal[pt.Color] = (0.5, 0.5, 0.5, 1),
    blend_type: TColorMixType = "MIX",
    clamp_result: bool = False,
    clamp_factor: bool = True,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a Mix Node with datatype Color

    NOTE: separated from float/vector mix() due to extra arguments

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/mix.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeMix",
        inputs={"Factor": factor, "A": a, "B": b},
        attrs={
            "blend_type": blend_type,
            "clamp_result": clamp_result,
            "clamp_factor": clamp_factor,
            "data_type": NodeDataType.RGBA,
        },
    )


def rgb_curve(
    fac: nt.SocketOrVal[float] = 1.0,
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    curves: list[np.ndarray] | None = None,
) -> nt.ProcNode:
    """
    Uses a RGBCurve Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/rgb_curves.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeRGBCurve",
        inputs={"Fac": fac, "Color": color},
        attrs={"curves": curves},
    )


def combine_color(
    red: nt.SocketOrVal[float] = 0.0,
    green: nt.SocketOrVal[float] = 0.0,
    blue: nt.SocketOrVal[float] = 0.0,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
) -> nt.ProcNode[pt.Color]:
    """
    Uses a CombineColor Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMBINE_COLOR.value,
        inputs={"Red": red, "Green": green, "Blue": blue},
        attrs={"mode": mode},
    )


def combine_rgb(
    red: nt.SocketOrVal[float] = 0.0,
    green: nt.SocketOrVal[float] = 0.0,
    blue: nt.SocketOrVal[float] = 0.0,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
) -> nt.ProcNode[pt.Color]:
    """
    Uses a CombineColor Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMBINE_COLOR.value,
        inputs={"Red": red, "Green": green, "Blue": blue},
        attrs={"mode": mode},
    )


def combine_hsv(
    hue: nt.SocketOrVal[float] = 0.0,
    saturation: nt.SocketOrVal[float] = 0.0,
    value: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a CombineColor Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMBINE_COLOR.value,
        inputs={"Hue": hue, "Saturation": saturation, "Value": value},
        attrs={"mode": "HSV"},
    )


def combine_hsl(
    hue: nt.SocketOrVal[float] = 0.0,
    saturation: nt.SocketOrVal[float] = 0.0,
    lightness: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a CombineHSV Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMBINE_COLOR.value,
        inputs={"Hue": hue, "Saturation": saturation, "Lightness": lightness},
        attrs={"mode": "HSL"},
    )


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
        node_type="ShaderNodeCombineXYZ",
        inputs={"X": x, "Y": y, "Z": z},
        attrs={},
    )


class SeparateHsvResult(NamedTuple):
    h: nt.ProcNode[float]
    s: nt.ProcNode[float]
    v: nt.ProcNode[float]


def separate_hsv(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
) -> SeparateHsvResult:
    """
    Uses a SeparateHSV Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/separate_color.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeSeparateHSV",
        inputs={"Color": color},
        attrs={},
    )
    return SeparateHsvResult(
        h=res._output_socket("h"),
        s=res._output_socket("s"),
        v=res._output_socket("v"),
    )


class SeparateRgbResult(NamedTuple):
    r: nt.ProcNode[float]
    g: nt.ProcNode[float]
    b: nt.ProcNode[float]


def separate_rgb(
    image: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
) -> SeparateRgbResult:
    """
    Uses a SeparateRGB Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/separate_color.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeSeparateRGB",
        inputs={"Image": image},
        attrs={},
    )
    return SeparateRgbResult(
        r=res._output_socket("r"),
        g=res._output_socket("g"),
        b=res._output_socket("b"),
    )


class SeparateXyzResult(NamedTuple):
    x: nt.ProcNode[float]
    y: nt.ProcNode[float]
    z: nt.ProcNode[float]


def separate_xyz(vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0)) -> SeparateXyzResult:
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


TInterpolationType = Literal["LINEAR", "STEPPED_LINEAR", "SMOOTHSTEP", "SMOOTHERSTEP"]


def map_range(
    value: nt.SocketOrVal[float] = 1.0,
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

    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeMapRange",
        inputs={
            "From Max": from_max,
            "From Min": from_min,
            "To Max": to_max,
            "To Min": to_min,
            "Value": value,
        },
        attrs={
            "clamp": clamp,
            "interpolation_type": interpolation_type,
            "data_type": data_type,
        },
    )


def float_curve(
    factor: nt.SocketOrVal[float] = 1.0,
    value: nt.SocketOrVal[float] = 1.0,
    curve: np.ndarray | None = None,
    use_clip: bool = True,
) -> nt.ProcNode[float]:
    """
    Uses a FloatCurve Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/float_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeFloatCurve",
        inputs={"Factor": factor, "Value": value},
    )


def vector_curve(
    fac: nt.SocketOrVal[float] = 1.0,
    vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    curves: np.ndarray | None = None,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a VectorCurve Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/vector/curves.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeVectorCurve",
        inputs={"Fac": fac, "Vector": vector},
        attrs={"curves": curves},
    )


TIndexSwitch = TypeVar(
    "TIndexSwitch",
    nt.SocketOrVal[bool],
    nt.SocketOrVal[int],
    nt.SocketOrVal[pt.Color],
    nt.SocketOrVal[str],
    nt.SocketOrVal[float],
    nt.SocketOrVal[nt.pt.Vector],
)


def index_switch(
    val_0: TIndexSwitch = 0,
    val_1: TIndexSwitch = 0,
    index: nt.SocketOrVal[int] = 0,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode:
    """
    Uses a IndexSwitch Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/index_switch.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [
                NodeDataType.BOOLEAN,
                NodeDataType.INT,
                NodeDataType.RGBA,
                NodeDataType.STRING,
                NodeDataType.FLOAT,
                NodeDataType.FLOAT_VECTOR,
            ],
            ["0", "1"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeIndexSwitch",
        inputs={"0": val_0, "1": val_1, "Index": index},
        attrs={
            "data_type": data_type,
        },
    )


TSwitchArgType = TypeVar(
    "TAnyDataVal",
    int,
    float,
    bool,
    str,
    pt.Vector,
    pt.Color,
    pt.Matrix,
    pt.Quaternion,
    nt.Geometry,
)

_SWITCH_DATA_TYPES = [
    NodeDataType.BOOLEAN,
    NodeDataType.INT,
    NodeDataType.FLOAT,
    NodeDataType.STRING,
    NodeDataType.FLOAT_VECTOR,
    NodeDataType.RGBA,
    NodeDataType.FLOAT_MATRIX,
    NodeDataType.GEOMETRY,
]


def switch(
    switch: nt.SocketOrVal[bool] = False,
    a: nt.SocketOrVal[TSwitchArgType] | None = None,
    b: nt.SocketOrVal[TSwitchArgType] | None = None,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TSwitchArgType]:
    """
    Uses a Switch Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/switch.html
    """

    if data_type is None:
        data_type = RuntimeResolveDataType(
            _SWITCH_DATA_TYPES,
            ["False", "True"],
        )

    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSwitch",
        inputs={"Switch": switch, "False": a, "True": b},
        attrs={"input_type": data_type},
    )
