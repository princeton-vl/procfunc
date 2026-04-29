"""
torch.fx / jax-like function-compute-graph tracing tool, but specially designed for procedural generation functions


This tool was heavily inspired by torch.fx.symbolic_trace https://docs.pytorch.org/docs/2.6/fx.html
"""

import builtins
import inspect
import logging
import math
import random
from types import ModuleType
from typing import Any, Callable

import numpy as np
import numpy.linalg

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.util import pytree

from .patch import (
    Patcher,
    PatchFunctionTarget,
    TraceLevel,
)
from .proxy import RngProxy

logger = logging.getLogger(__name__)

_autowrap_modules: list[tuple[ModuleType, bool, TraceLevel]] = []


def autowrap_module(
    module: ModuleType,
    allow_exec: bool = False,
    trace_level: TraceLevel = TraceLevel.PRIMITIVES,
):
    _autowrap_modules.append((module, allow_exec, trace_level))


autowrap_module(math, allow_exec=True)
autowrap_module(np, allow_exec=True)
autowrap_module(numpy.linalg, allow_exec=True)


_banned_modules: list[ModuleType] = [
    np.random,
    random,
]


def add_banned_module(module: ModuleType):
    _banned_modules.append(module)


_patch_function_targets: list[PatchFunctionTarget] = []


def add_wrap_target(target: PatchFunctionTarget):
    _patch_function_targets.append(target)


WRAP_BUILTINS = ["min", "max", "abs", "round", "sum"]

for _builtin_name in WRAP_BUILTINS:
    add_wrap_target(
        PatchFunctionTarget(
            frame=builtins.__dict__,
            name=_builtin_name,
            trace_level=TraceLevel.PRIMITIVES,
            normalize=False,
            allow_exec=True,
            source_name="builtins",
        )
    )

WRAP_CONSTRUCTORS = ["Vector", "Color", "Euler"]

for _name in WRAP_CONSTRUCTORS:
    add_wrap_target(
        PatchFunctionTarget(
            frame=pf.__dict__,
            name=_name,
            trace_level=TraceLevel.PRIMITIVES,
            normalize=False,
            allow_exec=True,
            source_name="mathutils",
        )
    )


_search_scopes: list[dict] = []


def add_search_scope(module: ModuleType):
    """
    Causes an intermediate module to be searched to discover any existing targets that need to be patched

    e.g. for procfunc.nodes.to_mesh_object, the original to_mesh_object is already a target, but we need to
    add_search_scope on the `nodes` module so that that module's references to to_mesh_object get wrapped.
    """

    _search_scopes.append(module.__dict__)


def _map_args(
    func: Callable,
    **inputs: Any,
) -> dict[str, cg.Proxy | Any]:
    signature = inspect.signature(func)

    res = {}

    for name, param in signature.parameters.items():
        if name in inputs:
            val = inputs[name]
            if isinstance(val, np.random.Generator):
                node = cg.ConstantNode(value=val)
                res[name] = RngProxy(node, val, dirty=False)
            elif isinstance(val, cg.ConstantNode) and isinstance(
                val.value, np.random.Generator
            ):
                res[name] = RngProxy(val, val.value, dirty=False)
            else:
                res[name] = val
            continue

        if param.default is not param.empty:
            res[name] = param.default
            continue

        node = cg.InputPlaceholderNode(
            name=name, default_value=None, metadata={"varname": name}
        )
        res[name] = cg.Proxy(node)

    return res


def trace(
    func: Callable,
    trace_level: TraceLevel = TraceLevel.GENERATORS,
    name: str | None = None,
    **inputs: Any,
):
    """
    Turn a python function into a graph datastructure.

    Using this datastructure is (usually) equivelent to executing the function.

    Args:
        func: The function to trace
        trace_level: Granularity of the graph. Functions at this level become leaves;
            finer functions are traced through. choice() peeks through all options when
            trace_level >= RANDOM_CONTROL, or resolves to the chosen branch when finer.
    """

    logger.debug(f"Tracing {func} {id(func)=} with {inputs=} {trace_level=}")

    if name is None:
        assert hasattr(func, "__name__")
        assert isinstance(func.__name__, str)
        name = func.__name__

    proxy_args = _map_args(func, **inputs)

    if pf.context.globals.current_trace_level is not None:
        # TODO we can lift this restriction fairly(?) easily by having a global patcher & saving/restoring this state
        # rather than setting to false at end of function. see fx.trace for an example
        raise RuntimeError(
            f"Can't trace {name}, tracing is already in progress for another function. "
            "Nested tracing is not yet supported - contact the developers to request"
        )

    pf.context.globals.current_trace_level = trace_level.value

    patcher = Patcher(
        trace_level=trace_level,
        autopatch_wrap_modules=_autowrap_modules,
        autopatch_remove_modules=_banned_modules,
        search_scopes=_search_scopes,
        patch_functions=_patch_function_targets,
    )

    try:
        func = patcher.apply_preexecute_patches(func, trace_level)
        logger.debug(f"Executing {func.__name__} {id(func)=}")
        func_result = func(**proxy_args)
    finally:
        pf.context.globals.current_trace_level = None
        patcher.unpatch_all()

    metadata = {
        "operations": [
            (trace, {"func": func, "trace_level": trace_level}),
        ],
    }

    def extract_node(v):
        if isinstance(v, cg.Proxy):
            return v.node
        return cg.ConstantNode(value=v)

    outputs = pytree.PyTree(func_result)
    outputs = outputs.map(extract_node)

    input_nodes = {
        k: v.node
        for k, v in proxy_args.items()
        if isinstance(v, cg.Proxy) and isinstance(v.node, cg.InputPlaceholderNode)
    }

    compgraph = cg.ComputeGraph(
        inputs=pytree.PyTree(input_nodes),
        outputs=outputs,
        name=name,
        metadata=metadata,
    )

    return compgraph
