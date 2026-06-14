import numpy as np

import procfunc as pf


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
