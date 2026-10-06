import inspect
from dataclasses import is_dataclass
from typing import Callable

import pytest

import procfunc as pf
from procfunc import codegen
from procfunc import compute_graph as cg
from procfunc.nodes import types as nt
from procfunc.util.pytree import PyTree


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


def test_nodes_expose_and_freeze_input_mappings() -> None:
    node = cg.ProceduralNode(
        node_type="ShaderNodeValue",
        attrs={"data_type": "FLOAT"},
        args=(),
        kwargs={"Value": 1.0},
    )

    assert is_dataclass(node)
    assert node.args == ()
    assert dict(node.kwargs) == {"Value": 1.0}
    with pytest.raises(AttributeError):
        node.args = (1.0,)
    with pytest.raises(TypeError):
        node.kwargs["Value"] = 2.0
    with pytest.raises(TypeError):
        node.attrs["data_type"] = "INT"

    replacement = node._replace(kwargs={"Value": 2.0})
    assert replacement.kwargs["Value"] == 2.0
    assert node.kwargs["Value"] == 1.0


def test_replace_in_graph_updates_replaced_node_children() -> None:
    inp = cg.InputPlaceholderNode(input_name="value", default_value=1.0, args=())
    call = cg.FunctionCallNode(func=pf.nodes.math.add, args=(inp, 2.0), kwargs={})
    graph = cg.ComputeGraph(
        inputs=PyTree({"value": inp}),
        outputs=PyTree(call),
        name="example",
        metadata={},
    )

    updated_input = inp._replace(default_value=None)
    updated_call = call._replace(metadata={"known_value_type": pf.ProcNode[float]})
    updated = cg.replace_in_graph(
        graph,
        {id(inp): updated_input, id(call): updated_call},
    )

    assert updated.inputs.obj()["value"] is updated.outputs.obj().args[0]


def test_node_mappings_reject_every_dict_bypass() -> None:
    node = cg.ProceduralNode("ShaderNodeValue", {"data_type": "FLOAT"}, {"Value": 1.0})

    with pytest.raises(TypeError):
        dict.__setitem__(node.kwargs, "Value", 2.0)
    with pytest.raises(TypeError):
        dict.update(node.kwargs, {"Value": 2.0})
    with pytest.raises(TypeError):
        dict.pop(node.attrs, "data_type")

    node.kwargs.__init__({"Value": 2.0})

    assert dict(node.kwargs) == {"Value": 1.0}
    assert dict(node.attrs) == {"data_type": "FLOAT"}


@pf.nodes.node_function
def _definition_inner(x: pf.ProcNode[float]) -> pf.ProcNode[float]:
    return x + 1.0


@pf.nodes.node_function
def _definition_outer(x: pf.ProcNode[float]) -> pf.ProcNode[float]:
    return _definition_inner(x=x)


def test_procnode_records_definition_metadata() -> None:
    with pf.context.override_globals(record_node_definitions=True):
        graph = pf.nodes.function_to_compute_graph(_definition_outer)
    calls = [
        node
        for node in cg.traverse_depth_first(graph)
        if isinstance(node, cg.SubgraphCallNode)
    ]
    assert calls
    assert all(node.metadata.get("definition") is not None for node in calls)


@pf.nodes.node_function
def traced_cube(size: nt.ProcNode[pf.Vector]) -> nt.ProcNode:
    components = pf.nodes.math.combine_xyz(size.x, size.y, size.z)
    mixed_size = size + (components + size.astype(dtype=pf.Vector))
    return pf.nodes.geo.mesh_cube(size=mixed_size).mesh


@pf.nodes.node_function
def nested_cube(size: nt.ProcNode[pf.Vector]) -> nt.ProcNode:
    return traced_cube(size)


def cube_object(size: pf.Vector) -> pf.MeshObject:
    return pf.nodes.to_mesh_object(nested_cube(size))


def _captured_cube():
    captured = nested_cube

    def call(size: pf.Vector) -> pf.MeshObject:
        return pf.nodes.to_mesh_object(captured(size))

    return call


def _reject_procnode(*args, **kwargs) -> None:
    raise AssertionError("A primitive executed during tracing")


@pytest.mark.parametrize("func", [cube_object, _captured_cube()])
@pytest.mark.parametrize("level", list(pf.tracer.TraceLevel))
@pytest.mark.parametrize("symbolic_size", [False, True])
def test_node_function_trace_never_constructs_procnodes(
    func: Callable,
    level: pf.tracer.TraceLevel,
    symbolic_size: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    size = pf.Vector((2, 3, 4))
    inputs = {} if symbolic_size else {"size": size}
    with monkeypatch.context() as patch:
        patch.setattr(nt.ProcNode, "__init__", _reject_procnode)
        graph = pf.trace(func, trace_level=level, **inputs)
        code = codegen.to_python(graph, toplevel_as_maincall=False)
    nodes = list(cg.traverse_depth_first(graph))
    assert not any(
        isinstance(n, (cg.ProceduralNode, cg.SubgraphCallNode)) for n in nodes
    )
    calls = [
        inspect.unwrap(n.func) for n in nodes if isinstance(n, cg.FunctionCallNode)
    ]
    assert (pf.nodes.geo.mesh_cube in calls) == (
        level == pf.tracer.TraceLevel.PRIMITIVES
    )
    namespace = {}
    exec(code, namespace)  # noqa: S102
    call_inputs = {"size": size} if symbolic_size else {}
    result = namespace[func.__name__](**call_inputs)
    assert len(result.item().data.vertices) == 8
    assert tuple(result.item().dimensions) == (6, 9, 12)


@pf.nodes.node_function
def default_cube(size: nt.SocketOrVal[pf.Vector] = None) -> nt.ProcNode:
    return pf.nodes.geo.mesh_cube(size=size + (2, 3, 4)).mesh


def default_cube_object() -> pf.MeshObject:
    return pf.nodes.to_mesh_object(default_cube())


def generic_typed_index_object() -> pf.MeshObject:
    index = pf.nodes.geo.input_index()
    index = pf.nodes.util.node_function.node_input(index, nt.ProcNode[float])
    cube = pf.nodes.geo.mesh_cube()
    mesh = pf.nodes.geo.set_position(cube.mesh, selection=index > 0.0)
    return pf.nodes.to_mesh_object(mesh)


def test_primitive_codegen_normalizes_procnode_value_type():
    graph = pf.trace(
        generic_typed_index_object, trace_level=pf.tracer.TraceLevel.PRIMITIVES
    )
    source = codegen.to_python(graph, toplevel_as_maincall=False)
    namespace = {}
    exec(source, namespace)  # noqa: S102
    result = namespace["generic_typed_index_object"]()
    assert len(result.item().data.vertices) == 8


def test_primitive_trace_preserves_socket_default():
    graph = pf.trace(default_cube_object, trace_level=pf.tracer.TraceLevel.PRIMITIVES)
    namespace = {}
    exec(codegen.to_python(graph, toplevel_as_maincall=False), namespace)  # noqa: S102
    result = namespace["default_cube_object"]()
    assert tuple(result.item().dimensions) == (2, 3, 4)
