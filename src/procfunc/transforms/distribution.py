import enum
import logging
from typing import Any, Callable

import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.compute_graph import transform_compute_graph
from procfunc.random import random_distrib_funcs

logger = logging.getLogger(__name__)


class NumpyRandomDistrib(enum.Enum):
    # from https://numpy.org/doc/2.2/reference/random/generator.html#distributions
    BETA = "beta"
    BINOMIAL = "binomial"
    CHISQUARE = "chisquare"
    EXPONENTIAL = "exponential"
    F = "f"
    GAMMA = "gamma"
    GAUSSIAN = "gaussian"
    GEOMETRIC = "geometric"
    GUMBEL = "gumbel"
    HYPERGEOMETRIC = "hypergeometric"
    LAPLACE = "laplace"
    LOGISTIC = "logistic"
    LOGNORMAL = "lognormal"
    LOGSERIES = "logseries"
    MULTINOMIAL = "multinomial"
    MULTIVARIATE_NORMAL = "multivariate_normal"
    NEGATIVE_BINOMIAL = "negative_binomial"
    NORMAL = "normal"
    NONCENTRAL_CHISQUARE = "noncentral_chisquare"
    NONCENTRAL_F = "noncentral_f"
    PARETO = "pareto"
    POISSON = "poisson"
    POWER = "power"
    RAYLEIGH = "rayleigh"
    SHUFFLE = "shuffle"
    STANDARD_CAUCHY = "standard_cauchy"
    STANDARD_EXPONENTIAL = "standard_exponential"
    STANDARD_GAMMA = "standard_gamma"
    STANDARD_NORMAL = "standard_normal"
    STANDARD_LOGISTIC = "standard_logistic"
    STANDARD_LAPLACE = "standard_laplace"
    STANDARD_PARETO = "standard_pareto"
    STANDARD_T = "standard_t"
    TRIANGULAR = "triangular"
    UNIFORM = "uniform"
    VONMISES = "vonmises"
    WALD = "wald"
    WEIBULL = "weibull"
    ZIPF = "zipf"
    INTEGER = "integers"


FUNCNAME_TO_DISTRIB = {v.value: v for v in NumpyRandomDistrib.__members__.values()}


def as_distribution(
    node: cg.Node,
) -> NumpyRandomDistrib | Callable[[np.random.Generator, ...], Any] | None:
    match node:
        case cg.FunctionCallNode(func=x) if x in random_distrib_funcs:
            return x
        case cg.MethodCallNode(method_name=method, args=(arg_0,)) if (
            method in FUNCNAME_TO_DISTRIB
            and isinstance(arg_0, cg.Node)
            and arg_0.metadata.get("known_value_type") is np.random.Generator
        ):
            return FUNCNAME_TO_DISTRIB[method]
        case _:
            return None


def distribution_to_mode(
    compute_graph: cg.ComputeGraph,
    graph_name: str | None = None,
) -> cg.ComputeGraph:
    """
    Transform a generator to use the mode of the distribution instead of random samples
    """

    def map_to_mode(node: cg.Node) -> cg.Node | float:
        match as_distribution(node):
            case NumpyRandomDistrib.UNIFORM:
                assert len(node.args) == 1 or len(node.kwargs) == 0, (
                    "implementation may be errored for mix of args and kwargs"
                )
                low = node.kwargs.get("low", node.args[1])
                high = node.kwargs.get("high", node.args[2])
                if isinstance(low, cg.Node) or isinstance(high, cg.Node):
                    logger.warning(
                        f"Uniform mode not implemented for {node=} with non-constant {low=} {high=}"
                    )
                    return node
                return (low + high) / 2
            case NumpyRandomDistrib.NORMAL:
                assert len(node.args) == 1 or len(node.kwargs) == 0, (
                    "implementation may be errored for mix of args and kwargs"
                )
                mean = node.kwargs.get("mean", node.args[1])
                _std = node.kwargs.get("std", node.args[2])
                if isinstance(mean, cg.Node):
                    logger.warning(
                        f"Normal mode not implemented for {node=} with non-constant {mean=}"
                    )
                    return node
                return mean
            case _:
                return node

    return transform_compute_graph(
        compute_graph,
        map_to_mode,
        graph_name=graph_name or compute_graph.name + "_mode",
    )


def map_to_outlier(
    node: cg.Node, pct: float = 0.05, normal_clip_std: float = 3.0
) -> cg.Node:
    varname = node.metadata.get("varname", None)
    varname = (varname + "_outlier") if varname else None

    match as_distribution(node):
        case NumpyRandomDistrib.UNIFORM:
            assert len(node.args) == 1 or len(node.kwargs) == 0, (
                "cant handle arg/kwarg mix"
            )
            low = node.kwargs.get("low", node.args[1])
            high = node.kwargs.get("high", node.args[2])
            if isinstance(low, cg.Node) or isinstance(high, cg.Node):
                logger.warning(
                    f"outlier not implemented for {node=} with {min=} {max=}"
                )
                return node
            rng = node.args[0]
            assert isinstance(rng, cg.Node), f"got {node.args[0]=}"
            return cg.FunctionCallNode(
                func=pf.random.uniform_tails,
                args=(rng,),
                kwargs=dict(low=low, high=high, tail_pct=pct),
                varname=varname,
            )
        case NumpyRandomDistrib.NORMAL:
            assert len(node.args) == 1 or len(node.kwargs) == 0, (
                "cant handle arg/kwarg mix"
            )
            mean = node.kwargs.get("mean", node.args[1])
            std = node.kwargs.get("std", node.args[2])
            if isinstance(mean, cg.Node):
                logger.warning(f"outlier not implemented for {node=} with {mean=}")
                return node
            rng = node.args[0]
            return cg.FunctionCallNode(
                func=pf.random.uniform_tails,
                args=(rng,),
                kwargs=dict(
                    tail_pct=pct,
                    low=mean - normal_clip_std * std,
                    high=mean + normal_clip_std * std,
                ),
                varname=varname,
            )
        case func if func in pf.random.random_distrib_funcs:
            logger.warning(
                f"{outlier_distribution.__name__} not implemented for {func}"
            )
            return node
        case _:
            return node


def outlier_distribution(
    compute_graph: cg.ComputeGraph,
    pct: float = 0.05,
    graph_name: str | None = None,
    normal_clip_std: float = 3.0,
) -> cg.ComputeGraph:
    """
    Transform a generator to generate outliers with a given probability
    """

    return transform_compute_graph(
        compute_graph,
        lambda node: map_to_outlier(node, pct, normal_clip_std),
        graph_name=graph_name or compute_graph.name + "_outlier",
    )
