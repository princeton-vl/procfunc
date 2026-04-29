import functools
import inspect
import logging
from types import UnionType
from typing import Any, Callable, Union, get_args, get_origin

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.compute_graph.node import normalize_args_to_kwargs
from procfunc.nodes import types as nt
from procfunc.tracer import TraceLevel, register_trace_target
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


def _procnode_placeholder(func: Callable, k: str, v: inspect.Parameter):
    if v.annotation is None:
        raise TypeError(
            f"{func.__name} had argument {k:!r} with non type annotation. "
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


def node_function(func: Callable):
    @functools.wraps(func)
    def node_function_wrapper(*args, **kwargs):
        subgraph = _execute_procnode_func_to_computegraph(func)
        subgraph.metadata["operations"] = [
            (node_function, {"func": func}),
        ]
        subgraph.metadata["bpy_cached_impls"] = {}

        return _subgraph_call_procnode(func, subgraph, *args, **kwargs)

    register_trace_target(
        node_function_wrapper,
        trace_level=TraceLevel.NODEGROUPS,
        allow_exec=False,
        custom_trace_wrapper_create=None,
    )

    return node_function_wrapper


def node_function_dynamic(func: Callable):
    @functools.wraps(func)
    def node_function_wrapper(*args, **kwargs):
        subgraph = _execute_procnode_func_to_computegraph(func)
        return _subgraph_call_procnode(func, subgraph, *args, **kwargs)

    return node_function_wrapper
