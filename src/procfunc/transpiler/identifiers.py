import logging
import re
from collections import Counter, defaultdict
from typing import Iterable, Literal, TypeVar

import bpy

from procfunc import compute_graph as cg

logger = logging.getLogger(__name__)


def pascal_to_snake(name: str) -> str:
    s = re.sub(r"[./\-\s]+", "_", name or "")
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return "_".join(part.lower() for part in s.split("_") if part)


def snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def bpy_name_to_pythonid(name: str) -> str:
    # remove .00X
    # name = re.sub(r"\.\d+$", "", name)

    # blender often pascal
    name = pascal_to_snake(name)

    # must come after pascal_to_snake or else can jam noncaps together?
    name = name.replace(".", "_")
    name = name.replace(" ", "_")
    name = name.replace(",", "_")
    name = name.replace("=", "")

    name = name.lower()

    name = re.sub(r"_+", "_", name).strip("_")

    # move number terms to end
    parts = name.split("_")
    for i in range(len(parts)):
        if parts[0][0].isdigit():
            parts = parts[1:] + [parts[0]]

    name = "_".join(parts)

    return name


def is_valid_snake_identifier(name: str) -> bool:
    if name == "":
        return False
    if name is None:
        raise ValueError(f"Name {name=!r} is None")
    if "." in name or " " in name:
        return False
    if name[0].isdigit():
        return False
    if name != name.lower():
        return False  # this is opinionated
    return True


def _find_reducible(
    curr_names: dict[int, str],
    mode: Literal["prefix", "postfix"] = "postfix",
    separator: str = ".",
    existing: dict[int, str] | None = None,
    limit_min_fields: int = 2,
    min_str_len_reduce: int = 10,
) -> set[int]:
    new_matched_counts = defaultdict(lambda: [[], 0])

    if existing is not None:
        for node_id, name in existing.items():
            entry = new_matched_counts[name]
            entry[0].append(node_id)
            entry[1] += 1

    def _next_name(name: str) -> str:
        return (
            name[name.find(separator) + 1 :]
            if mode == "postfix"
            else name[name.find(separator) + 1 :]
        )

    def _stop_reduce(newname: str) -> bool:
        return (
            len(newname.split(separator)) <= limit_min_fields
            or len(newname) < min_str_len_reduce
            or not is_valid_snake_identifier(newname)
        )

    for node_id, name in curr_names.items():
        matchval = _next_name(name)
        if _stop_reduce(matchval):
            matchval = name
        if separator in name:
            new_matched_counts[matchval][0].append(node_id)
        new_matched_counts[matchval][1] += 1

    continue_reduce_ids = set()
    for name, (ids, count) in new_matched_counts.items():
        if count != 1 or _stop_reduce(_next_name(name)):
            continue
        filtered = [
            nodeid for nodeid in ids if existing is None or nodeid not in existing
        ]
        continue_reduce_ids.update(filtered)

    return continue_reduce_ids


def duplicate_names(names: dict[int, str]) -> list[str]:
    return [
        (name, count) for name, count in Counter(names.values()).items() if count > 1
    ]


def reduce_name_prefix_suffix(
    names: dict[int, str],
    mode: Literal["prefix", "postfix"] = "postfix",
    separator: str = ".",
    existing: dict[int, str] | None = None,
) -> dict[int, str]:
    """
    remove the maximum number of `.`-separated prefix-fields from every name,
    but make sure the names remain as unique as possible.
    """

    # logger.debug(f"{reduce_name_prefix_suffix.__name__} for {mode=} {separator=} reducing {len(names)=}")

    curr_names = names.copy()

    while continue_reduce := _find_reducible(
        curr_names, mode=mode, separator=separator, existing=existing
    ):
        logger.debug(f"{reduce_name_prefix_suffix.__name__} reducing ")
        for node_id in continue_reduce:
            # TODO: this is not correct, we need to find the longest prefix that is shared by all nodes in the set.
            if mode == "prefix":
                curr_names[node_id] = curr_names[node_id].split(separator, 1)[1]
            else:
                raise NotImplementedError(f"Unsupported mode: {mode}")
                curr_names[node_id] = curr_names[node_id].split(separator, 1)[0]

    output_dups = duplicate_names(curr_names)
    if output_dups:  # and not duplicate_names(names):
        raise ValueError(
            f"{reduce_name_prefix_suffix.__name__} created duplicate names {output_dups} - "
            f"should be impossible, please contact the developers. input names were {names.values()}"
        )

    return curr_names


def apply_panel_names_to_input_names(
    node_tree: bpy.types.NodeTree,
    names: dict[str, str],
    only_dedup: bool = False,
) -> dict[str, str]:
    """
    apply the names of the panel sockets to the input names

    Args:
        node_tree: the node tree to apply the panel names to
        names: the input names to apply the panel names to
        only_dedup: If True, only add the panel name if there are multiple sockets with the same name
    """

    panel_sockets = [
        socket
        for socket in node_tree.interface.items_tree.values()
        if socket.item_type == "PANEL"
    ]

    if len(panel_sockets) == 0:
        return names

    if logger.isEnabledFor(logging.DEBUG):
        socketnames = [socket.name for socket in panel_sockets]
        logger.debug(
            f"apply_panel_names_to_input_names on {node_tree.name=} {only_dedup=} found panel sockets {socketnames=}"
        )

    basename_counts = defaultdict(lambda: 0)
    for socket in node_tree.interface.items_tree.values():
        if socket.item_type == "PANEL":
            continue
        basename_counts[socket.name] += 1

    seen_panel_members = set()
    for panel_socket in panel_sockets:
        for socket in panel_socket.interface_items.values():
            if socket.identifier in seen_panel_members:
                raise ValueError(
                    f"Panel socket {socket.identifier=} {socket.name=} appeared in multiple panels. "
                    "Contact the developers if this is needed."
                )
            seen_panel_members.add(socket.identifier)

            # we will leave .-separation for now so that we can try to dedup unnecessary ones
            panel_name = bpy_name_to_pythonid(panel_socket.name)
            socket_name = bpy_name_to_pythonid(names[socket.identifier])
            if only_dedup and basename_counts[socket.name] == 1:
                names[socket.identifier] = socket_name
            else:
                names[socket.identifier] = panel_name + "." + socket_name

    # any . that werent removed must now become _ to be valid python identifiers
    for k, v in names.items():
        names[k] = v.replace(".", "_")

    return names


TKey = TypeVar("TKey")


def dedup_names_with_suffix(
    names: dict[TKey, str],
    existing: dict[TKey, str] | None = None,
    separator: str = ".",
    order: Iterable[TKey] | None = None,
    first_use_suffix: bool = False,
) -> dict[TKey, str]:
    seen_counts: dict[str, int] = {}
    result_names: dict[TKey, str] = {}

    for nid, name in names.items():
        parts = name.split(separator)
        if len(parts) > 1 and parts[-1].isdigit():
            newname = separator.join(parts[:-1])
            names[nid] = newname

    total_counts = Counter(names.values())

    if existing is not None:
        for name in existing.values():
            if not isinstance(name, str):
                continue
            seen_counts[name] = 1
            if "." in name:
                seen_counts[name.split(".")[0]] = 1

    if order is None:
        order = list(names.keys())

    for node_id in order:
        if node_id not in names:
            continue
        if existing and node_id in existing:
            continue
        orig_name = names[node_id]

        count = seen_counts.get(orig_name, 0)
        if count == 0 and not (first_use_suffix and total_counts[orig_name] > 1):
            result_names[node_id] = orig_name
        else:
            newname = f"{orig_name}{separator}{count}"
            while newname in seen_counts:
                count += 1
                newname = f"{orig_name}{separator}{count}"
            seen_counts[newname] = count + 1
            result_names[node_id] = newname

        seen_counts[orig_name] = count + 1

    if dups := duplicate_names(result_names):
        raise ValueError(
            f"{dedup_names_with_suffix.__name__} created duplicate names {dups} - "
            "should be impossible, please contact the developers. "
            f"{result_names.values()=}"
        )

    return result_names


def _propogate_one_step(
    child: cg.Node,
    parent: cg.Node | None,
    argname: str | int,
    node_names_parts: dict[int, list[str]],
    limit_n_fields: int | None,
    usages: dict[int, list[cg.Node]],
    fold_map: dict[int, bool] | None,
    skip_propogate_words: list[str] | None = None,
):
    if parent is None:
        assert isinstance(argname, str), (argname, parent, child)
        return [argname]
    elif (
        fold_map is not None
        and fold_map.get(id(parent), False)
        and id(parent) not in node_names_parts
    ):
        assert isinstance(argname, str), (argname, parent, child)
        return [argname]
    elif id(parent) not in node_names_parts:
        raise ValueError(
            f"Visited {id(child)} as {argname=} of {id(parent)} {parent=} before parent was named?"
        )

    parent_parts = node_names_parts[id(parent)]

    while len(parent_parts) > 1 and parent_parts[-1] in skip_propogate_words:
        parent_parts = parent_parts[:-1]

    if limit_n_fields is not None and len(parent_parts) > limit_n_fields - 1:
        prefix = parent_parts[0] if parent_parts[0] != "result" else parent_parts[1]
        return [prefix, argname]
    elif fold_map is not None and all(
        fold_map.get(id(usage_parent), False) for usage_parent in usages[id(child)]
    ):
        # no need to have a different name from parent if that parent name is always folded / never used
        return parent_parts
    # elif (
    #    len(usages[id(child)]) == 1
    #    and child.kind == parent.kind
    #    and child.target == parent.target
    # ):
    #    # repeatedly applying a function to the same variable can reuse the same name
    #    return parent_parts
    else:
        return parent_parts + [argname]


def propogate_names_with_parts(
    graph: cg.ComputeGraph,
    fixed_names: dict[int, str] | None = None,
    seen_subgraphs: set[int] | None = None,
    limit_n_fields: int | None = None,
    fold_map: dict[int, bool] | None = None,
    skip_propogate_words: list[str] | None = None,
) -> dict[int, list[str]]:
    # logger.debug(f"{propogate_names_with_parts.__name__} for {graph.name}")

    node_names_parts: dict[int, list[str]] = {}
    fixed_name_ids: set[int] = set()

    if fixed_names is not None:
        for nid, v in fixed_names.items():
            node_names_parts[nid] = list(v.split("_"))
            fixed_name_ids.add(nid)

    for i, (name, outnode) in enumerate(graph.outputs.items()):
        if name == "":
            if len(graph.outputs) == 1:
                name = graph.name + "_result"
            name = f"result_{i}"
        node_names_parts[id(outnode)] = [name]

    if seen_subgraphs is None:
        seen_subgraphs = set()

    usages = cg.usages_per_node(graph)

    for argname, parent, child in cg.traverse_breadth_first(
        graph,
        yield_parent=True,
        yield_name=True,
    ):
        if parent is None:
            continue

        assert isinstance(parent, cg.Node), (parent, child, argname)
        assert argname is not None, (parent, child, argname)

        result = _propogate_one_step(
            child,
            parent,
            argname,
            node_names_parts,
            limit_n_fields,
            usages,
            fold_map,
            skip_propogate_words=skip_propogate_words,
        )

        resname = "_".join(result)
        if not is_valid_snake_identifier(resname):
            parent_name = "_".join(node_names_parts.get(id(parent), []))
            logger.warning(
                f"Propogate from {parent} {parent_name=} to {child=} produced invalid identifier {resname=}"
            )
            continue

        if id(child) not in node_names_parts:
            node_names_parts[id(child)] = result
        elif id(child) not in fixed_name_ids:
            newlen = sum(len(x) for x in result)
            oldlen = sum(len(x) for x in node_names_parts[id(child)])
            if newlen < oldlen:
                node_names_parts[id(child)] = result

    return node_names_parts


def _infill_names_propogate(
    graph: cg.ComputeGraph,
    node_names: dict[int, str],
    fold_map: dict[int, bool],
    existing: dict[int, str],
    skip_propogate_words: list[str] | None = None,
):
    propogated = propogate_names_with_parts(
        graph,
        fixed_names=node_names,
        limit_n_fields=4,
        fold_map=fold_map,
        skip_propogate_words=skip_propogate_words,
    )

    propogated_names = {
        id: "_".join(parts)
        for id, parts in propogated.items()
        if not fold_map.get(id, False)
    }

    propogated_names = dedup_names_with_suffix(
        propogated_names,
        existing={**existing, **node_names},
        separator="_",
        order=reversed([id(n) for n in cg.traverse_depth_first(graph)]),
        first_use_suffix=True,
    )

    # propogated_names = reduce_name_prefix_suffix(
    #    propogated_names,
    #    mode="prefix",
    #    separator="_",
    #    existing={**existing, **node_names},
    # )

    if intersection := set(propogated_names.values()).intersection(
        set(node_names.values())
    ):
        raise ValueError(f"Propogated and node names had overlap: {intersection=}")

    return propogated_names


def _name_from_functionality(node: cg.Node) -> str:
    match node:
        case cg.FunctionCallNode(func=func):
            return func.__name__
        case cg.MethodCallNode(method_name=method_name):
            return method_name
        case cg.SubgraphCallNode(subgraph=subgraph):
            return subgraph.name
        case cg.GetAttributeNode(attribute_name=attribute_name):
            return attribute_name
        case cg.MutatedArgumentNode():
            return _name_from_functionality(node.args[0])
        case cg.ConstantNode():
            return "const"
        case cg.InputPlaceholderNode(input_name=name):
            return name if name else "input"
        case _:
            raise NotImplementedError(f"Unsupported node: {node}")


def _infill_names_function(
    graph: cg.ComputeGraph,
    node_names: dict[int, str],
    fold_map: dict[int, bool],
    existing: dict[int, str],
):
    result = {}
    for node in cg.traverse_depth_first(graph):
        if id(node) in existing:
            continue
        if fold_map[id(node)]:
            continue
        if node_names.get(id(node), None) is not None:
            continue
        result[id(node)] = _name_from_functionality(node)

    result = dedup_names_with_suffix(
        result,
        existing={**existing, **node_names},
        separator="_",
        order=reversed([id(n) for n in cg.traverse_depth_first(graph)]),
    )

    if intersection := set(result.values()).intersection(set(node_names.values())):
        raise ValueError(f"Function and node names had overlap: {intersection=}")

    return result


def _fixed_name_for_node(
    node: cg.Node,
    scope_expressions: dict[int, str],
    avoid_parts: list[str] = [],
) -> str | None:
    """
    If `node` is significant enough to be given a name, rather than being named after
        its later usage, then we will return a str name for it here
    """

    match node:
        case cg.Node(metadata={"varname": varname}):
            return varname
        case cg.SubgraphCallNode(subgraph=subgraph):
            return subgraph.name + "_result"
        case cg.FunctionCallNode(func=func):
            func_resolve = scope_expressions.get(id(func), None)
            module = getattr(func, "__module__", "") or ""
            if not isinstance(func_resolve, str):
                return None
            if not (
                ".geo." in func_resolve
                or ".shader." in func_resolve
                or module.startswith("infinigen_v2.")
            ):
                return None
            name = "_".join(
                part for part in func.__name__.split("_") if part not in avoid_parts
            )
            if "." in func_resolve:
                module_alias = func_resolve.rsplit(".", 1)[0]
                if name == module_alias:
                    name = name + "_result"
            return name
        case _:
            return None


NONDESCRIPTIVE_NODE_NAME_PARTS = [
    "mesh",
    "geometry",
    "bsdf",
    "result",
    "distribution",
]


def nodenames_from_fixed_and_infill(
    graph: cg.ComputeGraph,
    fold_map: dict[int, bool],
    scope_expressions: dict[int, str],
    avoid_parts: list[str] | None = None,
) -> dict[int, str]:
    if avoid_parts is None:
        avoid_parts = NONDESCRIPTIVE_NODE_NAME_PARTS

    node_names = {}

    for name, output in graph.outputs.items():
        if name == "":
            name = _name_from_functionality(output)
        if not fold_map.get(id(output), False):
            node_names[id(output)] = name

    for name, input in graph.inputs.items():
        node_names[id(input)] = name

    for node in cg.traverse_depth_first(graph):
        if fold_map.get(id(node), False):
            continue
        if name := _fixed_name_for_node(
            node, scope_expressions, avoid_parts=avoid_parts
        ):
            node_names[id(node)] = name

    node_names = dedup_names_with_suffix(
        node_names,
        existing=scope_expressions,
        separator="_",
    )

    # node_names = reduce_name_prefix_suffix(
    #     node_names,
    #     mode="prefix",
    #     separator="_",
    #     existing=scope_expressions,
    # )

    result = _infill_names_propogate(
        graph,
        node_names,
        fold_map,
        existing=scope_expressions,
        skip_propogate_words=avoid_parts,
    )
    result.update(node_names)

    for name in result.values():
        if not is_valid_snake_identifier(name):
            logger.warning(f"Invalid node name: {name}")

    return result
