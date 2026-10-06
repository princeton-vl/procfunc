import logging
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from procfunc.util.pytree import PyTree

from .node import Node

logger = logging.getLogger(__name__)


@dataclass(frozen=True, eq=False)
class ComputeGraph:
    inputs: PyTree[Any, Node]
    outputs: PyTree[Any, Node]
    name: str
    metadata: MappingProxyType

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"

    def __call__(
        self,
        *args,
        **kwargs,
    ):
        """
        Execute the compute graph. If this graph came from a tracer,
        this should be exactly equivelant to executing the original python function.
        """

        raise NotImplementedError("Not implemented")
