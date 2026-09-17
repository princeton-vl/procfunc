import operator

import bpy
import numpy as np
import pytest

import procfunc as pf
from procfunc.codegen import codegen
from procfunc.codegen.identifiers import dedup_names_with_suffix
from procfunc.nodes import types as nt


def _codegen_and_call(func, **inputs):
    graph = pf.trace(func)
    src = codegen.to_python(graph, toplevel_as_maincall=False)
    namespace = {}
    exec(src, namespace)  # noqa: S102
    return src, namespace[func.__name__](**inputs)


def test_folded_operand_ending_in_call_keeps_parens():
    def sub_of_add_astype(a, b, c):
        return c - (a + b.astype(float))

    src, result = _codegen_and_call(
        sub_of_add_astype, a=np.float64(1.0), b=np.float64(2.0), c=np.float64(10.0)
    )
    assert "c - (a + b.astype(float))" in src, src
    assert result == 7.0


def test_negative_constant_pow_base_keeps_parens():
    def pow_negative_base(x):
        return (-2.0) ** x

    src, result = _codegen_and_call(pow_negative_base, x=2.0)
    assert "(-2.0) ** x" in src, src
    assert result == 4.0


def test_native_equality_codegen_executes_as_exact_operator():
    def is_zero(x):
        return x == 0

    src, result = _codegen_and_call(is_zero, x=np.float64(0.0))
    assert "_operator" not in src, src
    assert "x == 0" in src, src
    assert result is np.True_


@pytest.mark.parametrize(
    "operation,value,expected",
    [
        (operator.neg, 3, -3),
        (operator.pos, -3, -3),
        (operator.abs, -3, 3),
        (operator.invert, 3, -4),
    ],
)
def test_native_unary_operator_codegen_executes_without_private_module(
    operation, value, expected
):
    def apply_op(x):
        return operation(x)

    src, result = _codegen_and_call(apply_op, x=value)
    assert "_operator" not in src, src
    assert result == expected


def test_native_floor_division_codegen_executes_without_private_module():
    def halve(x):
        return x // 2

    src, result = _codegen_and_call(halve, x=5)
    assert "_operator" not in src, src
    assert result == 2


@pytest.mark.parametrize(
    "value_type",
    [
        pf.MeshObject | pf.CurveObject | nt.Instances | pf.VolumeObject,
        nt.ProcNode[float],
        nt.ProcNode[float] | float | None,
    ],
)
def test_type_value_survives_codegen(value_type):
    def type_value():
        return value_type

    _, result = _codegen_and_call(type_value)
    assert result == value_type


def _lamp_with_blackbody_emission():
    light = pf.ops.primitives.light.point_lamp(100.0)
    color = pf.nodes.color.blackbody(3000.0)
    emit = pf.nodes.shader.emission(color=color, strength=5.0)
    pf.nodes.execute.execute.to_light(light, surface=emit)
    return light


def _tree_has_node(tree, bl_idname):
    for n in tree.nodes:
        if n.bl_idname == bl_idname:
            return True
        if n.bl_idname == "ShaderNodeGroup" and n.node_tree is not None:
            if _tree_has_node(n.node_tree, bl_idname):
                return True
    return False


def test_to_light_shader_survives_codegen():
    graph = pf.trace(_lamp_with_blackbody_emission)
    code = codegen.to_python(graph, toplevel_as_maincall=False)
    assert "to_light" in code, code

    bpy.ops.wm.read_factory_settings(use_empty=True)
    namespace = {}
    exec(code, namespace)  # noqa: S102
    namespace["_lamp_with_blackbody_emission"]()

    lit = [
        light
        for light in bpy.data.lights
        if light.use_nodes
        and light.node_tree is not None
        and _tree_has_node(light.node_tree, "ShaderNodeBlackbody")
    ]
    assert lit, "re-executed light lost its Blackbody emission shader"


def test_dedup_suffix_collides_with_later_base_name():
    names = {
        0: "a_1",  # strips to 'a'
        1: "a_2",  # strips to 'a'
        2: "a_0_3",  # strips to 'a_0'
    }
    result = dedup_names_with_suffix(
        names,
        separator="_",
        order=[0, 1, 2],
        first_use_suffix=True,
    )
    print(f"{result=}")
    values = list(result.values())
    assert len(values) == len(set(values)), f"Duplicate names in {values}"
