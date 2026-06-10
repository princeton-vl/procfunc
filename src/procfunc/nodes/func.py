import logging
from typing import Literal, NamedTuple, TypeVar

from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import (
    ContextualNode,
    RuntimeResolveDataType,
    raise_io_error,
)
from procfunc.nodes.bpy_node_info import NodeDataType

logger = logging.getLogger(__name__)


def align_euler_to_vector(
    factor: nt.SocketOrVal[float],
    vector: nt.SocketOrVal[pt.Vector],
    rotation: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
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
    factor: nt.SocketOrVal[float],
    vector: nt.SocketOrVal[pt.Vector],
    rotation: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
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
    primary_axis_vector: nt.SocketOrVal[pt.Vector],
    secondary_axis_vector: nt.SocketOrVal[pt.Vector],
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
    axis: nt.SocketOrVal[pt.Vector] = (0, 0, 1),
    angle: nt.SocketOrVal[float] = 0.0,
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
    a: nt.SocketOrVal[bool],
    b: nt.SocketOrVal[bool],
) -> nt.ProcNode[bool]:
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeBooleanMath",
        inputs={("Boolean", 0): a, ("Boolean", 1): b},
        attrs={"operation": "OR"},
    )


def boolean_and(
    a: nt.SocketOrVal[bool],
    b: nt.SocketOrVal[bool],
) -> nt.ProcNode[bool]:
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeBooleanMath",
        inputs={("Boolean", 0): a, ("Boolean", 1): b},
        attrs={"operation": "AND"},
    )


def boolean_xor(
    a: nt.SocketOrVal[bool],
    b: nt.SocketOrVal[bool],
) -> nt.ProcNode[bool]:
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeBooleanMath",
        inputs={("Boolean", 0): a, ("Boolean", 1): b},
        attrs={"operation": "XOR"},
    )


def boolean_not(
    a: nt.SocketOrVal[bool],
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
    rotation: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
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

# RGBA-only Compare operations, valid only when data_type is RGBA
TCompareColorOperation = Literal["EQUAL", "NOT_EQUAL", "BRIGHTER", "DARKER"]

# matches Blender's FunctionNodeCompare Epsilon socket default
COMPARE_EPSILON_DEFAULT = 0.001


def _compare(
    a: TCompare,
    b: TCompare,
    epsilon: nt.SocketOrVal[float] = COMPARE_EPSILON_DEFAULT,
    operation: TCompareOperation | TCompareColorOperation = "EQUAL",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[bool]:
    """
    Compares two values, context-dispatching to FunctionNodeCompare in geometry
    trees (full data_type support incl. INT) and Math nodes elsewhere. Outside
    geometry, LESS_THAN / GREATER_THAN map to a single Math node, while
    EQUAL / NOT_EQUAL / LESS_EQUAL / GREATER_EQUAL lower to a small Math
    composition (see _lower_compare_outside_geometry). The `data_type` option and
    non-float operands remain geometry-only. `epsilon` defaults to Blender's own
    Compare node default (0.001) and only applies to EQUAL / NOT_EQUAL.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/math/compare.html
    """

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
    # tuple keys let inline operator dispatch (`<`, `>`) bind positional args and
    # let the contextual mapping remap A/B -> Value sockets for ShaderNodeMath
    inputs: dict[tuple[str, int], nt.SocketOrVal] = {("A", 0): a, ("B", 0): b}
    # the socket already holds the Blender default, so skip setting it - this also
    # keeps INT/STRING compares working, whose Epsilon socket is disabled
    if not (isinstance(epsilon, float) and epsilon == COMPARE_EPSILON_DEFAULT):
        inputs[("Epsilon", 0)] = epsilon
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMPARE.value,
        inputs=inputs,
        attrs={
            "operation": operation,
            "data_type": data_type,
        },
    )


TCompareNumeric = TypeVar("TCompareNumeric", nt.SocketOrVal[int], nt.SocketOrVal[float])


def less_than(
    a: TCompareNumeric,
    b: TCompareNumeric,
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="LESS_THAN")


def less_equal(
    a: TCompareNumeric,
    b: TCompareNumeric,
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="LESS_EQUAL")


def greater_than(
    a: TCompareNumeric,
    b: TCompareNumeric,
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="GREATER_THAN")


def greater_equal(
    a: TCompareNumeric,
    b: TCompareNumeric,
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="GREATER_EQUAL")


TCompareEqual = TypeVar(
    "TCompareEqual",
    nt.SocketOrVal[int],
    nt.SocketOrVal[float],
)


def equal(
    a: TCompareEqual,
    b: TCompareEqual,
    epsilon: nt.SocketOrVal[float] = COMPARE_EPSILON_DEFAULT,
) -> nt.ProcNode[bool]:
    return _compare(a, b, epsilon, operation="EQUAL")


def not_equal(
    a: TCompareEqual,
    b: TCompareEqual,
    epsilon: nt.SocketOrVal[float] = COMPARE_EPSILON_DEFAULT,
) -> nt.ProcNode[bool]:
    return _compare(a, b, epsilon, operation="NOT_EQUAL")


# FunctionNodeCompare's ELEMENT-mode VECTOR and RGBA variants gate the Epsilon
# socket on the operation (enabled only for EQUAL/NOT_EQUAL), so each operation
# is a separate binding that routes through _compare; the helper omits Epsilon
# unless it differs from the Blender default, keeping disabled sockets unwired.


def vector_elementwise_less_than(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="LESS_THAN", data_type=NodeDataType.FLOAT_VECTOR)


def vector_elementwise_less_equal(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="LESS_EQUAL", data_type=NodeDataType.FLOAT_VECTOR)


def vector_elementwise_greater_than(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="GREATER_THAN", data_type=NodeDataType.FLOAT_VECTOR)


def vector_elementwise_greater_equal(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
) -> nt.ProcNode[bool]:
    return _compare(
        a, b, operation="GREATER_EQUAL", data_type=NodeDataType.FLOAT_VECTOR
    )


def vector_elementwise_equal(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
    epsilon: nt.SocketOrVal[float] = COMPARE_EPSILON_DEFAULT,
) -> nt.ProcNode[bool]:
    return _compare(
        a, b, epsilon, operation="EQUAL", data_type=NodeDataType.FLOAT_VECTOR
    )


def vector_elementwise_not_equal(
    a: nt.SocketOrVal[pt.Vector],
    b: nt.SocketOrVal[pt.Vector],
    epsilon: nt.SocketOrVal[float] = COMPARE_EPSILON_DEFAULT,
) -> nt.ProcNode[bool]:
    return _compare(
        a, b, epsilon, operation="NOT_EQUAL", data_type=NodeDataType.FLOAT_VECTOR
    )


def color_equal(
    a: nt.SocketOrVal[pt.Color],
    b: nt.SocketOrVal[pt.Color],
    epsilon: nt.SocketOrVal[float] = COMPARE_EPSILON_DEFAULT,
) -> nt.ProcNode[bool]:
    return _compare(a, b, epsilon, operation="EQUAL", data_type=NodeDataType.RGBA)


def color_not_equal(
    a: nt.SocketOrVal[pt.Color],
    b: nt.SocketOrVal[pt.Color],
    epsilon: nt.SocketOrVal[float] = COMPARE_EPSILON_DEFAULT,
) -> nt.ProcNode[bool]:
    return _compare(a, b, epsilon, operation="NOT_EQUAL", data_type=NodeDataType.RGBA)


def color_brighter(
    a: nt.SocketOrVal[pt.Color],
    b: nt.SocketOrVal[pt.Color],
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="BRIGHTER", data_type=NodeDataType.RGBA)


def color_darker(
    a: nt.SocketOrVal[pt.Color],
    b: nt.SocketOrVal[pt.Color],
) -> nt.ProcNode[bool]:
    return _compare(a, b, operation="DARKER", data_type=NodeDataType.RGBA)


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
    float: nt.SocketOrVal[float],
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


def invert_matrix(matrix: nt.SocketOrVal[pt.Matrix]) -> InvertMatrixResult:
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
    rotation: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
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
    a: nt.SocketOrVal[pt.Matrix],
    b: nt.SocketOrVal[pt.Matrix],
) -> nt.ProcNode[pt.Matrix]:
    """
    Uses a MatrixMultiply Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/multiply_matrices.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="FunctionNodeMatrixMultiply",
        inputs={("Matrix", 0): a, ("Matrix", 1): b},
        attrs={},
    )


def project_point(
    vector: nt.SocketOrVal[pt.Vector],
    transform: nt.SocketOrVal[pt.Matrix],
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
        # bl4.2 FunctionNodeRandomValue only supports FLOAT/INT/FLOAT_VECTOR
        # (and BOOLEAN via random_boolean) — it has no color/RGBA data type.
        data_type = RuntimeResolveDataType(
            [
                NodeDataType.INT,
                NodeDataType.FLOAT,
                NodeDataType.FLOAT_VECTOR,
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
    string: nt.SocketOrVal[str],
    find: nt.SocketOrVal[str],
    replace: nt.SocketOrVal[str],
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
    rotation: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
    rotate_by: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
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
    vector: nt.SocketOrVal[pt.Vector],
    rotation: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
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
    rotation: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
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
    rotation: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
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
    rotation: nt.SocketOrVal[pt.Euler] = (0, 0, 0),
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


class SeparateMatrixResult(NamedTuple):
    column_1_row_1: nt.ProcNode[float]
    column_1_row_2: nt.ProcNode[float]
    column_1_row_3: nt.ProcNode[float]
    column_1_row_4: nt.ProcNode[float]
    column_2_row_1: nt.ProcNode[float]
    column_2_row_2: nt.ProcNode[float]
    column_2_row_3: nt.ProcNode[float]
    column_2_row_4: nt.ProcNode[float]
    column_3_row_1: nt.ProcNode[float]
    column_3_row_2: nt.ProcNode[float]
    column_3_row_3: nt.ProcNode[float]
    column_3_row_4: nt.ProcNode[float]
    column_4_row_1: nt.ProcNode[float]
    column_4_row_2: nt.ProcNode[float]
    column_4_row_3: nt.ProcNode[float]
    column_4_row_4: nt.ProcNode[float]


def separate_matrix(
    matrix: nt.SocketOrVal[pt.Matrix],
) -> SeparateMatrixResult:
    """
    Uses a SeparateMatrix Function Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/matrix/separate_matrix.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="FunctionNodeSeparateMatrix",
        inputs={"Matrix": matrix},
        attrs={},
    )
    return SeparateMatrixResult(
        node._output_socket("column_1_row_1"),
        node._output_socket("column_1_row_2"),
        node._output_socket("column_1_row_3"),
        node._output_socket("column_1_row_4"),
        node._output_socket("column_2_row_1"),
        node._output_socket("column_2_row_2"),
        node._output_socket("column_2_row_3"),
        node._output_socket("column_2_row_4"),
        node._output_socket("column_3_row_1"),
        node._output_socket("column_3_row_2"),
        node._output_socket("column_3_row_3"),
        node._output_socket("column_3_row_4"),
        node._output_socket("column_4_row_1"),
        node._output_socket("column_4_row_2"),
        node._output_socket("column_4_row_3"),
        node._output_socket("column_4_row_4"),
    )


class SeparateTransformResult(NamedTuple):
    translation: nt.ProcNode[pt.Vector]
    rotation: nt.ProcNode[pt.Vector]
    scale: nt.ProcNode[pt.Vector]


def separate_transform(
    transform: nt.SocketOrVal[pt.Matrix],
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
    string: nt.SocketOrVal[str],
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


def string_length(string: nt.SocketOrVal[str]) -> nt.ProcNode[int]:
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
    direction: nt.SocketOrVal[pt.Vector],
    transform: nt.SocketOrVal[pt.Matrix],
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
    vector: nt.SocketOrVal[pt.Vector],
    transform: nt.SocketOrVal[pt.Matrix],
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
    matrix: nt.SocketOrVal[pt.Matrix],
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
    value: nt.SocketOrVal[float], decimals: nt.SocketOrVal[int] = 0
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
    a: TIndexSwitch = 0,
    b: TIndexSwitch = 0,
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
                NodeDataType.FLOAT,
                NodeDataType.FLOAT_VECTOR,
                NodeDataType.ROTATION,
                NodeDataType.FLOAT_MATRIX,
                NodeDataType.STRING,
                NodeDataType.RGBA,
                NodeDataType.OBJECT,
                NodeDataType.IMAGE,
                NodeDataType.GEOMETRY,
                NodeDataType.COLLECTION,
                NodeDataType.MATERIAL,
            ],
            ["0", "1"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeIndexSwitch",
        inputs={"0": a, "1": b, "Index": index},
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
    NodeDataType.FLOAT_VECTOR,
    NodeDataType.ROTATION,
    NodeDataType.FLOAT_MATRIX,
    NodeDataType.STRING,
    NodeDataType.RGBA,
    NodeDataType.OBJECT,
    NodeDataType.IMAGE,
    NodeDataType.GEOMETRY,
    NodeDataType.COLLECTION,
    NodeDataType.MATERIAL,
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
