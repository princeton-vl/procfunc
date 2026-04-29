import logging
from collections import defaultdict
from typing import Any

import numpy as np

from procfunc import compute_graph as cg
from procfunc import types as t
from procfunc.color import hsv_color
from procfunc.random import randint, uniform
from procfunc.util import pytree

logger = logging.getLogger(__name__)


class TODO:
    """
    An undefined type we leave in the graph so the codegen clearly marks that it should be
    filled in by the user.
    """

    def __repr__(self):
        return "TODO()"


def todo():
    return cg.ConstantNode(value=TODO())


_REDUCE_TYPES = (
    float,
    int,
    tuple,
    t.Color,
    np.ndarray,
)


def _minmax_arraylike(
    values: list[float | int | tuple | np.ndarray | t.Color | t.Vector],
) -> tuple[np.ndarray, np.ndarray]:
    low = np.array(values[0])
    high = np.array(values[0])
    for v in values[1:]:
        low = np.minimum(low, np.array(v))
        high = np.maximum(high, np.array(v))
    return low, high


def _infer_hypercube_differing(
    rng_node: cg.Node, key: str, all_kwargs_k: list[Any]
) -> Any | TODO:
    # if logger.isEnabledFor(logging.DEBUG):
    #    logger.debug(f"{_infer_hypercube_differing.__name__} {key=} {all_kwargs_k=}")

    if len(set(type(v) for v in all_kwargs_k)) != 1:
        return todo()

    if all(np.array(v == all_kwargs_k[0]).all() for v in all_kwargs_k):
        return all_kwargs_k[0]

    if not all(isinstance(v, _REDUCE_TYPES) for v in all_kwargs_k):
        return todo()

    low, high = _minmax_arraylike(all_kwargs_k)
    res = cg.FunctionCallNode(uniform, args=(rng_node, low, high), kwargs={})
    # res.metadata["prefer_inline"] = isinstance(low, (float, int)) # TODO currently ignored
    return res


def infer_hypercube_differing_node(
    rng_node: cg.Node,
    nodes: list[cg.Node],
    memo: dict[int, cg.Node] | None = None,
) -> cg.Node | TODO | None:
    if memo is None:
        memo = {}

    if all(node is None for node in nodes):
        return None
    elif any(node is None for node in nodes):
        logger.debug(f"{infer_hypercube_differing_node=} exiting due to None")
        return todo()

    k = id(nodes[0])
    if k in memo:
        return memo[k]

    # logger.debug(f"{infer_hypercube_differing_node=} {nodes[0]=}")

    kinds = {type(node) for node in nodes}
    if len(kinds) > 1:
        logger.debug(
            f"{infer_hypercube_differing_node=} exiting for mismatching {kinds=}"
        )
        return todo()

    targets = {node.target for node in nodes}
    if len(targets) > 1:
        logger.debug(
            f"{infer_hypercube_differing_node=} exiting for mismatching {targets=}"
        )
        return todo()

    nargs = set(len(node.args) for node in nodes)
    nkwargs = set(len(node.kwargs) for node in nodes)
    if len(nargs) > 1 or len(nkwargs) > 1:
        logger.debug(
            f"{infer_hypercube_differing_node=} exiting for differing {nargs=} {nkwargs=}"
        )
        return todo()

    def _infer_differing(key, argvals):
        if all(isinstance(v, cg.Node) for v in argvals):
            return infer_hypercube_differing_node(rng_node, argvals, memo)
        elif all(v is None for v in argvals):
            return None
        else:
            return _infer_hypercube_differing(rng_node, key, argvals)

    args = [
        _infer_differing(str(i), [nodes[j].args[i] for j in range(len(nodes))])
        for i in range(len(nodes[0].args))
    ]
    kwargs = {
        k: _infer_differing(k, [nodes[j].kwargs[k] for j in range(len(nodes))])
        for k in nodes[0].kwargs.keys()
    }

    res = cg.Node(nodes[0].target, nodes[0].kind, tuple(args), kwargs)
    memo[id(nodes[0])] = res

    return res


def infer_distribution_hypercube(
    graphs: list[cg.ComputeGraph],
    memo: dict[int, cg.Node] | None = None,
) -> list[cg.ComputeGraph]:
    memo = {}

    rng_node = cg.InputPlaceholderNode(
        default_value=None,
        metadata={
            "varname": "rng",
            "known_value_type": "pf.RNG",  # TODO use actual type and resolve to string
        },
    )

    if len(graphs) <= 1:
        raise ValueError(
            f"{infer_distribution_hypercube.__name__} expected at least 2 graphs, got {len(graphs)}"
        )

    all_outputs = [g.outputs.dict() for g in graphs]
    outputs_mapped = {
        k: infer_hypercube_differing_node(rng_node, [g[k] for g in all_outputs], memo)
        for k in all_outputs[0].keys()
    }

    all_inputs = [g.inputs.obj() for g in graphs]
    inputs_mapped = {k: memo.get(id(all_inputs[0][k])) for k in all_inputs[0].keys()}

    n_inputs_missing = sum(1 for v in inputs_mapped.values() if v is None)
    if n_inputs_missing > 0:
        logger.warning(
            f"{infer_distribution_hypercube=} {n_inputs_missing=} {inputs_mapped} {all_inputs[0]}"
        )
    inputs_mapped = {k: v for k, v in inputs_mapped.items() if v is not None}

    # find a common prefix of the graph names
    lens = [len(graph.name) for graph in graphs]
    for i in range(min(lens), 0, -1):
        new_names = {graph.name[:i] for graph in graphs}
        if len(new_names) == 1:
            break
    prefix = graphs[0].name[:i].strip("_")

    res = cg.ComputeGraph(
        inputs=pytree.PyTree({**inputs_mapped, "rng": rng_node}),
        outputs=pytree.PyTree(t.Material(**outputs_mapped)),
        name=f"{prefix}_distribution",
        metadata={"func": infer_distribution_hypercube},
    )

    if logger.isEnabledFor(logging.DEBUG):
        n_inp_graph_nodes = len(list(cg.traverse_depth_first(graphs[0])))
        n_out_graph_nodes = len(list(cg.traverse_depth_first(res)))
        logger.debug(
            f"{infer_distribution_hypercube=} transformed {n_inp_graph_nodes=} to {n_out_graph_nodes=}"
        )

    return res


def _reduce_const(value: Any) -> cg.Node:
    if isinstance(value, np.ndarray) and len(value) == 1:
        value = value[0]
    return cg.ConstantNode(value=value)


def _infer_argument_distribution(
    values: list[Any],
    rng_node: cg.Node,
    colors_to_hsv: bool = True,
    use_randint: bool = False,
) -> cg.Node:
    if all(np.allclose(values[0], x) for x in values[1:]):
        # argument had only one valude (usually the default_value)
        return _reduce_const(values[0])
    elif use_randint and all(
        isinstance(x, (int, float)) and np.isclose(x, int(x)) for x in values
    ):
        # argument is integer range
        low, high = _minmax_arraylike(values)
        return cg.FunctionCallNode(
            randint, args=(rng_node, int(low), int(high)), kwargs={}
        )
    elif colors_to_hsv and any(isinstance(kv, t.Color) for kv in values):
        # treat color ranges as hsv ranges
        assert all(isinstance(kv, t.Color) for kv in values), values
        low, high = _minmax_arraylike([c.hsv for c in values])
        hsv = cg.FunctionCallNode(uniform, args=(rng_node, low, high), kwargs={})
        return cg.FunctionCallNode(hsv_color, args=(), kwargs={"hsv": hsv})
    else:
        # regular argument - usually float and numpy arrays
        low, high = _minmax_arraylike(values)
        return cg.FunctionCallNode(uniform, args=(rng_node, low, high), kwargs={})


def _infer_distribution_from_callnodes(
    callnodes: list[cg.Node],
    subgraph: cg.ComputeGraph,
    supported_types: tuple[type],
    colors_to_hsv: bool,
    use_randint: bool,
) -> cg.ComputeGraph:
    new_inputs = {}
    rng_node = cg.InputPlaceholderNode(
        name="rng",
        default_value=None,
        metadata={
            "known_value_type": "pf.RNG",  # TODO use actual type and resolve to string
        },
    )
    base_inputs = subgraph.inputs.dict()

    for k in base_inputs.keys():
        default_value = base_inputs[k].kwargs.get("default_value")
        kwarg_values = [cn.kwargs.get(k, default_value) for cn in callnodes]
        kwarg_values = [x for x in kwarg_values if x is not None]

        if any(isinstance(v, cg.Node) for v in kwarg_values):
            # argument had dynamic values connected up, make it a functionar gument
            orig_input_type = base_inputs[k].metadata.get("known_value_type", None)
            new_inputs[k] = cg.InputPlaceholderNode(
                name=k,
                default_value=None,
                metadata={
                    "known_value_type": orig_input_type,
                },
            )
        elif all(isinstance(v, supported_types) for v in kwarg_values):
            new_inputs[k] = _infer_argument_distribution(
                kwarg_values, rng_node, colors_to_hsv, use_randint=use_randint
            )
        else:
            uniq_types = set(type(v) for v in kwarg_values)
            logger.warning(
                f"Could not infer distribution for {subgraph.name=} {k=} {uniq_types=}"
            )
            new_inputs[k] = todo()

    result_call = cg.SubgraphCallNode(subgraph=subgraph, args=(), kwargs=new_inputs)

    placeholders = {"rng": rng_node}
    placeholders.update(
        {k: v for k, v in new_inputs.items() if isinstance(v, cg.InputPlaceholderNode)}
    )

    if len(placeholders) == len(new_inputs):
        return None

    graph = cg.ComputeGraph(
        inputs=pytree.PyTree(placeholders),
        outputs=pytree.PyTree(result_call),
        name=f"{subgraph.name}_distribution",
        metadata={"func": infer_nodegroup_distributions},
    )

    return graph


def infer_nodegroup_distributions(
    graphs: list[cg.ComputeGraph],
    supported_types: tuple[type] = (float, int, tuple, t.Vector, t.Color, np.ndarray),
    colors_to_hsv: bool = True,
    use_randint: bool = False,
) -> list[cg.ComputeGraph]:
    """
    Find all multi-use subgraphs within the graphs, and compute the hypercube distribution
    for all the numeric parameters ever used with each subgraph
    """

    subgraph_usages = defaultdict(list)  # id to list of call nodes
    for graph in graphs:
        for callnode, subgraph in cg.traverse_nested_graphs(
            graph, yield_call_nodes=True
        ):
            subgraph_usages[id(subgraph)].append((callnode, subgraph))

    result_distrib_fns = []
    for subgraph_id, calltuples in subgraph_usages.items():
        if len(calltuples) <= 1:
            continue
        distrib_fn = _infer_distribution_from_callnodes(
            callnodes=[ct[0] for ct in calltuples],
            subgraph=calltuples[0][1],
            supported_types=supported_types,
            colors_to_hsv=colors_to_hsv,
            use_randint=use_randint,
        )
        if distrib_fn is not None:
            result_distrib_fns.append(distrib_fn)

    return result_distrib_fns
