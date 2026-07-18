import pytest

import procfunc as pf
from procfunc import compute_graph as cg
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


def test_nodes_are_deeply_immutable_and_replaceable():
    node = cg.ProceduralNode("ShaderNodeValue", {"data_type": "FLOAT"}, {"Value": 1.0})

    with pytest.raises(AttributeError):
        node.args = ()
    with pytest.raises(TypeError):
        node.kwargs["Value"] = 2.0
    with pytest.raises(TypeError):
        node.attrs["data_type"] = "INT"

    replacement = node._replace(kwargs={"Value": 2.0})
    assert replacement.kwargs["Value"] == 2.0
    assert node.kwargs["Value"] == 1.0
