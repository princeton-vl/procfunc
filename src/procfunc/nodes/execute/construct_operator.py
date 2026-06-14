"""Inline Python operator dispatch: resolve a traced FunctionCallNode (e.g.
`a * b`, `a == b`) against NODE_OPERATOR_TABLE and construct the matching bpy
node, including the Math-composition lowering for eq/ne/le/ge outside geometry
trees (which lack FunctionNodeCompare)."""

import logging
from typing import Any

import bpy
import numpy as np

from procfunc import compute_graph as cg
from procfunc.compute_graph.operators_info import OPERATORS_TO_FUNCTIONS
from procfunc.nodes import func as pf_func
from procfunc.nodes import math as pf_math
from procfunc.nodes.util import bpy_node_info as bni
from procfunc.nodes.util.bindings_util import ContextualNode, RuntimeResolveDataType

from . import construct_standard
from .infer_runtime_data_type import (
    VectorLike,
    _infer_value_math_type,
    infer_operation_type,
    resolve_operation_data_type,
)
from .util import NODE_OPERATOR_TABLE, NodeOperatorResolution

logger = logging.getLogger(__name__)


def _find_operator_row(
    func: Any, data_type: bni.NodeDataType
) -> NodeOperatorResolution:
    search = (
        row
        for row in NODE_OPERATOR_TABLE
        if (
            row.operand_types is None
            and row.value_type == data_type
            and OPERATORS_TO_FUNCTIONS[row.operator_type] is func
        )
    )
    op_row = next(search, None)
    if op_row is None:
        raise ValueError(
            f"User called inline binary operator to invoke {func=} on {data_type=} "
            f"but this data type does not support that operator. Consider explicitly casting to another type with val.astype()"
        )
    return op_row


_VECTORLIKE_BY_LENGTH = {
    3: bni.NodeDataType.FLOAT_VECTOR,
    4: bni.NodeDataType.RGBA,
}

# Operator types whose operands may be matched in any order against a
# NODE_OPERATOR_TABLE row's operand_types. Permuted matches for any other
# operator would silently swap operands, so they raise instead.
_COMMUTATIVE_OPERATORS = frozenset(
    {
        cg.OperatorType.ADD,
        cg.OperatorType.MUL,
        cg.OperatorType.EQUAL,
        cg.OperatorType.NOT_EQUAL,
    }
)


def _operand_matches(
    operand_dtype: bni.NodeDataType | VectorLike | None,
    row_dtype: bni.NodeDataType,
) -> bool:
    """Does a single operand satisfy a row's required dtype? A VectorLike (a
    raw tuple/list of unknown semantic) matches by its length, a concrete
    NodeDataType by equality."""
    if isinstance(operand_dtype, VectorLike):
        return _VECTORLIKE_BY_LENGTH.get(operand_dtype.length) == row_dtype
    return operand_dtype == row_dtype


def _match_operand_permutation(
    operand_dtypes: list[bni.NodeDataType | VectorLike | None],
    row_dtypes: tuple[bni.NodeDataType, ...],
    operator_type: cg.OperatorType,
) -> list[int] | None:
    """Order-insensitive greedy match: for each required row dtype, claim the
    first unused operand that satisfies it. Returns the permutation of operand
    indices (in row order) on success, else None. At least one claimed operand
    must be a concrete dtype (an anchor) — an all-VectorLike match is too
    ambiguous to commit to. A non-identity permutation is only sound for
    commutative operators and raises otherwise."""
    if len(operand_dtypes) != len(row_dtypes):
        return None

    used = [False] * len(operand_dtypes)
    permutation: list[int] = []
    for row_dtype in row_dtypes:
        idx = next(
            (
                i
                for i, dt in enumerate(operand_dtypes)
                if not used[i] and _operand_matches(dt, row_dtype)
            ),
            None,
        )
        if idx is None:
            return None
        used[idx] = True
        permutation.append(idx)

    has_anchor = any(
        not isinstance(operand_dtypes[i], VectorLike) and operand_dtypes[i] is not None
        for i in permutation
    )
    if not has_anchor:
        return None

    if (
        permutation != list(range(len(permutation)))
        and operator_type not in _COMMUTATIVE_OPERATORS
    ):
        raise ValueError(
            f"Operands {operand_dtypes} match the operator table row "
            f"{row_dtypes} for {operator_type} only after reordering, but "
            f"{operator_type} is not commutative so operands cannot be swapped."
        )

    return permutation


def _construct_operator_call(
    node: cg.FunctionCallNode,
    bl_node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
) -> bpy.types.Node | bpy.types.NodeSocket | cg.Node:
    """Construct the bpy node for an inline-operator FunctionCallNode.

    Returns either the constructed bpy node/socket, or a rewritten cg.Node
    (the eq/ne/le/ge Math-composition lowering) for the caller to construct
    recursively.
    """
    assert len(node.kwargs) == 0, node.kwargs
    inputs = [input_results[i] for i in range(len(node.args))]

    do_coerce_integers = (
        bni.NodeGroupType(bl_node_tree.bl_idname) == bni.NodeGroupType.SHADER
    )

    # Mixed-operand rows (operand_types set) take precedence over the
    # single-type path: e.g. `vector * scalar` -> VectorMath SCALE, RGBA
    # `+`/`-`/`*` -> Mix.
    operand_dtypes = [
        _infer_value_math_type(val, arg, do_coerce_integers)
        for val, arg in zip(inputs, node.args)
    ]
    for row in NODE_OPERATOR_TABLE:
        if row.operand_types is None:
            continue
        if OPERATORS_TO_FUNCTIONS[row.operator_type] is not node.func:
            continue
        permutation = _match_operand_permutation(
            operand_dtypes, row.operand_types, row.operator_type
        )
        if permutation is None:
            continue
        permuted = [inputs[i] for i in permutation]
        spec: cg.Node = row.pf_func(*permuted).item()
        # the spec already records the resolved operands as its kwarg values,
        # so bind them directly
        return construct_standard._construct_procnode_standard(
            spec, bl_node_tree, dict(spec.kwargs)
        )

    data_type = infer_operation_type(node, inputs, do_coerce_integers)
    op_res = _find_operator_row(node.func, data_type)

    spec: cg.Node = op_res.pf_func(*inputs).item()

    # pin resolved data_type so construction doesn't re-infer it and lose .astype hints
    if "data_type" in spec.attrs:
        spec.attrs["data_type"] = data_type

    if (
        lowered := _lower_compare_outside_geometry(
            spec, bl_node_tree, dict(spec.kwargs)
        )
    ) is not None:
        return lowered

    # bind spec's operands directly from its kwargs
    return construct_standard._construct_procnode_standard(
        spec, bl_node_tree, dict(spec.kwargs)
    )


def _lower_compare_outside_geometry(
    node: cg.Node,
    bl_node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
) -> cg.Node | None:
    """`==` / `!=` / `<=` / `>=` lower to FunctionNodeCompare in geometry trees,
    but that node does not exist in shader/compositor/texture trees. There a Math
    node's COMPARE/GREATER_THAN/LESS_THAN operations express each one exactly, so
    rewrite the contextual Compare node to the equivalent Math composition:

        ==  ->  COMPARE(a, b, eps)
        !=  ->  1 - COMPARE(a, b, eps)
        <=  ->  1 - GREATER_THAN(a, b)
        >=  ->  1 - LESS_THAN(a, b)

    le/ge are derived exactly without eps, matching FunctionNodeCompare whose
    LESS_EQUAL/GREATER_EQUAL ignore the Epsilon socket. The eps for eq/ne comes
    from the Compare node's own Epsilon input if given, else Blender's Compare
    node default. Returns the replacement cg.Node, or None if no rewrite applies.

    The Math lowering is scalar-only: vector/color compares would silently
    degrade to per-float implicit conversion, so those data types raise here.
    An unpinned data_type is resolved from the operands in `input_results`
    before that check, so wired vector operands raise rather than lower.

    CAVEAT: Blender's Math COMPARE clamps its epsilon to >= 1e-5 while
    FunctionNodeCompare does not, so equal(a, b, epsilon=0) can differ between
    geometry and non-geometry trees."""
    if (
        not isinstance(node, cg.ProceduralNode)
        or ContextualNode.parse_name(node.node_type) is not ContextualNode.COMPARE
        or bni.NodeGroupType(bl_node_tree.bl_idname) is bni.NodeGroupType.GEOMETRY
    ):
        return None

    operation = node.attrs.get("operation")
    if operation not in ("EQUAL", "NOT_EQUAL", "LESS_EQUAL", "GREATER_EQUAL"):
        return None

    a = node.kwargs[("A", 0)]
    b = node.kwargs[("B", 0)]

    data_type = node.attrs.get("data_type")
    if isinstance(data_type, RuntimeResolveDataType):
        data_type = resolve_operation_data_type(
            node,
            input_results,
            data_type,
            coerce_integers=bl_node_tree.bl_idname == bni.NodeGroupType.SHADER.value,
        )
    scalar_compare_types = (
        bni.NodeDataType.FLOAT,
        bni.NodeDataType.INT,
        bni.NodeDataType.BOOLEAN,
    )
    nonscalar_dtype = (
        isinstance(data_type, bni.NodeDataType)
        and data_type not in scalar_compare_types
    )
    nonscalar_operand = any(isinstance(v, (tuple, list, np.ndarray)) for v in (a, b))
    if nonscalar_dtype or nonscalar_operand:
        described = data_type if nonscalar_dtype else "tuple/vector"
        raise ValueError(
            f"Compare (operation={operation}) on {described} operands is not "
            f"supported in a {bl_node_tree.bl_idname}: only geometry trees have "
            f"FunctionNodeCompare, and the Math-node lowering used elsewhere is "
            f"scalar (FLOAT/INT/BOOLEAN) only. Build this compare in a geometry "
            f"node context instead."
        )

    match operation:
        case "EQUAL":
            eps = node.kwargs.get(("Epsilon", 0), pf_func.COMPARE_EPSILON_DEFAULT)
            return pf_math.compare(a, b, eps).item()
        case "NOT_EQUAL":
            eps = node.kwargs.get(("Epsilon", 0), pf_func.COMPARE_EPSILON_DEFAULT)
            return pf_math.subtract(1.0, pf_math.compare(a, b, eps)).item()
        case "LESS_EQUAL":
            return pf_math.subtract(1.0, pf_math.greater_than(a, b)).item()
        case "GREATER_EQUAL":
            return pf_math.subtract(1.0, pf_math.less_than(a, b)).item()
