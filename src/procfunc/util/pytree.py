import logging
from dataclasses import dataclass
from typing import Any, Callable, Generic, Iterator, TypeVar

logger = logging.getLogger(__name__)

"""
A minimal pytree pack/unpack implementation inspired by JAX's docs.
"""


@dataclass
class PyTreeDef:
    container: type | None
    items: list["PyTreeDef"]
    aux: Any


@dataclass
class RegisteredPyTreeContainer:
    flatten_func: Callable[[Any], tuple[list[Any], Any]]
    unflatten_func: Callable[[list[Any], Any], Any]
    names_func: Callable[[Any], list[str]]


_registered_pytree_containers: dict[type, RegisteredPyTreeContainer] = {}


TRegister = TypeVar("TRegister")


def register_pytree_container(
    container: type,
    flatten_func: Callable[[TRegister], tuple[list[Any], Any]],
    unflatten_func: Callable[[list[Any], Any], TRegister],
    names_func: Callable[[TRegister], list[str]],
):
    _registered_pytree_containers[container] = RegisteredPyTreeContainer(
        flatten_func,
        unflatten_func,
        names_func,
    )


def _tuple_flatten(obj: tuple) -> tuple[list[Any], Any]:
    return list(obj), None


def _tuple_unflatten(objs: list[Any], spec: Any) -> tuple:
    return tuple(objs)


def _list_flatten(obj: list) -> tuple[list[Any], Any]:
    return obj, None


def _list_unflatten(objs: list[Any], spec: Any) -> list:
    return objs


def _dict_flatten(obj: dict) -> tuple[list[Any], Any]:
    return list(obj.values()), obj.keys()


def _dict_unflatten(objs: list[Any], spec: Any) -> dict:
    return dict(zip(spec, objs))


def _namedtuple_flatten(obj: tuple) -> tuple[list[Any], Any]:
    return list(obj), list(obj._fields)


def _namedtuple_unflatten(objs: list[Any], spec: Any) -> tuple:
    return spec.container(*objs)


def _namedtuple_names(obj: tuple) -> list[str]:
    return list(obj._fields)


register_pytree_container(
    list,
    flatten_func=lambda x: (x, None),
    unflatten_func=lambda x, spec: x,
    names_func=lambda x: [str(i) for i in range(len(x))],
)
register_pytree_container(
    dict,
    flatten_func=lambda x: (list(x.values()), x.keys()),
    unflatten_func=lambda x, spec: dict(zip(spec.aux, x)),
    names_func=lambda x: list(x.keys()),
)
register_pytree_container(
    tuple,
    flatten_func=lambda x: (list(x), None),
    unflatten_func=lambda x, spec: tuple(x),
    names_func=lambda x: [str(i) for i in range(len(x))],
)

NAMEDTUPLE_CONTAINER = RegisteredPyTreeContainer(
    flatten_func=_namedtuple_flatten,
    unflatten_func=_namedtuple_unflatten,
    names_func=_namedtuple_names,
)


def is_type_namedtuple(obj: type) -> bool:
    return issubclass(obj, tuple) and obj is not tuple


def is_obj_namedtuple(obj: Any) -> bool:
    # theres no good way to check isinstance namedtuple
    # namedtuple is a function not a type, and the returntype is only a subclass of tuple
    return is_type_namedtuple(type(obj)) and hasattr(obj, "_fields")


def flatten(obj: Any) -> tuple[list[Any], PyTreeDef]:
    registered_pytree_container = _registered_pytree_containers.get(type(obj))

    if registered_pytree_container is not None:
        flatten_func = registered_pytree_container.flatten_func
    elif is_obj_namedtuple(obj):
        flatten_func = _namedtuple_flatten
    else:
        return [obj], PyTreeDef(None, [], None)

    children, aux = flatten_func(obj)

    child_items = []
    spec_items = []
    for child in children:
        child_objs, child_spec = flatten(child)
        child_items.extend(child_objs)
        spec_items.append(child_spec)

    return child_items, PyTreeDef(type(obj), spec_items, aux)


def _get_container_funcs(container_type: type) -> RegisteredPyTreeContainer:
    rec = _registered_pytree_containers.get(container_type)
    if is_type_namedtuple(container_type):
        return NAMEDTUPLE_CONTAINER
    elif rec is None:
        return None
    else:
        return rec


def _unflatten_iterative(
    children: Iterator[Any],
    spec: PyTreeDef,
) -> Any:
    if spec.container is None:
        return next(children)

    container_spec = _get_container_funcs(spec.container)
    if container_spec is None:
        assert len(children) == 1
        return next(children)

    real_children = []
    for child_spec in spec.items:
        child = _unflatten_iterative(children, child_spec)
        real_children.append(child)

    return container_spec.unflatten_func(real_children, spec)


def unflatten(children: list[Any], spec: PyTreeDef, start_idx: int = 0) -> Any:
    return _unflatten_iterative(iter(children), spec)


def _compute_pytree_obj_names(
    obj: Any, separator: str = "_", nocontainer_name: str = ""
) -> Iterator[str]:
    container_spec = _get_container_funcs(type(obj))
    if container_spec is None:
        yield nocontainer_name
        return
    names = container_spec.names_func(obj)
    children = container_spec.flatten_func(obj)[0]

    for parentname, child in zip(names, children):
        for childname in _compute_pytree_obj_names(child, separator):
            yield (parentname + separator + childname if childname else parentname)


TItem = TypeVar("TItem")
TChildren = TypeVar("TChildren")
TChildrenNew = TypeVar("TChildrenNew")


class PyTree(Generic[TItem, TChildren]):
    """
    Data-structure for trees of python objects.Any

    Pytrees support flattening and unflattening, similar to Jax

    However, we additionally require that every registered pytree container provides names for each child.
    """

    def __init__(self, obj: TItem):
        flat = flatten(obj)
        self.children: list[TChildren] = flat[0]
        self.spec: PyTreeDef = flat[1]

    def __repr__(self):
        return f"PyTree({self.spec!r}, len(children)={len(self.children)})"

    def obj(self) -> TItem:
        """Get the original object used to construct this PyTree"""

        return unflatten(self.children, self.spec)

    def dict(self) -> dict[str, TChildren]:
        res = {}
        for name, child in self.items():
            if name in res:
                existing = res[name]
                raise ValueError(
                    f"pytree to dict had duplicate key {name} for {existing=} and {child=}"
                )
            res[name] = child
        return res

    def values(self) -> Iterator[TChildren]:
        return iter(self.children)

    def names(self, separator: str = "_", nocontainer_name: str = "") -> Iterator[str]:
        return _compute_pytree_obj_names(self.obj(), separator, nocontainer_name)

    def items(
        self, separator: str = "_", nocontainer_name: str = ""
    ) -> Iterator[tuple[str, TChildren]]:
        names = self.names(separator=separator, nocontainer_name=nocontainer_name)
        return iter(zip(names, self.children))

    def __len__(self) -> int:
        return len(self.children)

    @classmethod
    def from_values(
        cls, children: list[TChildren], spec: PyTreeDef
    ) -> "PyTree[TItem, TChildren]":
        return cls(unflatten(children, spec))

    @classmethod
    def from_children_spec(
        cls, children: list[TChildren], spec: PyTreeDef
    ) -> "PyTree[TItem, TChildren]":
        res = PyTree(None)
        res.children = children
        res.spec = spec
        return res

    def map(
        self, fn: Callable[[TChildren], TChildrenNew]
    ) -> "PyTree[TItem, TChildrenNew]":
        children = [fn(child) for child in self.children]
        return self.from_values(children, self.spec)

    def map_items(
        self, fn: Callable[[str, TChildren], TChildrenNew]
    ) -> "PyTree[TItem, TChildrenNew]":
        children = [fn(name, child) for name, child in self.items()]
        return self.from_values(children, self.spec)

    def is_single(self) -> bool:
        return self.spec.container is None

    def toplevel_type(self) -> type:
        return self.spec.container

    def children_one_level(self) -> list[Any]:
        obj = self.obj()

        container_funcs = _get_container_funcs(self.spec.container)

        child_objs = container_funcs.flatten_func(obj)[0]
        new_children = []
        for child_obj, child_spec in zip(child_objs, self.spec.items):
            if child_spec.container is not None:
                child_tree = PyTree(child_obj)
                new_children.append(child_tree)
            else:
                new_children.append(child_obj)

        return new_children

    def unflatten_one_level(
        self,
    ) -> TItem:
        container_funcs = _get_container_funcs(self.spec.container)
        return container_funcs.unflatten_func(self.children_one_level(), self.spec)

    def value(self) -> TItem:
        return unflatten(self.children, self.spec)


def repr_tree_to_str(
    tree: PyTree[Any, str] | str,
    type_namer: Callable[[type], str] | None = None,
) -> str:
    if type_namer is None:

        def type_namer(t):
            return t.__name__

    if isinstance(tree, str):
        return tree

    if tree.spec.container is None or tree.spec.container is type(None):
        assert len(tree.children) == 1, tree.children
        assert isinstance(tree.children[0], str)
        return tree.children[0]

    children = tree.children_one_level()
    childreprs = [repr_tree_to_str(child, type_namer) for child in children]

    if tree.spec.container is list:
        return f"[{', '.join(childreprs)}]"
    elif tree.spec.container is dict:
        keys = list(tree.unflatten_one_level().keys())
        return (
            "{" + ", ".join(f"{repr(k)}: {v}" for k, v in zip(keys, childreprs)) + "}"
        )
    elif tree.spec.container is tuple:
        return f"({', '.join(childreprs)})"
    elif is_type_namedtuple(tree.spec.container):
        return f"{type_namer(tree.spec.container)}({', '.join(childreprs)})"
    elif tree.spec.container in _registered_pytree_containers:
        container_funcs = _registered_pytree_containers[tree.spec.container]
        names = container_funcs.names_func(None)
        return f"{type_namer(tree.spec.container)}({', '.join(f'{n}={v}' for n, v in zip(names, childreprs))})"
    else:
        raise ValueError(f"Unsupported container type {tree.spec.container}")


__all__ = [
    "flatten",
    "unflatten",
    "PyTree",
]
