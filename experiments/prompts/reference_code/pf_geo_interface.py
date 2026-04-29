
###MODULE procfunc.nodes.math


def clamp(
    value: pf.SocketOrVal[float] = 1.0,
    min: pf.SocketOrVal[float] = 0.0,
    max: pf.SocketOrVal[float] = 1.0,
    clamp_type: Literal["MINMAX", "RANGE"] = "MINMAX",
) -> pf.ProcNode[float]:
    pass
# Math Nodes


# Basic Math Operations
def add(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def subtract(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def multiply(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def multiply_add(
    a: pf.SocketOrVal[float] = 0.5,
    b: pf.SocketOrVal[float] = 0.5,
    addend: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def divide(
    numerator: pf.SocketOrVal[float] = 0.5, denominator: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def power(
    base: pf.SocketOrVal[float] = 0.5, exponent: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def logarithm(
    value: pf.SocketOrVal[float] = 0.5, base: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def sqrt(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def inverse_sqrt(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def absolute(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def exponent(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
# Comparison Operations
def minimum(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def maximum(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def less_than(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def greater_than(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def sign(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def compare(
    a: pf.SocketOrVal[float] = 0.5,
    b: pf.SocketOrVal[float] = 0.5,
    epsilon: pf.SocketOrVal[float] = 0.001,
) -> pf.ProcNode[float]:
    pass
def smooth_minimum(
    a: pf.SocketOrVal[float] = 0.5,
    b: pf.SocketOrVal[float] = 0.5,
    distance: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def smooth_maximum(
    a: pf.SocketOrVal[float] = 0.5,
    b: pf.SocketOrVal[float] = 0.5,
    distance: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def round(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def floor(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def ceil(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def truncate(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def fraction(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def modulo(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def floor_mod(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def wrap(
    value: pf.SocketOrVal[float] = 0.5,
    max_val: pf.SocketOrVal[float] = 1.0,
    min_val: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def snap(
    value: pf.SocketOrVal[float] = 0.5, increment: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[float]:
    pass
def pingpong(
    value: pf.SocketOrVal[float] = 0.5, scale: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[float]:
    pass
# Trigonometric Operations
def sin(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def cos(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def tan(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def asin(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def acos(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def atan(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def atan2(
    y: pf.SocketOrVal[float] = 0.5, x: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def sinh(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def cosh(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def tanh(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
# Conversion Operations
def deg_to_rad(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def rad_to_deg(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
# Vector Math Operations
def vector_add(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_subtract(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_multiply(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_multiply_add(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    addend: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_divide(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_cross_product(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_project(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    onto: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[float]:
    pass
def vector_reflect(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_refract(
    incident: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    ior: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_faceforward(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    surface: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_dot_product(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_distance(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_length(vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0)) -> pf.ProcNode[float]:
    pass
def vector_scale(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0), scale: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_normalize(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_wrap(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    max_val: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
    min_val: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_snap(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_floor(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_ceil(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_modulo(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_fraction(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_round(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_truncate(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_absolute(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_minimum(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_maximum(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_sine(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_cosine(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_tangent(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_rotate_axis_angle(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    center: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    axis: pf.SocketOrVal[pf.Vector] = (0, 0, 1),
    angle: pf.SocketOrVal[float] = 0.0,
    invert: bool = False,
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_rotate_euler(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    center: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    invert: bool = False,
) -> pf.ProcNode[pf.Vector]:
    pass
# NOTE: mode XYZ have been dropped. transpiler specialcases will map these back to vector_rotate_euler calls.


def vector_transform(
    vector: pf.SocketOrVal[pf.Vector] = (0.5, 0.5, 0.5),
    convert_from: Literal["WORLD", "OBJECT", "CAMERA"] = "WORLD",
    convert_to: Literal["WORLD", "OBJECT", "CAMERA"] = "OBJECT",
    vector_type: Literal["POINT", "VECTOR", "NORMAL"] = "VECTOR",
) -> pf.ProcNode[pf.Vector]:
    pass

###MODULE procfunc.nodes.func


def constant(
    value: TConstant,
) -> pf.ProcNode[TConstant]:
    pass
def align_euler_to_vector(
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    factor: pf.SocketOrVal[float] = 1.0,
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 1),
    axis: Literal["X", "Y", "Z"] = "X",
    pivot_axis: Literal["AUTO", "X", "Y", "Z"] = "AUTO",
) -> pf.ProcNode[pf.Vector]:
    pass
def align_rotation_to_vector(
    rotation: Any = (0, 0, 0),
    factor: pf.SocketOrVal[float] = 1.0,
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 1),
    axis: Literal["X", "Y", "Z"] = "Z",
    pivot_axis: Literal["AUTO", "X", "Y", "Z"] = "AUTO",
) -> pf.ProcNode[pf.Vector]:
    pass
def axes_to_rotation(
    primary_axis_vector: pf.SocketOrVal[pf.Vector] = (0, 0, 1),
    secondary_axis_vector: pf.SocketOrVal[pf.Vector] = (1, 0, 0),
    primary_axis: Literal["X", "Y", "Z"] = "X",
    secondary_axis: Literal["X", "Y", "Z"] = "Y",
) -> pf.ProcNode[pf.Vector]:
    pass
def axis_angle_to_rotation(
    axis: pf.SocketOrVal[pf.Vector] = (0, 0, 1), angle: pf.SocketOrVal[float] = 0.0
) -> pf.ProcNode[pf.Vector]:
    pass
def boolean_or(
    a: pf.SocketOrVal[bool] = False,
    b: pf.SocketOrVal[bool] = False,
) -> pf.ProcNode[bool]:
    pass
def boolean_and(
    a: pf.SocketOrVal[bool] = False,
    b: pf.SocketOrVal[bool] = False,
) -> pf.ProcNode[bool]:
    pass
def boolean_xor(
    a: pf.SocketOrVal[bool] = False,
    b: pf.SocketOrVal[bool] = False,
) -> pf.ProcNode[bool]:
    pass
def boolean_not(
    a: pf.SocketOrVal[bool] = False,
) -> pf.ProcNode[bool]:
    pass
def combine_matrix(
    column_1_row_1: pf.SocketOrVal[float] = 1.0,
    column_1_row_2: pf.SocketOrVal[float] = 0.0,
    column_1_row_3: pf.SocketOrVal[float] = 0.0,
    column_1_row_4: pf.SocketOrVal[float] = 0.0,
    column_2_row_1: pf.SocketOrVal[float] = 0.0,
    column_2_row_2: pf.SocketOrVal[float] = 1.0,
    column_2_row_3: pf.SocketOrVal[float] = 0.0,
    column_2_row_4: pf.SocketOrVal[float] = 0.0,
    column_3_row_1: pf.SocketOrVal[float] = 0.0,
    column_3_row_2: pf.SocketOrVal[float] = 0.0,
    column_3_row_3: pf.SocketOrVal[float] = 1.0,
    column_3_row_4: pf.SocketOrVal[float] = 0.0,
    column_4_row_1: pf.SocketOrVal[float] = 0.0,
    column_4_row_2: pf.SocketOrVal[float] = 0.0,
    column_4_row_3: pf.SocketOrVal[float] = 0.0,
    column_4_row_4: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Matrix]:
    pass
def combine_transform(
    translation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    rotation: Any = (0, 0, 0),
    scale: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
) -> pf.ProcNode[pf.Matrix]:
    pass
TCompare = TypeVar(
    "TCompare",
    pf.SocketOrVal[int],
    pf.SocketOrVal[pf.Color],
    pf.SocketOrVal[str],
    pf.SocketOrVal[float],
    pf.SocketOrVal[pf.Vector],
)

TCompareOperation = Literal[
    "LESS_THAN", "LESS_EQUAL", "GREATER_THAN", "GREATER_EQUAL", "EQUAL", "NOT_EQUAL"
]


TCompareNumeric = TypeVar("TCompareNumeric", pf.SocketOrVal[int], pf.SocketOrVal[float])


def less_than(
    a: TCompareNumeric = None,
    b: TCompareNumeric = None,
) -> pf.ProcNode[bool]:
    pass
def less_equal(
    a: TCompareNumeric = None,
    b: TCompareNumeric = None,
) -> pf.ProcNode[bool]:
    pass
def greater_than(
    a: TCompareNumeric = None,
    b: TCompareNumeric = None,
) -> pf.ProcNode[bool]:
    pass
def greater_equal(
    a: TCompareNumeric = None,
    b: TCompareNumeric = None,
) -> pf.ProcNode[bool]:
    pass
TCompareEqual = TypeVar(
    "TCompareEqual",
    pf.SocketOrVal[int],
    pf.SocketOrVal[float],
)


def equal(
    a: TCompareEqual = None,
    b: TCompareEqual = None,
    epsilon: pf.SocketOrVal[float] | None = None,
) -> pf.ProcNode[bool]:
    pass
def not_equal(
    a: TCompareEqual = None,
    b: TCompareEqual = None,
    epsilon: pf.SocketOrVal[float] | None = None,
) -> pf.ProcNode[bool]:
    pass
def vector_compare_elementwise(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    epsilon: pf.SocketOrVal[float] = 0.001,
    operation: TCompareOperation = "EQUAL",
) -> pf.ProcNode[bool]:
    pass
def compare_color(
    a: pf.SocketOrVal[pf.Color],
    b: pf.SocketOrVal[pf.Color],
    operation: Literal["EQUAL", "NOT_EQUAL", "BRIGHTER", "DARKER"],
    epsilon: pf.SocketOrVal[float] = 0.001,
) -> pf.ProcNode[bool]:
    pass
def euler_to_rotation(
    euler: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def float_to_int(
    float: pf.SocketOrVal[float] = 0.0,
    rounding_mode: Literal["ROUND", "FLOOR", "CEILING", "TRUNCATE"] = "ROUND",
) -> pf.ProcNode[int]:
    pass
class InputSpecialCharactersResult(NamedTuple):
    line_break: pf.ProcNode[str]
    tab: pf.ProcNode[str]


def input_special_characters() -> InputSpecialCharactersResult:
    pass
def input_string(string: str = "") -> pf.ProcNode[str]:
    pass
def input_vector(vector: tuple = (0.0, 0.0, 0.0)) -> pf.ProcNode[pf.Vector]:
    pass
class InvertMatrixResult(NamedTuple):
    matrix: pf.ProcNode[pf.Matrix]
    invertible: pf.ProcNode[bool]


def invert_matrix(matrix: pf.SocketOrVal[pf.Matrix] = None) -> InvertMatrixResult:
    pass
def invert_rotation(
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def matrix_multiply(
    matrix_0: pf.SocketOrVal[pf.Matrix] = None,
    matrix_1: pf.SocketOrVal[pf.Matrix] = None,
) -> pf.ProcNode[pf.Matrix]:
    pass
def project_point(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    transform: pf.SocketOrVal[pf.Matrix] = None,
) -> pf.ProcNode[pf.Vector]:
    pass
def quaternion_to_rotation(
    w: pf.SocketOrVal[float] = 1.0,
    x: pf.SocketOrVal[float] = 0.0,
    y: pf.SocketOrVal[float] = 0.0,
    z: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.Vector]:
    pass
TRandomValue = TypeVar("TRandomValue", int, float, pf.Vector, pf.Color)


def random_value(
    min: pf.SocketOrVal[TRandomValue] = 0.0,
    max: pf.SocketOrVal[TRandomValue] = 1.0,
    id: pf.SocketOrVal[int] = 0,
    seed: pf.SocketOrVal[int] = 0,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TRandomValue]:
    pass
def random_boolean(
    probability: pf.SocketOrVal[float] = 0.5,
    id: pf.SocketOrVal[int] = 0,
    seed: pf.SocketOrVal[int] = 0,
) -> pf.ProcNode[bool]:
    pass
def replace_string(
    string: pf.SocketOrVal[str] = "",
    find: pf.SocketOrVal[str] = "",
    replace: pf.SocketOrVal[str] = "",
) -> pf.ProcNode[str]:
    pass
def rotate_euler(
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    rotate_by: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    rotation_type: Literal["EULER", "AXIS_ANGLE"] = "EULER",
    space: Literal["OBJECT", "LOCAL"] = "OBJECT",
) -> pf.ProcNode[pf.Vector]:
    pass
def rotate_rotation(
    rotation: Any = (0, 0, 0),
    rotate_by: Any = (0, 0, 0),
    rotation_space: Literal["GLOBAL", "LOCAL"] = "GLOBAL",
) -> pf.ProcNode[pf.Vector]:
    pass
def rotate_vector(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0), rotation: Any = (0, 0, 0)
) -> pf.ProcNode[pf.Vector]:
    pass
class RotationToAxisAngleResult(NamedTuple):
    axis: pf.ProcNode[pf.Vector]
    angle: pf.ProcNode[float]


def rotation_to_axis_angle(
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> RotationToAxisAngleResult:
    pass
def rotation_to_euler(
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
class RotationToQuaternionResult(NamedTuple):
    w: pf.ProcNode[float]
    x: pf.ProcNode[float]
    y: pf.ProcNode[float]
    z: pf.ProcNode[float]


def rotation_to_quaternion(
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> RotationToQuaternionResult:
    pass
class SeparateColorResult(NamedTuple):
    red: pf.ProcNode[float]
    green: pf.ProcNode[float]
    blue: pf.ProcNode[float]
    alpha: pf.ProcNode[float]


def separate_color(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
    ycc_mode: Literal["ITUBT601", "ITUBT709", "JFIF"] = "ITUBT709",
) -> SeparateColorResult:
    pass
class SeparateTransformResult(NamedTuple):
    translation: pf.ProcNode[pf.Vector]
    rotation: pf.ProcNode[pf.Vector]
    scale: pf.ProcNode[pf.Vector]


def separate_transform(
    transform: pf.SocketOrVal[pf.Matrix] = None,
) -> SeparateTransformResult:
    pass
def slice_string(
    string: pf.SocketOrVal[str] = "",
    position: pf.SocketOrVal[int] = 0,
    length: pf.SocketOrVal[int] = 10,
) -> pf.ProcNode[str]:
    pass
def string_length(string: pf.SocketOrVal[str] = "") -> pf.ProcNode[int]:
    pass
def transform_direction(
    direction: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    transform: pf.SocketOrVal[pf.Matrix] = None,
) -> pf.ProcNode[pf.Vector]:
    pass
def transform_point(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    transform: pf.SocketOrVal[pf.Matrix] = None,
) -> pf.ProcNode[pf.Vector]:
    pass
def transpose_matrix(
    matrix: pf.SocketOrVal[pf.Matrix] = None,
) -> pf.ProcNode[pf.Matrix]:
    pass
def value_to_string(
    value: pf.SocketOrVal[float] = 0.0, decimals: pf.SocketOrVal[int] = 0
) -> pf.ProcNode[str]:
    pass
TMix = TypeVar("TMix", pf.SocketOrVal[float], pf.SocketOrVal[pf.Vector])


def mix(
    a: TMix | None = None,
    b: TMix | None = None,
    factor: pf.SocketOrVal[float] = 0.5,
    clamp_factor: bool = True,
    factor_mode: Literal["UNIFORM", "NON_UNIFORM"] = "UNIFORM",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TMix]:
    pass
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
    factor: pf.SocketOrVal[float] = 0.5,
    a: pf.SocketOrVal[pf.Color] = (0.5, 0.5, 0.5, 1),
    b: pf.SocketOrVal[pf.Color] = (0.5, 0.5, 0.5, 1),
    blend_type: TColorMixType = "MIX",
    clamp_result: bool = False,
    clamp_factor: bool = True,
) -> pf.ProcNode[pf.Color]:
    pass
def rgb_curve(
    fac: pf.SocketOrVal[float] = 1.0,
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    curves: list[np.ndarray] | None = None,
) -> pf.ProcNode:
    pass
def combine_color(
    red: pf.SocketOrVal[float] = 0.0,
    green: pf.SocketOrVal[float] = 0.0,
    blue: pf.SocketOrVal[float] = 0.0,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
) -> pf.ProcNode[pf.Color]:
    pass
def combine_rgb(
    red: pf.SocketOrVal[float] = 0.0,
    green: pf.SocketOrVal[float] = 0.0,
    blue: pf.SocketOrVal[float] = 0.0,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
) -> pf.ProcNode[pf.Color]:
    pass
def combine_hsv(
    hue: pf.SocketOrVal[float] = 0.0,
    saturation: pf.SocketOrVal[float] = 0.0,
    value: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.Color]:
    pass
def combine_hsl(
    hue: pf.SocketOrVal[float] = 0.0,
    saturation: pf.SocketOrVal[float] = 0.0,
    lightness: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.Color]:
    pass
def combine_xyz(
    x: pf.SocketOrVal[float] = 0.0,
    y: pf.SocketOrVal[float] = 0.0,
    z: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.Vector]:
    pass
class SeparateHsvResult(NamedTuple):
    h: pf.ProcNode[float]
    s: pf.ProcNode[float]
    v: pf.ProcNode[float]


def separate_hsv(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
) -> SeparateHsvResult:
    pass
class SeparateRgbResult(NamedTuple):
    r: pf.ProcNode[float]
    g: pf.ProcNode[float]
    b: pf.ProcNode[float]


def separate_rgb(
    image: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
) -> SeparateRgbResult:
    pass
class SeparateXyzResult(NamedTuple):
    x: pf.ProcNode[float]
    y: pf.ProcNode[float]
    z: pf.ProcNode[float]


def separate_xyz(vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0)) -> SeparateXyzResult:
    pass
TInterpolationType = Literal["LINEAR", "STEPPED_LINEAR", "SMOOTHSTEP", "SMOOTHERSTEP"]


def map_range(
    value: pf.SocketOrVal[float] = 1.0,
    from_max: pf.SocketOrVal[float] = 1.0,
    from_min: pf.SocketOrVal[float] = 0.0,
    to_max: pf.SocketOrVal[float] = 1.0,
    to_min: pf.SocketOrVal[float] = 0.0,
    clamp: bool = True,
    interpolation_type: TInterpolationType = "LINEAR",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode:
    pass
def float_curve(
    factor: pf.SocketOrVal[float] = 1.0,
    value: pf.SocketOrVal[float] = 1.0,
    curve: np.ndarray | None = None,
    handle_type: str = "AUTO",
    use_clip: bool = True,
) -> pf.ProcNode[float]:
    pass
def vector_curve(
    fac: pf.SocketOrVal[float] = 1.0,
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    curves: np.ndarray | None = None,
) -> pf.ProcNode[pf.Vector]:
    pass
TIndexSwitch = TypeVar(
    "TIndexSwitch",
    pf.SocketOrVal[bool],
    pf.SocketOrVal[int],
    pf.SocketOrVal[pf.Color],
    pf.SocketOrVal[str],
    pf.SocketOrVal[float],
    pf.SocketOrVal[pf.pf.Vector],
)


def index_switch(
    val_0: TIndexSwitch = 0,
    val_1: TIndexSwitch = 0,
    index: pf.SocketOrVal[int] = 0,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode:
    pass
TSwitchArgType = TypeVar(
    "TAnyDataVal",
    int,
    float,
    bool,
    str,
    pf.Vector,
    pf.Color,
    pf.Matrix,
    pf.Quaternion,
    pf.Geometry,
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
    switch: pf.SocketOrVal[bool] = False,
    a: pf.SocketOrVal[TSwitchArgType] | None = None,
    b: pf.SocketOrVal[TSwitchArgType] | None = None,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TSwitchArgType]:
    pass

###MODULE procfunc.nodes.shader


def add_shader(
    shader_0: pf.ProcNode[pf.Shader] | None = None,
    shader_1: pf.ProcNode[pf.Shader] | None = None,
) -> pf.ProcNode[pf.Shader]:
    pass
class AmbientOcclusionResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    ao: pf.ProcNode[float]


def ambient_occlusion(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    distance: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    inside: bool = False,
    only_local: bool = False,
    samples: int = 16,
) -> AmbientOcclusionResult:
    pass
class AttributeResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    vector: pf.ProcNode[pf.Vector]
    fac: pf.ProcNode[float]
    alpha: pf.ProcNode[float]


def attribute(
    attribute_name: str = "",
    attribute_type: Literal[
        "GEOMETRY", "OBJECT", "INSTANCER", "VIEW_LAYER"
    ] = "GEOMETRY",
) -> AttributeResult:
    pass
def background(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    strength: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Shader]:
    pass
def bevel(
    radius: pf.SocketOrVal[float] = 0.05,
    normal: pf.SocketOrVal[pf.Vector] = None,
    samples: int = 4,
) -> pf.ProcNode[pf.Vector]:
    pass
def blackbody(temperature: pf.SocketOrVal[float] = 1500.0) -> pf.ProcNode[pf.Color]:
    pass
def bright_contrast(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    bright: pf.SocketOrVal[float] = 0.0,
    contrast: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.Color]:
    pass
def anisotropic_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.5,
    anisotropy: pf.SocketOrVal[float] = 0.0,
    rotation: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    tangent: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    distribution: Literal[
        "BECKMANN", "GGX", "ASHIKHMIN_SHIRLEY", "MULTI_GGX"
    ] = "MULTI_GGX",
) -> pf.ProcNode[pf.Shader]:
    pass
def diffuse_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
) -> pf.ProcNode[pf.Shader]:
    pass
def glass_bsdf(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.5,
    normal: pf.SocketOrVal[pf.Vector] = None,
    distribution: Literal["BECKMANN", "GGX", "MULTI_GGX"] = "MULTI_GGX",
) -> pf.ProcNode[pf.Shader]:
    pass
def hair_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    offset: pf.SocketOrVal[float] = 0.0,
    roughness_u: pf.SocketOrVal[float] = 0.1,
    roughness_v: pf.SocketOrVal[float] = 1.0,
    tangent: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    component: Literal["Reflection", "Transmission"] = "Reflection",
) -> pf.ProcNode[pf.Shader]:
    pass
def principled_hair_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.017513, 0.005763, 0.002059, 1),
    roughness: pf.SocketOrVal[float] = 0.3,
    radial_roughness: pf.SocketOrVal[float] = 0.3,
    coat: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.55,
    offset: pf.SocketOrVal[float] = 0.034907,
    random_roughness: pf.SocketOrVal[float] = 0.0,
    random: pf.SocketOrVal[float] = 0.0,
    model: Literal["CHIANG", "HUANG"] = "CHIANG",
    parametrization: Literal["ABSORPTION", "MELANIN", "COLOR"] = "COLOR",
) -> pf.ProcNode[pf.Shader]:
    pass
TSubsurfaceMethod = Literal["BURLEY", "RANDOM_WALK", "RANDOM_WALK_SKIN"]


def principled_bsdf(
    base_color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    metallic: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    ior: pf.SocketOrVal[float] = 1.5,
    alpha: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
    # subsurface scattering
    subsurface_method: TSubsurfaceMethod = "RANDOM_WALK",
    subsurface_weight: pf.SocketOrVal[float] = 0.0,
    subsurface_radius: pf.SocketOrVal[pf.Vector] = (1, 0.2, 0.1),
    subsurface_scale: pf.SocketOrVal[float] = 0.05,
    subsurface_ior: pf.SocketOrVal[float] | None = None,
    subsurface_anisotropy: pf.SocketOrVal[float] | None = None,
    # specular
    distribution: Literal["GGX", "MULTI_GGX"] = "MULTI_GGX",
    specular_ior_level: pf.SocketOrVal[float] = 0.5,
    specular_tint: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    anisotropic: pf.SocketOrVal[float] = 0.0,
    anisotropic_rotation: pf.SocketOrVal[float] = 0.0,
    tangent: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    transmission_weight: pf.SocketOrVal[float] = 0.0,
    coat_weight: pf.SocketOrVal[float] = 0.0,
    coat_roughness: pf.SocketOrVal[float] = 0.03,
    coat_ior: pf.SocketOrVal[float] = 1.5,
    coat_tint: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    coat_normal: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
    sheen_weight: pf.SocketOrVal[float] = 0.0,
    sheen_roughness: pf.SocketOrVal[float] = 0.5,
    sheen_tint: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    emission_color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    emission_strength: pf.SocketOrVal[float] = 0.0,
    thin_film_thickness: pf.SocketOrVal[float] = 0.0,
    thin_film_ior: pf.SocketOrVal[float] = 1.33,
) -> pf.ProcNode[pf.Shader]:
    pass
def ray_portal_bsdf(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    position: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    direction: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Shader]:
    pass
def refraction_bsdf(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.45,
    normal: pf.SocketOrVal[pf.Vector] = None,
    distribution: Literal["BECKMANN", "GGX"] = "BECKMANN",
) -> pf.ProcNode[pf.Shader]:
    pass
def sheen_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.5,
    normal: pf.SocketOrVal[pf.Vector] = None,
    distribution: Literal["ASHIKHMIN", "MICROFIBER"] = "MICROFIBER",
) -> pf.ProcNode[pf.Shader]:
    pass
def toon_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    size: pf.SocketOrVal[float] = 0.5,
    smooth: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    component: Literal["DIFFUSE", "GLOSSY"] = "DIFFUSE",
) -> pf.ProcNode[pf.Shader]:
    pass
def translucent_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    normal: pf.SocketOrVal[pf.Vector] = None,
) -> pf.ProcNode[pf.Shader]:
    pass
def transparent_bsdf(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
) -> pf.ProcNode[pf.Shader]:
    pass
def bump(
    strength: pf.SocketOrVal[float] = 1.0,
    distance: pf.SocketOrVal[float] = 1.0,
    height: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    invert: bool = False,
) -> pf.ProcNode[pf.Vector]:
    pass
class CameraDataResult(NamedTuple):
    view_vector: pf.ProcNode[pf.Vector]
    view_z_depth: pf.ProcNode[float]
    view_distance: pf.ProcNode[float]


def camera_data() -> CameraDataResult:
    pass
def displacement(
    height: pf.SocketOrVal[float] = 0.0,
    midlevel: pf.SocketOrVal[float] = 0.5,
    scale: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
) -> pf.ProcNode[pf.Vector]:
    pass
def eevee_specular(
    base_color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    specular: pf.SocketOrVal[pf.Color] = (0.03, 0.03, 0.03, 1),
    roughness: pf.SocketOrVal[float] = 0.2,
    emissive_color: pf.SocketOrVal[pf.Color] = (0, 0, 0, 1),
    transparency: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    clear_coat: pf.SocketOrVal[float] = 0.0,
    clear_coat_roughness: pf.SocketOrVal[float] = 0.0,
    clear_coat_normal: pf.SocketOrVal[pf.Vector] = None,
) -> pf.ProcNode[pf.Shader]:
    pass
def emission(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    strength: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Shader]:
    pass
def fresnel(
    ior: pf.SocketOrVal[float] = 1.5, normal: pf.SocketOrVal[pf.Vector] = None
) -> pf.ProcNode[float]:
    pass
def gamma(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1), gamma: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[pf.Color]:
    pass
class HairInfoResult(NamedTuple):
    is_strand: pf.ProcNode[float]
    intercept: pf.ProcNode[float]
    length: pf.ProcNode[float]
    thickness: pf.ProcNode[float]
    tangent_normal: pf.ProcNode[pf.Vector]
    random: pf.ProcNode[float]


def hair_info() -> HairInfoResult:
    pass
def holdout() -> pf.ProcNode[pf.Shader]:
    pass
def hue_saturation(
    hue: pf.SocketOrVal[float] = 0.5,
    saturation: pf.SocketOrVal[float] = 1.0,
    value: pf.SocketOrVal[float] = 1.0,
    fac: pf.SocketOrVal[float] = 1.0,
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
) -> pf.ProcNode[pf.Color]:
    pass
def invert(
    fac: pf.SocketOrVal[float] = 1.0, color: pf.SocketOrVal[pf.Color] = (0, 0, 0, 1)
) -> pf.ProcNode[pf.Color]:
    pass
class LayerWeightResult(NamedTuple):
    fresnel: pf.ProcNode[float]
    facing: pf.ProcNode[float]


def layer_weight(
    blend: pf.SocketOrVal[float] = 0.5,
    normal: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
) -> LayerWeightResult:
    pass
class LightFalloffResult(NamedTuple):
    quadratic: pf.ProcNode[float]
    linear: pf.ProcNode[float]
    constant: pf.ProcNode[float]


def light_falloff(
    strength: pf.SocketOrVal[float] = 100.0, smooth: pf.SocketOrVal[float] = 0.0
) -> LightFalloffResult:
    pass
class LightPathResult(NamedTuple):
    is_camera_ray: pf.ProcNode[float]
    is_shadow_ray: pf.ProcNode[float]
    is_diffuse_ray: pf.ProcNode[float]
    is_glossy_ray: pf.ProcNode[float]
    is_singular_ray: pf.ProcNode[float]
    is_reflection_ray: pf.ProcNode[float]
    is_transmission_ray: pf.ProcNode[float]
    ray_length: pf.ProcNode[float]
    ray_depth: pf.ProcNode[float]
    diffuse_depth: pf.ProcNode[float]
    glossy_depth: pf.ProcNode[float]
    transparent_depth: pf.ProcNode[float]
    transmission_depth: pf.ProcNode[float]


def light_path() -> LightPathResult:
    pass
def mapping(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    location: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    scale: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
    vector_type: Literal["POINT", "TEXTURE", "VECTOR", "NORMAL"] = "POINT",
) -> pf.ProcNode[pf.Vector]:
    pass
def mix_shader(
    factor: pf.SocketOrVal[float] = 0.5,
    a: pf.ProcNode[pf.Shader] | None = None,
    b: pf.ProcNode[pf.Shader] | None = None,
) -> pf.ProcNode[pf.Shader]:
    pass
class NormalResult(NamedTuple):
    normal: pf.ProcNode[pf.Vector]
    dot: pf.ProcNode[float]


def normal(normal: pf.SocketOrVal[pf.Vector] = (0, 0, 1)) -> NormalResult:
    pass
def normal_map(
    strength: pf.SocketOrVal[float] = 1.0,
    color: pf.SocketOrVal[pf.Color] = (0.5, 0.5, 1, 1),
    space: Literal[
        "TANGENT", "OBJECT", "WORLD", "BLENDER_OBJECT", "BLENDER_WORLD"
    ] = "TANGENT",
    uv_map: str = "",
) -> pf.ProcNode[pf.Vector]:
    pass
class ObjectInfoResult(NamedTuple):
    location: pf.ProcNode[pf.Vector]
    color: pf.ProcNode[pf.Color]
    alpha: pf.ProcNode[float]
    object_index: pf.ProcNode[int]
    material_index: pf.ProcNode[int]
    random: pf.ProcNode[float]


def object_info() -> ObjectInfoResult:
    pass
# NOTE: procfunc expects python code to `return LightResult()` instead



class ParticleInfoResult(NamedTuple):
    index: pf.ProcNode[int]
    random: pf.ProcNode[float]
    age: pf.ProcNode[float]
    lifetime: pf.ProcNode[float]
    location: pf.ProcNode[pf.Vector]
    size: pf.ProcNode[float]
    velocity: pf.ProcNode[pf.Vector]
    angular_velocity: pf.ProcNode[pf.Vector]


def particle_info() -> ParticleInfoResult:
    pass
class PointInfoResult(NamedTuple):
    position: pf.ProcNode[pf.Vector]
    radius: pf.ProcNode[float]
    random: pf.ProcNode[float]


def point_info() -> PointInfoResult:
    pass
def rgb() -> pf.ProcNode[pf.Color]:
    pass
def rgb_to_bw(
    color: pf.SocketOrVal[pf.Color] = (0.5, 0.5, 0.5, 1),
) -> pf.ProcNode[float]:
    pass
def script(
    bytecode: str = "",
    bytecode_hash: str = "",
    filepath: str = "",
    mode: Literal["INTERNAL", "EXTERNAL"] = "INTERNAL",
    script: Any = None,
    use_auto_update: bool = False,
) -> pf.ProcNode[pf.Shader]:
    pass
def shader_to_rgb(
    shader: pf.ProcNode[pf.Shader] | None = None,
) -> pf.ProcNode[pf.Color]:
    pass
def squeeze(
    value: pf.SocketOrVal[float] = 0.0,
    width: pf.SocketOrVal[float] = 1.0,
    center: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def subsurface_scattering(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    scale: pf.SocketOrVal[float] = 0.05,
    radius: pf.SocketOrVal[pf.Vector] = (1, 0.2, 0.1),
    ior: pf.SocketOrVal[float] = 1.4,
    roughness: pf.SocketOrVal[float] = 1.0,
    anisotropy: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
    falloff: Literal["BURLEY", "RANDOM_WALK", "RANDOM_WALK_SKIN"] = "RANDOM_WALK",
) -> pf.ProcNode[pf.Shader]:
    pass
def tangent(
    axis: Literal["X", "Y", "Z"] = "Z",
    direction_type: Literal["RADIAL", "UV_MAP"] = "RADIAL",
    uv_map: str = "",
) -> pf.ProcNode[pf.Vector]:
    pass
class TextureResult(NamedTuple):
    fac: pf.ProcNode[float]
    color: pf.ProcNode[pf.Color]


def brick(
    vector: pf.SocketOrVal[pf.Vector],
    color1: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    color2: pf.SocketOrVal[pf.Color] = (0.2, 0.2, 0.2, 1),
    mortar: pf.SocketOrVal[pf.Color] = (0, 0, 0, 1),
    scale: pf.SocketOrVal[float] = 5.0,
    mortar_size: pf.SocketOrVal[float] = 0.02,
    mortar_smooth: pf.SocketOrVal[float] = 0.1,
    bias: pf.SocketOrVal[float] = 0.0,
    brick_width: pf.SocketOrVal[float] = 0.5,
    row_height: pf.SocketOrVal[float] = 0.25,
    offset: float = 0.5,
    offset_frequency: int = 2,
    squash: float = 1.0,
    squash_frequency: int = 2,
) -> TextureResult:
    pass
def checker(
    vector: pf.SocketOrVal[pf.Vector],
    color1: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    color2: pf.SocketOrVal[pf.Color] = (0.2, 0.2, 0.2, 1),
    scale: pf.SocketOrVal[float] = 5.0,
) -> TextureResult:
    pass
class CoordResult(NamedTuple):
    generated: pf.ProcNode[pf.Vector]
    normal: pf.ProcNode[pf.Vector]
    uv: pf.ProcNode[pf.Vector]
    object: pf.ProcNode[pf.Vector]
    camera: pf.ProcNode[pf.Vector]
    window: pf.ProcNode[pf.Vector]


def coord(from_instancer: bool = False, object: Any = None) -> CoordResult:
    pass
class GeometryResult(NamedTuple):
    position: pf.ProcNode[pf.Vector]
    normal: pf.ProcNode[pf.Vector]
    tangent: pf.ProcNode[pf.Vector]
    true_normal: pf.ProcNode[pf.Vector]
    incoming: pf.ProcNode[pf.Vector]
    parametric: pf.ProcNode[pf.Vector]
    backfacing: pf.ProcNode[float]
    pointiness: pf.ProcNode[float]
    random_per_island: pf.ProcNode[float]


def geometry() -> GeometryResult:
    pass
TTextureInterpolationType = Literal["Linear", "Closest", "Cubic", "Smart"]  # TODO


def environment(
    vector: pf.SocketOrVal[pf.Vector],
    image: Any = None,
    interpolation: TTextureInterpolationType = "Linear",
    projection: Literal["EQUIRECTANGULAR", "MIRROR_BALL"] = "EQUIRECTANGULAR",
) -> pf.ProcNode[pf.Color]:
    pass
def gradient(
    vector: pf.SocketOrVal[pf.Vector],
    gradient_type: Literal[
        "LINEAR",
        "QUADRATIC",
        "EASING",
        "DIAGONAL",
        "SPHERICAL",
        "QUADRATIC_SPHERE",
        "RADIAL",
    ] = "LINEAR",
) -> TextureResult:
    pass
def ies(
    vector: pf.SocketOrVal[pf.Vector],
    strength: pf.SocketOrVal[float] = 1.0,
    filepath: str = "",
    ies: Any = None,
    mode: Literal["INTERNAL", "EXTERNAL"] = "INTERNAL",
) -> pf.ProcNode[float]:
    pass
def image(
    vector: pf.SocketOrVal[pf.Vector],
    extension: Literal["REPEAT", "EXTEND", "CLIP", "MIRROR"] = "REPEAT",
    image: Any = None,
    interpolation: TTextureInterpolationType = "Linear",
    projection: Literal["FLAT", "BOX", "SPHERE", "CUBE"] = "FLAT",
    projection_blend: float = 0.0,
) -> TextureResult:
    pass
def magic(
    vector: pf.SocketOrVal[pf.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    distortion: pf.SocketOrVal[float] = 1.0,
    turbulence_depth: int = 2,
) -> TextureResult:
    pass
TNoiseType = Literal[
    "MULTIFRACTAL",
    "FBM",
    "RIDGED_MULTIFRACTAL",
    "HYBRID_MULTIFRACTAL",
    "HETERO_TERRAIN",
]
TNoiseDimensions = Literal["1D", "2D", "3D", "4D"]


def noise(
    vector: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
    scale: pf.SocketOrVal[float] = 5.0,
    detail: pf.SocketOrVal[float] = 2.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    lacunarity: pf.SocketOrVal[float] = 2.0,
    offset: pf.SocketOrVal[float] = 0.0,
    gain: pf.SocketOrVal[float] = 1.0,
    distortion: pf.SocketOrVal[float] = 0.0,
    noise_dimensions: TNoiseDimensions = "3D",
    noise_type: TNoiseType = "FBM",
    normalize: bool = True,
    w: pf.SocketOrVal[float] = 0.0,
) -> TextureResult:
    pass
class PointDensityResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    density: pf.ProcNode[float]


def point_density(
    vector: pf.SocketOrVal[pf.Vector],
    interpolation: Literal["Closest", "Linear", "Cubic"] = "Linear",
    object: Any = None,
    particle_color_source: Literal[
        "PARTICLE_AGE", "PARTICLE_SPEED", "PARTICLE_VELOCITY"
    ] = "PARTICLE_AGE",
    particle_system: Any = None,
    point_source: Literal["OBJECT", "PARTICLE_SYSTEM"] = "PARTICLE_SYSTEM",
    radius: float = 0.3,
    resolution: int = 100,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
    vertex_attribute_name: str = "",
    vertex_color_source: Literal[
        "VERTEX_COLOR", "VERTEX_NORMAL", "VERTEX_WEIGHT"
    ] = "VERTEX_COLOR",
) -> PointDensityResult:
    pass
def sky(
    air_density: float = 1.0,
    altitude: float = 0.0,
    dust_density: float = 1.0,
    ground_albedo: float = 0.3,
    ozone_density: float = 1.0,
    sky_type: Literal["NISHITA", "HOSEK_WILKIE", "PREETHAM"] = "NISHITA",
    sun_direction: tuple = (0.0, 0.0, 1.0),
    sun_disc: bool = True,
    sun_elevation: float = 0.261799,
    sun_intensity: float = 1.0,
    sun_rotation: float = 0.0,
    sun_size: float = 0.009512,
    turbidity: float = 2.2,
) -> pf.ProcNode[pf.Color]:
    pass
class VoronoiResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    distance: pf.ProcNode[float]
    position: pf.ProcNode[pf.Vector]
    w: pf.ProcNode[float] | None


TDistanceMetric = Literal["EUCLIDEAN", "MANHATTAN", "CHEBYCHEV", "MINKOWSKI"]


def voronoi(
    vector: pf.SocketOrVal[pf.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    detail: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    lacunarity: pf.SocketOrVal[float] = 2.0,
    randomness: pf.SocketOrVal[float] = 1.0,
    exponent: pf.SocketOrVal[float] = 0.0,
    distance: TDistanceMetric = "EUCLIDEAN",
    feature: Literal["F1", "F2"] = "F1",
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = 0.0,
) -> VoronoiResult:
    pass
def voronoi_distance(
    vector: pf.SocketOrVal[pf.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    detail: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    lacunarity: pf.SocketOrVal[float] = 2.0,
    randomness: pf.SocketOrVal[float] = 1.0,
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def voronoi_smooth_f1(
    vector: pf.SocketOrVal[pf.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    detail: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    lacunarity: pf.SocketOrVal[float] = 2.0,
    smoothness: pf.SocketOrVal[float] = 0.5,
    randomness: pf.SocketOrVal[float] = 1.0,
    distance: TDistanceMetric = "EUCLIDEAN",
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = 0.0,
) -> VoronoiResult:
    pass
def voronoi_n_spheres_distance(
    vector: pf.SocketOrVal[pf.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    randomness: pf.SocketOrVal[float] = 1.0,
    normalize: bool = False,
) -> pf.ProcNode[float]:
    pass
def wave(
    vector: pf.SocketOrVal[pf.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    distortion: pf.SocketOrVal[float] = 0.0,
    detail: pf.SocketOrVal[float] = 2.0,
    detail_scale: pf.SocketOrVal[float] = 1.0,
    detail_roughness: pf.SocketOrVal[float] = 0.5,
    phase_offset: pf.SocketOrVal[float] = 0.0,
    bands_direction: Literal["X", "Y", "Z", "SPHERICAL"] = "X",
    rings_direction: Literal["X", "Y", "Z", "SPHERICAL"] = "X",
    wave_profile: Literal["SIN", "SAW", "TRI"] = "SIN",
    wave_type: Literal["BANDS", "RINGS"] = "BANDS",
) -> TextureResult:
    pass
def white_noise(
    vector: pf.SocketOrVal[pf.Vector] | None = None,
    noise_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = None,
) -> TextureResult:
    pass
def uv_along_stroke(use_tips: bool = False) -> pf.ProcNode[pf.Vector]:
    pass
def uv_map(from_instancer: bool = False, uv_map: str = "") -> pf.ProcNode[pf.Vector]:
    pass
class ColorRampResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    alpha: pf.ProcNode[float]


TRampInterpolationType = Literal["EASE", "CARDINAL", "LINEAR", "B_SPLINE", "CONSTANT"]


# Manual
def color_ramp(
    fac: pf.SocketOrVal[float] = 0.5,
    points: list[tuple[float, pf.Color]] | None = None,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
    interpolation: TRampInterpolationType = "LINEAR",
) -> ColorRampResult:
    pass
def value() -> pf.ProcNode[float]:
    pass
def vector_displacement(
    vector: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    midlevel: pf.SocketOrVal[float] = 0.0,
    scale: pf.SocketOrVal[float] = 1.0,
    space: Literal["TANGENT", "OBJECT", "WORLD"] = "TANGENT",
) -> pf.ProcNode[pf.Vector]:
    pass
def vertex_color(layer_name: str = "") -> pf.ProcNode[pf.Color]:
    pass
def volume_absorption(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    density: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Shader]:
    pass
def volume_info() -> pf.ProcNode:
    pass
def volume_principled(
    color: pf.SocketOrVal[pf.Color] = (0.5, 0.5, 0.5, 1),
    color_attribute: pf.SocketOrVal[str] = "",
    density: pf.SocketOrVal[float] = 1.0,
    density_attribute: pf.SocketOrVal[str] = "density",
    anisotropy: pf.SocketOrVal[float] = 0.0,
    absorption_color: pf.SocketOrVal[pf.Color] = (0, 0, 0, 1),
    emission_strength: pf.SocketOrVal[float] = 0.0,
    emission_color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    blackbody_intensity: pf.SocketOrVal[float] = 0.0,
    blackbody_tint: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    temperature: pf.SocketOrVal[float] = 1000.0,
    temperature_attribute: pf.SocketOrVal[str] = "temperature",
) -> pf.ProcNode[pf.Shader]:
    pass
def volume_scatter(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    density: pf.SocketOrVal[float] = 1.0,
    anisotropy: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.Shader]:
    pass
def wavelength(wavelength: pf.SocketOrVal[float] = 500.0) -> pf.ProcNode[pf.Color]:
    pass
def wireframe(
    size: pf.SocketOrVal[float] = 0.01, use_pixel_size: bool = False
) -> pf.ProcNode[float]:
    pass

###MODULE procfunc.nodes.geo


class AccumulateFieldResult(NamedTuple, Generic[TAttribute]):
    leading: pf.ProcNode[TAttribute]
    total: pf.ProcNode[TAttribute]
    trailing: pf.ProcNode[TAttribute]


def accumulate_field(
    value: pf.ProcNode[TAttribute] | None = None,
    group_id: pf.SocketOrVal[int] = 0,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> AccumulateFieldResult[TAttribute]:
    pass
class AttributeDomainSizeResult(NamedTuple):
    point_count: pf.ProcNode[int]
    edge_count: pf.ProcNode[int]
    face_count: pf.ProcNode[int]
    face_corner_count: pf.ProcNode[int]
    spline_count: pf.ProcNode[int]
    instance_count: pf.ProcNode[int]


def attribute_domain_size(
    geometry: pf.ProcNode[pf.Geometry],
    component: Literal["MESH", "POINTCLOUD", "CURVE", "INSTANCES"] = "MESH",
) -> AttributeDomainSizeResult:
    pass
class AttributeStatisticResult(NamedTuple, Generic[TAttribute]):
    max: pf.ProcNode[TAttribute]
    mean: pf.ProcNode[TAttribute]
    median: pf.ProcNode[TAttribute]
    min: pf.ProcNode[TAttribute]
    range: pf.ProcNode[TAttribute]
    standard_deviation: pf.ProcNode[TAttribute]
    sum: pf.ProcNode[TAttribute]
    variance: pf.ProcNode[TAttribute]


def attribute_statistic(
    geometry: pf.ProcNode[pf.Geometry],
    attribute: pf.ProcNode[TAttribute] | None = None,
    selection: pf.SocketOrVal[bool] = True,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> AttributeStatisticResult[TAttribute]:
    pass
def blur_attribute(
    value: pf.ProcNode[TAttribute] | None = None,
    iterations: pf.SocketOrVal[int] = 1,
    weight: pf.SocketOrVal[float] = 1.0,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TAttribute]:
    pass
class BoundBoxResult(NamedTuple):
    bounding_box: pf.ProcNode[pf.MeshObject]
    min: pf.ProcNode[pf.Vector]
    max: pf.ProcNode[pf.Vector]


def bound_box(geometry: pf.ProcNode[pf.Geometry]) -> BoundBoxResult:
    pass
@dataclass
class CaptureAttributeResult(Generic[TAnyGeometry]):
    geometry: pf.ProcNode[TAnyGeometry]
    attributes: dict[str, pf.ProcNode]

    def __getattr__(self, name: str) -> pf.ProcNode:
        if name in self.attributes:
            return self.attributes[name]
        else:
            return object.__getattribute__(self, name)


def capture_attribute(
    geometry: pf.ProcNode[TAnyGeometry],
    # active_index: int = 0, # TODO unsure how active_* function
    # active_item: Any = None,
    domain: TDomain = "POINT",
    **attributes: pf.SocketOrVal[TAttribute],
) -> CaptureAttributeResult[TAnyGeometry]:
    pass
def collection_info(
    collection: pf.SocketOrVal[pf.Collection],
    separate_children: pf.SocketOrVal[bool] = False,
    reset_children: pf.SocketOrVal[bool] = False,
    transform_space: Literal["ORIGINAL", "RELATIVE"] = "ORIGINAL",
) -> pf.ProcNode[pf.Instances]:
    pass
def convex_hull(geometry: pf.ProcNode[pf.Geometry]) -> pf.ProcNode[pf.MeshObject]:
    pass
class CornerResult(NamedTuple):
    corner_index: pf.ProcNode[int]
    total: pf.ProcNode[int]


def corners_of_edge(
    edge_index: pf.SocketOrVal[int] = 0,
    weights: pf.SocketOrVal[float] = 0.0,
    sort_index: pf.SocketOrVal[int] = 0,
) -> CornerResult:
    pass
def corners_of_face(
    face_index: pf.SocketOrVal[int] = 0,
    weights: pf.SocketOrVal[float] = 0.0,
    sort_index: pf.SocketOrVal[int] = 0,
) -> CornerResult:
    pass
def corners_of_vertex(
    vertex_index: pf.SocketOrVal[int] = 0,
    weights: pf.SocketOrVal[float] = 0.0,
    sort_index: pf.SocketOrVal[int] = 0,
) -> CornerResult:
    pass
def curve_arc(
    resolution: pf.SocketOrVal[int] = 16,
    radius: pf.SocketOrVal[float] = 1.0,
    start_angle: pf.SocketOrVal[float] = 0.0,
    sweep_angle: pf.SocketOrVal[float] = 5.497787,
    connect_center: pf.SocketOrVal[bool] = False,
    invert_arc: pf.SocketOrVal[bool] = False,
    mode: Literal["POINTS", "RADIUS"] = "RADIUS",
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_endpoint_selection(
    start_size: pf.SocketOrVal[int] = 1, end_size: pf.SocketOrVal[int] = 1
) -> pf.ProcNode[bool]:
    pass
# def curve_handle_type_selection(
#    handle_type: Literal["FREE", "AUTO", "VECTOR", "ALIGN"] = "AUTO",
#    mode: Literal["LEFT", "RIGHT"] = "RIGHT",
# ) -> t.ProcNode:
#    """
#    Uses a CurveHandleTypeSelection Geometry Node.
#
#    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/handle_type_selection.html
#    """
#    return t.ProcNode.from_nodetype(
#        node_type="GeometryNodeCurveHandleTypeSelection",
#        inputs={},
#        attrs={"handle_type": handle_type, "mode": mode},
#    )


def curve_length(curve: pf.ProcNode[pf.CurveObject]) -> pf.ProcNode[float]:
    pass
class CurveOfPointResult(NamedTuple):
    curve_index: pf.ProcNode[int]
    index_in_curve: pf.ProcNode[int]


def curve_of_point(point_index: pf.SocketOrVal[int] = 0) -> CurveOfPointResult:
    pass
def curve_bezier_segment(
    resolution: pf.SocketOrVal[int] = 16,
    start: pf.SocketOrVal[pf.pf.Vector] = (-1, 0, 0),
    start_handle: pf.SocketOrVal[pf.pf.Vector] = (-0.5, 0.5, 0),
    end_handle: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    end: pf.SocketOrVal[pf.pf.Vector] = (1, 0, 0),
    mode: Literal["POSITION", "OFFSET"] = "POSITION",
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_circle(
    resolution: pf.SocketOrVal[int] = 32,
    radius: pf.SocketOrVal[float] = 1.0,
    mode: Literal["POINTS", "RADIUS"] = "RADIUS",
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_line(
    start: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    end: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 1),
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_line_from_direction(
    start: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    direction: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 1),
    length: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_quadrilateral(
    width: pf.SocketOrVal[float] = 2.0,
    height: pf.SocketOrVal[float] = 2.0,
    mode: Literal[
        "RECTANGLE", "PARALLELOGRAM", "TRAPEZOID", "KITE", "POINTS"
    ] = "RECTANGLE",
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_bezier(
    resolution: pf.SocketOrVal[int] = 16,
    start: pf.SocketOrVal[pf.pf.Vector] = (-1, 0, 0),
    middle: pf.SocketOrVal[pf.pf.Vector] = (0, 2, 0),
    end: pf.SocketOrVal[pf.pf.Vector] = (1, 0, 0),
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_set_handles(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    handle_type: Literal["FREE", "AUTO", "VECTOR", "ALIGN"] = "AUTO",
    mode: Literal["LEFT", "RIGHT"] = "RIGHT",
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_spiral(
    resolution: pf.SocketOrVal[int] = 32,
    rotations: pf.SocketOrVal[float] = 2.0,
    start_radius: pf.SocketOrVal[float] = 1.0,
    end_radius: pf.SocketOrVal[float] = 2.0,
    height: pf.SocketOrVal[float] = 2.0,
    reverse: pf.SocketOrVal[bool] = False,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def curve_spline_type(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    spline_type: Literal["CATMULL_ROM", "POLY", "BEZIER", "NURBS"] = "POLY",
) -> pf.ProcNode[pf.CurveObject]:
    pass
class CurveStarResult(NamedTuple):
    curve: pf.ProcNode[pf.CurveObject]
    outer_points: pf.ProcNode[bool]


def curve_star(
    points: pf.SocketOrVal[int] = 8,
    inner_radius: pf.SocketOrVal[float] = 1.0,
    outer_radius: pf.SocketOrVal[float] = 2.0,
    twist: pf.SocketOrVal[float] = 0.0,
) -> CurveStarResult:
    pass
def curve_to_mesh(
    curve: pf.ProcNode[pf.CurveObject],
    profile_curve: pf.ProcNode[pf.CurveObject] | None = None,
    fill_caps: pf.SocketOrVal[bool] = False,
) -> pf.ProcNode[pf.MeshObject]:
    pass
class CurveToPointsResult(NamedTuple):
    points: pf.ProcNode[pf.MeshObject]
    tangent: pf.ProcNode[pf.Vector]
    normal: pf.ProcNode[pf.Vector]
    rotation: pf.ProcNode[pf.Vector]


def curve_to_points(
    curve: pf.ProcNode[pf.CurveObject],
    count: pf.SocketOrVal[int] = 10,
    length: pf.SocketOrVal[float] = 1.0,
    mode: Literal["EVALUATED", "COUNT", "LENGTH"] = "COUNT",
) -> CurveToPointsResult:
    pass
def curve_to_points_evaluated(
    curve: pf.ProcNode[pf.CurveObject],
) -> CurveToPointsResult:
    pass
def curve_to_points_count(
    curve: pf.ProcNode[pf.CurveObject],
    count: pf.SocketOrVal[int] = 10,
) -> CurveToPointsResult:
    pass
def curve_to_points_length(
    curve: pf.ProcNode[pf.CurveObject],
    length: pf.SocketOrVal[float] = 0.1,
) -> CurveToPointsResult:
    pass
def deform_curves_on_surface(
    curves: pf.ProcNode[pf.HairObject],
) -> pf.ProcNode[pf.HairObject]:
    pass
TDeleteGeometry = TypeVar(
    "TDeleteGeometry",
    pf.ProcNode[pf.MeshObject],
    pf.ProcNode[pf.CurveObject],
)


def delete_geometry(
    geometry: pf.ProcNode[TDeleteGeometry],
    selection: pf.SocketOrVal[bool] = True,
    domain: Literal["POINT", "EDGE", "FACE", "CURVE", "INSTANCE", "LAYER"] = "POINT",
    mode: Literal["ALL", "EDGE_FACE", "ONLY_FACE"] = "ALL",
) -> pf.ProcNode[TDeleteGeometry]:
    pass
def distribute_points_in_grid(
    grid: pf.SocketOrVal[float] = 0.0,
    density: pf.SocketOrVal[float] = 1.0,
    seed: pf.SocketOrVal[int] = 0,
    mode: Literal["DENSITY_RANDOM", "DENSITY_GRID"] = "DENSITY_RANDOM",
) -> pf.ProcNode[pf.MeshObject]:
    pass
def distribute_points_in_volume(
    volume: pf.ProcNode[pf.VolumeObject],
    density: pf.SocketOrVal[float] = 1.0,
    seed: pf.SocketOrVal[int] = 0,
    mode: Literal["DENSITY_RANDOM", "DENSITY_GRID"] = "DENSITY_RANDOM",
) -> pf.ProcNode[pf.VolumeObject]:
    pass
class DistributePointsOnFacesResult(NamedTuple):
    points: pf.ProcNode[pf.MeshObject]
    normal: pf.ProcNode[pf.Vector]
    rotation: pf.ProcNode[pf.Vector]


def distribute_points_on_faces(
    mesh: pf.ProcNode[pf.MeshObject],
    selection: pf.SocketOrVal[bool] = True,
    density: pf.SocketOrVal[float] | None = None,
    seed: pf.SocketOrVal[int] = 0,
    use_legacy_normal: bool = False,
) -> DistributePointsOnFacesResult:
    pass
def distribute_points_on_faces_poisson(
    mesh: pf.ProcNode[pf.MeshObject],
    selection: pf.SocketOrVal[bool] = True,
    distance_min: pf.SocketOrVal[float] = 0.0,
    density_max: pf.SocketOrVal[float] = 10.0,
    density_factor: pf.SocketOrVal[float] = 1.0,
    seed: pf.SocketOrVal[int] = 0,
    use_legacy_normal: bool = False,
) -> DistributePointsOnFacesResult:
    pass
def dual_mesh(
    mesh: pf.ProcNode[pf.MeshObject], keep_boundaries: pf.SocketOrVal[bool] = False
) -> pf.ProcNode[pf.MeshObject]:
    pass
class DuplicateElementsResult(NamedTuple, Generic[TAnyGeometry]):
    geometry: pf.ProcNode[TAnyGeometry]
    duplicate_index: pf.ProcNode[int]


def duplicate_elements(
    geometry: pf.ProcNode[TAnyGeometry],
    selection: pf.SocketOrVal[bool] = True,
    amount: pf.SocketOrVal[int] = 1,
    domain: Literal["POINT", "EDGE", "FACE", "SPLINE", "INSTANCE"] = "POINT",
) -> DuplicateElementsResult[TAnyGeometry]:
    pass
def edge_paths_to_curves(
    mesh: pf.ProcNode[pf.MeshObject],
    start_vertices: pf.SocketOrVal[bool] = True,
    next_vertex_index: pf.SocketOrVal[int] = -1,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def edge_paths_to_selection(
    start_vertices: pf.SocketOrVal[bool] = True,
    next_vertex_index: pf.SocketOrVal[int] = -1,
) -> pf.ProcNode[bool]:
    pass
class EdgesOfCornerResult(NamedTuple):
    next_edge_index: pf.ProcNode[int]
    previous_edge_index: pf.ProcNode[int]


def edges_of_corner(corner_index: pf.SocketOrVal[int] = 0) -> EdgesOfCornerResult:
    pass
class EdgesOfVertexResult(NamedTuple):
    edge_index: pf.ProcNode[int]
    total: pf.ProcNode[int]


def edges_of_vertex(
    vertex_index: pf.SocketOrVal[int] = 0,
    weights: pf.SocketOrVal[float] = 0.0,
    sort_index: pf.SocketOrVal[int] = 0,
) -> EdgesOfVertexResult:
    pass
def edges_to_face_groups(
    boundary_edges: pf.SocketOrVal[bool] = True,
) -> pf.ProcNode[int]:
    pass
class ExtrudeMeshResult(NamedTuple):
    mesh: pf.ProcNode[pf.MeshObject]
    top: pf.ProcNode[bool]
    side: pf.ProcNode[bool]


def extrude_mesh(
    mesh: pf.ProcNode[pf.MeshObject],
    selection: pf.SocketOrVal[bool] = True,
    offset: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    offset_scale: pf.SocketOrVal[float] = 1.0,
    individual: pf.SocketOrVal[bool] = True,
    mode: Literal["VERTICES", "EDGES", "FACES"] = "FACES",
) -> ExtrudeMeshResult:
    pass
class FaceOfCornerResult(NamedTuple):
    face_index: pf.ProcNode[int]
    index_in_face: pf.ProcNode[int]


def face_of_corner(corner_index: pf.SocketOrVal[int] = 0) -> FaceOfCornerResult:
    pass
def field_at_index(
    value: TAttribute | None = None,
    index: pf.SocketOrVal[int] = 0,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TAttribute]:
    pass
TFieldOnDomain = TypeVar(
    "TFieldOnDomain", pf.SocketOrVal[bool], pf.SocketOrVal[int], pf.SocketOrVal[float]
)


def field_on_domain(
    value: TFieldOnDomain = 0,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TFieldOnDomain]:
    pass
def fill_curve(
    curve: pf.ProcNode[pf.CurveObject],
    group_id: pf.SocketOrVal[int] = 0,
    mode: Literal["TRIANGLES", "NGONS"] = "TRIANGLES",
) -> pf.ProcNode[pf.MeshObject]:
    pass
def fillet_curve(
    curve: pf.ProcNode[pf.CurveObject],
    radius: pf.SocketOrVal[float] = 0.25,
    limit_radius: pf.SocketOrVal[bool] = False,
    count: pf.SocketOrVal[int] = 1,
    mode: Literal["BEZIER", "POLY"] = "BEZIER",
) -> pf.ProcNode[pf.CurveObject]:
    pass
def flip_faces(
    mesh: pf.ProcNode[pf.MeshObject], selection: pf.SocketOrVal[bool] = True
) -> pf.ProcNode[pf.MeshObject]:
    pass
def geometry_to_instance(
    geometry: pf.ProcNode[TAnyGeometry],
) -> pf.ProcNode[pf.Instances]:
    pass
def get_named_grid(
    volume: pf.ProcNode[pf.Geometry],
    name: pf.SocketOrVal[str] = "",
    remove: pf.SocketOrVal[bool] = True,
) -> pf.ProcNode:
    pass
def grid_to_mesh(
    grid: pf.SocketOrVal[float] = 0.0,
    threshold: pf.SocketOrVal[float] = 0.1,
    adaptivity: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.MeshObject]:
    pass
class ImageInfoResult(NamedTuple):
    width: pf.ProcNode[int]
    height: pf.ProcNode[int]
    has_alpha: pf.ProcNode[bool]
    frame_count: pf.ProcNode[int]
    fps: pf.ProcNode[float]


def image_info(
    image: pf.SocketOrVal[pf.Image], frame: pf.SocketOrVal[int] = 0
) -> ImageInfoResult:
    pass
def image_texture(
    image: pf.SocketOrVal[pf.Image],
    vector: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    frame: pf.SocketOrVal[int] = 0,
    extension: Literal["REPEAT", "EXTEND", "CLIP", "MIRROR"] = "REPEAT",
    interpolation: Literal["Linear", "Closest", "Cubic"] = "Linear",
) -> pf.ProcNode:
    pass
def index_of_nearest(
    position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    group_id: pf.SocketOrVal[int] = 0,
) -> pf.ProcNode[int]:
    pass
def input_active_camera() -> pf.ProcNode[pf.Object]:
    pass
class InputCurveHandlePositionsResult(NamedTuple):
    left: pf.ProcNode[pf.Vector]
    right: pf.ProcNode[pf.Vector]


def input_curve_handle_positions(
    relative: pf.SocketOrVal[bool] = False,
) -> InputCurveHandlePositionsResult:
    pass
def input_curve_tilt() -> pf.ProcNode[float]:
    pass
def input_edge_smooth() -> pf.ProcNode[bool]:
    pass
def input_id() -> pf.ProcNode[int]:
    pass
def input_image(image: Any = None) -> pf.ProcNode[pf.Image]:
    pass
def input_index() -> pf.ProcNode[int]:
    pass
def input_instance_rotation() -> pf.ProcNode[pf.Vector]:
    pass
def input_instance_scale() -> pf.ProcNode[pf.Vector]:
    pass
def input_material(material: Any = None) -> pf.ProcNode[pf.Material]:
    pass
def input_material_index() -> pf.ProcNode[int]:
    pass
class InputMeshEdgeAngleResult(NamedTuple):
    unsigned_angle: pf.ProcNode[float]
    signed_angle: pf.ProcNode[float]


def input_mesh_edge_angle() -> InputMeshEdgeAngleResult:
    pass
def input_mesh_edge_neighbors() -> pf.ProcNode[int]:
    pass
class InputMeshEdgeVerticesResult(NamedTuple):
    vertex_index_1: pf.ProcNode[int]
    vertex_index_2: pf.ProcNode[int]
    position_1: pf.ProcNode[pf.Vector]
    position_2: pf.ProcNode[pf.Vector]


def input_mesh_edge_vertices() -> InputMeshEdgeVerticesResult:
    pass
def input_mesh_face_area() -> pf.ProcNode[float]:
    pass
def input_mesh_face_is_planar(
    threshold: pf.SocketOrVal[float] = 0.01,
) -> pf.ProcNode[bool]:
    pass
class InputMeshFaceNeighborsResult(NamedTuple):
    vertex_count: pf.ProcNode[int]
    face_count: pf.ProcNode[int]


def input_mesh_face_neighbors() -> InputMeshFaceNeighborsResult:
    pass
class InputMeshIslandResult(NamedTuple):
    island_index: pf.ProcNode[int]
    island_count: pf.ProcNode[int]


def input_mesh_island() -> InputMeshIslandResult:
    pass
class InputMeshVertexNeighborsResult(NamedTuple):
    vertex_count: pf.ProcNode[int]
    face_count: pf.ProcNode[int]


def input_mesh_vertex_neighbors() -> InputMeshVertexNeighborsResult:
    pass
class InputNamedAttributeResult(NamedTuple):
    attribute: pf.ProcNode
    exists: pf.ProcNode[bool]


def input_named_attribute(
    name: pf.SocketOrVal[str] = "",
    data_type: NodeDataType | None = None,
) -> InputNamedAttributeResult:
    pass
def input_named_layer_selection(name: pf.SocketOrVal[str] = "") -> pf.ProcNode[bool]:
    pass
def input_normal() -> pf.ProcNode[pf.Vector]:
    pass
def input_position() -> pf.ProcNode[pf.Vector]:
    pass
def input_radius() -> pf.ProcNode[float]:
    pass
class InputSceneTimeResult(NamedTuple):
    seconds: pf.ProcNode[float]
    frame: pf.ProcNode[int]


def input_scene_time() -> InputSceneTimeResult:
    pass
def input_shade_smooth() -> pf.ProcNode[bool]:
    pass
class InputShortestEdgePathsResult(NamedTuple):
    next_vertex_index: pf.ProcNode[int]
    total_cost: pf.ProcNode[float]


def input_shortest_edge_paths(
    end_vertex: pf.SocketOrVal[bool] = False, edge_cost: pf.SocketOrVal[float] = 1.0
) -> InputShortestEdgePathsResult:
    pass
def input_spline_cyclic() -> pf.ProcNode[bool]:
    pass
def input_spline_resolution() -> pf.ProcNode[int]:
    pass
def input_tangent() -> pf.ProcNode[pf.Vector]:
    pass
def instance_on_points(
    points: pf.ProcNode[pf.Geometry] | None = None,
    instance: pf.ProcNode[pf.Geometry] | None = None,
    selection: pf.SocketOrVal[bool] = True,
    pick_instance: pf.SocketOrVal[bool] = False,
    instance_index: pf.SocketOrVal[int] = 0,
    rotation: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    scale: pf.SocketOrVal[pf.pf.Vector] = (1, 1, 1),
) -> pf.ProcNode[pf.Instances]:
    pass
def instance_transform() -> pf.ProcNode:
    pass
def instances_to_points(
    instances: pf.ProcNode[pf.Instances] | None = None,
    selection: pf.SocketOrVal[bool] = True,
    position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    radius: pf.SocketOrVal[float] = 0.05,
) -> pf.ProcNode[pf.Points]:
    pass
class InterpolateCurvesResult(NamedTuple):
    curves: pf.ProcNode[pf.HairObject]
    closest_index: pf.ProcNode[int]
    closest_weight: pf.ProcNode[float]


def interpolate_curves(
    guide_curves: pf.ProcNode[pf.HairObject],
    points: pf.ProcNode[pf.Geometry],
    guide_up: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    guide_group_id: pf.SocketOrVal[int] = 0,
    point_up: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    point_group_id: pf.SocketOrVal[int] = 0,
    max_neighbors: pf.SocketOrVal[int] = 4,
) -> InterpolateCurvesResult:
    pass
def is_viewport() -> pf.ProcNode[bool]:
    pass
def join_geometry(
    geometries: list[pf.ProcNode[TAnyGeometry]],
) -> pf.ProcNode[TAnyGeometry]:
    pass
def material_selection(
    material: pf.SocketOrVal[pf.Material] = None,
) -> pf.ProcNode[bool]:
    pass
def merge_by_distance(
    geometry: pf.ProcNode[pf.Geometry],
    selection: pf.SocketOrVal[bool] = True,
    distance: pf.SocketOrVal[float] = 0.001,
    mode: Literal["ALL", "CONNECTED"] = "ALL",
) -> pf.ProcNode[pf.Geometry]:
    pass
def mesh_boolean(
    mesh_1: pf.ProcNode[pf.Geometry] | None = None,
    mesh_2: pf.ProcNode[pf.Geometry] | None = None,
    self_intersection: pf.SocketOrVal[bool] = False,
    hole_tolerant: pf.SocketOrVal[bool] = False,
    operation: Literal["INTERSECT", "UNION", "DIFFERENCE"] = "DIFFERENCE",
    solver: Literal["EXACT", "FLOAT"] = "FLOAT",
) -> pf.ProcNode[pf.MeshObject]:
    pass
def mesh_circle(
    vertices: pf.SocketOrVal[int] = 32,
    radius: pf.SocketOrVal[float] = 1.0,
    fill_type: Literal["NONE", "NGON", "TRIANGLE_FAN"] = "NONE",
) -> pf.ProcNode[pf.MeshObject]:
    pass
class MeshResult(NamedTuple):
    mesh: pf.ProcNode[pf.MeshObject]
    uv_map: pf.ProcNode[pf.MeshObject]


class MeshConeResult(NamedTuple):
    mesh: pf.ProcNode[pf.MeshObject]
    uv_map: pf.ProcNode[pf.MeshObject]
    top: pf.ProcNode[pf.MeshObject]
    bottom: pf.ProcNode[pf.MeshObject]
    side: pf.ProcNode[pf.MeshObject]


def mesh_cone(
    vertices: pf.SocketOrVal[int] = 32,
    side_segments: pf.SocketOrVal[int] = 1,
    fill_segments: pf.SocketOrVal[int] = 1,
    radius_top: pf.SocketOrVal[float] = 0.0,
    radius_bottom: pf.SocketOrVal[float] = 1.0,
    depth: pf.SocketOrVal[float] = 2.0,
    fill_type: Literal["NONE", "NGON", "TRIANGLE_FAN"] = "NGON",
) -> MeshConeResult:
    pass
def mesh_cube(
    size: pf.SocketOrVal[pf.pf.Vector] = (1, 1, 1),
    vertices_x: pf.SocketOrVal[int] = 2,
    vertices_y: pf.SocketOrVal[int] = 2,
    vertices_z: pf.SocketOrVal[int] = 2,
) -> MeshResult:
    pass
class MeshCylinderResult(NamedTuple):
    mesh: pf.ProcNode[pf.MeshObject]
    top: pf.ProcNode[pf.MeshObject]
    side: pf.ProcNode[pf.MeshObject]
    bottom: pf.ProcNode[pf.MeshObject]
    uv_map: pf.ProcNode[pf.MeshObject]


def mesh_cylinder(
    vertices: pf.SocketOrVal[int] = 32,
    side_segments: pf.SocketOrVal[int] = 1,
    fill_segments: pf.SocketOrVal[int] = 1,
    radius: pf.SocketOrVal[float] = 1.0,
    depth: pf.SocketOrVal[float] = 2.0,
    fill_type: Literal["NONE", "NGON", "TRIANGLE_FAN"] = "NGON",
) -> MeshCylinderResult:
    pass
def mesh_face_set_boundaries(
    face_group_id: pf.SocketOrVal[int] = 0,
) -> pf.ProcNode[bool]:
    pass
def mesh_grid(
    size_x: pf.SocketOrVal[float] = 1.0,
    size_y: pf.SocketOrVal[float] = 1.0,
    vertices_x: pf.SocketOrVal[int] = 3,
    vertices_y: pf.SocketOrVal[int] = 3,
) -> MeshResult:
    pass
def mesh_icosphere(
    radius: pf.SocketOrVal[float] = 1.0, subdivisions: pf.SocketOrVal[int] = 1
) -> MeshResult:
    pass
def mesh_line(
    start_location: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    offset: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 1),
    count: pf.SocketOrVal[int] = 10,
    count_mode: Literal["TOTAL", "RESOLUTION"] = "TOTAL",
) -> pf.ProcNode[pf.MeshObject]:
    pass
def mesh_line_from_endpoints(
    start_location: pf.SocketOrVal[pf.pf.Vector],
    end_location: pf.SocketOrVal[pf.pf.Vector],
    count: pf.SocketOrVal[int] = 10,
    count_mode: Literal["TOTAL", "RESOLUTION"] = "TOTAL",
) -> pf.ProcNode[pf.MeshObject]:
    pass
def mesh_to_curve(
    mesh: pf.ProcNode[pf.MeshObject], selection: pf.SocketOrVal[bool] = True
) -> pf.ProcNode[pf.CurveObject]:
    pass
def mesh_to_density_grid(
    mesh: pf.ProcNode[pf.MeshObject],
    density: pf.SocketOrVal[float] = 1.0,
    voxel_size: pf.SocketOrVal[float] = 0.3,
    gradient_width: pf.SocketOrVal[float] = 0.2,
) -> pf.ProcNode:
    pass
def mesh_to_points(
    mesh: pf.ProcNode[pf.MeshObject],
    selection: pf.SocketOrVal[bool] = True,
    position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    radius: pf.SocketOrVal[float] = 0.05,
    mode: Literal["VERTICES", "EDGES", "FACES", "CORNERS"] = "VERTICES",
) -> pf.ProcNode[pf.Points]:
    pass
def mesh_to_sdf_grid(
    mesh: pf.ProcNode[pf.MeshObject],
    voxel_size: pf.SocketOrVal[float] = 0.3,
    band_width: pf.SocketOrVal[int] = 3,
) -> pf.ProcNode:
    pass
def mesh_to_volume(
    mesh: pf.ProcNode[pf.MeshObject],
    density: pf.SocketOrVal[float] = 1.0,
    voxel_amount: pf.SocketOrVal[float] = 64.0,
    interior_band_width: pf.SocketOrVal[float] = 0.2,
    resolution_mode: Literal["VOXEL_AMOUNT", "VOXEL_SIZE"] = "VOXEL_AMOUNT",
) -> pf.ProcNode[pf.VolumeObject]:
    pass
def mesh_uv_sphere(
    segments: pf.SocketOrVal[int] = 32,
    rings: pf.SocketOrVal[int] = 16,
    radius: pf.SocketOrVal[float] = 1.0,
) -> MeshResult:
    pass
TObjectInfo = TypeVar("TObjectInfo", pf.MeshObject, pf.CurveObject, pf.VolumeObject)


class ObjectInfoResult(NamedTuple, Generic[TObjectInfo]):
    geometry: pf.ProcNode[TObjectInfo]
    transform: pf.ProcNode[pf.Vector]
    location: pf.ProcNode[pf.Vector]
    rotation: pf.ProcNode[pf.Vector]
    scale: pf.ProcNode[pf.Vector]


def object_info(
    object: pf.SocketOrVal[TObjectInfo],
    as_instance: pf.SocketOrVal[bool] = False,
    transform_space: Literal["ORIGINAL", "RELATIVE"] = "ORIGINAL",
) -> ObjectInfoResult[TObjectInfo]:
    pass
def offset_corner_in_face(
    corner_index: pf.SocketOrVal[int] = 0, offset: pf.SocketOrVal[int] = 0
) -> pf.ProcNode[int]:
    pass
class OffsetPointInCurveResult(NamedTuple):
    is_valid_offset: pf.ProcNode[bool]
    point_index: pf.ProcNode[int]


def offset_point_in_curve(
    point_index: pf.SocketOrVal[int] = 0, offset: pf.SocketOrVal[int] = 0
) -> OffsetPointInCurveResult:
    pass
def points(
    count: pf.SocketOrVal[int] = 1,
    position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    radius: pf.SocketOrVal[float] = 0.1,
) -> pf.ProcNode[pf.Points]:
    pass
class PointsOfCurveResult(NamedTuple):
    point_index: pf.ProcNode[int]
    total: pf.ProcNode[int]


def points_of_curve(
    curve_index: pf.SocketOrVal[int] = 0,
    weights: pf.SocketOrVal[float] = 0.0,
    sort_index: pf.SocketOrVal[int] = 0,
) -> PointsOfCurveResult:
    pass
def points_to_curves(
    points: pf.ProcNode[pf.Geometry],
    curve_group_id: pf.SocketOrVal[int] = 0,
    weight: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def points_to_sdf_grid(
    points: pf.ProcNode[pf.Points],
    radius: pf.SocketOrVal[float] = 0.5,
    voxel_size: pf.SocketOrVal[float] = 0.3,
) -> pf.ProcNode:
    pass
def points_to_vertices(
    points: pf.ProcNode[pf.Points], selection: pf.SocketOrVal[bool] = True
) -> pf.ProcNode[pf.MeshObject]:
    pass
def points_to_volume(
    points: pf.ProcNode[pf.Points],
    density: pf.SocketOrVal[float] = 1.0,
    voxel_amount: pf.SocketOrVal[float] = 64.0,
    radius: pf.SocketOrVal[float] = 0.5,
    resolution_mode: Literal["VOXEL_AMOUNT", "VOXEL_SIZE"] = "VOXEL_AMOUNT",
) -> pf.ProcNode[pf.VolumeObject]:
    pass
class ProximityResult(NamedTuple):
    position: pf.ProcNode[pf.pf.Vector]
    distance: pf.ProcNode[float]
    is_valid: pf.ProcNode[bool]


def proximity(
    geometry: pf.ProcNode[pf.MeshObject],
    group_id: pf.SocketOrVal[int] = 0,
    sample_position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    sample_group_id: pf.SocketOrVal[int] = 0,
    target_element: Literal["POINTS", "EDGES", "FACES"] = "FACES",
) -> ProximityResult:
    pass
TRaycast = TypeVar(
    "TRaycast", pf.SocketOrVal[bool], pf.SocketOrVal[int], pf.SocketOrVal[float]
)


class RaycastResult(NamedTuple):
    attribute: pf.ProcNode[pf.pf.Vector]
    hit_distance: pf.ProcNode[float]
    hit_normal: pf.ProcNode[pf.pf.Vector]
    hit_position: pf.ProcNode[pf.pf.Vector]
    is_hit: pf.ProcNode[bool]


def raycast(
    geometry: pf.ProcNode[pf.MeshObject],
    attribute: TRaycast = 0,
    ray_direction: pf.SocketOrVal[pf.pf.Vector] = (0, 0, -1),
    ray_length: pf.SocketOrVal[float] = 100.0,
    source_position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    mapping: Literal["INTERPOLATED", "NEAREST"] = "INTERPOLATED",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> RaycastResult:
    pass
def realize_instances(
    geometry: pf.ProcNode[pf.Geometry] | pf.ProcNode[pf.Instances],
    selection: pf.SocketOrVal[bool] = True,
    realize_all: pf.SocketOrVal[bool] = True,
    depth: pf.SocketOrVal[int] = 0,
) -> pf.ProcNode[pf.Geometry]:
    pass
def remove_attribute(
    geometry: pf.ProcNode[TAnyGeometry],
    name: pf.SocketOrVal[str] = "",
    pattern_mode: Literal["EXACT", "WILDCARD"] = "EXACT",
) -> pf.ProcNode[TAnyGeometry]:
    pass
def replace_material(
    geometry: pf.ProcNode[pf.MeshObject],
    old: pf.SocketOrVal[pf.Material] | None = None,
    new: pf.SocketOrVal[pf.Material] | None = None,
) -> pf.ProcNode[pf.MeshObject]:
    pass
def resample_curve_evaluated(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def resample_curve_count(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    count: pf.SocketOrVal[int] = 10,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def resample_curve_length(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    length: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def reverse_curve(
    curve: pf.ProcNode[pf.CurveObject], selection: pf.SocketOrVal[bool] = True
) -> pf.ProcNode[pf.CurveObject]:
    pass
def rotate_instances(
    instances: pf.ProcNode[pf.Instances],
    selection: pf.SocketOrVal[bool] = True,
    rotation: Any = (0, 0, 0),
    pivot_point: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    local_space: pf.SocketOrVal[bool] = True,
) -> pf.ProcNode[pf.Instances]:
    pass
def sdf_grid_boolean(
    grid_1: pf.SocketOrVal[float] = 0.0, grid_2: pf.SocketOrVal[float] = 0.0
) -> pf.ProcNode[pf.Geometry]:
    pass
class SampleCurveResult(NamedTuple):
    normal: pf.ProcNode[pf.pf.Vector]
    position: pf.ProcNode[pf.pf.Vector]
    tangent: pf.ProcNode[pf.pf.Vector]
    value: pf.ProcNode[TAttribute]


def sample_curve(
    curves: pf.ProcNode[pf.Geometry],
    curve_index: pf.SocketOrVal[int] = 0,
    factor: pf.SocketOrVal[float] = 0.0,
    value: pf.SocketOrVal[TAttribute] | None = None,
    mode: Literal["FACTOR", "LENGTH"] = "FACTOR",
    use_all_curves: bool = False,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> SampleCurveResult:
    pass
def sample_curve_length(
    curves: pf.ProcNode[pf.Geometry],
    length: pf.SocketOrVal[float] = 0.0,
    curve_index: pf.SocketOrVal[int] = 0,
    value: pf.SocketOrVal[TAttribute] | None = None,
    use_all_curves: bool = False,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> SampleCurveResult:
    pass
def sample_index(
    geometry: pf.ProcNode[TAnyGeometry],
    index: pf.SocketOrVal[int] = 0,
    value: pf.ProcNode[TAttribute] | None = None,
    clamp: bool = False,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TAttribute]:
    pass
def sample_nearest(
    geometry: pf.ProcNode[pf.Points],
    sample_position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    domain: Literal["POINT", "EDGE", "FACE", "CORNER"] = "POINT",
) -> pf.ProcNode[int]:
    pass
class SampleResult(NamedTuple, Generic[TAttribute]):
    value: pf.ProcNode[TAttribute]
    is_valid: pf.ProcNode[bool]


def sample_nearest_surface(
    mesh: pf.ProcNode[pf.MeshObject],
    value: pf.ProcNode[TAttribute] | None = None,
    group_id: pf.SocketOrVal[int] = 0,
    sample_group_id: pf.SocketOrVal[int] = 0,
    sample_position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> SampleResult[TAttribute]:
    pass
def sample_uv_surface(
    mesh: pf.ProcNode[pf.MeshObject],
    value: pf.ProcNode[TAttribute] | None = None,
    sample_uv: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    uv_map: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> SampleResult[TAttribute]:
    pass
def scale_elements(
    geometry: pf.ProcNode[pf.Geometry],
    selection: pf.SocketOrVal[bool] = True,
    scale: pf.SocketOrVal[float] = 1.0,
    center: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    axis: pf.SocketOrVal[pf.pf.Vector] | None = None,
    domain: Literal["FACE", "EDGE"] = "FACE",
    scale_mode: Literal["UNIFORM", "SINGLE_AXIS"] = "UNIFORM",
) -> pf.ProcNode[pf.Geometry]:
    pass
def scale_instances(
    instances: pf.ProcNode[pf.Instances],
    selection: pf.SocketOrVal[bool] = True,
    scale: pf.SocketOrVal[pf.pf.Vector] = (1, 1, 1),
    center: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    local_space: pf.SocketOrVal[bool] = True,
) -> pf.ProcNode[pf.Instances]:
    pass
def self_object() -> pf.ProcNode[pf.Object]:
    pass
class SeparateComponentsResult(NamedTuple):
    mesh: pf.ProcNode[pf.MeshObject]
    curve: pf.ProcNode[pf.CurveObject]
    point_cloud: pf.ProcNode[pf.Points]
    volume: pf.ProcNode[pf.VolumeObject]
    instances: pf.ProcNode[pf.Instances]


def separate_components(
    geometry: pf.ProcNode[pf.Geometry],
) -> SeparateComponentsResult:
    pass
class SeparateGeometryResult(NamedTuple, Generic[TMeshOrCurve]):
    selection: pf.ProcNode[TMeshOrCurve]
    inverted: pf.ProcNode[TMeshOrCurve]


def separate_geometry(
    geometry: pf.ProcNode[TMeshOrCurve],
    selection: pf.SocketOrVal[bool] = True,
    domain: Literal["POINT", "EDGE", "FACE", "CURVE", "INSTANCE", "LAYER"] = "POINT",
) -> SeparateGeometryResult[TMeshOrCurve]:
    pass
def set_curve_handle_positions(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    position: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    offset: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    mode: Literal["LEFT", "RIGHT"] = "LEFT",
) -> pf.ProcNode[pf.CurveObject]:
    pass
def set_curve_normal(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    mode: Literal["MINIMUM_TWIST", "Z_UP", "FREE"] = "MINIMUM_TWIST",
    normal: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 1),
) -> pf.ProcNode[pf.CurveObject]:
    pass
def set_curve_radius(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    radius: pf.SocketOrVal[float] = 0.005,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def set_curve_tilt(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    tilt: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def set_id(
    geometry: pf.ProcNode[TAnyGeometry],
    selection: pf.SocketOrVal[bool] = True,
    id: pf.SocketOrVal[int] = 0,
) -> pf.ProcNode[TAnyGeometry]:
    pass
def set_instance_transform(
    instances: pf.ProcNode[pf.Instances],
    transform: pf.SocketOrVal[pf.Matrix] | None = None,
    selection: pf.SocketOrVal[bool] = True,
) -> pf.ProcNode[pf.Instances]:
    pass
def set_material(
    geometry: pf.ProcNode[pf.MeshObject],
    material: pf.SocketOrVal[pf.Material] = None,
    selection: pf.SocketOrVal[bool] = None,
) -> pf.ProcNode[pf.MeshObject]:
    pass
def set_material_index(
    geometry: pf.ProcNode[pf.MeshObject],
    selection: pf.SocketOrVal[bool] = True,
    material_index: pf.SocketOrVal[int] = 0,
) -> pf.ProcNode[pf.MeshObject]:
    pass
def set_point_radius(
    points: pf.ProcNode[pf.PointCloudObject],
    selection: pf.SocketOrVal[bool] = True,
    radius: pf.SocketOrVal[float] = 0.05,
) -> pf.ProcNode[pf.PointCloudObject]:
    pass
def set_position(
    geometry: pf.ProcNode[TAnyGeometry],
    selection: pf.SocketOrVal[bool] = True,
    position: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    offset: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[TAnyGeometry]:
    pass
def set_shade_smooth(
    geometry: pf.ProcNode[pf.MeshObject],
    selection: pf.SocketOrVal[bool] = True,
    shade_smooth: pf.SocketOrVal[bool] = True,
    domain: Literal["EDGE", "FACE"] = "FACE",
) -> pf.ProcNode[pf.MeshObject]:
    pass
def set_spline_cyclic(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    cyclic: pf.SocketOrVal[bool] = False,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def set_spline_resolution(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    resolution: pf.SocketOrVal[int] = 12,
) -> pf.ProcNode[pf.CurveObject]:
    pass
def sort_elements(
    geometry: pf.ProcNode[TAnyGeometry],
    selection: pf.SocketOrVal[bool] = True,
    group_id: pf.SocketOrVal[int] = 0,
    sort_weight: pf.SocketOrVal[float] = 0.0,
    domain: Literal["POINT", "EDGE", "FACE", "CURVE", "INSTANCE"] = "POINT",
) -> pf.ProcNode[TAnyGeometry]:
    pass
class SplineLengthResult(NamedTuple):
    length: pf.ProcNode[float]
    point_count: pf.ProcNode[int]


def spline_length() -> SplineLengthResult:
    pass
class SplineParameterResult(NamedTuple):
    factor: pf.ProcNode[float]
    length: pf.ProcNode[float]
    index: pf.ProcNode[int]


def spline_parameter() -> SplineParameterResult:
    pass
def split_edges(
    mesh: pf.ProcNode[pf.MeshObject], selection: pf.SocketOrVal[bool] = True
) -> pf.ProcNode[pf.MeshObject]:
    pass
class SplitToInstancesResult(NamedTuple):
    instances: pf.ProcNode[pf.Instances]
    group_id: pf.ProcNode[int]


def split_to_instances(
    geometry: pf.ProcNode[pf.MeshObject],
    selection: pf.SocketOrVal[bool] = True,
    group_id: pf.SocketOrVal[int] = 0,
    domain: Literal["POINT", "EDGE", "FACE", "CURVE", "INSTANCE", "LAYER"] = "POINT",
) -> SplitToInstancesResult:
    pass
def store_named_attribute(
    geometry: pf.ProcNode[TMeshOrCurve],
    name: pf.SocketOrVal[str] = "",
    selection: pf.SocketOrVal[bool] = True,
    value: pf.SocketOrVal[TAttribute] | None = None,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TMeshOrCurve]:
    pass
def store_named_grid(
    volume: pf.ProcNode[pf.Geometry],
    grid: pf.SocketOrVal[float] = 0.0,
    name: pf.SocketOrVal[str] = "",
) -> pf.ProcNode:
    pass
def string_join(
    strings: list[pf.SocketOrVal[str]],
    delimiter: pf.SocketOrVal[str] = "",
) -> pf.ProcNode[str]:
    pass
class StringToCurvesResult(NamedTuple):
    curve_instances: pf.ProcNode[pf.Instances]
    line: pf.ProcNode[pf.CurveObject]
    pivot_point: pf.ProcNode[pf.pf.Vector]


def string_to_curves(
    string: pf.SocketOrVal[str],
    size: pf.SocketOrVal[float] = 1.0,
    character_spacing: pf.SocketOrVal[float] = 1.0,
    word_spacing: pf.SocketOrVal[float] = 1.0,
    line_spacing: pf.SocketOrVal[float] = 1.0,
    text_box_width: pf.SocketOrVal[float] = 0.0,
    align_x: Literal["LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"] = "LEFT",
    align_y: Literal[
        "TOP", "TOP_BASELINE", "MIDDLE", "BOTTOM_BASELINE", "BOTTOM"
    ] = "TOP_BASELINE",
    overflow: Literal["OVERFLOW", "SCALE_TO_FIT", "TRUNCATE"] = "OVERFLOW",
    pivot_mode: Literal[
        "MIDPOINT",
        "TOP_LEFT",
        "TOP_CENTER",
        "TOP_RIGHT",
        "BOTTOM_LEFT",
        "BOTTOM_CENTER",
        "BOTTOM_RIGHT",
    ] = "BOTTOM_LEFT",
) -> StringToCurvesResult:
    pass
def subdivide_curve(
    curve: pf.ProcNode[pf.CurveObject], cuts: pf.SocketOrVal[int] = 1
) -> pf.ProcNode[pf.CurveObject]:
    pass
def subdivide_mesh(
    mesh: pf.ProcNode[pf.MeshObject], level: pf.SocketOrVal[int] = 1
) -> pf.ProcNode[pf.MeshObject]:
    pass
def subdivision_surface(
    mesh: pf.ProcNode[pf.MeshObject],
    level: pf.SocketOrVal[int] = 1,
    edge_crease: pf.SocketOrVal[float] = 0.0,
    vertex_crease: pf.SocketOrVal[float] = 0.0,
    boundary_smooth: Literal["PRESERVE_CORNERS", "ALL"] = "ALL",
    uv_smooth: Literal[
        "NONE",
        "PRESERVE_CORNERS",
        "PRESERVE_CORNERS_AND_JUNCTIONS",
        "PRESERVE_CORNERS_JUNCTIONS_AND_CONCAVE",
        "PRESERVE_BOUNDARIES",
        "SMOOTH_ALL",
    ] = "PRESERVE_BOUNDARIES",
) -> pf.ProcNode[pf.MeshObject]:
    pass
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
    # NodeDataType.IMAGE, # TODO verify support
    NodeDataType.GEOMETRY,
    NodeDataType.COLLECTION,
    # NodeDataType.TEXTURE, # TODO verify support
    NodeDataType.MATERIAL,
]



def transform(
    geometry: pf.ProcNode[TMeshOrCurve],
    translation: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    rotation: Any = (0, 0, 0),
    scale: pf.SocketOrVal[pf.pf.Vector] = (1, 1, 1),
) -> pf.ProcNode[TMeshOrCurve]:
    pass
def transform_by_matrix(
    geometry: pf.ProcNode[TMeshOrCurve],
    matrix: pf.SocketOrVal[pf.Matrix],
):
    pass
def translate_instances(
    instances: pf.ProcNode[pf.Instances],
    selection: pf.SocketOrVal[bool] = True,
    translation: pf.SocketOrVal[pf.pf.Vector] = (0, 0, 0),
    local_space: pf.SocketOrVal[bool] = True,
) -> pf.ProcNode[pf.Instances]:
    pass
def triangulate(
    mesh: pf.ProcNode[pf.MeshObject],
    selection: pf.SocketOrVal[bool] = True,
    minimum_vertices: pf.SocketOrVal[int] = 4,
    ngon_method: Literal["BEAUTY", "CLIP"] = "BEAUTY",
    quad_method: Literal[
        "BEAUTY", "FIXED", "FIXED_ALTERNATE", "SHORTEST_DIAGONAL", "LONGEST_DIAGONAL"
    ] = "SHORTEST_DIAGONAL",
) -> pf.ProcNode[pf.MeshObject]:
    pass
def trim_curve(
    curve: pf.ProcNode[pf.CurveObject],
    selection: pf.SocketOrVal[bool] = True,
    start: pf.SocketOrVal[float] = 0.0,
    end: pf.SocketOrVal[float] = 1.0,
    mode: Literal["FACTOR", "LENGTH"] = "FACTOR",
) -> pf.ProcNode[pf.CurveObject]:
    pass
def uv_pack_islands(
    uv: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    selection: pf.SocketOrVal[bool] = True,
    margin: pf.SocketOrVal[float] = 0.001,
    rotate: pf.SocketOrVal[bool] = True,
) -> pf.ProcNode[pf.Vector]:
    pass
def uv_unwrap(
    selection: pf.SocketOrVal[bool] = True,
    seam: pf.SocketOrVal[bool] = False,
    margin: pf.SocketOrVal[float] = 0.001,
    fill_holes: pf.SocketOrVal[bool] = True,
    method: Literal["ANGLE_BASED", "CONFORMAL"] = "ANGLE_BASED",
) -> pf.ProcNode[pf.Vector]:
    pass
def vertex_of_corner(corner_index: pf.SocketOrVal[int] = 0) -> pf.ProcNode[int]:
    pass
TViewer = TypeVar(
    "TViewer", pf.SocketOrVal[bool], pf.SocketOrVal[int], pf.SocketOrVal[float]
)




class ViewportTransformResult(NamedTuple):
    projection: pf.ProcNode
    view: pf.ProcNode
    is_orthographic: pf.ProcNode[bool]


def viewport_transform() -> ViewportTransformResult:
    pass
def volume_cube(
    density: pf.SocketOrVal[float] = 1.0,
    background: pf.SocketOrVal[float] = 0.0,
    min: pf.SocketOrVal[pf.pf.Vector] = (-1, -1, -1),
    max: pf.SocketOrVal[pf.pf.Vector] = (1, 1, 1),
    resolution_x: pf.SocketOrVal[int] = 32,
    resolution_y: pf.SocketOrVal[int] = 32,
    resolution_z: pf.SocketOrVal[int] = 32,
) -> pf.ProcNode[pf.VolumeObject]:
    pass
def volume_to_mesh(
    volume: pf.ProcNode[pf.VolumeObject],
    threshold: pf.SocketOrVal[float] = 0.1,
    adaptivity: pf.SocketOrVal[float] = 0.0,
    resolution_mode: Literal["GRID", "VOXEL_AMOUNT", "VOXEL_SIZE"] = "GRID",
) -> pf.ProcNode[pf.MeshObject]:
    pass