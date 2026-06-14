import dataclasses
import enum
import logging
import math
from pathlib import Path
from typing import Any, Union, get_args, get_origin

import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes import types as nt

logger = logging.getLogger(__name__)


def repr_type(x: Any) -> str:
    # TODO: make the user pass in special resolutions for types, or else we will just do verbose types

    if isinstance(x, str):
        return x

    if x.__name__ == "NoneType":
        return "None"

    origin = get_origin(x)
    args = get_args(x)

    if x.__name__ == "ProcNode":
        if len(args) == 1:
            return f"pf.ProcNode[{repr_type(args[0])}]"
        elif len(args) == 0:
            return "pf.ProcNode"
        else:
            raise ValueError(f"Unsupported ProcNode type: {x} {args=}")

    if hasattr(pf, x.__name__):
        if len(args):
            raise ValueError(f"procfunc type had unhandled annotations: {x} {args=}")
        return f"pf.{x.__name__}"

    if x.__module__ == "builtins":
        return x.__name__

    origin = get_origin(x)
    args = get_args(x)

    if origin is Union:
        args_0 = get_args(args[0])
        if get_origin(args[0]) is nt.ProcNode and args_0[0] is args[1]:
            return f"t.SocketOrVal[{repr_type(args_0[0])}]"
        else:
            return " | ".join([repr_type(a) for a in args])

    if getattr(x, "__module__", None) == "procfunc.nodes.types":
        return f"t.{x.__name__}"

    return x.__name__


def repr_float(value: float) -> str:
    if not math.isfinite(value):
        return f'float("{value}")'
    # float32 socket values: shortest exact round-trip (round(x, 8) would destroy small magnitudes)
    return str(np.float32(value))


def repr_value(value: Any) -> str:
    if hasattr(value, "__wrapped__"):
        value = value.__wrapped__

    if isinstance(value, cg.Proxy):
        logger.warning(
            f"Proxy object {value} should never appear as a raw value in codegen - "
            f"its underlying node {value.node} was not resolved to a variable"
        )
    if isinstance(value, nt.ProcNode):
        logger.warning(
            f"Procnode object {value} should never be treated as a raw value in codegen"
        )

    if isinstance(value, np.random.Generator):
        return "np.random.default_rng()"
    elif isinstance(value, type):
        return repr_type(value)
    elif isinstance(value, np.ndarray):
        # tolist + per-element repr is exact, unlike repr(value) which truncates
        # to numpy printoptions precision
        body = (
            repr_value(value.tolist())
            if value.dtype == np.float32
            else repr(value.tolist())
        )
        return f"np.array({body}, dtype=np.{value.dtype.name})"
    elif isinstance(value, np.dtype):
        return f"np.dtype('{value}')"
    elif isinstance(value, pf.Matrix):
        # matrix constants travel as numpy arrays; stray Matrix values delegate
        return repr_value(np.array(value, dtype=np.float32))
    elif isinstance(value, (pf.Color, pf.Vector, pf.Euler, pf.Quaternion)):
        comps = ", ".join(repr_float(c) for c in value)
        return f"pf.{value.__class__.__name__}(({comps}))"
    elif isinstance(value, enum.Enum):
        return f"{type(value).__name__}.{value.name}"
    elif isinstance(value, Path):
        return f"Path({str(value)!r})"
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        args_str = ", ".join(
            f"{f.name}={repr_value(getattr(value, f.name))}"
            for f in dataclasses.fields(value)
        )
        return f"{type(value).__name__}({args_str})"
    elif isinstance(value, list):
        return f"[{', '.join([repr_value(x) for x in value])}]"
    elif isinstance(value, tuple):
        inner = ", ".join(repr_value(x) for x in value)
        return f"({inner},)" if len(value) == 1 else f"({inner})"
    elif isinstance(value, float) and not isinstance(value, bool):
        return repr_float(value)
    else:
        return repr(value)
