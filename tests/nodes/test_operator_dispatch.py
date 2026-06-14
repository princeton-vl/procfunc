"""Tests for operator dispatch added to NODE_OPERATOR_TABLE / construct_operator:
unary minus (`-x`), mixed `vector * scalar` -> VectorMath SCALE, and RGBA
`+` `-` `*` -> Mix with the matching blend_type."""

import pytest

import procfunc as pf
from conftest import node_operations as _ops
from conftest import realize as _realize
from procfunc import compute_graph as cg
from procfunc.nodes import bpy_node_info as bni
from procfunc.nodes.bpy_node_info import NodeGroupType
from procfunc.nodes.execute import construct_operator


def _set_position(offset):
    cube = pf.nodes.geo.mesh_cube()
    return pf.nodes.geo.set_position(cube.mesh, offset=offset)


def test_neg_float_dispatches_to_math_multiply():
    def fn():
        idx = pf.nodes.geo.input_index().astype(float)
        off = pf.nodes.math.combine_xyz(x=-idx, y=0.0, z=0.0)
        return _set_position(off)

    ng = _realize(fn, NodeGroupType.GEOMETRY)
    assert _ops(ng, "ShaderNodeMath") == ["MULTIPLY"]


def test_neg_vector_dispatches_to_vector_scale():
    def fn():
        v = pf.nodes.geo.input_position()
        return _set_position(-v)

    ng = _realize(fn, NodeGroupType.GEOMETRY)
    assert _ops(ng, "ShaderNodeVectorMath") == ["SCALE"]


@pytest.mark.parametrize("reverse", [False, True])
def test_vector_times_scalar_dispatches_to_scale(reverse):
    def fn():
        v = pf.nodes.geo.input_position()
        return _set_position(2.0 * v if reverse else v * 2.0)

    ng = _realize(fn, NodeGroupType.GEOMETRY)
    assert _ops(ng, "ShaderNodeVectorMath") == ["SCALE"]
    scale = next(n for n in ng.nodes if n.bl_idname == "ShaderNodeVectorMath")
    assert scale.inputs["Vector"].is_linked
    assert scale.inputs["Scale"].default_value == 2.0


def test_vector_times_vector_keeps_multiply():
    def fn():
        v = pf.nodes.geo.input_position()
        return _set_position(v * v)

    ng = _realize(fn, NodeGroupType.GEOMETRY)
    assert _ops(ng, "ShaderNodeVectorMath") == ["MULTIPLY"]


@pytest.mark.parametrize(
    "op,blend",
    [("add", "ADD"), ("sub", "SUBTRACT"), ("mul", "MULTIPLY")],
)
def test_color_arithmetic_dispatches_to_mix(op, blend):
    def fn():
        a = pf.nodes.shader.coord().generated.astype(pf.Color)
        b = pf.nodes.shader.coord().object.astype(pf.Color)
        out = {"add": a + b, "sub": a - b, "mul": a * b}[op]
        return pf.nodes.shader.emission(color=out, strength=1.0)

    ng = _realize(fn, NodeGroupType.SHADER)
    mix = next(n for n in ng.nodes if n.bl_idname == "ShaderNodeMix")
    assert mix.blend_type == blend
    assert mix.data_type == "RGBA"
    assert mix.inputs["Factor"].default_value == 1.0


def test_color_times_scalar_is_rejected():
    # color * scalar is ambiguous; it must not silently mix and instead falls
    # through to the standard mismatched-operand error.
    def fn():
        a = pf.nodes.shader.coord().generated.astype(pf.Color)
        return pf.nodes.shader.emission(color=a * 2.0, strength=1.0)

    with pytest.raises(ValueError, match="non-matching input types"):
        _realize(fn, NodeGroupType.SHADER)


def test_float_plus_tuple_raises_disambiguation_error():
    # mixing a FLOAT operand with a raw tuple must raise the astype hint, not
    # silently infer FLOAT and fail far downstream.
    def fn():
        idx = pf.nodes.geo.input_index().astype(float)
        return _set_position(idx + (1.0, 2.0, 3.0))

    with pytest.raises(ValueError, match="astype"):
        _realize(fn, NodeGroupType.GEOMETRY)


def test_vector_times_length4_tuple_raises():
    # a length-4 tuple alongside FLOAT_VECTOR operands must raise, not silently
    # infer FLOAT_VECTOR and truncate.
    def fn():
        v = pf.nodes.geo.input_position()
        return _set_position(v * (1.0, 1.0, 1.0, 1.0))

    with pytest.raises(ValueError, match="length-4"):
        _realize(fn, NodeGroupType.GEOMETRY)


def test_permuted_operand_match_requires_commutative_operator():
    # the (FLOAT_VECTOR, FLOAT) row matched in swapped order is accepted for
    # commutative MUL but raises for a non-commutative operator like DIV.
    operands = [bni.NodeDataType.FLOAT, bni.NodeDataType.FLOAT_VECTOR]
    row = (bni.NodeDataType.FLOAT_VECTOR, bni.NodeDataType.FLOAT)

    permutation = construct_operator._match_operand_permutation(
        operands, row, cg.OperatorType.MUL
    )
    assert permutation == [1, 0]

    with pytest.raises(ValueError, match="not commutative"):
        construct_operator._match_operand_permutation(
            operands, row, cg.OperatorType.DIV
        )
