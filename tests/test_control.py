import inspect
from typing import Callable

import numpy as np
import pytest

import procfunc as pf
from procfunc import codegen
from procfunc import compute_graph as cg
from procfunc.tracer import TraceLevel


def _choice_bound(rng: np.random.Generator) -> float:
    low = pf.control.choice(rng, [(1.0, 0.5), (3.0, 0.5)])
    return pf.random.uniform(rng, low, low + 1.0)


def _small_sample(rng: np.random.Generator) -> float:
    return pf.random.uniform(rng, 1.0, 2.0)


def _large_sample(rng: np.random.Generator) -> float:
    return pf.random.uniform(rng, 3.0, 4.0)


def _choice_callable(rng: np.random.Generator) -> float:
    sample = pf.control.choice(rng, [(_small_sample, 0.5), (_large_sample, 0.5)])
    return sample(rng)


@pytest.mark.parametrize("level", list(TraceLevel))
@pytest.mark.parametrize("func", [_choice_bound, _choice_callable])
def test_choice_resolves_at_requested_level(
    level: TraceLevel, func: Callable[[np.random.Generator], float]
):
    graph = pf.trace(func, trace_level=level, rng=np.random.default_rng(0))
    calls = [
        inspect.unwrap(n.func)
        for n in cg.traverse_depth_first(graph)
        if isinstance(n, cg.FunctionCallNode)
    ]
    assert (pf.control.choice in calls) == (level >= TraceLevel.RANDOM_CONTROL)
    assert (pf.random.uniform in calls) == (level >= TraceLevel.RANDOM_PARAMS)
    if func is _choice_callable and level >= TraceLevel.RANDOM_CONTROL:
        assert calls.count(pf.random.uniform) == 2
    source = codegen.to_python(graph, toplevel_as_maincall=False)
    namespace = {}
    exec(source, namespace)  # noqa: S102
    result = namespace[func.__name__]()
    assert 1.0 <= result <= 2.0 or 3.0 <= result <= 4.0
    if level < TraceLevel.RANDOM_PARAMS:
        assert result == pytest.approx(func(np.random.default_rng(0)))
