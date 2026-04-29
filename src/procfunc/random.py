import logging
from typing import TypeVar

import numpy as np

import procfunc as pf

T = TypeVar("T")

logger = logging.getLogger(__name__)


@pf.tracer.primitive(allow_exec=True)
def uniform(
    rng: np.random.Generator,
    low: float,
    high: float,
) -> float:
    return rng.uniform(low, high)


@pf.tracer.primitive(allow_exec=True)
def normal(
    rng: np.random.Generator,
    mean: float,
    std: float,
) -> float:
    return rng.normal(mean, std)


@pf.tracer.primitive(allow_exec=True)
def randint(
    rng: np.random.Generator,
    low: int,
    high: int,
) -> int:
    return rng.integers(low, high)


@pf.tracer.primitive(allow_exec=True)
def uniform_tails(
    rng: np.random.Generator,
    low: float,
    high: float,
    tail_pct: float = 0.05,
) -> float:
    if rng.random() < 0.5:
        return rng.uniform(low, low + (high - low) * tail_pct)
    else:
        return rng.uniform(high - (high - low) * tail_pct, high)


@pf.tracer.primitive(allow_exec=True)
def clip_gaussian(
    rng: np.random.Generator,
    mean: float,
    std: float,
    low: float | None = None,
    high: float | None = None,
    max_tries: int = 20,
) -> float:
    low = low or mean - 3 * std
    high = high or mean + 3 * std

    for _ in range(max_tries):
        val = rng.normal(mean, std)
        if low <= val and val <= high:
            return val

    raise ValueError(
        f"clip_gaussian({mean=}, {std=}, {low=}, {high=}) failed to "
        f"sample a value in the range after {max_tries=}"
    )


def wrap_gaussian(
    rng: np.random.Generator,
    mean: float,
    std: float,
    low: float,
    high: float,
):
    x = rng.normal(mean, std)

    if x < low:
        x = high - (low - x) % (high - low)
    elif x > high:
        x = low + (x - high) % (high - low)

    return x


def exponential(
    rng: np.random.Generator,
    scale: float,
) -> float:
    return rng.exponential(scale)


def log_uniform(
    rng: np.random.Generator,
    low: float,
    high: float,
    size: tuple | None = None,
) -> float:
    return np.exp(rng.uniform(np.log(low), np.log(high), size=size))


def log_normal(
    rng: np.random.Generator,
    mean: float,
    std: float,
    size: tuple | None = None,
) -> float:
    return np.exp(rng.normal(np.log(mean), std, size=size))


def spherical_sample(
    rng: np.random.Generator,
    min_elevation: float | None = None,
    max_elevation: float | None = None,
    retries: int = 100,
) -> float:
    for _ in range(retries):
        P = rng.standard_normal(3)
        x = np.arctan2(np.abs(P[2]), (P[0] ** 2 + P[1] ** 2) ** 0.5)
        if (min_elevation is None or x > np.radians(min_elevation)) and (
            max_elevation is None or x < np.radians(max_elevation)
        ):
            return np.degrees(x)

    raise ValueError(
        f"spherical_sample({min_elevation=}, {max_elevation=}) failed to "
        f"sample a value in the range after {retries=}"
    )


def mixture_of_gaussian(
    rng: np.random.Generator,
    means: np.ndarray,
    stds: np.ndarray,
    weights: list[float],
    low: np.ndarray | float | None = None,
    high: np.ndarray | float | None = None,
):
    p = np.array(weights) / np.sum(weights)
    idx = rng.choice(len(p), p=p)

    mu = means[idx]
    std = stds[idx]

    res = rng.normal(mu, std)

    if low is not None:
        res = np.maximum(res, low)
    if high is not None:
        res = np.minimum(res, high)

    return res


def beta(
    rng: np.random.Generator,
    a: float,
    b: float,
) -> float:
    return rng.beta(a, b)


def poisson(
    rng: np.random.Generator,
    lam: float,
) -> float:
    return rng.poisson(lam)


def triangular(
    rng: np.random.Generator,
    low: float,
    high: float,
    mode: float,
) -> float:
    return rng.triangular(low, mode, high)


def gamma(
    rng: np.random.Generator,
    shape: float,
    scale: float,
) -> float:
    return rng.gamma(shape, scale)


def binomial(
    rng: np.random.Generator,
    n: int,
    p: float,
) -> float:
    return rng.binomial(n, p)


def geometric(
    rng: np.random.Generator,
    p: float,
) -> float:
    return rng.geometric(p)


random_distrib_funcs = (
    uniform,
    normal,
    uniform_tails,
    clip_gaussian,
    wrap_gaussian,
    log_uniform,
    log_normal,
    spherical_sample,
    mixture_of_gaussian,
    beta,
    poisson,
    triangular,
    gamma,
    binomial,
    geometric,
    exponential,
)


__all__ = [
    "uniform",
    "normal",
    "uniform_tails",
    "clip_gaussian",
    "wrap_gaussian",
    "log_uniform",
    "log_normal",
    "spherical_sample",
    "mixture_of_gaussian",
    "beta",
    "poisson",
    "triangular",
    "gamma",
    "binomial",
    "geometric",
    "exponential",
    "random_distrib_funcs",
]
