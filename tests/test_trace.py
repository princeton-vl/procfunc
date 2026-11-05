import ast
from dataclasses import dataclass
from typing import NamedTuple, Unpack

import pytest

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.codegen import codegen
from procfunc.nodes import types as t


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


class CubeResult(NamedTuple):
    mesh: pf.MeshObject


@pf.tracer.generator
def cube_result(size: float) -> CubeResult:
    return CubeResult(mesh=pf.ops.primitives.mesh_cube(size=size))


def moved_cube_reread(size: float):
    res = cube_result(size=size)
    pf.ops.object.set_transform(res.mesh, location=(1.0, 2.0, 3.0))
    pf.ops.object.set_transform(res.mesh, rotation_euler=(0.0, 0.0, 0.5))
    return res.mesh


def test_trace_mutation_through_attribute_reread():
    graph = pf.trace(moved_cube_reread)
    calls = [
        n
        for n in cg.traverse_depth_first(graph)
        if isinstance(n, cg.FunctionCallNode) and n.func is pf.ops.object.set_transform
    ]
    assert len(calls) == 2, calls
    code = codegen.to_python(graph, toplevel_as_maincall=False)
    namespace = {}
    exec(code, namespace)  # noqa: S102
    obj = namespace["moved_cube_reread"](size=1.0).item()
    assert tuple(obj.location) == (1.0, 2.0, 3.0), code
    assert abs(obj.rotation_euler.z - 0.5) < 1e-6, code


def cube_with_write_attr(size: float):
    cube = pf.ops.primitives.mesh_cube(size=size)
    pf.ops.attr.write_attribute(cube, 1.0, "crease_edge", domain="EDGE")
    pf.ops.attr.write_material_index(cube, 0)
    return cube


def test_trace_attr_writes_reach_output():
    graph = pf.trace(cube_with_write_attr)
    funcs = {
        n.func
        for n in cg.traverse_depth_first(graph)
        if isinstance(n, cg.FunctionCallNode)
    }
    assert pf.ops.attr.write_attribute in funcs
    assert pf.ops.attr.write_material_index in funcs
    code = codegen.to_python(graph, toplevel_as_maincall=False)
    assert "write_attribute" in code, code


@pf.nodes.node_function
def _rough_shader(roughness: t.SocketOrVal[float] = 0.5):
    return pf.nodes.shader.principled_bsdf(roughness=roughness)


def cubes_sharing_material(size: float):
    material = pf.Material(surface=_rough_shader(roughness=0.3))
    a = pf.ops.primitives.mesh_cube(size=size)
    b = pf.ops.primitives.mesh_cube(size=size)
    pf.ops.object.set_material(a, material=material)
    pf.ops.object.set_material(b, material=material)
    pf.ops.object.join(a, b)
    return a


def cubes_with_equal_materials(size: float):
    a = pf.ops.primitives.mesh_cube(size=size)
    b = pf.ops.primitives.mesh_cube(size=size)
    pf.ops.object.set_material(a, material=pf.Material(surface=_rough_shader(0.3)))
    pf.ops.object.set_material(b, material=pf.Material(surface=_rough_shader(0.3)))
    pf.ops.object.join(a, b)
    return a


@pytest.mark.parametrize(
    "func, num_slots",
    [(cubes_sharing_material, 1), (cubes_with_equal_materials, 2)],
)
def test_trace_preserves_material_identity(func, num_slots: int):
    assert len(func(1.0).item().material_slots) == num_slots
    graph = pf.trace(func)
    code = codegen.to_python(graph, toplevel_as_maincall=False)
    namespace = {}
    exec(code, namespace)  # noqa: S102
    traced = namespace[graph.name](size=1.0)
    assert len(traced.item().material_slots) == num_slots, code
