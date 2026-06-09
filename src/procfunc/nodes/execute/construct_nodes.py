import logging
from typing import Any

import bpy

from procfunc import compute_graph as cg
from procfunc import types as pt
from procfunc.compute_graph.operators_info import OPERATORS_TO_FUNCTIONS
from procfunc.nodes import bpy_node_info as bni
from procfunc.nodes import func as pf_func
from procfunc.nodes import math as pf_math
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import (
    ContextualNode,
    RuntimeResolveDataType,
    resolve_contextual_node,
)
from procfunc.util import pytree
from procfunc.util.bpy_info import bpy_nocollide_data_name
from procfunc.util.log import add_exception_context_msg

from .construct_special_cases import NODE_SPECIAL_CASES
from .infer_runtime_data_type import (
    VectorLike,
    _infer_value_math_type,
    infer_operation_type,
    map_data_type_for_differing_node_interface,
    resolve_operation_data_type,
)
from .util import (
    NODE_OPERATOR_TABLE,
    NodeOperatorResolution,
    assign_default_value,
    get_active_sockets,
    get_input_socket_to_connect_to,
    get_nth_socket,
    normalize_socket_type,
)

logger = logging.getLogger(__name__)


def connect_single_input(
    node_tree: bpy.types.NodeTree,
    to_socket: bpy.types.NodeSocket,
    input_val: bpy.types.NodeSocket | Any | None,
):
    if isinstance(input_val, nt.ProcNode):
        raise ValueError(
            f"ProcNode {input_val} is not allowed as input to {to_socket.name}"
        )

    match input_val:
        case None:
            pass
        # case nt.Keyframes():
        #    apply_keyframes(to_input_socket, input_val)
        case bpy.types.NodeSocket() as from_socket:
            _connect_socket(node_tree, from_socket, to_socket, input_val.node.name)
        case bpy.types.NodeInternal():
            raise ValueError(
                f"{input_val=} is a bpy.types.NodeInternal, but this should have been "
                f"resolved to a specific socket at an earlier stage"
            )
        case _ if hasattr(to_socket, "default_value"):
            assign_default_value(to_socket, input_val)
        case _:
            raise ValueError(
                f"Could not handle {input_val=} as input to {to_socket.name=}"
            )


def connect_multisocket_input(
    node_tree: bpy.types.NodeTree,
    to_socket: bpy.types.NodeSocket,
    input_result: list[bpy.types.NodeSocket | Any | None],
    from_py_input: list[cg.Node],
):
    if not to_socket.is_multi_input:
        raise ValueError(
            f"list of sockets {input_result} is not valid to connect to {to_socket} as it is not a "
            f"valid multi-input socket"
        )

    assert isinstance(input_result, list)
    assert isinstance(from_py_input, list)

    for input_val, py_input in zip(input_result, from_py_input):
        if input_val is None:
            continue
        connect_single_input(node_tree, to_socket, input_val)


def _connect_socket(
    node_tree: bpy.types.NodeTree,
    source_socket: bpy.types.NodeSocket,
    target_socket: bpy.types.NodeSocket,
    source_node_name: str = "unknown",
):
    """Helper function to connect sockets with type compatibility checking."""
    output_type = getattr(source_socket, "bl_idname", source_socket.type)
    input_type = getattr(target_socket, "bl_idname", target_socket.type)

    normalized_output = normalize_socket_type(output_type)
    normalized_input = normalize_socket_type(input_type)

    if not bni.are_socket_types_compatible(normalized_output, normalized_input):
        raise ValueError(
            f"Incompatible socket types: cannot connect {output_type} output to {input_type} input. "
            f"Source: {source_node_name}.{source_socket.name} -> "
            f"Target: {getattr(target_socket.node, 'name', 'unknown')}.{target_socket.name}"
        )

    node_tree.links.new(source_socket, target_socket)


def _get_primary_output_socket(
    node_spec: cg.Node,
    bpy_node: bpy.types.Node,
) -> bpy.types.NodeSocket:
    """
    Sometimes a node will have multiple output sockets, but the user didnt say which one they want.
    """

    enabled = list(get_active_sockets(bpy_node.outputs))
    if len(enabled) == 0:
        raise ValueError(
            f"Got {len(enabled)=} enabled sockets for {node_spec=} {bpy_node.name=}"
        )
    if len(enabled) == 1:
        assert isinstance(enabled[0], bpy.types.NodeSocket), enabled[0]
        return enabled[0]
    names = [socket.name for socket in enabled]

    raise ValueError(
        f"{node_spec=} should have a single anonymous output, "
        f"but there was actually >1 {enabled=} {names=} for {bpy_node.bl_idname=}"
    )


def _find_operator_row(
    func: Any, data_type: bni.NodeDataType
) -> NodeOperatorResolution:
    search = (
        row
        for row in NODE_OPERATOR_TABLE
        if (
            row.operand_types is None
            and row.value_type == data_type
            and OPERATORS_TO_FUNCTIONS[row.operator_type] is func
        )
    )
    op_row = next(search, None)
    if op_row is None:
        raise ValueError(
            f"User called inline binary operator to invoke {func=} on {data_type=} "
            f"but this data type does not support that operator. Consider explicitly casting to another type with val.astype()"
        )
    return op_row


def _bind_positional_to_tuple_kwargs(
    node: cg.Node, input_results: dict[str | int, Any]
) -> dict[str | int, Any]:
    """
    operator call recieved input_results with anonymous positional args, which have keys 0, 1, 2
    we need to match these up against the node's expected tuple input keys e.g. ("Value", 0) uses the 0th positional arg
    """

    inputs_bound = {}
    for k, v in node.kwargs.items():
        assert isinstance(k, tuple)
        assert isinstance(k[1], int)
        if v is None:
            inputs_bound[k] = None
        else:
            inputs_bound[k] = input_results[k[1]]

    return inputs_bound


_VECTORLIKE_BY_LENGTH = {
    3: bni.NodeDataType.FLOAT_VECTOR,
    4: bni.NodeDataType.RGBA,
}


def _operand_matches(
    operand_dtype: bni.NodeDataType | VectorLike | None,
    row_dtype: bni.NodeDataType,
) -> bool:
    """Does a single operand satisfy a row's required dtype? A VectorLike (a
    raw tuple/list of unknown semantic) matches by its length, a concrete
    NodeDataType by equality."""
    if isinstance(operand_dtype, VectorLike):
        return _VECTORLIKE_BY_LENGTH.get(operand_dtype.length) == row_dtype
    return operand_dtype == row_dtype


def _match_operand_permutation(
    operand_dtypes: list[bni.NodeDataType | VectorLike | None],
    row_dtypes: tuple[bni.NodeDataType, ...],
) -> list[int] | None:
    """Order-insensitive greedy match: for each required row dtype, claim the
    first unused operand that satisfies it. Returns the permutation of operand
    indices (in row order) on success, else None. At least one claimed operand
    must be a concrete dtype (an anchor) — an all-VectorLike match is too
    ambiguous to commit to."""
    if len(operand_dtypes) != len(row_dtypes):
        return None

    used = [False] * len(operand_dtypes)
    permutation: list[int] = []
    for row_dtype in row_dtypes:
        idx = next(
            (
                i
                for i, dt in enumerate(operand_dtypes)
                if not used[i] and _operand_matches(dt, row_dtype)
            ),
            None,
        )
        if idx is None:
            return None
        used[idx] = True
        permutation.append(idx)

    has_anchor = any(
        not isinstance(operand_dtypes[i], VectorLike) and operand_dtypes[i] is not None
        for i in permutation
    )
    if not has_anchor:
        return None

    return permutation


def _construct_operator_call(
    node: cg.FunctionCallNode,
    bl_node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
    cache: dict[int, bpy.types.Node],
) -> bpy.types.Node | bpy.types.NodeSocket:
    assert len(node.kwargs) == 0, node.kwargs
    inputs = [input_results[i] for i in range(len(node.args))]

    do_coerce_integers = (
        bni.NodeGroupType(bl_node_tree.bl_idname) == bni.NodeGroupType.SHADER
    )

    # Mixed-operand rows (operand_types set) take precedence over the
    # single-type path: e.g. `vector * scalar` -> VectorMath SCALE, RGBA
    # `+`/`-`/`*` -> Mix.
    operand_dtypes = [
        _infer_value_math_type(val, arg, do_coerce_integers)
        for val, arg in zip(inputs, node.args)
    ]
    for row in NODE_OPERATOR_TABLE:
        if row.operand_types is None:
            continue
        if OPERATORS_TO_FUNCTIONS[row.operator_type] is not node.func:
            continue
        permutation = _match_operand_permutation(operand_dtypes, row.operand_types)
        if permutation is None:
            continue
        permuted = [inputs[i] for i in permutation]
        spec: cg.Node = row.pf_func(*permuted).item()
        # The spec already records the resolved operands as its kwarg values, so
        # bind them directly rather than via _bind_positional_to_tuple_kwargs
        # (vector_scale's ("Vector", 0)/("Scale", 0) keys share sub-index 0 and
        # would collide in that binder's positional logic).
        return _construct_procnode_standard(spec, bl_node_tree, dict(spec.kwargs))

    data_type = infer_operation_type(node, inputs, do_coerce_integers)
    op_res = _find_operator_row(node.func, data_type)

    spec: cg.Node = op_res.pf_func(*inputs).item()

    # eq/ne/le/ge spec is a contextual Compare node; outside geometry trees it has
    # no FunctionNodeCompare so lower it to an equivalent Math composition. The
    # spec's inputs are already-resolved sockets, so the rewritten graph carries
    # them through construct_procnode_to_bpy unchanged. The rewrite is anchored
    # on the graph-owned node: results are cached by id(), so a garbage-collected
    # spec would let a later node alias its cache entry.
    if (lowered := _lower_compare_outside_geometry(spec, bl_node_tree)) is not None:
        node.metadata["lowered_spec"] = lowered
        return construct_procnode_to_bpy(lowered, bl_node_tree, cache)

    inputs_bound = _bind_positional_to_tuple_kwargs(spec, input_results)
    return _construct_procnode_standard(spec, bl_node_tree, inputs_bound)


def _set_node_attribute(bl_node: bpy.types.Node, k: str, v: Any):
    if isinstance(v, pt.BlenderAsset):
        v = v.item()
    if not hasattr(bl_node, k):
        available = [
            a for a in dir(bl_node) if not a.startswith("_") and not a.startswith("bl_")
        ]
        raise ValueError(
            f"{bl_node.bl_idname} has no attribute {k!r}={v!r} — likely a "
            f"shader/geometry-only option used in a {bl_node.id_data.bl_idname} "
            f"context. Available attributes: {available}"
        )
    try:
        setattr(bl_node, k, v)
    except Exception as e:
        options = (
            bl_node.bl_rna.properties[k].enum_items.keys()
            if k in bl_node.bl_rna.properties
            and hasattr(bl_node.bl_rna.properties[k], "enum_items")
            else "unknown"
        )
        raise ValueError(
            f"Could not set attribute {k!r} of {bl_node.name} to {v}, {options=}"
        ) from e


def _map_keys(d: dict, map: dict) -> dict:
    return {map.get(k, k): v for k, v in d.items() if map.get(k, k) is not None}


def _resolve_output_socket_name(
    source: cg.Node, attribute_name: str, bl_node_tree: bpy.types.NodeTree
) -> str:
    """If `source` is a contextual ProceduralNode, remap the output socket name per its output_keys_map."""
    if not isinstance(source, cg.ProceduralNode):
        return attribute_name
    ctx = ContextualNode.parse_name(source.node_type)
    if ctx is None:
        return attribute_name
    group_type = bni.NodeGroupType(bl_node_tree.bl_idname)
    output_keys_map = resolve_contextual_node(ctx, group_type).output_keys_map or {}
    return output_keys_map.get(attribute_name, attribute_name)


def _resolve_data_type(
    data_type: bni.NodeDataType | RuntimeResolveDataType | None,
    attr_key: str,
    node: cg.Node,
    bl_node: bpy.types.Node,
    node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
) -> Any:
    is_shader = node_tree.bl_idname == bni.NodeGroupType.SHADER.value
    match data_type:
        case RuntimeResolveDataType() as runtime:
            result: bni.NodeDataType = resolve_operation_data_type(
                node,
                input_results,
                runtime,
                coerce_integers=is_shader,
            )
            mapped = map_data_type_for_differing_node_interface(
                result,
                bl_node,
                attr_key,
            )
            logger.debug(
                f"Inferred runtime dtype for {node=}, got  {result=} and mapped to {mapped=}"
            )
            return mapped
        case bni.NodeDataType() as user_provided:
            return map_data_type_for_differing_node_interface(
                user_provided,
                bl_node,
                attr_key,
            )
        case str() as s:
            return map_data_type_for_differing_node_interface(
                bni.NodeDataType(s),
                bl_node,
                attr_key,
            )
        case unknown:
            raise ValueError(
                f"Got misconfigured data_type {unknown=} {type(unknown)=} for {node=}"
            )


def _construct_procnode_standard(
    node: cg.ProceduralNode,
    bl_node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
) -> bpy.types.Node:
    """
    Construct a procnode which is "standard", meaning kind=PROCEDURAL NODE (is not NOT an operator or getattr)

    Returns:
        bpy.types.Node: A blender geometry/shader/compositor node which corresponds to the given procfunc.nodes definition
    """

    assert isinstance(node, cg.ProceduralNode), node

    node_type = node.node_type
    kwargs = node.kwargs.copy()
    attrs = node.attrs.copy()

    # logger.debug(
    #    f"{_construct_procnode_standard.__name__} for {node=} with {kwargs=} {attrs=} {input_results=}"
    # )

    #  resolve cases when the `node_type` is not known precisely in advance
    #   difference happens when we are using a given operation for shader vs geometry vs compositor - the same op has a different name via the bl4.2 api
    if nt := ContextualNode.parse_name(node_type):
        group_type = bni.NodeGroupType(bl_node_tree.bl_idname)
        resolution = resolve_contextual_node(nt, group_type)
        node_type = resolution.node_type
        if keymap := resolution.input_keys_map:
            logger.debug(
                f"Applying keymap {keymap} to {input_results.keys()=} for context {node_type=} {group_type=}"
            )
            noop = resolution.input_drop_noop or {}
            for dropped in (k for k, v in keymap.items() if v is None):
                if dropped not in noop or dropped not in input_results:
                    continue
                value = input_results[dropped]
                wired = isinstance(
                    value, (bpy.types.NodeSocket, bpy.types.NodeInternal)
                )
                if wired or value != noop[dropped]:
                    raise ValueError(
                        f"{node_type} has no {dropped} socket; {dropped.lower()}="
                        f"{value!r} cannot be honored (only the no-op {noop[dropped]}). "
                        "Synthesizing a mix node would be needed to support this."
                    )
            kwargs = _map_keys(kwargs, keymap)
            input_results = _map_keys(input_results, keymap)
            attrs = _map_keys(attrs, keymap)

    bl_node = bl_node_tree.nodes.new(node_type)

    for attr_key in ["data_type", "input_type"]:  # Switch node uses input_type
        if attr_key not in attrs:
            continue
        if isinstance(attrs[attr_key], RuntimeResolveDataType) and not hasattr(
            bl_node, attr_key
        ):
            # auto-resolve default landed on a node without this attr; drop it
            attrs.pop(attr_key)
            continue
        attrs[attr_key] = _resolve_data_type(
            attrs[attr_key], attr_key, node, bl_node, bl_node_tree, input_results
        )

    # some nodes need to pop attrs and apply special handling instead of just setattr. we do it here so that they get a chance to
    # remove the attrs / inputs that are problematic before they get applied by code below
    if specialcase := NODE_SPECIAL_CASES.get(node_type):
        specialcase_kwargs = dict(
            node_tree=bl_node_tree,
            bl_node=bl_node,
            attrs=attrs,
            kwargs=kwargs,
            inputs=input_results,
        )
        specialcase(**specialcase_kwargs)

    for k, v in attrs.items():
        _set_node_attribute(bl_node, k, v)

    for input_name, input_py in kwargs.items():
        input_result = input_results[input_name]
        if input_result is None:
            # Strict-None policy: None means "leave disconnected" and is only
            # allowed for sockets with no default_value attr at all (Geometry,
            # Shader, Matrix, Virtual) - never rely on Blender's internal
            # defaults, whose values may change across versions. A disabled or
            # missing socket name is a binding bug and propagates as ValueError.
            to_socket = get_input_socket_to_connect_to(
                bl_node_tree, bl_node, input_name, None
            )
            # IMAGE default_value is a datablock pointer; None faithfully means "no image assigned"
            if (
                to_socket.is_multi_input
                or not hasattr(to_socket, "default_value")
                or to_socket.type == "IMAGE"
            ):
                continue
            raise ValueError(
                f"Node {bl_node.name!r} input {to_socket.name!r} (socket type "
                f"{to_socket.type}) received None. Explicitly pass a value; None is "
                f"only allowed for sockets with no default_value attribute "
                f"(e.g. Geometry/Shader) or with a datablock pointer one (Image)."
            )
        to_socket = get_input_socket_to_connect_to(
            bl_node_tree, bl_node, input_name, input_result
        )
        if to_socket.is_multi_input and isinstance(input_py, list):
            assert isinstance(input_result, list), (input_result, to_socket.node.name)
            connect_multisocket_input(bl_node_tree, to_socket, input_result, input_py)
        else:
            assert not isinstance(input_result, list), (
                input_result,
                to_socket.node.name,
            )
            connect_single_input(bl_node_tree, to_socket, input_result)

    return bl_node


def instantiate_nodegroup(
    node_tree: bpy.types.NodeTree,
    nodegroup: bpy.types.NodeTree,
) -> bpy.types.Node:
    nodegroup_instance_type = bni.NODEGROUPTYPE_TO_INSTANCE_NODE[node_tree.bl_idname]
    bpy_nodegroup_call = node_tree.nodes.new(nodegroup_instance_type)
    bpy_nodegroup_call.node_tree = nodegroup
    return bpy_nodegroup_call


def _construct_subgraph_call(
    node: cg.SubgraphCallNode,
    bl_node_tree: bpy.types.NodeTree,
    input_results: dict[str | int, Any],
) -> bpy.types.Node | bpy.types.NodeSocket | bpy.types.Material:
    node_group_type = bni.NodeGroupType(bl_node_tree.bl_idname)
    nodegroup = as_nodegroup(node.subgraph, node_group_type)
    bpy_nodegroup_call = instantiate_nodegroup(bl_node_tree, nodegroup)

    for input_name, input_py in node.kwargs.items():
        input_val = input_results[input_name]
        if input_val is None:
            continue
        to_socket = bpy_nodegroup_call.inputs[input_name]
        connect_single_input(
            node_tree=bl_node_tree,
            to_socket=to_socket,
            input_val=input_val,
        )

    return bpy_nodegroup_call


def _dispatch_construct_procnode_by_type(
    node: cg.Node,
    bl_node_tree: bpy.types.NodeTree,
    cache: dict[int, bpy.types.Node],
    input_results: dict[str | int, Any],
):
    if isinstance(node, cg.GetAttributeNode):
        base_node = construct_procnode_to_bpy(node.source, bl_node_tree, cache)
        socket_name = _resolve_output_socket_name(
            node.source, node.attribute_name, bl_node_tree
        )
        return get_nth_socket(base_node.outputs, socket_name, 0, base_node.type)

    match node:
        case cg.GetAttributeNode(args=(source,), attribute_name=socket_name):
            base_node = construct_procnode_to_bpy(source, bl_node_tree, cache)
            socket_name = _resolve_output_socket_name(source, socket_name, bl_node_tree)
            return get_nth_socket(base_node.outputs, socket_name, 0, base_node.type)
        case cg.ProceduralNode():
            return _construct_procnode_standard(node, bl_node_tree, input_results)
        case cg.FunctionCallNode():
            return _construct_operator_call(node, bl_node_tree, input_results, cache)
        case cg.SubgraphCallNode():
            return _construct_subgraph_call(node, bl_node_tree, input_results)
        case cg.InputPlaceholderNode():
            input_node = next(
                n for n in bl_node_tree.nodes if n.bl_idname == "NodeGroupInput"
            )
            assert input_node is not None, bl_node_tree.nodes.keys()
            return input_node.outputs[node.input_name]
        case _:
            raise ValueError(f"Got misconfigured {node=}")


def _construct_inputs(
    node: cg.Node,
    bl_node_tree: bpy.types.NodeTree,
    cache: dict[int, bpy.types.Node] | None = None,
) -> dict[int | str, bpy.types.NodeSocket | bpy.types.NodeInternal]:
    assert isinstance(node, cg.Node), node

    input_results: dict[str | int, Any] = {}
    for k, input_val in node.kwargs.items():
        input_results[k] = construct_input(input_val, bl_node_tree, cache)  # noqa: F821
    for i, input_val in enumerate(node.args):
        input_results[i] = construct_input(input_val, bl_node_tree, cache)  # noqa: F821

    # any raw Node types indicate the user declined to specify a specific socket,
    #   so we will use the primary/first socket on that node

    return input_results


def _lower_compare_outside_geometry(
    node: cg.Node,
    bl_node_tree: bpy.types.NodeTree,
) -> cg.Node | None:
    """`==` / `!=` / `<=` / `>=` lower to FunctionNodeCompare in geometry trees,
    but that node does not exist in shader/compositor/texture trees. There a Math
    node's COMPARE/GREATER_THAN/LESS_THAN operations express each one exactly, so
    rewrite the contextual Compare node to the equivalent Math composition:

        ==  ->  COMPARE(a, b, eps)
        !=  ->  1 - COMPARE(a, b, eps)
        <=  ->  1 - GREATER_THAN(a, b)
        >=  ->  1 - LESS_THAN(a, b)

    le/ge are derived exactly without eps, matching FunctionNodeCompare whose
    LESS_EQUAL/GREATER_EQUAL ignore the Epsilon socket. The eps for eq/ne comes
    from the Compare node's own Epsilon input if given, else Blender's Compare
    node default. Returns the replacement cg.Node, or None if no rewrite applies."""
    if (
        not isinstance(node, cg.ProceduralNode)
        or ContextualNode.parse_name(node.node_type) is not ContextualNode.COMPARE
        or bni.NodeGroupType(bl_node_tree.bl_idname) is bni.NodeGroupType.GEOMETRY
    ):
        return None

    operation = node.attrs.get("operation")
    if operation not in ("EQUAL", "NOT_EQUAL", "LESS_EQUAL", "GREATER_EQUAL"):
        return None

    a = node.kwargs[("A", 0)]
    b = node.kwargs[("B", 0)]

    match operation:
        case "EQUAL":
            eps = node.kwargs.get(("Epsilon", 0), pf_func.COMPARE_EPSILON_DEFAULT)
            return pf_math.compare(a, b, eps).item()
        case "NOT_EQUAL":
            eps = node.kwargs.get(("Epsilon", 0), pf_func.COMPARE_EPSILON_DEFAULT)
            return pf_math.subtract(1.0, pf_math.compare(a, b, eps)).item()
        case "LESS_EQUAL":
            return pf_math.subtract(1.0, pf_math.greater_than(a, b)).item()
        case "GREATER_EQUAL":
            return pf_math.subtract(1.0, pf_math.less_than(a, b)).item()


def construct_procnode_to_bpy(
    node: cg.Node,
    bl_node_tree: bpy.types.NodeTree,
    cache: dict[int, bpy.types.Node] | None = None,
) -> bpy.types.NodeSocket | bpy.types.NodeInternal:
    assert node is not None
    assert isinstance(bl_node_tree, bpy.types.NodeTree), bl_node_tree

    if cache is None:
        cache = {}
    elif cached := cache.get(id(node), None):
        return cached

    if (lowered := _lower_compare_outside_geometry(node, bl_node_tree)) is not None:
        # anchored on the graph-owned node: results are cached by id(), so a
        # garbage-collected spec would let a later node alias its cache entry
        node.metadata["lowered_spec"] = lowered
        result = construct_procnode_to_bpy(lowered, bl_node_tree, cache)
        cache[id(node)] = result
        return result

    if isinstance(node, cg.GetAttributeNode):
        assert len(node.args) == 1, node.args
        assert len(node.kwargs) == 0, node.kwargs
        source = node.args[0]
        if isinstance(source, cg.SubgraphCallNode):
            # an absent subgraph output leaf (None, e.g. a Material with no
            # displacement) has no output socket; resolve to it directly
            for k, v in source.subgraph.outputs.items(nocontainer_name="result"):
                if k == node.attribute_name and not isinstance(v, cg.Node):
                    return v
        base_node = construct_procnode_to_bpy(source, bl_node_tree, cache)
        assert isinstance(base_node, bpy.types.Node), base_node
        socket_name = _resolve_output_socket_name(
            source, node.attribute_name, bl_node_tree
        )
        return get_nth_socket(base_node.outputs, socket_name, 0, base_node.type)

    def _construct_leaf(input_val: cg.Node | Any | None):
        if not isinstance(input_val, cg.Node):
            return input_val
        bpy_res = construct_procnode_to_bpy(input_val, bl_node_tree, cache)
        if isinstance(bpy_res, bpy.types.NodeInternal):
            # nodes that need non-socket input (GetAttribute) wont reach here, so we can return the primary socket
            return _get_primary_output_socket(input_val, bpy_res)
        return bpy_res

    # resolve pt.Material before PyTree traversal, since Material is a registered
    # PyTree container and would be destructured into shader ProcNodes otherwise
    kwargs_for_tree = {
        k: v.item() if isinstance(v, pt.Material) else v for k, v in node.kwargs.items()
    }

    # construct any inputs inside lists/dicts e.g. for join_geometry
    input_sockets: dict = pytree.PyTree(kwargs_for_tree).map(_construct_leaf).obj()
    input_sockets.update(
        {
            i: v
            for i, v in enumerate(pytree.PyTree(node.args).map(_construct_leaf).obj())
        }
    )

    with add_exception_context_msg(
        f"While instantiating {nt.node_definition_context_message(node)}{node=}:\n"
    ):
        result = _dispatch_construct_procnode_by_type(
            node, bl_node_tree, cache, input_sockets
        )

    assert isinstance(result, (bpy.types.Node, bpy.types.NodeSocket)), result

    logger.debug(
        f"{construct_procnode_to_bpy.__name__} for {node=} produced {type(result)=}"
    )
    cache[id(node)] = result
    return result


def _graph_requires_scene_tree(graph: cg.ComputeGraph) -> bool:
    return any(
        isinstance(node, cg.ProceduralNode)
        and node.node_type in bni.SCENE_BOUND_NODE_TYPES
        for subgraph in cg.traverse_nested_graphs(graph)
        for node in cg.traverse_depth_first(subgraph)
    )


def _construct_nodegroup(
    graph: cg.ComputeGraph,
    node_tree_type: bni.NodeGroupType,
) -> bpy.types.NodeTree:
    # Scene-bound compositor nodes (e.g. Render Layers) poll False inside a
    # standalone node group, so build on the active scene's compositing tree
    # instead, replacing its contents. That tree still accepts group IO nodes
    # and an interface, so the rest of the scaffold below is unchanged.
    if _graph_requires_scene_tree(graph):
        scene = bpy.context.scene
        scene.use_nodes = True
        nodegroup = scene.node_tree
    else:
        name = (
            graph.name
            if graph.name is not None
            else bpy_nocollide_data_name(graph, bpy.data.node_groups)
        )
        nodegroup = bpy.data.node_groups.new(name, node_tree_type.value)

    for k in nodegroup.interface.items_tree.keys():
        nodegroup.interface.items_tree.remove(k)
    for k in nodegroup.nodes:
        nodegroup.nodes.remove(k)

    input_node = nodegroup.nodes.new("NodeGroupInput")
    output_node = nodegroup.nodes.new("NodeGroupOutput")

    cache = {}

    for k, v in graph.inputs.items():
        v_type = v.metadata.get("known_value_type", None)
        if v_type is None:
            raise ValueError(f"Got {v=} with no known value type")
        socket_type = bni.PYTHON_TYPE_TO_SOCKET_TYPE[v_type]
        nodegroup.interface.new_socket(
            name=k,
            in_out="INPUT",
            socket_type=socket_type.value,
        )
        cache[id(v)] = input_node.outputs[k]

    for k, v in graph.outputs.items(nocontainer_name="result"):
        # an absent output (None, e.g. a Material with no displacement) gets no
        # output socket
        if not isinstance(v, cg.Node):
            continue

        res = construct_procnode_to_bpy(v, nodegroup, cache)

        # accessor nodes can resolve to an absent output (None, e.g. a
        # Material's missing displacement read through a subgraph boundary)
        if not isinstance(res, (bpy.types.Node, bpy.types.NodeSocket)):
            continue

        if isinstance(res, bpy.types.Node):
            res = _get_primary_output_socket(v, res)
        assert isinstance(res, bpy.types.NodeSocket), res

        nodegroup.interface.new_socket(
            name=k,
            in_out="OUTPUT",
            socket_type=normalize_socket_type(res.bl_idname),
        )

        to_socket = output_node.inputs[k]
        connect_single_input(nodegroup, to_socket, res)

    return nodegroup


def as_nodegroup(
    graph: cg.ComputeGraph,
    node_tree_type: bni.NodeGroupType,
) -> bpy.types.NodeTree:
    # Scene-bound graphs (e.g. Render Layers) are built on the active scene's
    # compositing tree, replacing its contents.
    ops = graph.metadata.get("operations", [])
    use_cache = len(ops) > 0 and ops[0][0].__name__ == "node_function"

    if use_cache:
        cached = graph.metadata["bpy_cached_impls"].get(node_tree_type, None)
        if cached is not None:
            return cached

    with add_exception_context_msg(
        prefix=f"While constructing nodegroup for {graph=} {node_tree_type=}:\n",
    ):
        nodegroup = _construct_nodegroup(graph, node_tree_type)

    if use_cache:
        graph.metadata["bpy_cached_impls"][node_tree_type] = nodegroup

    return nodegroup
