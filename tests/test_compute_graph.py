import inspect

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.compute_graph import node as node_mod
from procfunc.util import pytree


def test_traverse():
    def func_a(x):
        pass

    def func_b(x):
        pass

    def func_c(a, b):
        pass

    pholder = cg.InputPlaceholderNode(default_value=None, name="input")

    a = cg.FunctionCallNode(func_a, args=(pholder,), kwargs={})
    b = cg.FunctionCallNode(func_b, args=(pholder,), kwargs={})
    c = cg.FunctionCallNode(func_c, args=(a, b), kwargs={})

    graph = cg.ComputeGraph(
        inputs=pytree.PyTree((pholder,)),
        outputs=pytree.PyTree([b, c]),
        name="test",
        metadata={},
    )

    nodes = list(cg.traverse_breadth_first(graph))
    print(nodes)
    assert nodes[0] is b
    assert nodes[1] is c
    assert nodes[2] is pholder
    assert nodes[3] is a


def test_traverse_arg_has_list_of_nodes():
    def func(geoms: list[pf.MeshObject]):
        return geoms[0]

    geom1 = cg.FunctionCallNode(pf.ops.primitives.mesh_cube, (), {})
    geom2 = cg.FunctionCallNode(pf.ops.primitives.mesh_cube, (), {})

    func_node = cg.FunctionCallNode(func, args=([geom1, geom2],), kwargs={})

    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"result": func_node}),
        name="test",
        metadata={},
    )

    nodes = list(cg.traverse_breadth_first(graph))
    assert len(nodes) == 3, nodes
    assert nodes[0] is func_node
    assert nodes[1] is geom1
    assert nodes[2] is geom2

    nodes = list(cg.traverse_depth_first(graph))
    assert len(nodes) == 3, nodes
    assert nodes[0] is geom1
    assert nodes[1] is geom2
    assert nodes[2] is func_node


def test_nodes_identity_equality_and_hashable():
    source = cg.ConstantNode(value=1.0)
    a = cg.GetAttributeNode(source, "x")
    b = cg.GetAttributeNode(source, "x")
    assert a != b
    assert len({a, b}) == 2

    p = cg.ProceduralNode(node_type="ShaderNodeValue", attrs={}, kwargs={})
    q = cg.ProceduralNode(node_type="ShaderNodeValue", attrs={}, kwargs={})
    assert p != q
    assert len({p, q}) == 2


def test_all_node_classes_identity_hashable():
    """The bpy construction cache keys by node object; an eq=True dataclass
    node (hash=None) or structural __eq__/__hash__ would break it."""
    for name, cls in inspect.getmembers(node_mod, inspect.isclass):
        if issubclass(cls, cg.Node):
            assert cls.__hash__ is object.__hash__, name
            assert cls.__eq__ is object.__eq__, name
