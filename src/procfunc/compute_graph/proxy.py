"""General-purpose Proxy wrapper for Node with all dunders."""

import operator
from dataclasses import dataclass
from typing import Generic, TypeVar

from .node import FunctionCallNode, GetAttributeNode, MethodCallNode, Node

T = TypeVar("T")


@dataclass
class Proxy(Generic[T]):
    """General-purpose wrapper for Node that provides all dunder methods."""

    node: Node

    def __repr__(self):
        return f"Proxy({self.node!r})"

    def __getattr__(self, attr: str) -> "AttributeProxy":
        node = GetAttributeNode(source=self.node, attribute_name=attr)
        return AttributeProxy(node)

    def __call__(self, *args, **kwargs) -> "Proxy":
        raise NotImplementedError("Proxy.__call__ is not implemented")

    def __len__(self) -> int:
        raise ValueError(
            "Tracing does not allow __len__ since real values are not evaluated"
        )

    def __iter__(self):
        raise ValueError(
            "Proxy does not support __iter__. Use explicit indexing instead."
        )

    def __getitem__(self, idx) -> "Proxy":
        idx_node = idx.node if isinstance(idx, Proxy) else idx
        getitem_node = FunctionCallNode(
            func=operator.getitem,
            args=(self.node, idx_node),
            kwargs={},
        )
        return Proxy(getitem_node)

    def __bool__(self):
        raise ValueError(
            "Base Proxy does not allow __bool__ during tracing since real values are unknown"
        )


NODE_DUNDER_METHODS = {
    "__add__": operator.add,
    "__sub__": operator.sub,
    "__mul__": operator.mul,
    "__truediv__": operator.truediv,
    "__floordiv__": operator.floordiv,
    "__mod__": operator.mod,
    "__pow__": operator.pow,
    "__lshift__": operator.lshift,
    "__rshift__": operator.rshift,
    "__and__": operator.and_,
    "__xor__": operator.xor,
    "__or__": operator.or_,
    "__neg__": operator.neg,
    "__pos__": operator.pos,
    "__abs__": operator.abs,
    "__invert__": operator.invert,
    "__eq__": operator.eq,
    "__ne__": operator.ne,
    "__lt__": operator.lt,
    "__le__": operator.le,
    "__gt__": operator.gt,
    "__ge__": operator.ge,
}

NODE_REFLECTABLE_METHODS = [
    "add",
    "sub",
    "mul",
    "floordiv",
    "truediv",
    "div",
    "mod",
    "pow",
    "lshift",
    "rshift",
    "and_",
    "or_",
    "xor",
    "getitem",
    "matmul",
]


def _add_proxy_operator(cls, name, operator_func):
    def proxy_method(self, *args, **kwargs):
        # Convert any Proxy args to their underlying nodes
        node_args = tuple(arg.node if isinstance(arg, Proxy) else arg for arg in args)
        node_kwargs = {
            k: v.node if isinstance(v, Proxy) else v for k, v in kwargs.items()
        }
        node = FunctionCallNode(
            func=operator_func,
            args=(self.node, *node_args),
            kwargs=node_kwargs,
        )
        return Proxy(node)

    setattr(cls, name, proxy_method)


def _add_proxy_reflection(cls, name: str):
    # __rmul__(self, rhs) means rhs * self — use the same operator but swap arg order
    fwd_dunder = f"__{name.rstrip('_')}__"
    operator_func = NODE_DUNDER_METHODS.get(fwd_dunder)
    if operator_func is None:
        return  # no matching forward op, skip

    def proxy_method(self, rhs):
        rhs_node = rhs.node if isinstance(rhs, Proxy) else rhs
        node = FunctionCallNode(
            func=operator_func,
            args=(rhs_node, self.node),
            kwargs={},
        )
        return Proxy(node)

    setattr(cls, f"__r{name}__", proxy_method)


# Add all dunder methods to Proxy
for name, operator_func in NODE_DUNDER_METHODS.items():
    _add_proxy_operator(Proxy, name, operator_func)

# Add reflected methods
for name in NODE_REFLECTABLE_METHODS:
    _add_proxy_reflection(Proxy, name)


@dataclass
class AttributeProxy(Proxy):
    """Special proxy for attribute access that supports peekthrough optimization"""

    def __init__(self, node: Node):
        super().__init__(node)
        assert isinstance(node, GetAttributeNode), node

    def __call__(self, *args, **kwargs) -> Proxy:
        """
        Someone did func = proxy.xyz, then func(), or equivelantly thats just proxy.xyz().
        We can convert that to just a single node which is a method call on the obj node.

        torch.fx.symbolic_trace calls this a _peekthrough optimization_

        TODO: this means that `self` is very often dropped from the graph. need to account for this if we check for drops.
        """
        assert isinstance(self.node, GetAttributeNode), self.node

        # Convert any Proxy args to their underlying nodes
        node_args = tuple(arg.node if isinstance(arg, Proxy) else arg for arg in args)
        node_kwargs = {
            k: v.node if isinstance(v, Proxy) else v for k, v in kwargs.items()
        }
        # self.node.args[0] is the source node that we're calling the method on
        call_node = MethodCallNode(
            callee=self.node.args[0],
            method_name=self.node.attribute_name,
            args=node_args,
            kwargs=node_kwargs,
        )
        return Proxy(call_node)
