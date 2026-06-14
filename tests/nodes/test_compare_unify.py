"""Tests for the unified, context-dispatching compare API and the
`<=` / `>=` / `==` / `!=` operator dispatch added to NODE_OPERATOR_TABLE."""

import pytest

import procfunc as pf
from conftest import node_operations as _ops
from conftest import realize as _realize
from procfunc.nodes.bpy_node_info import NodeGroupType


def _set_position_from_scalar(scalar):
    offset = pf.nodes.math.combine_xyz(x=scalar, y=0.0, z=0.0)
    cube = pf.nodes.geo.mesh_cube()
    return pf.nodes.geo.set_position(cube.mesh, offset=offset)


def test_comparison_operators_dispatch_to_compare_in_geometry():
    def fn():
        idx = pf.nodes.geo.input_index().astype(float)
        out = (
            (idx <= 5.0).astype(float)
            + (idx >= 2.0).astype(float)
            + (idx == 3.0).astype(float)
            + (idx != 4.0).astype(float)
        )
        return _set_position_from_scalar(out)

    ng = _realize(fn, NodeGroupType.GEOMETRY)
    assert _ops(ng, "FunctionNodeCompare") == [
        "EQUAL",
        "GREATER_EQUAL",
        "LESS_EQUAL",
        "NOT_EQUAL",
    ]


def test_less_greater_dispatch_to_math_in_geometry():
    # `<` / `>` keep their ShaderNodeMath implementation (contextual MATH path).
    def fn():
        idx = pf.nodes.geo.input_index().astype(float)
        out = (idx < 7.0).astype(float) + (idx > 1.0).astype(float)
        return _set_position_from_scalar(out)

    ng = _realize(fn, NodeGroupType.GEOMETRY)
    math_ops = set(_ops(ng, "ShaderNodeMath"))
    assert {"LESS_THAN", "GREATER_THAN"} <= math_ops
    assert not any(n.bl_idname == "FunctionNodeCompare" for n in ng.nodes)


def test_func_less_than_is_contextual_in_shader():
    # The unified func.less_than dispatches to ShaderNodeMath outside geometry.
    def fn():
        coord = pf.nodes.shader.coord()
        sep = pf.nodes.math.separate_xyz(coord.generated)
        lt = pf.nodes.func.less_than(sep.x, 0.5)
        return pf.nodes.shader.emission(color=(1, 1, 1, 1), strength=lt)

    ng = _realize(fn, NodeGroupType.SHADER)
    assert "LESS_THAN" in _ops(ng, "ShaderNodeMath")
    assert not any(n.bl_idname == "FunctionNodeCompare" for n in ng.nodes)


# eq/ne/le/ge have no FunctionNodeCompare outside geometry, so they lower to a
# Math composition: == -> COMPARE(eps), != -> 1 - COMPARE(eps),
# <= -> 1 - GREATER_THAN, >= -> 1 - LESS_THAN.
_COMPARE_MATH_OPS = {
    "EQUAL": (pf.nodes.func.equal, {"COMPARE"}),
    "NOT_EQUAL": (pf.nodes.func.not_equal, {"COMPARE", "SUBTRACT"}),
    "LESS_EQUAL": (pf.nodes.func.less_equal, {"GREATER_THAN", "SUBTRACT"}),
    "GREATER_EQUAL": (pf.nodes.func.greater_equal, {"LESS_THAN", "SUBTRACT"}),
}


@pytest.mark.parametrize("op", list(_COMPARE_MATH_OPS))
def test_equality_and_le_ge_lower_to_math_in_shader(op):
    operation, expected_ops = _COMPARE_MATH_OPS[op]

    def fn():
        coord = pf.nodes.shader.coord()
        sep = pf.nodes.math.separate_xyz(coord.generated)
        cmp = operation(sep.x, 0.5)
        return pf.nodes.shader.emission(color=(1, 1, 1, 1), strength=cmp)

    ng = _realize(fn, NodeGroupType.SHADER)
    assert expected_ops <= set(_ops(ng, "ShaderNodeMath"))
    assert not any(n.bl_idname == "FunctionNodeCompare" for n in ng.nodes)


def test_compare_epsilon_kwarg_lowers_to_math():
    def fn():
        coord = pf.nodes.shader.coord()
        sep = pf.nodes.math.separate_xyz(coord.generated)
        return pf.nodes.shader.emission(
            color=(1, 1, 1, 1), strength=pf.nodes.func.equal(sep.x, 0.5, epsilon=0.25)
        )

    ng = _realize(fn, NodeGroupType.SHADER)
    compare = next(
        n
        for n in ng.nodes
        if n.bl_idname == "ShaderNodeMath" and n.operation == "COMPARE"
    )
    assert compare.inputs[2].default_value == pytest.approx(0.25)


def test_less_than_on_tuples_resolves_to_vector_compare():
    # ambiguous 3-tuples resolve to FLOAT_VECTOR (not RGBA, whose Compare only
    # supports EQUAL/NOT_EQUAL/BRIGHTER/DARKER and would fail at execute).
    def fn():
        lt = pf.nodes.func.less_than((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)).astype(float)
        return _set_position_from_scalar(lt)

    ng = _realize(fn, NodeGroupType.GEOMETRY)
    compare = next(n for n in ng.nodes if n.bl_idname == "FunctionNodeCompare")
    assert compare.data_type == "VECTOR"
    assert compare.operation == "LESS_THAN"


def test_equal_on_tuples_resolves_to_vector_not_rgba():
    def fn():
        eq = pf.nodes.func.equal((1.0, 2.0, 3.0), (1.0, 2.0, 3.0)).astype(float)
        return _set_position_from_scalar(eq)

    ng = _realize(fn, NodeGroupType.GEOMETRY)
    compare = next(n for n in ng.nodes if n.bl_idname == "FunctionNodeCompare")
    assert compare.data_type == "VECTOR"


def test_vector_compare_raises_outside_geometry():
    # the Math-node lowering is scalar-only; vector operands must raise rather
    # than silently degrade to a scalar Math COMPARE via implicit conversion.
    def fn():
        eq = pf.nodes.func.equal((1.0, 2.0, 3.0), (4.0, 5.0, 6.0))
        return pf.nodes.shader.emission(color=(1, 1, 1, 1), strength=eq)

    with pytest.raises(ValueError, match="scalar"):
        _realize(fn, NodeGroupType.SHADER)


def test_explicit_vector_data_type_compare_raises_outside_geometry():
    def fn():
        coord = pf.nodes.shader.coord()
        sep = pf.nodes.math.separate_xyz(coord.generated)
        eq = pf.nodes.func._compare(
            sep.x, 0.5, data_type=pf.nodes.NodeDataType.FLOAT_VECTOR
        )
        return pf.nodes.shader.emission(color=(1, 1, 1, 1), strength=eq)

    with pytest.raises(ValueError, match="FLOAT_VECTOR"):
        _realize(fn, NodeGroupType.SHADER)


def test_comparison_operators_lower_to_math_outside_geometry():
    # the inline `<=`/`>=`/`==`/`!=` operator path (not just the func.* bindings).
    def fn():
        coord = pf.nodes.shader.coord()
        sep = pf.nodes.math.separate_xyz(coord.generated)
        out = (
            (sep.x <= 0.5).astype(float)
            + (sep.y >= 0.2).astype(float)
            + (sep.z == 0.1).astype(float)
        )
        return pf.nodes.shader.emission(color=(1, 1, 1, 1), strength=out)

    ng = _realize(fn, NodeGroupType.SHADER)
    assert not any(n.bl_idname == "FunctionNodeCompare" for n in ng.nodes)
    assert "COMPARE" in _ops(ng, "ShaderNodeMath")
