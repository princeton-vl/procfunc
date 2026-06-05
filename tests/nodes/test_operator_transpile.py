"""Every NODE_OPERATOR_TABLE row transpiles back to its Python operator symbol.

Parametrizes over each operator-backed binding (float math, vector math,
compare) and round-trips it: realize the binding to a real bpy node group via
as_nodegroup, transpile that group back to Python, and assert the generated
source uses the infix operator (e.g. ``a + b``) rather than a function call.
"""

import importlib

import bpy
import pytest

from procfunc.compute_graph.operators_info import OPERATOR_TEMPLATES, OperatorType
from procfunc.nodes import NODE_OPERATOR_TABLE
from procfunc.nodes.bpy_node_info import NodeDataType, NodeGroupType
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.transpiler.main import transpile_targets

# node_function is re-exported as a name in procfunc.nodes, shadowing the
# submodule; reach the module (and its graph-builder helper) via importlib.
_node_function_mod = importlib.import_module("procfunc.nodes.node_function")

# NOOP rows (separate_xyz) have no infix symbol to assert on.
_ROWS = [r for r in NODE_OPERATOR_TABLE if r.operator_type is not OperatorType.NOOP]
_IDS = [r.pf_func.__name__ for r in _ROWS]

_OPERANDS = {
    NodeDataType.FLOAT: (2.0, 3.0),
    NodeDataType.FLOAT_VECTOR: ((2.0, 3.0, 4.0), (5.0, 6.0, 7.0)),
}


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_operator_transpiles_to_symbol(row):
    a, b = _OPERANDS[row.value_type]

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
