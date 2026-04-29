import functools
import logging
from typing import Callable, TypeVar

import numpy as np

import procfunc.compute_graph as cg
from procfunc import context
from procfunc import types as t
from procfunc.tracer import (
    PatchFunctionTarget,
    RngProxy,
    TraceLevel,
    register_trace_target,
)
from procfunc.util import pytree

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _unwrap_proxy(x):
    return x.node if isinstance(x, cg.Proxy) else x


def choice_idx(rng: np.random.Generator, weights: list[float]) -> int:
    weights = np.array(weights)
    weights = weights / weights.sum()
    return rng.choice(len(weights), p=weights)


def _peekthrough_execute_all_choices(
    choice_options: list[tuple[Callable[..., T], float]],
    chosen_idx: int,
    args: tuple,
    kwargs: dict,
) -> cg.Proxy:
    evald = []
    for func, weight in choice_options:
        res = func(*args, **kwargs)
        res = pytree.PyTree(res).map(_unwrap_proxy).obj()
        evald.append((res, weight))

    new_kwargs = dict(
        choice_options=evald,
        chosen_idx=chosen_idx,
    )
    node = cg.FunctionCallNode(
        func=choice,
        args=(),
        kwargs=new_kwargs,
    )
    return cg.Proxy(node)


class ChoiceResultProxy(cg.Proxy):
    def __init__(self, node: cg.FunctionCallNode):
        assert node.func is choice
        super().__init__(node)

    def __call__(self, *args, **kwargs) -> cg.Proxy:
        current_level = context.globals.current_trace_level
        if current_level is None:
            raise ValueError(f"Executed {self} while not in a tracing context?")
        if current_level >= TraceLevel.RANDOM_CONTROL:
            return _peekthrough_execute_all_choices(
                self.node.kwargs["choice_options"],
                self.node.kwargs["chosen_idx"],
                args,
                kwargs,
            )
        else:
            idx = self.node.kwargs["chosen_idx"]
            chosen_value = self.node.kwargs["choice_options"][idx][0]
            return chosen_value(*args, **kwargs)


def _choice_create_custom_tracer_wrapper(
    target: PatchFunctionTarget,
    patcher,
    **_kwargs,
):
    """
    choice needs a custom tracing wrapper since we want to trace what happens inside its sub-options.

    Behavior depends on trace_level vs RANDOM_CONTROL:
        - >= RANDOM_CONTROL: peekthrough all options exhaustively
        - < RANDOM_CONTROL: trace only the branch that would actually be chosen (active resolution)
    """

    @functools.wraps(choice)
    def wrapper(
        choice_rng: RngProxy,
        choice_options: list[tuple[T, float]] | None = None,
        chosen_idx: int | None = None,
    ):
        choice_values, choice_weights = zip(*choice_options)
        if chosen_idx is None:
            chosen_idx = choice_idx(choice_rng.rng, choice_weights)

        unwrapped_options = [
            (pytree.PyTree(v).map(_unwrap_proxy).obj(), w) for v, w in choice_options
        ]
        new_kwargs = dict(
            choice_rng=choice_rng.node,
            choice_options=unwrapped_options,
            chosen_idx=chosen_idx,
        )
        node = cg.FunctionCallNode(
            func=choice,
            args=(),
            kwargs=new_kwargs,
        )
        return ChoiceResultProxy(node)

    return wrapper


TArgs = TypeVar("TArgs")


def choice(
    choice_rng: np.random.Generator,
    choice_options: list[tuple[T, float]],
    chosen_idx: int | None = None,
) -> T:
    """
    Args:
        rng: random number generator
        weights: list of weights for each option - will be normalized to sum to 1 as a probability distribution
        options: list of callables to choose from
        chosen: if not None, use this value instead of choosing randomly. Cannot be traced, but may appear in the output of the tracer.
        chosen_idx: if not None, use this index instead of choosing randomly. Cannot be traced, but may appear in the output of the tracer.
        **child_kwargs: keyword arguments to pass to the chosen callable

    TODO: this function should really take args and kwargs as tuple & dict, not via expansion
    but this requires our Node to handle cases with pytrees as inputs. Currently it would fail to execute the children if they are hidden in a pytree
    """

    choice_values, choice_weights = zip(*choice_options)
    if chosen_idx is None:
        chosen_idx = choice_idx(choice_rng, choice_weights)
    option = choice_values[chosen_idx]
    return option


_ORIG_EXECUTE_CHOICE = choice
register_trace_target(
    func=choice,
    trace_level=TraceLevel.RANDOM_CONTROL,
    allow_exec=False,
    custom_trace_wrapper_create=_choice_create_custom_tracer_wrapper,
)


def sample_collection(
    rng: np.random.Generator,
    func: Callable[[np.random.Generator], T],
    n: int,
    skip_none: bool = False,
) -> t.Collection:
    rngs = rng.spawn(n)
    objects = [func(rng) for rng in rngs]
    if skip_none:
        objects = [obj for obj in objects if obj is not None]
    return t.Collection(objects, name=func.__name__)


__all__ = [
    "choice",
    "choice_idx",
    "choice",
]
