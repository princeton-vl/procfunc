"""Codegen of matrix constants and the value-repr edge cases around them:
pf.Matrix / np.ndarray values must emit valid, float-exact Python, non-finite
floats must not emit bare `inf`/`nan`, and --add_line_comments must work."""

import ast

import numpy as np
import pytest

import procfunc as pf
from procfunc.codegen import codegen
from procfunc.codegen import repr as codegen_repr

_TRANSLATION = (0.1, 2.0, 3.0)


def _transform_by_constant_matrix(geo):
    matrix = pf.Matrix.Translation(_TRANSLATION)
    return pf.nodes.geo.transform_by_matrix(geo, matrix=matrix)


def test_repr_value_matrix_is_valid_and_exact():
    # stray Matrix values are emitted as np.array constants, not pf.Matrix
    m = pf.Matrix.Translation(_TRANSLATION)
    src = codegen_repr.repr_value(m)

    ast.parse(src, mode="eval")
    restored = eval(src, {"np": np})  # noqa: S307
    assert isinstance(restored, np.ndarray)
    assert restored.dtype == np.float32
    assert np.array_equal(restored, np.array(m, dtype=np.float32))


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_repr_value_ndarray_is_valid_and_exact(dtype):
    arr = np.array(pf.Matrix.Translation(_TRANSLATION), dtype=dtype)
    src = codegen_repr.repr_value(arr)

    ast.parse(src, mode="eval")
    restored = eval(src, {"np": np})  # noqa: S307
    assert restored.dtype == arr.dtype
    assert np.array_equal(restored, arr)


def test_repr_value_ndarray_exact_beyond_printoptions_precision():
    # repr(arr) truncates to numpy printoptions precision (8); emission must not
    arr = np.array([0.123456789123456, 1e-30])
    restored = eval(codegen_repr.repr_value(arr), {"np": np})  # noqa: S307
    assert np.array_equal(restored, arr)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_repr_float_nonfinite_is_valid_python(value):
    src = codegen_repr.repr_float(value)
    restored = eval(src)  # noqa: S307
    assert restored == value or (np.isnan(restored) and np.isnan(value))


def _matrix_kwarg(graph) -> pf.Matrix | np.ndarray:
    from procfunc import compute_graph as cg

    for node in cg.traverse_depth_first(graph):
        if isinstance(node, cg.FunctionCallNode) and "matrix" in node.kwargs:
            return node.kwargs["matrix"]
    raise AssertionError("no node with a matrix kwarg found")


def test_to_python_matrix_constant_roundtrip():
    graph = pf.trace(_transform_by_constant_matrix)

    assert isinstance(_matrix_kwarg(graph), pf.Matrix)

    src = codegen.to_python(graph, toplevel_as_maincall=False)
    ast.parse(src)

    ns: dict = {}
    exec(src, ns)  # noqa: S102
    regraph = pf.trace(ns["_transform_by_constant_matrix"])

    original = np.array(_matrix_kwarg(graph), dtype=np.float32)
    restored = np.array(_matrix_kwarg(regraph), dtype=np.float32)
    assert np.array_equal(original, restored)


def test_to_python_line_comments_parse():
    graph = pf.trace(_transform_by_constant_matrix)
    src = codegen.to_python(graph, toplevel_as_maincall=False, add_line_comments=True)
    ast.parse(src)
    assert any("  # " in line for line in src.splitlines())


def test_return_annotation_has_no_trailing_space():
    graph = pf.trace(_transform_by_constant_matrix)
    src = codegen.to_python(graph, toplevel_as_maincall=False)
    annotated = [line for line in src.splitlines() if ") ->" in line]
    assert all(not line.endswith(" ") for line in annotated)


def test_printoptions_restored_on_codegen_error(monkeypatch):
    graph = pf.trace(_transform_by_constant_matrix)
    linewidth_before = np.get_printoptions()["linewidth"]

    def _boom(g):
        raise RuntimeError("injected")

    monkeypatch.setattr(codegen, "_topo_sort_subgraphs", _boom)
    with pytest.raises(RuntimeError, match="injected"):
        codegen.to_python(graph, toplevel_as_maincall=False)

    assert np.get_printoptions()["linewidth"] == linewidth_before
