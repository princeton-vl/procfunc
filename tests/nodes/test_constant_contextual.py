"""Tests for the context-dispatching `math.constant` (ContextualNode VALUE/RGB)
that replaced the hardcoded ShaderNodeValue/ShaderNodeRGB and the retired
compositor.value / compositor.rgb bindings."""

import pytest

import procfunc as pf
from conftest import realize as _realize
from procfunc.nodes.util.bpy_node_info import NodeGroupType


def _bl_idnames(ng) -> set[str]:
    return {n.bl_idname for n in ng.nodes}


@pytest.mark.parametrize(
    "group, expected",
    [
        (NodeGroupType.SHADER, "ShaderNodeValue"),
        (NodeGroupType.GEOMETRY, "ShaderNodeValue"),
        (NodeGroupType.COMPOSITOR, "CompositorNodeValue"),
    ],
)
def test_float_constant_is_contextual(group, expected):
    ng = _realize(lambda: pf.nodes.math.constant(0.5), group)
    assert expected in _bl_idnames(ng)


@pytest.mark.parametrize(
    "group, expected",
    [
        (NodeGroupType.SHADER, "ShaderNodeRGB"),
        (NodeGroupType.GEOMETRY, "FunctionNodeInputColor"),
        (NodeGroupType.COMPOSITOR, "CompositorNodeRGB"),
    ],
)
def test_color_constant_is_contextual(group, expected):
    ng = _realize(
        lambda: pf.nodes.math.constant(pf.types.Color((0.1, 0.2, 0.3))), group
    )
    assert expected in _bl_idnames(ng)


@pytest.mark.parametrize(
    "group, expected",
    [
        # outside geometry, int degrades to the float Value node
        (NodeGroupType.SHADER, "ShaderNodeValue"),
        (NodeGroupType.GEOMETRY, "FunctionNodeInputInt"),
        (NodeGroupType.COMPOSITOR, "CompositorNodeValue"),
    ],
)
def test_int_constant_is_contextual(group, expected):
    ng = _realize(lambda: pf.nodes.math.constant(5), group)
    assert expected in _bl_idnames(ng)


@pytest.mark.parametrize(
    "group, expected",
    [
        # outside geometry, vector constants lower to CombineXYZ socket defaults
        (NodeGroupType.SHADER, "ShaderNodeCombineXYZ"),
        (NodeGroupType.GEOMETRY, "FunctionNodeInputVector"),
        (NodeGroupType.COMPOSITOR, "CompositorNodeCombineXYZ"),
    ],
)
def test_vector_constant_is_contextual(group, expected):
    ng = _realize(lambda: pf.nodes.math.constant((1.0, 2.0, 3.0)), group)
    node = next(n for n in ng.nodes if n.bl_idname == expected)
    if expected == "FunctionNodeInputVector":
        assert tuple(node.vector) == (1.0, 2.0, 3.0)
    else:
        assert tuple(s.default_value for s in node.inputs) == (1.0, 2.0, 3.0)


def test_bool_constant_geometry():
    # bool must dispatch before int (bool is a subclass of int)
    ng = _realize(lambda: pf.nodes.math.constant(True), NodeGroupType.GEOMETRY)
    node = next(n for n in ng.nodes if n.bl_idname == "FunctionNodeInputBool")
    assert node.boolean is True


def test_rotation_constant_geometry():
    euler = pf.types.Euler((0.1, 0.2, 0.3))
    ng = _realize(lambda: pf.nodes.math.constant(euler), NodeGroupType.GEOMETRY)
    assert "FunctionNodeInputRotation" in _bl_idnames(ng)


def test_string_constant_geometry():
    ng = _realize(lambda: pf.nodes.math.constant("hello"), NodeGroupType.GEOMETRY)
    node = next(n for n in ng.nodes if n.bl_idname == "FunctionNodeInputString")
    assert node.string == "hello"


def test_texture_constant_errors_clearly():
    # Texture trees have no constant node; the contextual lookup must fail.
    with pytest.raises(ValueError):
        _realize(lambda: pf.nodes.math.constant(0.5), NodeGroupType.TEXTURE)


def test_bool_constant_errors_outside_geometry():
    # No bool constant node exists in shader trees; intentionally unmapped.
    with pytest.raises(ValueError):
        _realize(lambda: pf.nodes.math.constant(True), NodeGroupType.SHADER)
