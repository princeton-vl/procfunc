import operator
from enum import Enum


class OperatorType(Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    TRUEDIV = "truediv"
    POW = "pow"
    MOD = "mod"
    LESS_THAN = "lt"
    LESS_THAN_EQUAL = "le"
    GREATER_THAN = "gt"
    GREATER_THAN_EQUAL = "ge"
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    AND = "and"
    OR = "or"
    NOT = "invert"
    LSHIFT = "lshift"
    RSHIFT = "rshift"
    BIT_AND = "and"
    BIT_OR = "or"
    BIT_XOR = "xor"

    GETITEM = "getitem"

    VECTOR_PACK = "VECTOR_PACK"
    NOOP = "NOOP"


OPERATOR_TEMPLATES = {
    OperatorType.ADD: "{} + {}",
    OperatorType.SUB: "{} - {}",
    OperatorType.MUL: "{} * {}",
    OperatorType.DIV: "{} / {}",
    OperatorType.POW: "{} ** {}",
    OperatorType.MOD: "{} % {}",
    OperatorType.LESS_THAN: "{} < {}",
    OperatorType.LESS_THAN_EQUAL: "{} <= {}",
    OperatorType.GREATER_THAN: "{} > {}",
    OperatorType.GREATER_THAN_EQUAL: "{} >= {}",
    OperatorType.EQUAL: "{} == {}",
    OperatorType.NOT_EQUAL: "{} != {}",
    OperatorType.VECTOR_PACK: "({}, {}, {})",
    OperatorType.NOOP: "{}",
    OperatorType.LSHIFT: "{} << {}",
    OperatorType.RSHIFT: "{} >> {}",
    OperatorType.BIT_AND: "{} & {}",
    OperatorType.BIT_OR: "{} | {}",
    OperatorType.BIT_XOR: "{} ^ {}",
    OperatorType.GETITEM: "{}[{}]",
}

OPERATORS_TO_FUNCTIONS = {
    OperatorType.ADD: operator.add,
    OperatorType.SUB: operator.sub,
    OperatorType.MUL: operator.mul,
    OperatorType.DIV: operator.truediv,
    OperatorType.MOD: operator.mod,
    OperatorType.POW: operator.pow,
    OperatorType.LESS_THAN: operator.lt,
    OperatorType.LESS_THAN_EQUAL: operator.le,
    OperatorType.GREATER_THAN: operator.gt,
    OperatorType.GREATER_THAN_EQUAL: operator.ge,
    OperatorType.EQUAL: operator.eq,
    OperatorType.NOT_EQUAL: operator.ne,
    OperatorType.LSHIFT: operator.lshift,
    OperatorType.RSHIFT: operator.rshift,
    OperatorType.BIT_AND: operator.and_,
    OperatorType.BIT_OR: operator.or_,
    OperatorType.BIT_XOR: operator.xor,
    OperatorType.GETITEM: operator.getitem,
}

FUNCTIONS_TO_OPERATORS = {v: k for k, v in OPERATORS_TO_FUNCTIONS.items()}

REFLECTABLE_OPERATORS = {
    OperatorType.ADD,
    OperatorType.SUB,
    OperatorType.MUL,
    OperatorType.DIV,
    OperatorType.MOD,
    OperatorType.POW,
    OperatorType.LSHIFT,
    OperatorType.RSHIFT,
    OperatorType.BIT_AND,
    OperatorType.BIT_OR,
    OperatorType.BIT_XOR,
}
