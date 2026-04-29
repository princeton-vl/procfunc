import copy
import inspect
import logging
from pathlib import Path
from typing import Any, Generic, TypeVar, Union

import bpy

from procfunc import compute_graph as cg
from procfunc import types as pt
from procfunc.compute_graph.operators_info import (
    OPERATORS_TO_FUNCTIONS,
    OperatorType,
)
from procfunc.util import pytree
from procfunc.util.manifest import module_path

logger = logging.getLogger(__name__)

INPUT_NODE_TYPE = "NodeGroupInput"
OUTPUT_NODE_TYPE = "NodeGroupOutput"
NODE_FUNCTION_INSTANCE_TYPE = "NodeFunctionInstance"

T = TypeVar("T")


PROCNODE_OPERATORS = {
    OperatorType.ADD,
    OperatorType.SUB,
    OperatorType.MUL,
    OperatorType.DIV,
    OperatorType.POW,
    OperatorType.MOD,
    OperatorType.LESS_THAN,
    OperatorType.LESS_THAN_EQUAL,
    OperatorType.GREATER_THAN,
    OperatorType.GREATER_THAN_EQUAL,
    OperatorType.EQUAL,
    OperatorType.NOT_EQUAL,
}


def _node_definition_metadata() -> tuple[str, int, str]:
    """
    Dig through this functions callstack to find user-space filename/line number, and the procfunc function name
    """

    procfunc_frame = inspect.currentframe().f_back  # type: ignore
    while (
        module_path() in Path(procfunc_frame.f_back.f_code.co_filename).parents  # type: ignore
    ):
        procfunc_frame = procfunc_frame.f_back  # type: ignore
    return (
        procfunc_frame.f_back.f_code.co_filename,  # type: ignore
        procfunc_frame.f_back.f_lineno,  # type: ignore
        procfunc_frame.f_code.co_name,  # type: ignore
    )


def _has_unpreprocessed_inputs(node: cg.Node) -> bool:
    any_args = any(isinstance(a, ProcNode) for a in node.args)
    any_kwargs = any(isinstance(v, ProcNode) for v in node.kwargs.values())
    return any_args or any_kwargs


class ProcNode(Generic[T]):
    """
    Result datatype for all functions that return shader nodes, geometry nodes or compositor nodes.

    ProcNode stores the data necessary to construct a blender nodegroup upon later execution.

    ProcNode defines dunders to allow concise construction of nodegraphs e.g. __getattr__ and __add__, which map to appropriate blender nodes.
    """

    def __init__(
        self,
        node: cg.Node,
        known_value_type: type | None = None,
    ):
        self._node = node

        if known_value_type is not None:
            logger.debug(f"{self} using provided known_value_type={known_value_type}")
            self._node.metadata["known_value_type"] = known_value_type

        if _has_unpreprocessed_inputs(node):
            raise ValueError(
                f"{node=} has inputs which are ProcNode, "
                f"these should have been unwrapped to cg.Node {node.args} {node.kwargs}"
            )

        self._node.metadata["definition"] = _node_definition_metadata()

    def astype(self, dtype: type) -> "ProcNode":
        """
        Marks a node as having been converted to a different internal data type, similarly to np.astype

        Currently this just adds runtime NodeType data to help subsequent type-inferred functions/operators
        make a correct choice of data_type.

        e.g noise.color + (0.5, 0.5, 0.5) fails but noise.color.astype(t.Vector) + (0.5, 0.5, 0.5) works,
        because `+` is defined for Vector but not Color
        """

        node = copy.copy(self._node)
        node.metadata = copy.copy(self._node.metadata)
        node.metadata["known_value_type"] = dtype

        logger.debug(f"{self}.astype() using provided known_value_type={dtype}")
        return ProcNode(node)

    def __repr__(self):
        # NOTE: dont change this to be anything verbose, it may slow down system
        #   due to generating strings for debug logs (even if they arent actually printed)
        return f"ProcNode({self.item()!r})"

    @classmethod
    def from_nodetype(
        cls,
        node_type: str,
        inputs: dict[str, Any],
        attrs: dict[str, Any],
    ) -> "ProcNode":
        def _unwrap(v: Any) -> cg.Node:
            if isinstance(v, ProcNode):
                return object.__getattribute__(v, "_node")
            return v

        inputs = pytree.PyTree(inputs).map(_unwrap).obj()

        if any(isinstance(v, ProcNode) for v in attrs.values()):
            raise ValueError(
                f"Attrs {attrs} contains ProcNode, which is not allowed. Must specify a constant."
            )

        node = cg.ProceduralNode(node_type=node_type, attrs=attrs, kwargs=inputs)
        node.metadata["definition"] = _node_definition_metadata()

        return cls(node=node)

    def item(self) -> cg.Node:
        return object.__getattribute__(self, "_node")

    def __post_init__(self):
        for k, v in self.attrs.items():
            if isinstance(v, (bpy.types.NodeInternal, ProcNode)):
                raise ValueError(
                    f"Node {self.type} has a {k} attribute that is a Node, which is not allowed. Must specify a constant."
                )

    def _output_socket(self, name: str) -> "ProcNode":
        node = cg.GetAttributeNode(source=self.item(), attribute_name=name)
        return ProcNode(node)

    def _procnode_operator(
        self,
        op: OperatorType,
        lhs: "ProcNode[T]",
        rhs: "ProcNode[T] | T",
        reverse: bool = False,
    ) -> "ProcNode[T]":
        rhs_unwrap = rhs.item() if isinstance(rhs, ProcNode) else rhs

        if reverse:
            args = (rhs_unwrap, lhs.item())
        else:
            args = (lhs.item(), rhs_unwrap)

        node = cg.FunctionCallNode(
            func=OPERATORS_TO_FUNCTIONS[op],
            args=args,
            kwargs={},
            metadata=None,
        )
        return ProcNode(node)

    def _getattr_xyz(
        self: "ProcNode[pt.Vector]",
        name: str,
    ) -> "ProcNode[float]":
        sep = ProcNode.from_nodetype(
            node_type="ShaderNodeSeparateXYZ",
            inputs={"Vector": self},
            attrs={},
        )
        return sep._output_socket(name)

    @property
    def x(self: "ProcNode[pt.Vector]") -> "ProcNode[float]":
        return self._getattr_xyz(name="x")

    @property
    def y(self: "ProcNode[pt.Vector]") -> "ProcNode[float]":
        return self._getattr_xyz(name="y")

    @property
    def z(self: "ProcNode[pt.Vector]") -> "ProcNode[float]":
        return self._getattr_xyz(name="z")

    def __add__(self, other: "ProcNode[T] | T | tuple") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.ADD, self, other)

    def __radd__(self, other: "ProcNode[T] | T | tuple") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.ADD, self, other, reverse=True)

    def __sub__(self, other: "ProcNode[T] | T | tuple") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.SUB, self, other)

    def __rsub__(self, other: "ProcNode[T] | T | tuple") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.SUB, self, other, reverse=True)

    def __mul__(self, other: "ProcNode[T] | T | tuple") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.MUL, self, other)

    def __rmul__(self, other: "ProcNode[T] | T | tuple") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.MUL, self, other, reverse=True)

    def __truediv__(self, other: "ProcNode[T] | T | tuple") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.DIV, self, other)

    def __rtruediv__(self, other: "ProcNode[T] | T | tuple") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.DIV, self, other, reverse=True)

    def __pow__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.POW, self, other)

    def __rpow__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.POW, self, other, reverse=True)

    def __mod__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.MOD, self, other)

    def __rmod__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.MOD, self, other, reverse=True)

    def __lt__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.LESS_THAN, self, other)

    def __rlt__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(
            OperatorType.LESS_THAN, self, other, reverse=True
        )

    def __le__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.LESS_THAN_EQUAL, self, other)

    def __rle__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(
            OperatorType.LESS_THAN_EQUAL, self, other, reverse=True
        )

    def __gt__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.GREATER_THAN, self, other)

    def __rgt__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(
            OperatorType.GREATER_THAN, self, other, reverse=True
        )

    def __ge__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.GREATER_THAN_EQUAL, self, other)

    def __rge__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(
            OperatorType.GREATER_THAN_EQUAL, self, other, reverse=True
        )

    def __eq__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.EQUAL, self, other)

    def __req__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.EQUAL, self, other, reverse=True)

    def __ne__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(OperatorType.NOT_EQUAL, self, other)

    def __rne__(self, other: "ProcNode[T] | T") -> "ProcNode[T]":
        return self._procnode_operator(
            OperatorType.NOT_EQUAL, self, other, reverse=True
        )


def node_definition_context_message(node: cg.Node):
    metadata = object.__getattribute__(node, "metadata")
    lineno_metadata = metadata.get("definition", None)
    if lineno_metadata is None:
        return ""
    file, lineno, procfunc_name = lineno_metadata
    return f" {procfunc_name}() call on {file}:{lineno} "


TSocketVal = TypeVar("TSocketVal")
SocketOrVal = Union[ProcNode[TSocketVal], TSocketVal]


class Instances:
    pass


Points = Union[pt.MeshObject, pt.CurveObject]

Geometry = Union[pt.MeshObject, pt.CurveObject, Instances, pt.VolumeObject]

AnyShaderDataVal = Union[
    pt.Vector,
    pt.Color,
    float,
]

AnyDataVal = Union[AnyShaderDataVal, int, str, bool, pt.Matrix, pt.Quaternion]
"""
Union of all types that are data-like in a geometrynodes context
IE pretty much all the geonodes sockettypes except specialones like Material or Object
"""

AnyAssetVal = Union[
    pt.Object,
    pt.Collection,
    pt.Material,
    pt.Texture,
]
"""
Union of all types that are object-like in a geometrynodes context
"""

AnyVal = Union[AnyDataVal, AnyAssetVal]


class Shader:
    """
    Used only for type-annotating nodes as returning a shader.

    Anythnig that would be a green socket in a SHADER nodegraph should be ProcNode[Shader]
    """

    pass


__all__ = [
    "ProcNode",
    "Shader",
    "SocketOrVal",
    "AnyShaderDataVal",
    "AnyDataVal",
    "AnyAssetVal",
    "node_definition_context_message",
]
