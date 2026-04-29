import inspect
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from procfunc.compute_graph.compute_graph import ComputeGraph

from procfunc.util.pytree import PyTree

logger = logging.getLogger(__name__)


class Node:
    def __init__(self, args: tuple, kwargs: dict, metadata: dict[str, Any] = None):
        assert isinstance(args, tuple), args
        assert isinstance(kwargs, dict), kwargs
        self.args = args
        self.kwargs = kwargs
        if metadata is None:
            metadata = {}
        self.metadata = metadata

    def inputs_pytree(self) -> PyTree:
        return PyTree((self.args, self.kwargs))


class SubgraphCallNode(Node):
    def __init__(
        self,
        subgraph: "ComputeGraph",
        args: tuple,
        kwargs: dict,
        metadata: dict[str, Any] = None,
    ):
        super().__init__(args, kwargs, metadata)
        self.subgraph = subgraph

    def __repr__(self):
        return f"{self.__class__.__name__}({self.subgraph.name}, ...)"


class FunctionCallNode(Node):
    def __init__(
        self,
        func: Callable[..., Any],
        args: tuple,
        kwargs: dict,
        metadata: dict[str, Any] = None,
    ):
        super().__init__(args=args, kwargs=kwargs, metadata=metadata)
        self.func = func

    def __repr__(self):
        return f"{self.__class__.__name__}({self.func.__name__}, ...)"


class MethodCallNode(Node):
    """
    represents an {args[0]}.{method_name}(*args[1:], **kwargs) call

    - the node to be used as `self` is the first arg, since it is a dynamic value
    - the method name is assumed to be const
    """

    def __init__(
        self,
        callee: Node,
        method_name: str,
        args: tuple,
        kwargs: dict,
        metadata: dict[str, Any] = None,
    ):
        super().__init__(args=(callee, *args), kwargs=kwargs, metadata=metadata)
        self.method_name = method_name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.method_name}, ...)"


@dataclass
class GetAttributeNode(Node):
    def __init__(
        self, source: Node, attribute_name: str, metadata: dict[str, Any] = None
    ):
        # store source as args since it is a Node and may need to be recursively constructed
        super().__init__(args=(source,), kwargs={}, metadata=metadata)
        self.attribute_name = attribute_name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.attribute_name})"


@dataclass
class ProceduralNode(Node):
    def __init__(
        self,
        node_type: str,
        attrs: dict[str, Any],
        kwargs: dict,
        metadata: dict[str, Any] = None,
    ):
        super().__init__(args=(), kwargs=kwargs, metadata=metadata)
        self.node_type = node_type

        for k, v in attrs.items():
            if isinstance(v, Node):
                raise ValueError(
                    f"{self.__class__.__name__}({node_type=}) recieved attrs with non-constant value {k}={v}. "
                    "(Node values are not allowed as attrs)"
                )
        self.attrs = attrs

    def __repr__(self):
        return f"{self.__class__.__name__}({self.node_type}, ...)"


class MutatedArgumentNode(Node):
    def __init__(
        self,
        original_node: "Node",
        mutator_call_node: "FunctionCallNode | MethodCallNode",
        metadata: dict[str, Any] = None,
    ):
        # store orig/mutator as args() since they are Node and may need to be recursively constructed
        super().__init__(
            args=(original_node, mutator_call_node), kwargs={}, metadata=metadata
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(...)"


class ConstantNode(Node):
    def __init__(self, value: Any, metadata: dict[str, Any] = None):
        super().__init__(args=(), kwargs={}, metadata=metadata)
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


class InputPlaceholderNode(Node):
    def __init__(self, name: str, default_value: Any, metadata: dict[str, Any] = None):
        super().__init__(args=(), kwargs={}, metadata=metadata)
        self.input_name = name
        self.default_value = default_value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.default_value})"


T = TypeVar("T")


def normalize_args_to_kwargs(
    func: Callable,
    args: tuple,
    kwargs: dict,
) -> tuple[tuple, dict]:
    """
    Try to fully populate kwargs, by moving over positional args & filling in defaults

    Some args may not be able to be converted to kwargs, e.g. *args have no names that work

    Args:
        func: The function whose signature we should respect
        args: The original positional arguments to the function
        kwargs: The keyword arguments to the function

    Returns:
        A tuple of (args, kwargs) where args is a tuple of positional arguments and kwargs is a dictionary of keyword arguments.

    GUARANTEE: func(*returned_args, **returned_kwargs) == func(*args, **kwargs) and does not crash
    """

    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()  # optional: fills in default values

    # Extract any *args parameter back to args tuple
    remaining_args = ()
    updated_kwargs = {}

    for param_name, value in bound.arguments.items():
        param = sig.parameters[param_name]
        if param.kind == inspect.Parameter.VAR_POSITIONAL:  # *args
            remaining_args = value
        elif param.kind == inspect.Parameter.VAR_KEYWORD:  # **kwargs
            # Unpack **kwargs back to individual kwargs instead of wrapping in dict
            updated_kwargs.update(value)
        else:
            updated_kwargs[param_name] = value

    if False and logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            f"normalized {func.__name__} with {args=} {kwargs=} to {remaining_args=} {updated_kwargs=}"
        )

    return remaining_args, updated_kwargs
