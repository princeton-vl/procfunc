"""Every NODE_OPERATOR_TABLE row transpiles back to its Python operator symbol.

Parametrizes over each operator-backed binding (float math, vector math,
compare) and round-trips it: realize the binding to a real bpy node group via
as_nodegroup, transpile that group back to Python, and assert the generated
source uses the infix operator (e.g. ``a + b``) rather than a function call.

RGBA rows are excluded: color `+`/`-`/`*` lowers to a Mix node, and the
transpiler intentionally keeps such nodes as plain mix_rgb(...) calls rather
than recovering the operator.
"""

import importlib

import bpy
import pytest

from procfunc.compute_graph.operators_info import OPERATOR_TEMPLATES, OperatorType
from procfunc.nodes import NODE_OPERATOR_TABLE, func
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.util.bpy_node_info import NodeDataType, NodeGroupType
from procfunc.transpiler.main import transpile_targets

# node_function is re-exported as a name in procfunc.nodes, shadowing the
# submodule; reach the module (and its graph-builder helper) via importlib.
_node_function_mod = importlib.import_module("procfunc.nodes.util.node_function")

# Compare ==/!= is epsilon-tolerant except for int/string, which stay exact ==.
_EXACT_EQUALITY_TYPES = (NodeDataType.INT, NodeDataType.STRING)


def _is_epsilon_equality(row):
    return (
        row.operator_type in (OperatorType.EQUAL, OperatorType.NOT_EQUAL)
        and row.value_type not in _EXACT_EQUALITY_TYPES
    )


# NOOP has no infix; RGBA lowers to mix_rgb; MOD stays named (fmod vs floored %); epsilon ==/!= stays named
_ROWS = [
    r
    for r in NODE_OPERATOR_TABLE
    if r.operator_type not in (OperatorType.NOOP, OperatorType.MOD)
    and r.value_type is not NodeDataType.RGBA
    and not _is_epsilon_equality(r)
]
_IDS = [f"{r.pf_func.__name__}_{r.value_type.name}" for r in _ROWS]

_EPSILON_EQ_ROWS = [r for r in NODE_OPERATOR_TABLE if _is_epsilon_equality(r)]
_EPSILON_EQ_IDS = [
    f"{r.pf_func.__name__}_{r.value_type.name}" for r in _EPSILON_EQ_ROWS
]

# one representative pair per dtype, plus a single value used when a row's
# operand_types calls for two *different* dtypes (e.g. vector * scalar).
_OPERANDS = {
    NodeDataType.FLOAT: (2.0, 3.0),
    NodeDataType.INT: (2, 3),
    NodeDataType.STRING: ("a", "b"),
    NodeDataType.FLOAT_VECTOR: ((2.0, 3.0, 4.0), (5.0, 6.0, 7.0)),
    NodeDataType.RGBA: ((0.1, 0.2, 0.3, 1.0), (0.4, 0.5, 0.6, 1.0)),
}
_OPERAND_SINGLE = {
    NodeDataType.FLOAT: 2.0,
    NodeDataType.INT: 2,
    NodeDataType.STRING: "a",
    NodeDataType.FLOAT_VECTOR: (2.0, 3.0, 4.0),
    NodeDataType.RGBA: (0.1, 0.2, 0.3, 1.0),
}


def _operands_for(row):
    # Mixed-operand rows declare their per-operand dtypes; same-type rows fall
    # back to the dtype pair for row.value_type.
    if row.operand_types is not None:
        return tuple(_OPERAND_SINGLE[dt] for dt in row.operand_types)
    return _OPERANDS[row.value_type]


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_operator_transpiles_to_symbol(row):
    a, b = _operands_for(row)

    def fn():
        return row.pf_func(a, b)

    graph = _node_function_mod._execute_procnode_func_to_computegraph(fn)
    nodegroup = as_nodegroup(graph, NodeGroupType.GEOMETRY)
    try:
        src = transpile_targets([nodegroup], transforms=[], add_version_comment=False)
    finally:
        bpy.data.node_groups.remove(nodegroup)

    # e.g. "{} + {}" -> " + "; surrounding spaces disambiguate * from **
    symbol = OPERATOR_TEMPLATES[row.operator_type].replace("{}", "")
    assert symbol in src, f"expected infix {symbol.strip()!r} in:\n{src}"
    assert f"{row.pf_func.__name__}(" not in src, (
        f"transpile emitted a function call instead of {symbol.strip()!r}:\n{src}"
    )


def test_color_operator_transpiles_to_mix_call():
    # RGBA `+` lowers to a Mix node; the transpiler keeps the mix_rgb call.
    row = next(
        r
        for r in NODE_OPERATOR_TABLE
        if r.value_type is NodeDataType.RGBA and r.operator_type is OperatorType.ADD
    )
    a, b = _OPERANDS[NodeDataType.RGBA]

    def fn():
        return row.pf_func(a, b)

    graph = _node_function_mod._execute_procnode_func_to_computegraph(fn)
    nodegroup = as_nodegroup(graph, NodeGroupType.GEOMETRY)
    try:
        src = transpile_targets([nodegroup], transforms=[], add_version_comment=False)
    finally:
        bpy.data.node_groups.remove(nodegroup)

    assert "mix_rgb(" in src, src
    assert " + " not in src, src


@pytest.mark.parametrize(
    "row",
    [r for r in NODE_OPERATOR_TABLE if r.operator_type is OperatorType.MOD],
    ids=lambda r: r.pf_func.__name__,
)
def test_modulo_operator_transpiles_to_named_call(row):
    a, b = _operands_for(row)

    def fn():
        return row.pf_func(a, b)

    graph = _node_function_mod._execute_procnode_func_to_computegraph(fn)
    nodegroup = as_nodegroup(graph, NodeGroupType.GEOMETRY)
    try:
        src = transpile_targets([nodegroup], transforms=[], add_version_comment=False)
    finally:
        bpy.data.node_groups.remove(nodegroup)

    assert f"{row.pf_func.__name__}(" in src, src
    assert " % " not in src, src


@pytest.mark.parametrize("row", _EPSILON_EQ_ROWS, ids=_EPSILON_EQ_IDS)
def test_epsilon_equality_transpiles_to_named_call(row):
    # float ==/!= is epsilon-tolerant, so it must stay a named call, not exact ==.
    a, b = _operands_for(row)

    def fn():
        return row.pf_func(a, b)

    graph = _node_function_mod._execute_procnode_func_to_computegraph(fn)
    nodegroup = as_nodegroup(graph, NodeGroupType.GEOMETRY)
    try:
        src = transpile_targets([nodegroup], transforms=[], add_version_comment=False)
    finally:
        bpy.data.node_groups.remove(nodegroup)

    assert f"pf.nodes.func.{row.pf_func.__name__}(" in src, src
    infix = OPERATOR_TEMPLATES[row.operator_type].format(a, b)
    assert infix not in src, f"expected named call, not infix {infix!r}:\n{src}"


def test_nondefault_epsilon_declines_operator():
    # `==` has no slot for epsilon, so a non-default value must force codegen to
    # fall back to a named call instead of silently dropping it.
    def fn():
        return func.equal(2.0, 3.0, epsilon=0.5)

    graph = _node_function_mod._execute_procnode_func_to_computegraph(fn)
    nodegroup = as_nodegroup(graph, NodeGroupType.GEOMETRY)
    try:
        src = transpile_targets([nodegroup], transforms=[], add_version_comment=False)
    finally:
        bpy.data.node_groups.remove(nodegroup)

    assert "pf.nodes.func.equal(" in src, src
    assert "epsilon=0.5" in src, src
    assert "2.0 == 3.0" not in src, src
