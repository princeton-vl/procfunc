import copy
import logging
from collections import defaultdict, deque
from typing import Any, Callable, Generator, Literal, TypeVar

import numpy as np

from procfunc.util import pytree

from .compute_graph import ComputeGraph
from .node import (
    ConstantNode,
    FunctionCallNode,
    GetAttributeNode,
    InputPlaceholderNode,
    MethodCallNode,
    Node,
    ProceduralNode,
    SubgraphCallNode,
)

logger = logging.getLogger(__name__)


T = TypeVar("T")


class LiteralConstant:
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self) -> Any:
        return self.value


def traverse_breadth_first(
    graph: ComputeGraph,
    yield_parent: bool = False,
    yield_name: bool = False,
    yield_consts: bool = False,
) -> Generator[Any, None, None]:
    """
    Traverse all nodes in the compute graph.

    Args:
        graph: The compute graph to traverse
        yield_parent: If True, yield (parent, child), with output nodes having parent=None
        yield_name: If True, yield (name, child) or (name, parent, child) if yield_parent is also True
        yield_consts: If True, yield child arguments of nodes even if they are not Nodes
    """

    visited = set()
    frontier = deque((None, name, node) for name, node in graph.outputs.items())
    visited.update(id(node) for _, _, node in frontier)
    # logger.debug(f"{traverse_breadth_first.__name__} {graph.name} {len(frontier)=}")

    def res(parent, name, child):
        res = (child,)
        if yield_parent:
            res = (parent,) + res
        if yield_name:
            res = (name,) + res

        return res[0] if len(res) == 1 else tuple(res)

    while len(frontier) > 0:
        parent, name, node = frontier.popleft()

        if yield_consts and not isinstance(node, Node):
            yield res(parent, name, node)
            continue

        if not isinstance(node, Node):
            continue

        yield res(parent, name, node)

        children = list(pytree.PyTree(node.args).items()) + list(
            pytree.PyTree(node.kwargs).items()
        )
        for key, arg in children:
            if not yield_consts and not isinstance(arg, Node):
                continue
            if id(arg) in visited:
                continue
            visited.add(id(arg))
            frontier.append((node, key, arg))


def _traverse_depth_first_node(
    node: Node,
    visited: set[int],
    parent: Node | None,
    name: str,
    order: Literal["preorder", "postorder"],
    yield_parent: bool,
    yield_name: bool,
    yield_consts: bool,
) -> Generator[Any, None, None]:
    def res(parent, name, child):
        res = (child,)
        if yield_parent:
            res = (parent,) + res
        if yield_name:
            res = (name,) + res
        return res[0] if len(res) == 1 else tuple(res)

    assert isinstance(node, Node), node
    if id(node) in visited:
        return
    visited.add(id(node))

    if order == "preorder":
        yield res(parent, name, node)

    children = list(pytree.PyTree(node.args).items()) + list(
        pytree.PyTree(node.kwargs).items()
    )

    for key, arg in children:
        if not isinstance(arg, Node):
            if yield_consts:
                yield res(node, key, arg)
            continue
        yield from _traverse_depth_first_node(
            node=arg,
            visited=visited,
            parent=node,
            name=key,
            order=order,
            yield_parent=yield_parent,
            yield_name=yield_name,
            yield_consts=yield_consts,
        )

    if order == "postorder":
        yield res(parent, name, node)


def traverse_depth_first_node(
    node: Node,
    yield_consts: bool = False,
    order: Literal["preorder", "postorder"] = "postorder",
) -> Generator[Any, None, None]:
    return _traverse_depth_first_node(
        node=node,
        visited=set(),
        parent=None,
        name="",
        order=order,
        yield_parent=False,
        yield_name=False,
        yield_consts=yield_consts,
    )


def traverse_depth_first(
    graph: ComputeGraph,
    yield_parent: bool = False,
    yield_name: bool = False,
    yield_consts: bool = False,
    order: Literal["preorder", "postorder"] = "postorder",
) -> Generator[Any, None, None]:
    visited = set()
    for name, node in graph.outputs.items():
        # an absent output leaf (None, e.g. a Material with no displacement) is
        # not part of the node graph
        if not isinstance(node, Node):
            continue
        yield from _traverse_depth_first_node(
            node, visited, None, name, order, yield_parent, yield_name, yield_consts
        )


def traverse_nested_graphs(
    graph: ComputeGraph,
    yield_call_nodes: bool = False,
) -> Generator[tuple[Node | None, ComputeGraph], None, None]:
    visited = set()
    frontier = deque([(None, graph)])

    while len(frontier) > 0:
        node, graph = frontier.popleft()

        if id(graph) in visited:
            continue
        visited.add(id(graph))

        if yield_call_nodes:
            yield node, graph
        else:
            yield graph

        frontier.extend(
            (node, node.subgraph)
            for node in traverse_depth_first(graph)
            if isinstance(node, SubgraphCallNode)
        )


def usages_per_node(
    graph: ComputeGraph,
) -> dict[int, list[Node]]:
    usages = defaultdict(list)
    for node in traverse_depth_first(graph):
        argtree = pytree.PyTree((node.args, node.kwargs))
        for arg in argtree.values():
            if isinstance(arg, Node):
                usages[id(arg)].append(node)
    return dict(usages)


def _value_equal(a: Any, b: Any) -> bool:
    """Array-safe equality for non-node values (constants, attrs, defaults)."""
    if a is b:
        return True
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.array_equal(a, b)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_value_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return (
            type(a) is type(b)
            and len(a) == len(b)
            and all(_value_equal(x, y) for x, y in zip(a, b))
        )
    try:
        return bool(a == b)
    except (ValueError, TypeError):
        return False


def _args_equal(a: Any, b: Any, memo: dict[tuple[int, int], bool]) -> bool:
    """Structural equality of an args/kwargs tree: same container shape, with
    node-valued leaves compared recursively and other leaves by value."""
    tree_a = pytree.PyTree(a)
    tree_b = pytree.PyTree(b)
    if tree_a.spec != tree_b.spec:
        return False
    for leaf_a, leaf_b in zip(tree_a.values(), tree_b.values()):
        a_is_node = isinstance(leaf_a, Node)
        b_is_node = isinstance(leaf_b, Node)
        if a_is_node != b_is_node:
            return False
        if a_is_node:
            if not _nodes_equal(leaf_a, leaf_b, memo):
                return False
        elif not _value_equal(leaf_a, leaf_b):
            return False
    return True


def _nodes_equal(node1: Node, node2: Node, memo: dict[tuple[int, int], bool]) -> bool:
    if node1 is node2:
        return True
    if type(node1) is not type(node2):
        return False

    key = (id(node1), id(node2))
    cached = memo.get(key)
    if cached is not None:
        return cached
    memo[key] = True  # optimistic, breaks cycles in shared DAGs

    result = True
    if isinstance(node1, SubgraphCallNode):
        result = graph_nodes_equal(node1.subgraph, node2.subgraph)
    if result and isinstance(node1, FunctionCallNode):
        result = node1.func is node2.func
    if result and isinstance(node1, MethodCallNode):
        result = node1.method_name == node2.method_name
    if result and isinstance(node1, GetAttributeNode):
        result = node1.attribute_name == node2.attribute_name
    if result and isinstance(node1, ProceduralNode):
        result = node1.node_type == node2.node_type and _value_equal(
            node1.attrs, node2.attrs
        )
    if result and isinstance(node1, ConstantNode):
        result = _value_equal(node1.value, node2.value)
    if result and isinstance(node1, InputPlaceholderNode):
        result = node1.input_name == node2.input_name and _value_equal(
            node1.default_value, node2.default_value
        )
    if result:
        result = _args_equal(node1.args, node2.args, memo) and _args_equal(
            node1.kwargs, node2.kwargs, memo
        )

    memo[key] = result
    return result


def graph_nodes_equal(graph1: ComputeGraph, graph2: ComputeGraph) -> bool:
    nodes1 = list(traverse_depth_first(graph1))
    nodes2 = list(traverse_depth_first(graph2))
    if len(nodes1) != len(nodes2):
        return False
    memo: dict[tuple[int, int], bool] = {}
    return all(_nodes_equal(node1, node2, memo) for node1, node2 in zip(nodes1, nodes2))


def transform_nodetree(
    root: Node,
    transform_fn: Callable[[Node], Any],
    memo: dict[int, Node] | None = None,
):
    raise NotImplementedError(
        "transform_nodetree is not yet implemented, use transform_compute_graph"
    )

    new_root = transform_fn(root)

    for parent, parent_key, node in traverse_breadth_first(root, parent_child=True):
        if parent is None:
            continue
        elif parent is root:
            parent = new_root

        new_node = transform_fn(node)
        if new_node is None:
            raise ValueError(
                f"Transform function {transform_fn.__name__} returned None for node {node.name}"
            )
        if isinstance(parent_key, int):
            args_list = list(parent.args)
            args_list[parent_key] = new_node
            parent.args = tuple(args_list)
        else:
            parent.kwargs[parent_key] = new_node

    return new_root


def transform_compute_graph(
    compute_graph: ComputeGraph,
    transform_fn: Callable[[Node], Any],
    graph_name: str | None = None,
) -> ComputeGraph:
    id_map: dict[int, Any] = {}

    def lookup(value: Any) -> Any:
        return id_map[id(value)] if isinstance(value, Node) else value

    for node in traverse_depth_first(compute_graph, order="postorder"):
        new_node = copy.copy(node)
        new_node.args = pytree.PyTree(node.args).map(lookup).obj()
        new_node.kwargs = pytree.PyTree(node.kwargs).map(lookup).obj()
        new_node.metadata = copy.copy(node.metadata)

        res = transform_fn(new_node)
        if res is None:
            raise ValueError(f"{transform_fn} returned None for {node=}")
        id_map[id(node)] = res

    new_outputs = compute_graph.outputs.map(lambda v: id_map.get(id(v), v))
    new_inputs = compute_graph.inputs.map(lambda v: id_map.get(id(v), v))

    new_metadata = copy.copy(compute_graph.metadata)
    op = (transform_compute_graph, {"transform_fn": transform_fn, "id_map": id_map})
    new_metadata["operations"] = new_metadata.get("operations", []) + [op]

    return ComputeGraph(
        inputs=new_inputs,
        outputs=new_outputs,
        name=graph_name or compute_graph.name + "_transformed",
        metadata=new_metadata,
    )
