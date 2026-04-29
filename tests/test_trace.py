import ast
from dataclasses import dataclass
from typing import Unpack

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.transpiler import codegen


def test_normalize_args_to_kwargs():
    def func(a, *fargs, d=3):
        return a + sum(args) + d

    args = (1, 2, 3)
    kwargs = {"d": 4}
    args, kwargs = cg.normalize_args_to_kwargs(func, args, kwargs)
    assert len(args) == 2
    assert args[0] == 2
    assert args[1] == 3
    assert kwargs["a"] == 1
    assert kwargs["d"] == 4


def test_normalize_args_to_kwargs_retrieves_defaults():
    def func(a, b=2, c=3):
        return a + b + c

    args = (1,)
    kwargs = {}
    args, kwargs = cg.normalize_args_to_kwargs(func, args, kwargs)
    assert kwargs["a"] == 1
    assert kwargs["b"] == 2
    assert kwargs["c"] == 3


def test_normalize_args_to_kwargs_doesnt_mess_variadic_kwargs():
    def func(a, b, **kwargs):
        return a + b + kwargs["c"] + kwargs["d"]

    args = (1, 2)
    kwargs = {"c": 3, "d": 4}
    args, kwargs = cg.normalize_args_to_kwargs(func, args, kwargs)
    assert args == ()
    assert kwargs["a"] == 1
    assert kwargs["b"] == 2
    assert kwargs["c"] == 3
    assert kwargs["d"] == 4


def test_normalize_args_to_kwargs_doesnt_mess_unpack_dataclass():
    @dataclass
    class TestParams:
        c: int
        d: int

    def func(a, b, **parameters: Unpack[TestParams]):
        return a + b + parameters["c"] + parameters["d"]

    args = (1, 2)
    kwargs = {"c": 3, "d": 4}
    args, kwargs = cg.normalize_args_to_kwargs(func, args, kwargs)
    assert args == ()
    assert kwargs["a"] == 1
    assert kwargs["b"] == 2
    assert kwargs["c"] == 3
    assert kwargs["d"] == 4
    assert "parameters" not in kwargs


def cube_with_read_attr(size: float, attr_key: str):
    cube = pf.ops.primitives.mesh_cube(size=size)
    attr_data = pf.ops.attr.read_attribute(cube, key=attr_key)
    return {"cube": cube, "attr_data": attr_data}


def test_trace_cube():
    graph = pf.trace(cube_with_read_attr)
    nodes = list(cg.traverse_depth_first(graph, order="postorder"))

    func_nodes = [n for n in nodes if isinstance(n, cg.FunctionCallNode)]
    input_nodes = [n for n in nodes if isinstance(n, cg.InputPlaceholderNode)]

    assert len(input_nodes) == 2, nodes

    cube_node, read_node = func_nodes
    assert cube_node.func is pf.ops.primitives.mesh_cube
    assert read_node.func is pf.ops.attr.read_attribute
    assert isinstance(cube_node, cg.FunctionCallNode)
    assert isinstance(read_node, cg.FunctionCallNode)

    assert cube_node in read_node.args


def test_trace_cube_codegen():
    graph = pf.trace(cube_with_read_attr)
    code = codegen.to_python(graph, toplevel_as_maincall=False)

    print(code)

    # Check code is syntactically valid
    ast.parse(code)

    # function args
    assert "    size" in code, code
    assert "    attr_key" in code, code

    assert "key=attr_key" in code, "attr_key was called as kwargs so should be kwarg"
    assert "size" in code, "size was called as arg so should be arg"


def test_trace_cube_with_args_nodes():
    graph = pf.trace(cube_with_read_attr, size=2.0, attr_key="position")
    nodes = list(cg.traverse_depth_first(graph, order="postorder"))

    func_nodes = [n for n in nodes if isinstance(n, cg.FunctionCallNode)]
    input_nodes = [n for n in nodes if isinstance(n, cg.InputPlaceholderNode)]

    assert len(input_nodes) == 0, nodes  # these were all filled with constants
    assert len(func_nodes) == 2

    cube_node, read_node = func_nodes
    assert cube_node.func is pf.ops.primitives.mesh_cube
    assert read_node.func is pf.ops.attr.read_attribute
    assert isinstance(cube_node, cg.FunctionCallNode)
    assert isinstance(read_node, cg.FunctionCallNode)


def test_trace_cube_with_args_codegen():
    graph = pf.trace(cube_with_read_attr, size=2.0, attr_key="position")
    code = codegen.to_python(graph, toplevel_as_maincall=False)

    print(code)

    # Check code is syntactically valid
    ast.parse(code)

    # Check expected function names appear in generated code
    assert "mesh_cube" in code
    assert "read_attribute" in code

    # Check the function definition is present
    assert "def cube_with_read_attr" in code
