import pytest

import procfunc as pf
from procfunc.nodes import types as nt


def test_missing_annotation_error_message():
    def no_annotation(x):
        return x

    with pytest.raises(TypeError, match=r"no_annotation had argument 'x' with no type"):
        pf.nodes.function_to_compute_graph(no_annotation)


def test_non_procnode_annotation_error_message():
    def bad_annotation(x: float):
        return x

    with pytest.raises(TypeError, match=r"bad_annotation had argument x"):
        pf.nodes.function_to_compute_graph(bad_annotation)


def test_procnode_annotation_accepted():
    def ok(x: nt.ProcNode) -> nt.ProcNode:
        return x

    graph = pf.nodes.function_to_compute_graph(ok)
    assert "x" in graph.inputs.obj()
