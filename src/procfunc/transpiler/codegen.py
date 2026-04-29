import dataclasses
import enum
import inspect
import itertools
import logging
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Callable, Generator, Union, get_args, get_origin

import numpy as np

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.compute_graph.operators_info import (
    FUNCTIONS_TO_OPERATORS,
    OPERATOR_TEMPLATES,
    OperatorType,
)
from procfunc.nodes import types as nt
from procfunc.transpiler import identifiers
from procfunc.util import pytree

logger = logging.getLogger(__name__)

INDENT = "    "


def indent_lines(lines: list[str], indent: str = INDENT) -> list[str]:
    return [indent + line for line in lines]


def _repr_type(x: Any) -> str:
    # TODO: make the user pass in special resolutions for types, or else we will just do verbose types

    if isinstance(x, str):
        return x

    if x.__name__ == "NoneType":
        return "None"

    origin = get_origin(x)
    args = get_args(x)

    if x.__name__ == "ProcNode":
        if len(args) == 1:
            return f"pf.ProcNode[{_repr_type(args[0])}]"
        elif len(args) == 0:
            return "pf.ProcNode"
        else:
            raise ValueError(f"Unsupported ProcNode type: {x} {args=}")

    if hasattr(pf, x.__name__):
        if len(args):
            raise ValueError(f"procfunc type had unhandled annotations: {x} {args=}")
        return f"pf.{x.__name__}"

    if x.__module__ == "builtins":
        return x.__name__

    origin = get_origin(x)
    args = get_args(x)

    if origin is Union:
        args_0 = get_args(args[0])
        if get_origin(args[0]) is nt.ProcNode and args_0[0] is args[1]:
            return f"t.SocketOrVal[{_repr_type(args_0[0])}]"
        else:
            return " | ".join([_repr_type(a) for a in args])

    if getattr(x, "__module__", None) == "procfunc.nodes.types":
        return f"t.{x.__name__}"

    return x.__name__


def _repr_value(value: Any) -> str:
    if hasattr(value, "__wrapped__"):
        value = value.__wrapped__

    if isinstance(value, cg.Proxy):
        logger.warning(
            f"Proxy object {value} should never appear as a raw value in codegen - "
            f"its underlying node {value.node} was not resolved to a variable"
        )
    if isinstance(value, nt.ProcNode):
        logger.warning(
            f"Procnode object {value} should never be treated as a raw value in codegen"
        )

    if isinstance(value, np.random.Generator):
        return "np.random.default_rng()"
    elif isinstance(value, type):
        return _repr_type(value)
    elif isinstance(value, np.ndarray):
        nprepr = repr(value).replace("\n", "")
        return f"np.{nprepr}"
    elif isinstance(value, np.dtype):
        return f"np.dtype('{value}')"
    elif isinstance(value, (pf.Color, pf.Vector, pf.Euler, pf.Quaternion, pf.Matrix)):
        x = tuple(round(x, 6) for x in value)
        return f"pf.{value.__class__.__name__}({x})"
    elif isinstance(value, enum.Enum):
        return f"{type(value).__name__}.{value.name}"
    elif isinstance(value, Path):
        return f"Path({str(value)!r})"
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        args_str = ", ".join(
            f"{f.name}={_repr_value(getattr(value, f.name))}"
            for f in dataclasses.fields(value)
        )
        return f"{type(value).__name__}({args_str})"
    elif isinstance(value, list):
        return f"[{', '.join([_repr_value(x) for x in value])}]"
    else:
        return repr(value)


def _repr_inp(
    arg: Any,
    scope_expressions: dict[int, str | list[str]],
    extra_parens: bool = False,
) -> str:
    if isinstance(arg, cg.Node):
        if id(arg) not in scope_expressions:
            raise ValueError(
                f"Scope expressions {scope_expressions} did not contain {arg=} possibly due to bad visit ordering"
            )
        expr = scope_expressions[id(arg)]
    else:
        expr = _repr_value(arg)

    if isinstance(expr, list):
        if len(expr) > 1:
            raise ValueError(
                "Inlined values should not resolve to more than one line in current implementation, "
                f"got {expr=} for {arg=}"
            )
        expr = expr[0]
    assert isinstance(expr, str)

    if " " in expr and extra_parens and expr[0] != "(" and expr[-1] != ")":
        return f"({expr})"
    else:
        return expr


def _kwarg_matches_default(sig: inspect.Signature, key: str, value: Any) -> bool:
    if isinstance(value, (cg.Node, cg.Proxy)):
        return False
    param = sig.parameters.get(key)
    if param is None or param.default is inspect.Parameter.empty:
        return False
    try:
        return bool(value == param.default)
    except Exception:
        return False


def _repr_args(
    func: Callable[..., Any] | None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    scope_expressions: dict[int, str | list[str]],
) -> list[str]:
    """
    Create string for arg and kwarg def for function inputs
    """

    try:
        sig = inspect.signature(func) if func is not None else None
    except ValueError:
        sig = None

    if sig is not None:
        kwargs = {
            k: v for k, v in kwargs.items() if not _kwarg_matches_default(sig, k, v)
        }

    # common specialcase: nodes with a single output which would unnecessarily be a kwarg can just be a positional arg instead
    if len(args) == 0 and len(kwargs) == 1 and sig is not None:
        if next(iter(kwargs)) == next(iter(sig.parameters)):
            args = (kwargs[next(iter(kwargs))],)
            kwargs = {}

    argreprs = pytree.PyTree(args).map(lambda x: _repr_inp(x, scope_expressions))
    argreprs = [
        pytree.repr_tree_to_str(v, type_namer=_repr_type)
        for v in argreprs.unflatten_one_level()
    ]

    kwargreprs = (
        pytree.PyTree(kwargs)
        .map(lambda x: _repr_inp(x, scope_expressions))
        .unflatten_one_level()
    )
    kwargreprs = {
        k: pytree.repr_tree_to_str(v, type_namer=_repr_type)
        for k, v in kwargreprs.items()
    }

    # use func sig to sort kwargs
    if sig is not None:
        kwargkeys = list(sig.parameters.keys())
        has_var_keyword = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        )
        if not has_var_keyword:
            assert set(kwargreprs.keys()).issubset(set(kwargkeys)), (
                f"{kwargreprs.keys()=} {kwargkeys=}"
            )
        else:
            kwargkeys = kwargkeys + [k for k in kwargreprs.keys() if k not in kwargkeys]
    else:
        kwargkeys = list(kwargs.keys())

    kwarglist = [f"{k}={kwargreprs[k]}" for k in kwargkeys if k in kwargreprs]

    return argreprs + kwarglist


def _repr_function_call(
    node: cg.FunctionCallNode | cg.MethodCallNode | cg.SubgraphCallNode,
    scope_expressions: dict[int, str | list[str]],
    line_limit: int = 80,
) -> list[str]:
    match node:
        case cg.FunctionCallNode():
            func = node.func
            func_str = scope_expressions[id(func)]
        case cg.MethodCallNode(args=(target, *_), method_name=method_name):
            if not isinstance(target, cg.Node):
                raise ValueError(f"Method call {node=} has non-node target {target=}")
            func = None
            func_str = f"{_repr_inp(target, scope_expressions)}.{method_name}"
        case cg.SubgraphCallNode(subgraph=subgraph):
            func = None
            func_str = scope_expressions.get(id(subgraph))
            if func_str is None:
                raise ValueError(
                    f"Scope expressions did not contain definition for {subgraph=}"
                )
            assert isinstance(func_str, str), func_str
        case _:
            raise TypeError(f"Unsupported {node=}")

    args = node.args[1:] if isinstance(node, cg.MethodCallNode) else node.args
    arg_reprs = _repr_args(func, args, node.kwargs, scope_expressions)  # type: ignore

    if len(arg_reprs) == 0:
        return [f"{func_str}()"]

    total_len = len(func_str) + sum(len(arg) for arg in arg_reprs)
    multiline = total_len > line_limit

    if len(arg_reprs) > 1 and multiline:
        arg_reprs = [line + "," for line in arg_reprs]

    if multiline:
        return [f"{func_str}("] + indent_lines(arg_reprs) + [")"]
    else:
        return [f"{func_str}({', '.join(arg_reprs)})"]


def _repr_operator_call(
    node: cg.FunctionCallNode,
    scope_expressions: dict[int, str | list[str]],
) -> list[str]:
    assert isinstance(node, cg.FunctionCallNode), node

    # Support both positional args and kwargs for operator templates
    all_args = [
        _repr_inp(v, scope_expressions, extra_parens=True) for v in node.args
    ] + [
        _repr_inp(v, scope_expressions, extra_parens=True) for v in node.kwargs.values()
    ]

    operator_template = scope_expressions[id(node.func)]
    assert isinstance(operator_template, str), operator_template
    return [operator_template.format(*all_args)]


def _codegen_for_node(
    node: cg.Node,
    scope_expressions: dict[int, str | list[str]],
) -> list[str]:
    match node:
        case cg.FunctionCallNode(func=func):
            funcres = scope_expressions[id(func)]
            if isinstance(funcres, list):
                raise ValueError(
                    f"{node} resolved to {funcres} but functions should always resolve to names, not expressions"
                )
            elif funcres == OperatorType.NOOP:
                return []  # no code needed
            elif "{}" in funcres:
                return _repr_operator_call(node, scope_expressions)
            else:
                return _repr_function_call(node, scope_expressions)
        case cg.MethodCallNode() if node.method_name == "__getitem__":
            callee_expr = _repr_inp(node.args[0], scope_expressions)
            idx_expr = _repr_inp(node.args[1], scope_expressions)
            return [f"{callee_expr}[{idx_expr}]"]
        case cg.MethodCallNode():
            return _repr_function_call(node, scope_expressions)
        case cg.SubgraphCallNode():
            return _repr_function_call(node, scope_expressions)
        case cg.GetAttributeNode(args=(source,), attribute_name=attribute_name):
            arg_expr = scope_expressions[id(source)]
            if isinstance(arg_expr, list) and len(arg_expr) == 1:
                arg_expr = arg_expr[0]
            if not isinstance(arg_expr, str):
                raise ValueError(
                    f"Attribute access {attribute_name!r} on {source!r} resolved to {arg_expr} but should be a string"
                )
            if " " in arg_expr:
                raise ValueError(
                    f"f{_codegen_for_node.__name__} got would attempt to create getattr expression "
                    f"{arg_expr!r}.{attribute_name} due to space in {arg_expr=} "
                    f"for {id(node)=} {node=} {id(source)=} {source=}"
                )
            return [f"{arg_expr}.{attribute_name}"]
        case cg.ConstantNode(value=value):
            return [_repr_value(value)]
        case _:
            raise TypeError(f"Unsupported {node=}")


def _codegen_graph_inputs(
    graph: cg.ComputeGraph,
    node_names: dict[int, str],
    typename: str | None,
    func_name: str | None = None,
) -> list[str]:
    args = sorted(
        list(graph.inputs.values()),
        key=lambda x: x.kwargs.get("default_value", None) is not None,
    )

    func_name = func_name or graph.name

    if logger.isEnabledFor(logging.DEBUG):
        argnames = [node_names.get(id(node)) for node in args]
        logger.debug(f"Codegen inputs for {func_name} {argnames=}")

    if len(args) == 0:
        return [f"def {func_name}():"]

    args_lines = []
    for node in args:
        if id(node) not in node_names:
            raise ValueError(f"Node {node} has no name in {node_names}")
        name = node_names[id(node)]

        known_value_type = node.metadata.get("known_value_type", None)
        line = (
            f"{name}: {_repr_type(known_value_type)}"
            if known_value_type is not None
            else f"{name}"
        )

        if (default := node.kwargs.get("default_value")) is not None:
            line += f" = {_repr_value(default)}"

        args_lines.append(line + ",")

    end_statement = "):" if typename is None else f") -> {typename}: "

    return [f"def {func_name}("] + indent_lines(args_lines) + [end_statement]


def _codegen_namedtuple_def(outputs: pytree.PyTree):
    tupletype = outputs.toplevel_type()

    type_lines = []
    for name, node in outputs.items():
        if node is None:
            continue
        vt = node.metadata.get("known_value_type", None)
        if vt is None:
            type_lines.append(f"{name}: Any")
        else:
            type_lines.append(f"{name}: {_repr_type(vt)}")

    return [f"class {tupletype.__name__}(NamedTuple):"] + indent_lines(type_lines)


def _codegen_for_outputs(
    graph: cg.ComputeGraph,
    scope_expressions: dict[int, str | list[str]],
) -> tuple[str | None, list[str], list[str]]:
    if len(graph.outputs) == 0:
        return None, [], []
    if len(graph.outputs) == 1:
        single_output = next(graph.outputs.values())
        vt = single_output.metadata.get("known_value_type", None)
        type_name = _repr_type(vt) if vt is not None else None
        return type_name, [], [f"return {_repr_inp(single_output, scope_expressions)}"]

    graph_output_type = graph.outputs.toplevel_type()
    type_name = _repr_type(graph_output_type)

    is_pf_type = hasattr(pf, graph_output_type.__name__)
    if is_pf_type:
        type_def = []
    elif graph_output_type.__module__ == "builtins":
        type_def = []
    elif id(graph_output_type) in scope_expressions:
        assert scope_expressions[id(graph_output_type)] == type_name
        logger.debug(f"Skipping redefinition of {graph_output_type}")
        type_def = []
    elif pytree.is_type_namedtuple(graph_output_type):
        type_def = _codegen_namedtuple_def(graph.outputs)
        scope_expressions[id(graph_output_type)] = type_name
    else:
        raise ValueError(f"Unhandled graph output type: {graph_output_type}")

    reprs_tree = graph.outputs.map(lambda node: _repr_inp(node, scope_expressions))
    return_lines = [
        f"return {pytree.repr_tree_to_str(reprs_tree, type_namer=_repr_type)}"
    ]

    return type_name, type_def, return_lines


def _check_graph_input_names(
    graph: cg.ComputeGraph,
    scope_names: dict[int, str],
):
    input_names = {id(node): name for name, node in graph.inputs.items()}
    if len(input_names.values()) != len(set(input_names.values())):
        raise ValueError(
            f"Input names for {graph.name} had duplicate values. {input_names.values()=}"
        )

    overlap = set(input_names.values()).intersection(set(scope_names.values()))
    for k, v in input_names.items():
        if v not in overlap:
            continue

        newname = v + "_val"
        assert newname not in input_names.values()
        input_names[k] = newname
        logger.warning(
            f"Renaming input {k=} of {graph.name=} from {v} to {newname} to avoid "
            f"collision, since {v} is also the name of a util function"
        )

    for orig_name, node in graph.inputs.items():
        identifier = input_names[id(node)]
        if not identifiers.is_valid_snake_identifier(identifier):
            raise ValueError(
                f"{graph.name=} had input {orig_name=} {node=} which recieved invalid identifier {identifier=}"
            )

    return input_names


def _codegen_graph_decorator(graph: cg.ComputeGraph) -> list[str]:
    if graph.metadata.get("is_node_function"):
        return ["@pf.nodes.node_function"]
    return []


def _should_fold_node(
    node: cg.Node,
    parent: cg.Node | None,
    scope_expressions: dict[int, str | list[str]],
    usages: dict[int, list[cg.Node]],
    fold_map: dict[int, bool],
) -> bool:
    if isinstance(node, cg.MethodCallNode) and node.method_name in (
        "astype",
        "__getitem__",
    ):
        return True

    if isinstance(node, cg.GetAttributeNode):
        return True

    if any(isinstance(u, cg.GetAttributeNode) for u in usages.get(id(node), [])):
        return False

    if len(usages.get(id(node), [])) > 1:
        return False

    if parent is None:
        return False

    if (
        isinstance(node, cg.FunctionCallNode)
        and "{}" in scope_expressions[id(node.func)]
    ):
        return not fold_map.get(id(parent), False)

    return False


def _expression_fold_map(
    graph: cg.ComputeGraph,
    scope_expressions: dict[int, str | list[str]],
    usages: dict[int, list[cg.Node]],
) -> dict[int, bool]:
    fold_map: dict[int, bool] = {}

    for output in graph.outputs.values():
        fold_map[id(output)] = (
            output is None
            or isinstance(output, cg.ConstantNode)
            or isinstance(output, cg.GetAttributeNode)
        )
    for parent, node in cg.traverse_breadth_first(graph, yield_parent=True):
        if id(node) in fold_map:
            continue  # dont overwrite output settings
        should_fold = _should_fold_node(
            node, parent, scope_expressions, usages, fold_map
        )
        fold_map[id(node)] = should_fold

    return fold_map


def traverse_chunks(
    graph: cg.ComputeGraph,
    pred: Callable[[cg.Node, list[cg.Node]], bool],
) -> Generator[list[cg.Node], None, None]:
    visited = set()

    def _greedy_singleuses(node: cg.Node, chunk: list[cg.Node]):
        if id(node) in visited:
            return
        visited.add(id(node))
        yield node

        for arg in itertools.chain(node.args, node.kwargs.values()):
            if not isinstance(arg, cg.Node):
                continue
            if id(arg) in visited:
                continue
            if not pred(arg, chunk):
                continue
            yield from _greedy_singleuses(arg, chunk)

    for node in cg.traverse_breadth_first(graph):
        if id(node) in visited:
            continue
        chunk = []
        yield list(_greedy_singleuses(node, chunk))


def _code_paragraphing_predicate(
    node: cg.Node,
    chunk: list[cg.Node],
    scope_expressions: dict[int, str | list[str]],
    usages: dict[int, list[cg.Node]],
) -> bool:
    if not isinstance(node, cg.FunctionCallNode):
        return False

    target_expr = scope_expressions[id(node.func)]
    if not (".math." not in target_expr or "{}" not in target_expr):
        return False

    uses = usages[id(node)]
    if len(uses) == 1:
        return True
    elif not all(any(id(u) == id(v) for v in chunk) for u in uses):
        return False

    return True


def _codegen_for_assignment(
    assign_varname: str,
    node_code: list[str] | str,
    add_line_comments: bool,
) -> list[str]:
    assert isinstance(assign_varname, str)
    assert identifiers.is_valid_snake_identifier(assign_varname)

    if isinstance(node_code, list):
        node_code[0] = f"{assign_varname} = " + node_code[0]
    else:
        node_code = [f"{assign_varname} = {node_code}"]
    if add_line_comments:
        node_code[0] += f" # {node}"  # noqa: F821

    return node_code


def _expressions_scope_for_graph(
    graph: cg.ComputeGraph,
    scope_expressions: dict[int, str | list[str]],
) -> tuple[dict[int, str | list[str]], dict[int, bool]]:
    expressions: dict[int, str | list[str]] = {
        **scope_expressions.copy(),
        **_check_graph_input_names(graph, scope_expressions),
    }

    # when we want to refer to a value, what string should we insert?
    # - for most nodes: refer to a variable name
    # - for inlined expressions: emplace a expression string
    usages = cg.usages_per_node(graph)
    fold_map = _expression_fold_map(graph, expressions, usages=usages)

    node_names = identifiers.nodenames_from_fixed_and_infill(
        graph,
        fold_map=fold_map,
        scope_expressions=expressions,
    )
    if duplicates := identifiers.duplicate_names(node_names):
        raise ValueError(f"Duplicate node names: {duplicates}")

    if intersection := set(expressions.values()).intersection(set(node_names.values())):
        raise ValueError(f"Scope and node names had overlap: {intersection=}")
    expressions.update(node_names)

    return expressions, fold_map


def _codegen_for_graph(
    graph: cg.ComputeGraph,
    scope_expressions: dict[int, str],
    as_maincall: bool = True,
    add_version_comment: bool = True,
    add_line_comments: bool = False,
    func_name: str | None = None,
) -> list[str]:
    code_lines: list[str] = []

    if add_version_comment:
        code_lines.append(f"# Code generated by procfunc v{pf.__version__}")

    expressions, fold_map = _expressions_scope_for_graph(graph, scope_expressions)
    _input_ids = set(id(node) for node in graph.inputs.values())  # noqa: F841

    last_varname: str = ""

    # Collect mutator call nodes so they emit as bare statements (no assignment)
    mutator_call_ids = set()
    for node in cg.traverse_depth_first(graph):
        if isinstance(node, cg.MutatedArgumentNode):
            mutator_call_ids.add(id(node.args[1]))

    for node in cg.traverse_depth_first(graph):
        if isinstance(node, cg.InputPlaceholderNode):
            continue  # arguments are defined in _codegen_graph_inputs
        if isinstance(node, cg.MutatedArgumentNode):
            # alias to the original node, since mutation is in-place
            original_node = node.args[0]
            expressions[id(node)] = expressions[id(original_node)]
            continue

        node_code = _codegen_for_node(node, expressions.copy())

        if fold_map[id(node)]:
            assert id(node) not in expressions, f"{node=} {expressions[id(node)]=}"
            expressions[id(node)] = node_code
            continue

        if id(node) in mutator_call_ids:
            code_lines.extend(node_code if isinstance(node_code, list) else [node_code])
            continue

        varname = expressions[id(node)]
        node_code = _codegen_for_assignment(varname, node_code, add_line_comments)
        code_lines.extend(node_code)

        if last_varname.split("_")[0] != varname.split("_")[0]:
            code_lines.append("")
        last_varname = varname

    if as_maincall:
        assert len(graph.inputs) == 0, graph.inputs
        return ["if __name__ == '__main__':"] + indent_lines(code_lines)

    typename, typedef, return_lines = _codegen_for_outputs(graph, expressions)

    return (
        typedef
        + [""]
        + _codegen_graph_decorator(graph)
        + _codegen_graph_inputs(graph, expressions, typename, func_name=func_name)
        + indent_lines(code_lines)
        + indent_lines(return_lines)
    )


def _resolve_func(func: Any) -> tuple[str | None, str]:
    """
    Returns:
        tuple[str, str]: import string, function callsite string
    """

    if isinstance(func, np.ufunc):
        return "import numpy as np", f"np.{func.__name__}"

    module = getattr(func, "__module__", None)

    if module is None:
        raise NotImplementedError(f"Unsupported function: {func}")
    elif module == "builtins":
        return None, func.__name__
    elif module.startswith("procfunc."):
        callsite = "pf." + module[len("procfunc.") :] + "." + func.__name__
        importstring = "import procfunc as pf"
        return importstring, callsite
    elif module.startswith("infinigen_v2."):
        parent, _, mod_name = module.rpartition(".")
        importstring = f"from {parent} import {mod_name}"
        callsite = f"{mod_name}.{func.__name__}"
        return importstring, callsite
    else:
        callsite = f"{module}.{func.__name__}"
        importstring = f"import {module}"
        return importstring, callsite


def default_func_resolution_map(
    toplevel_graph: cg.ComputeGraph,
    skip_funcs: set | None = None,
) -> tuple[dict[Any, str | OperatorType], list[str]]:
    func_resolution = {}
    import_lines = set()

    for graph in cg.traverse_nested_graphs(toplevel_graph):
        assert isinstance(graph, cg.ComputeGraph), graph
        for node in cg.traverse_depth_first(graph):
            if not isinstance(node, cg.FunctionCallNode):
                continue

            if skip_funcs is not None and node.func in skip_funcs:
                continue

            if node.func in FUNCTIONS_TO_OPERATORS:
                func_resolution[node.func] = FUNCTIONS_TO_OPERATORS[node.func]
                continue

            importstring, callsite = _resolve_func(node.func)
            func_resolution[node.func] = callsite
            if importstring is not None:
                import_lines.add(importstring)

    return func_resolution, list(import_lines)


def _topo_sort_subgraphs(graph: cg.ComputeGraph) -> list[cg.ComputeGraph]:
    """DFS post-order traversal: dependencies before dependents."""
    visited = set()
    result = []

    def visit(g: cg.ComputeGraph):
        if id(g) in visited:
            return
        visited.add(id(g))
        for node in cg.traverse_depth_first(g):
            if isinstance(node, cg.SubgraphCallNode):
                visit(node.subgraph)
        result.append(g)

    visit(graph)
    return result


def graphs_to_python_functions(
    graph: cg.ComputeGraph,
    func_resolution: dict[Any, str],
    toplevel_as_maincall: bool = True,
    add_version_comment: bool = True,
    add_line_comments: bool = False,
) -> OrderedDict[str, list[str]]:
    np_linewidth = np.get_printoptions()["linewidth"]
    np.set_printoptions(linewidth=100000)

    targets = _topo_sort_subgraphs(graph)

    def _clean_graph_name(name: str) -> str:
        for suffix in identifiers.NONDESCRIPTIVE_NODE_NAME_PARTS:
            if name.endswith("_" + suffix):
                name = name[: -(len(suffix) + 1)]
        return name

    for subgraph in cg.traverse_nested_graphs(graph):
        subgraph.name = _clean_graph_name(subgraph.name)

    subgraph_names = {
        id(subgraph): subgraph.name for subgraph in cg.traverse_nested_graphs(graph)
    }
    subgraph_names = identifiers.dedup_names_with_suffix(subgraph_names, separator="_")

    scope_expressions = subgraph_names.copy()
    for k, v in func_resolution.items():
        if isinstance(v, OperatorType):
            scope_expressions[id(k)] = OPERATOR_TEMPLATES[v]
        else:
            scope_expressions[id(k)] = v

    lines_for_modules = []
    for subgraph in targets:
        func_name = subgraph_names[id(subgraph)]
        result = _codegen_for_graph(
            subgraph,
            scope_expressions=scope_expressions.copy(),
            as_maincall=(subgraph is graph and toplevel_as_maincall),
            add_version_comment=add_version_comment,
            add_line_comments=add_line_comments,
            func_name=func_name,
        )
        lines_for_modules.append((subgraph_names[id(subgraph)], result))

    np.set_printoptions(linewidth=np_linewidth)

    return OrderedDict(lines_for_modules)


def _define_multiuse_return_types(
    graph: cg.ComputeGraph,
    func_resolution: dict,
) -> list[str]:
    counts, graphs_by_type, seen = defaultdict(int), {}, set()
    for subgraph in cg.traverse_nested_graphs(graph):
        rettype = subgraph.outputs.toplevel_type()

        if (
            id(subgraph) in seen
            or rettype is None
            or hasattr(pf, rettype.__name__)
            or not pytree.is_type_namedtuple(rettype)
        ):
            continue
        seen.add(id(subgraph))

        counts[rettype] += 1
        graphs_by_type[rettype] = subgraph
        # logger.debug(f"Found {rettype=} for {subgraph.name} {counts[rettype]=}")

    multiuse = {
        rettype: subgraph
        for rettype, subgraph in graphs_by_type.items()
        if counts[rettype] > 1
    }

    lines = []
    for rettype, subgraph in multiuse.items():
        lines.extend(_codegen_namedtuple_def(subgraph.outputs))
        lines.append("")
        func_resolution[rettype] = rettype.__name__

    return lines


def _collect_graph_value_imports(graph: cg.ComputeGraph) -> list[str]:
    import_lines = set()

    def _collect_from_value(v):
        if isinstance(v, cg.Node):
            return
        if isinstance(v, enum.Enum):
            t = type(v)
            if t.__module__ != "builtins":
                import_lines.add(f"from {t.__module__} import {t.__name__}")
        elif isinstance(v, Path):
            import_lines.add("from pathlib import Path")
        elif dataclasses.is_dataclass(v) and not isinstance(v, type):
            t = type(v)
            if t.__module__ != "builtins":
                import_lines.add(f"from {t.__module__} import {t.__name__}")
            for f in dataclasses.fields(v):
                _collect_from_value(getattr(v, f.name))
        elif isinstance(v, list):
            for item in v:
                _collect_from_value(item)

    for subgraph in cg.traverse_nested_graphs(graph):
        for node in cg.traverse_depth_first(subgraph):
            for arg in itertools.chain(node.args, node.kwargs.values()):
                _collect_from_value(arg)

    return list(import_lines)


def to_python(
    graph: cg.ComputeGraph,
    func_resolution: dict[Any, str | OperatorType] | None = None,
    import_lines: list[str] | None = None,
    toplevel_as_maincall: bool = True,
    add_version_comment: bool = True,
    add_line_comments: bool = False,
) -> str:
    code_lines = []
    code_lines.append("from typing import NamedTuple, Annotated")
    code_lines.append("import numpy as np")
    code_lines.append("import bpy")
    # code_lines.append("import logging; logging.basicConfig(level=logging.DEBUG)")
    code_lines.append("from procfunc.nodes import types as t")
    code_lines.append("from procfunc.nodes.types import ProcNode, SocketOrVal")

    if func_resolution is None:
        func_resolution, import_lines = default_func_resolution_map(graph)
    else:
        assert import_lines is not None

    all_imports = set(import_lines) | set(_collect_graph_value_imports(graph))
    code_lines.extend(sorted(all_imports))
    code_lines.append("")

    code_lines.extend(_define_multiuse_return_types(graph, func_resolution))

    lines_for_modules = graphs_to_python_functions(
        graph,
        func_resolution,
        add_version_comment=add_version_comment,
        add_line_comments=add_line_comments,
        toplevel_as_maincall=toplevel_as_maincall,
    )
    for module_name, module_lines in lines_for_modules.items():
        code_lines.extend(module_lines)
        code_lines.append("")

    return "\n".join(code_lines)
