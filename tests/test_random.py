import numpy as np
import pytest

import procfunc as pf
from procfunc import compute_graph as cg

_distribution_calls = {
    pf.random.uniform: lambda rng: pf.random.uniform(rng, 0.1, 1.0),
    pf.random.normal: lambda rng: pf.random.normal(rng, 0.0, 1.0),
    pf.random.randint: lambda rng: pf.random.randint(rng, 0, 10),
    pf.random.uniform_tails: lambda rng: pf.random.uniform_tails(rng, 0.0, 1.0),
    pf.random.clip_gaussian: lambda rng: pf.random.clip_gaussian(rng, 0.0, 1.0),
    pf.random.wrap_gaussian: lambda rng: pf.random.wrap_gaussian(
        rng, 0.0, 1.0, -1.0, 1.0
    ),
    pf.random.exponential: lambda rng: pf.random.exponential(rng, 1.0),
    pf.random.log_uniform: lambda rng: pf.random.log_uniform(rng, 0.4, 2.0),
    pf.random.log_normal: lambda rng: pf.random.log_normal(rng, 1.0, 0.5),
    pf.random.spherical_sample: lambda rng: pf.random.spherical_sample(rng),
    pf.random.mixture_of_gaussian: lambda rng: pf.random.mixture_of_gaussian(
        rng, np.array([0.0, 5.0]), np.array([1.0, 1.0]), [1.0, 1.0]
    ),
    pf.random.beta: lambda rng: pf.random.beta(rng, 2.0, 5.0),
    pf.random.poisson: lambda rng: pf.random.poisson(rng, 3.0),
    pf.random.triangular: lambda rng: pf.random.triangular(rng, 0.0, 1.0, 0.5),
    pf.random.gamma: lambda rng: pf.random.gamma(rng, 2.0, 1.0),
    pf.random.binomial: lambda rng: pf.random.binomial(rng, 10, 0.5),
    pf.random.geometric: lambda rng: pf.random.geometric(rng, 0.3),
}


def test_distribution_call_table_is_complete():
    assert set(_distribution_calls) >= set(pf.random.random_distrib_funcs)


@pytest.mark.parametrize("func", list(_distribution_calls), ids=lambda f: f.__name__)
def test_distribution_bakes_to_constant_when_traced(func):
    def generator(rng):
        return _distribution_calls[func](rng)

    graph = pf.trace(
        generator,
        rng=np.random.default_rng(0),
        trace_level=pf.tracer.TraceLevel.GENERATORS,
    )
    out = list(graph.outputs.dict().values())[0]
    assert isinstance(out, cg.ConstantNode)


def test_clip_gaussian_respects_zero_bounds():
    """low=0.0 / high=0.0 are real bounds, not "unset"."""
    rng = np.random.default_rng(0)
    samples = [
        pf.random.clip_gaussian(
            rng, mean=-0.5, std=1.0, low=0.0, high=2.0, max_tries=1000
        )
        for _ in range(50)
    ]
    assert all(0.0 <= s <= 2.0 for s in samples)

    samples = [
        pf.random.clip_gaussian(
            rng, mean=0.5, std=1.0, low=-2.0, high=0.0, max_tries=1000
        )
        for _ in range(50)
    ]
    assert all(-2.0 <= s <= 0.0 for s in samples)


def test_clip_gaussian_default_bounds():
    rng = np.random.default_rng(0)
    samples = [pf.random.clip_gaussian(rng, mean=5.0, std=1.0) for _ in range(50)]
    assert all(2.0 <= s <= 8.0 for s in samples)
