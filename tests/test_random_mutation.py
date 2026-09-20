import ast
from collections.abc import Callable

import numpy as np
import pytest

import procfunc as pf
from procfunc.codegen import codegen

RANDOM_CALLS = [
    ("uniform", (0.0, 1.0)),
    ("normal", (0.0, 1.0)),
    ("randint", (0, 10)),
    ("uniform_tails", (0.0, 1.0)),
    ("clip_gaussian", (0.0, 1.0)),
    ("wrap_gaussian", (0.0, 1.0, -1.0, 1.0)),
    ("exponential", (1.0,)),
    ("log_uniform", (0.4, 2.0)),
    ("log_normal", (1.0, 0.5)),
    ("spherical_sample", ()),
    ("mixture_of_gaussian", ([0.0, 5.0], [1.0, 1.0], [1.0, 1.0])),
    ("beta", (2.0, 5.0)),
    ("poisson", (3.0,)),
    ("triangular", (0.0, 1.0, 0.5)),
    ("gamma", (2.0, 1.0)),
    ("binomial", (10, 0.5)),
    ("geometric", (0.3,)),
]
TRACE_LEVELS = [
    pf.tracer.TraceLevel.RANDOM_PARAMS,
    pf.tracer.TraceLevel.RANDOM_CONTROL,
    pf.tracer.TraceLevel.PRIMITIVES,
]


def generated_function(
    generator: Callable, level: pf.tracer.TraceLevel, concrete: bool
) -> Callable:
    inputs = {"rng": np.random.default_rng(17)} if concrete else {}
    graph = pf.trace(generator, trace_level=level, **inputs)
    source = codegen.to_python(graph, toplevel_as_maincall=False)
    source = source.replace("np.random.default_rng()", "np.random.default_rng(17)")
    namespace = {}
    exec(source, namespace)  # noqa: S102
    return namespace[generator.__name__]


def test_unused_mutator_return_emits_bare_call() -> None:
    def generator(rng):
        pf.random.uniform(rng, 0.0, 1.0)
        return pf.random.uniform(rng, 0.0, 1.0)

    graph = pf.trace(generator, trace_level=pf.tracer.TraceLevel.RANDOM_PARAMS)
    tree = ast.parse(codegen.to_python(graph, toplevel_as_maincall=False))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    assert isinstance(function.body[0], ast.Expr)
    assert isinstance(function.body[1], ast.Assign)


@pytest.mark.parametrize("name,args", RANDOM_CALLS, ids=[x[0] for x in RANDOM_CALLS])
@pytest.mark.parametrize("level", TRACE_LEVELS, ids=lambda level: level.name)
@pytest.mark.parametrize("concrete", [False, True], ids=["input", "seeded"])
def test_discarded_random_draw_advances_generated_rng(
    name: str, args: tuple, level: pf.tracer.TraceLevel, concrete: bool
) -> None:
    def generator(rng):
        getattr(pf.random, name)(rng, *args)
        return pf.random.uniform(rng, 0.0, 1.0)

    generated = generated_function(generator, level, concrete)
    expected = generator(np.random.default_rng(17))
    actual = generated() if concrete else generated(np.random.default_rng(17))
    tolerance = 1e-7 if concrete and level < pf.tracer.TraceLevel.RANDOM_PARAMS else 0
    assert actual == pytest.approx(expected, rel=tolerance, abs=0)


@pytest.mark.parametrize("level", TRACE_LEVELS, ids=lambda level: level.name)
@pytest.mark.parametrize("concrete", [False, True], ids=["input", "seeded"])
def test_reversed_outputs_preserve_aliased_rng_order(
    level: pf.tracer.TraceLevel, concrete: bool
) -> None:
    def generator(rng):
        other = rng
        width = pf.random.uniform(rng, 1.0, 2.0)
        height = pf.random.uniform(other, 3.0, 4.0)
        return {"height": height, "width": width}

    generated = generated_function(generator, level, concrete)
    expected = generator(np.random.default_rng(17))
    actual = generated() if concrete else generated(np.random.default_rng(17))
    tolerance = 1e-7 if concrete and level < pf.tracer.TraceLevel.RANDOM_PARAMS else 0
    assert actual == pytest.approx(expected, rel=tolerance, abs=0)
