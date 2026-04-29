from collections import namedtuple

from procfunc.util import pytree


def test_pytree_list_dict_tuple():
    obj = [1, {"a": 2, "b": (3, 4)}]
    children, spec = pytree.flatten(obj)
    assert children == [1, 2, 3, 4]
    assert spec.container is list
    assert spec.items[0].container is None
    assert spec.items[1].container is dict
    assert spec.items[1].items[0].container is None
    assert spec.items[1].items[1].container is tuple
    assert spec.items[1].items[1].items[0].container is None
    assert spec.items[1].items[1].items[1].container is None

    assert pytree.unflatten(children, spec) == obj


def test_pytree_namedtuple():
    nt = namedtuple("Test", ["a", "b"])
    obj = nt(1, 2)
    children, spec = pytree.flatten(obj)
    assert children == [1, 2]
    assert spec.container is nt
    assert spec.items[0].container is None
    assert spec.items[1].container is None


def test_pytree_class():
    obj = [1, {"a": 2, "b": (3, 4)}]
    obj_pt = pytree.PyTree(obj)
    assert obj_pt.obj() == obj
    assert list(obj_pt.values()) == [1, 2, 3, 4]
    assert len(obj_pt) == 4


def test_pytree_names():
    obj = {"a": 2, "b": (3, 4)}
    obj_pt = pytree.PyTree(obj)
    items = list(obj_pt.items())
    assert items[0] == ("a", 2)
    assert items[1] == ("b_0", 3)
    assert items[2] == ("b_1", 4)
