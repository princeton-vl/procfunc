import itertools
import logging
from dataclasses import dataclass
from typing import Any

from procfunc.util.pytree import PyTree

from .node import Node

logger = logging.getLogger(__name__)


def _evaluate_node(node: Node) -> Any:
    if node.result is not None:
        return node.result

    for arg in itertools.chain(node.args, node.kwargs.values()):
        if isinstance(arg, Node):
            arg.result = _evaluate_node(arg)

    arg_eval, kwarg_eval = node.inputs.map(
        lambda x: x.result if isinstance(x, Node) else x
    ).obj()

    # match node:
    #     case cg.FunctionCallNode:
    #         return node.func(*arg_vals, **kwarg_vals)
    #     case cg.PlaceholderNode:
    #         raise NotImplementedError(
    #             f"Placeholder {node!r} or '<unnamed>'} should not be evaluated - "
    #             "its .result should be populated in advance"
    #         )
    #     case cg.MutatedArgumentNode:
    #         # Evaluate the mutation call first (for side effects), then return the original object
    #         mutation_call_node = node.args[1]
    #         _evaluate_node(mutation_call_node)
    #         return (
    #             node.args[0].result if isinstance(node.args[0], Node) else node.args[0]
    #         )
    #     case _:
    #         raise NotImplementedError(f"Unsupported node operation: {node.kind}")


def _clear_node_results(node: Node):
    node.result = None
    for arg in itertools.chain(node.args, node.kwargs.values()):
        if isinstance(arg, Node) and arg.result is not None:
            _clear_node_results(arg)


@dataclass
class ComputeGraph:
    inputs: PyTree[Any, Node]
    outputs: PyTree[Any, Node]
    name: str
    metadata: dict[str, Any]

    def __post_init__(self):
        # input_names = set(self.inputs.names())
        # if len(input_names) != len(set(input_names)):
        #     raise ValueError(f"Input names had duplicates: {input_names}")

        # output_names = set(self.outputs.names())
        # if len(output_names) != len(set(output_names)):
        #     raise ValueError(f"Output names had duplicates: {output_names}")
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"

    def clear_values(self):
        for node in self.outputs.values():
            _clear_node_results(node)

    def __call__(
        self,
        *args,
        allow_clear: bool = True,
        **kwargs,
    ):
        """
        Execute the compute graph. If this graph came from a tracer,
        this should be exactly equivelant to executing the original python function.
        """

        raise NotImplementedError("Not implemented")

        if len(args) != len(self.inputs):
            raise ValueError(f"Expected {len(self.inputs)} arguments, got {len(args)}")

        if allow_clear:
            self.clear_values()

        extra_kwargs = self.kwarg_nodes.keys() - kwargs.keys()
        if extra_kwargs:
            raise ValueError(
                f"{self.__class__.__name__} {self.name!r} got unexpected keyword arguments: {extra_kwargs}"
            )

        missing_kwargs = kwargs.keys() - self.kwarg_nodes.keys()
        if missing_kwargs:
            raise ValueError(
                f"{self.__class__.__name__} {self.name!r} had missing keyword arguments: {missing_kwargs}"
            )

        for arg, arg_node in zip(args, self.arg_nodes):
            arg_node.result = arg

        for k, v in kwargs.items():
            self.kwarg_nodes[k].result = v

        for node in self.outputs.values():
            _evaluate_node(node)

        return {name: node.result for name, node in self.outputs.items()}
