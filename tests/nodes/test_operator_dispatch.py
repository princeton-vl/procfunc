"""Tests for operator dispatch added to NODE_OPERATOR_TABLE / construct_nodes:
unary minus (`-x`), mixed `vector * scalar` -> VectorMath SCALE, and RGBA
`+` `-` `*` -> Mix with the matching blend_type."""

import pytest

import procfunc as pf
from conftest import node_operations as _ops
from conftest import realize as _realize
from procfunc.nodes.bpy_node_info import NodeGroupType


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
