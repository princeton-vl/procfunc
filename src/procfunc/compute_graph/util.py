import copy
import logging
from collections import defaultdict, deque
from typing import Any, Callable, Generator, Literal, TypeVar

from procfunc.util import pytree

from .compute_graph import ComputeGraph
from .node import Node, SubgraphCallNode

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

        if node is None:
            continue

        if id(node) in visited:
            continue
        visited.add(id(node))

        yield res(parent, name, node)

        children = list(pytree.PyTree(node.args).items()) + list(
            pytree.PyTree(node.kwargs).items()
        )
        for key, arg in children:
            if not yield_consts and not isinstance(arg, Node):
                continue
            if id(arg) in visited:
                continue
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
        if node is None:
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


def graph_nodes_equal(graph1: ComputeGraph, graph2: ComputeGraph) -> bool:
    nodes1 = list(traverse_depth_first(graph1))
    nodes2 = list(traverse_depth_first(graph2))
    if len(nodes1) != len(nodes2):
        return False
    for node1, node2 in zip(nodes1, nodes2):
        if type(node1) is not type(node2):
            return False
        if isinstance(node1, SubgraphCallNode):
            if not graph_nodes_equal(node1.subgraph, node2.subgraph):
                return False
        elif node1.args != node2.args or node1.kwargs != node2.kwargs:
            return False
    return True


def transform_nodetree(
    root: Node,
    transform_fn: Callable[[Node], Any],
    memo: dict[int, Node] = {},
):
    raise NotImplementedError("Not implemented")

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
):
    raise NotImplementedError("Not implemented")

    id_map: dict[int, Node] = {}

    def wrapper(node: Node) -> Node:
        res = transform_fn(node)
        id_map[id(node)] = res
        return res

    memo = {}

    new_output_values = [
        transform_nodetree(v, wrapper, memo) for v in compute_graph.outputs.values()
    ]
    new_output = pytree.PyTree.from_values(new_output_values, compute_graph.output.spec)

    new_metadata = copy.copy(compute_graph.metadata)
    if "operations" not in new_metadata:
        new_metadata["operations"] = []
    op = (transform_compute_graph, {"transform_fn": transform_fn, "id_map": id_map})
    new_metadata["operations"].append(op)

    new_inputs = compute_graph.inputs.map(lambda v: id_map[id(v)])

    return ComputeGraph(
        inputs=new_inputs,
        outputs=new_output,
        name=compute_graph.name + "_transformed",
        metadata=new_metadata,
    )
