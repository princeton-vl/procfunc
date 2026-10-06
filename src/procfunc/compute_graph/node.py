import inspect
import logging
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from procfunc.compute_graph.compute_graph import ComputeGraph

from procfunc.util.pytree import PyTree

logger = logging.getLogger(__name__)


@dataclass(frozen=True, init=False, eq=False)
class Node:
    args: tuple[Any, ...]
    kwargs: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    def __init__(
        self,
        args: tuple = (),
        kwargs: dict | None = None,
        metadata: dict | None = None,
    ) -> None:
        object.__setattr__(self, "args", tuple(args))
        object.__setattr__(self, "kwargs", MappingProxyType(dict(kwargs or {})))
        object.__setattr__(self, "metadata", MappingProxyType(dict(metadata or {})))

    def _replace(self, **changes: Any) -> "Node":
        return replace(self, **changes)

    def inputs_pytree(self) -> PyTree:
        return PyTree((self.args, self.kwargs))


@dataclass(frozen=True, init=False, eq=False)
class SubgraphCallNode(Node):
    subgraph: "ComputeGraph"

    def __init__(
        self, subgraph, args=(), kwargs=None, metadata=None, **changes
    ) -> None:
        Node.__init__(self, args, kwargs, metadata, **changes)
        object.__setattr__(self, "subgraph", subgraph)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.subgraph.name}, ...)"


@dataclass(frozen=True, init=False, eq=False)
class FunctionCallNode(Node):
    func: Callable[..., Any]

    def __init__(self, func, args=(), kwargs=None, metadata=None, **changes) -> None:
        Node.__init__(self, args, kwargs, metadata, **changes)
        object.__setattr__(self, "func", func)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.func.__name__}, ...)"


@dataclass(frozen=True, init=False, eq=False)
class MethodCallNode(Node):
    method_name: str

    def __init__(
        self,
        callee=None,
        method_name=None,
        args=(),
        kwargs=None,
        metadata=None,
        **changes,
    ) -> None:
        if callee is not None:
            args = (callee, *changes.pop("args", args))
        Node.__init__(self, args, kwargs, metadata, **changes)
        object.__setattr__(self, "method_name", method_name)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.method_name}, ...)"


@dataclass(frozen=True, init=False, eq=False)
class GetAttributeNode(Node):
    attribute_name: str

    def __init__(
        self, source=None, attribute_name=None, metadata=None, **changes
    ) -> None:
        if "args" not in changes:
            changes["args"] = (source,)
        Node.__init__(self, metadata=metadata, **changes)
        object.__setattr__(self, "attribute_name", attribute_name)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.attribute_name})"


@dataclass(frozen=True, init=False, eq=False)
class ProceduralNode(Node):
    node_type: str
    attrs: MappingProxyType

    def __init__(self, node_type, attrs, kwargs=None, metadata=None, **changes) -> None:
        Node.__init__(self, kwargs=kwargs, metadata=metadata, **changes)
        attrs = MappingProxyType(dict(attrs))
        if any(isinstance(value, Node) for value in attrs.values()):
            raise ValueError(
                f"{self.__class__.__name__}({node_type=}) received Node attrs"
            )
        object.__setattr__(self, "node_type", node_type)
        object.__setattr__(self, "attrs", attrs)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.node_type}, ...)"


@dataclass(frozen=True, init=False, eq=False)
class MutatedArgumentNode(Node):
    def __init__(
        self, original_node=None, mutator_call_node=None, metadata=None, **changes
    ) -> None:
        if "args" not in changes:
            changes["args"] = (original_node, mutator_call_node)
        Node.__init__(self, metadata=metadata, **changes)

    def __repr__(self):
        return f"{self.__class__.__name__}(...)"


@dataclass(frozen=True, init=False, eq=False)
class ConstantNode(Node):
    value: Any

    def __init__(self, value, metadata=None, **changes) -> None:
        Node.__init__(self, metadata=metadata, **changes)
        object.__setattr__(self, "value", value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


@dataclass(frozen=True, init=False, eq=False)
class InputPlaceholderNode(Node):
    input_name: str
    default_value: Any

    def __init__(
        self,
        name=None,
        default_value=None,
        metadata=None,
        *,
        input_name=None,
        **changes,
    ) -> None:
        Node.__init__(self, metadata=metadata, **changes)
        object.__setattr__(self, "input_name", input_name or name)
        object.__setattr__(self, "default_value", default_value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.default_value})"


T = TypeVar("T")


def normalize_args_to_kwargs(
    func: Callable, args: tuple, kwargs: dict
) -> tuple[tuple, dict]:
    """
    Try to fully populate kwargs, by moving over positional args & filling in defaults

    Some args may not be able to be converted to kwargs, e.g. ``*args`` have no names that work

    Args:
        func: The function whose signature we should respect
        args: The original positional arguments to the function
        kwargs: The keyword arguments to the function

    Returns:
        A tuple of (args, kwargs) where args is a tuple of positional arguments and kwargs is a dictionary of keyword arguments.

    GUARANTEE: ``func(*returned_args, **returned_kwargs) == func(*args, **kwargs)`` and does not crash
    """
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    remaining_args = ()
    updated_kwargs = {}
    for param_name, value in bound.arguments.items():
        param = sig.parameters[param_name]
        if param.kind == inspect.Parameter.VAR_POSITIONAL:  # *args
            remaining_args = value
        elif param.kind == inspect.Parameter.VAR_KEYWORD:  # **kwargs
            updated_kwargs.update(value)
        else:
            updated_kwargs[param_name] = value
    return remaining_args, updated_kwargs
