import functools
import inspect
import logging
from types import UnionType
from typing import Any, Callable, Union, get_args, get_origin

import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.compute_graph.node import normalize_args_to_kwargs
from procfunc.nodes import types as nt
from procfunc.tracer import TraceLevel, register_trace_target
from procfunc.tracer.patch import Patcher, PatchSetAttr
from procfunc.tracer.trace import capture_as_function_call
from procfunc.util import pytree

logger = logging.getLogger(__name__)


def _find_procnode_type(t: type) -> type | None:
    origin = get_origin(t)
    if origin is nt.ProcNode:
        args = get_args(t)
        return args[0] if args else None
    elif origin in (Union, UnionType):
        for a in get_args(t):
            res = _find_procnode_type(a)
            if res is not None:
                return res
        return None
    else:
        return None


def _procnode_value_type(func: Callable, k: str, v: inspect.Parameter) -> type:
    if v.annotation is None or v.annotation is inspect.Parameter.empty:
        raise TypeError(
            f"{func.__name__} had argument {k!r} with no type annotation. "
            f"All @{node_function.__name__} arguments must have a type annotation."
        )

    value_type = _find_procnode_type(v.annotation)
    if value_type is None and v.annotation is nt.ProcNode:
        value_type = nt.Geometry
    if value_type is None:
        raise TypeError(
            f"{func.__name__} had argument {k} with {v.annotation=} which is not allowed - "
            f"all func annotations must contain a ProcNode to be used with @{node_function.__name__}"
        )

    return value_type


def _procnode_placeholder(func: Callable, k: str, v: inspect.Parameter):
    value_type = _procnode_value_type(func, k, v)
    node = cg.InputPlaceholderNode(
        name=k, default_value=v.default, metadata={"known_value_type": value_type}
    )
    logger.debug(
        f"Using known_value_type={value_type} for {node=} for {k=} {v.default=}"
    )
    node = nt.ProcNode(node)
    return node


def _execute_procnode_func_to_computegraph(func: Callable):
    sig = inspect.signature(func)
    input_placeholders = {
        k: _procnode_placeholder(func, k, v) for k, v in sig.parameters.items()
    }
    result = func(**input_placeholders)

    def _unwrap(x):
        if isinstance(x, nt.ProcNode):
            return x.item()
        return x

    inp_pt = pytree.PyTree(input_placeholders).map(_unwrap)
    out_pt = pytree.PyTree(result).map(_unwrap)
    graph = cg.ComputeGraph(
        inputs=inp_pt,
        outputs=out_pt,
        name=func.__name__,
        metadata={},
    )

    value_types = {
        k: v.metadata.get("known_value_type", None) for k, v in graph.inputs.items()
    }
    if any(v is None for v in value_types.values()):
        raise ValueError(
            f"Subgraph {func.__name__} has inputs with no known value type: {value_types}"
        )
    graph.metadata["known_value_types"] = value_types

    return graph


def function_to_compute_graph(func: Callable) -> cg.ComputeGraph:
    """Build the ComputeGraph for a node-building callable.

    Accepts either a plain callable that builds ProcNodes or a
    @node_function-decorated function (whose original is recovered via
    ``__wrapped__``). The result can be passed to ``as_nodegroup``.
    """
    func = getattr(func, "__wrapped__", func)
    return _execute_procnode_func_to_computegraph(func)


def _preprocess_procnode_call_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for k, v in kwargs.items():
        match v:
            case nt.ProcNode():
                result[k] = v.item()
            case pf.MeshObject() | pf.CurveObject():
                result[k] = pf.nodes.geo.object_info(v).geometry.item()
            case dict():
                result[k] = _preprocess_procnode_call_kwargs(v)
            case _:
                result[k] = v
    return result


def _subgraph_call_procnode(func: Callable, subgraph: cg.ComputeGraph, *args, **kwargs):
    args, kwargs = normalize_args_to_kwargs(func, args, kwargs)
    kwargs_unwrap = _preprocess_procnode_call_kwargs(kwargs)
    node = cg.SubgraphCallNode(subgraph=subgraph, args=args, kwargs=kwargs_unwrap)

    output_socket_names = list(subgraph.outputs.names(nocontainer_name="result"))
    logger.debug(f"Created {func.__name__} with {output_socket_names=}")
    call_node = nt.ProcNode(node)

    if len(output_socket_names) == 1:
        return call_node

    sig = inspect.signature(func)
    return_type = sig.return_annotation

    subgraph_outputs = subgraph.outputs.dict()
    outputs = {}
    for k in output_socket_names:
        # dont add non-None values where the original was None
        if subgraph_outputs[k] is not None:
            outputs[k] = call_node._output_socket(k)
        else:
            outputs[k] = None
    outputs = {k: v for k, v in outputs.items() if v is not None}
    return return_type(**outputs)


@pf.tracer.primitive
def node_input(value: Any, value_type: type) -> Any:
    """Coerce a node-function socket argument at execution time."""
    if value_type is pf.Material:
        return value
    if value is None:
        if value_type not in (float, int, bool, str, pf.Vector, pf.Color, pf.Euler):
            return None
        value = value_type()
    if isinstance(value, nt.ProcNode):
        return value.astype(value_type)
    if isinstance(value, (pf.MeshObject, pf.CurveObject)):
        return pf.nodes.geo.object_info(value).geometry
    if value_type in (pf.Vector, pf.Color, pf.Euler) and isinstance(
        value, (tuple, list, np.ndarray)
    ):
        value = value_type(value)
    if isinstance(value, np.generic):
        value = value.item()
    return pf.nodes.math.constant(value).astype(value_type)


def _node_function_trace_wrapper(
    func: Callable,
    decorated: Callable,
    target: pf.tracer.PatchFunctionTarget,
    patcher: Patcher,
) -> Callable:
    if decorated._trace_wrapper is not None:
        return decorated._trace_wrapper
    traced_func = patcher.create_wrapper(func)
    signature = inspect.signature(func)

    @functools.wraps(decorated)
    def wrapper(*args, **kwargs):
        if patcher.trace_level >= TraceLevel.NODEGROUPS:
            return capture_as_function_call(decorated, args, kwargs)
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        inputs = {
            name: node_input(
                value, _procnode_value_type(func, name, signature.parameters[name])
            )
            for name, value in bound.arguments.items()
        }
        return traced_func(**inputs)

    patcher.patch(PatchSetAttr(decorated, "_trace_wrapper", None, wrapper))
    return wrapper


def node_function(func: Callable):
    @functools.wraps(func)
    def node_function_wrapper(*args, **kwargs):
        if pf.context.globals.current_trace_level is not None:
            return node_function_wrapper._trace_wrapper(*args, **kwargs)

        subgraph = _execute_procnode_func_to_computegraph(func)
        subgraph.metadata["operations"] = [
            (node_function, {"func": func}),
        ]
        subgraph.metadata["bpy_cached_impls"] = {}

        return _subgraph_call_procnode(func, subgraph, *args, **kwargs)

    node_function_wrapper._trace_wrapper = None
    register_trace_target(
        node_function_wrapper,
        trace_level=TraceLevel.NODEGROUPS,
        allow_exec=False,
        custom_trace_wrapper_create=functools.partial(
            _node_function_trace_wrapper, func, node_function_wrapper
        ),
    )

    return node_function_wrapper


def node_function_dynamic(func: Callable):
    @functools.wraps(func)
    def node_function_wrapper(*args, **kwargs):
        subgraph = _execute_procnode_func_to_computegraph(func)
        return _subgraph_call_procnode(func, subgraph, *args, **kwargs)

    return node_function_wrapper
