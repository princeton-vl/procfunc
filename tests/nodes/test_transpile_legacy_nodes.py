"""Reverse-transpile fidelity for legacy nodes with implied no-op semantics.

TextureNodeMixRGB / ShaderNodeMixRGB carry result clamping as a `use_clamp`
property rather than a socket; transpile must emit it as `clamp_result`.
CompositorNodeCurveVec has no Fac socket; transpile must rely on the
`fac=1.0` wrapper default rather than emitting bogus kwargs, mirroring the
forward no-op-input handling in bindings_util.
"""

import ast
import uuid

import bpy
import numpy as np
import pytest

import procfunc as pf
from procfunc.codegen import to_python
from procfunc.nodes.execute.construct_nodes import as_nodegroup
from procfunc.nodes.util.bpy_node_info import NodeGroupType
from procfunc.transpiler import parse_node_tree
from procfunc.transpiler.bpy_to_computegraph import ParseMemo


def _make_tree(group_type: str):
    suffix = uuid.uuid4().hex[:8]
    if group_type == "CompositorNodeTree":
        scene = bpy.data.scenes.new(f"_pf_legacy_test_{suffix}")
        scene.use_nodes = True
        scene.node_tree.nodes.clear()
        return scene.node_tree
    return bpy.data.node_groups.new(f"_pf_legacy_test_{suffix}", group_type)


def _wire_output(tree, node, socket_type: str):
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket("Result", in_out="OUTPUT", socket_type=socket_type)
    tree.links.new(node.outputs[0], out.inputs[0])


def _transpile(tree) -> str:
    graph, _ = parse_node_tree(tree, ParseMemo())
    src = to_python(graph, toplevel_as_maincall=False)
    ast.parse(src)
    return src


def _realize(src: str, group_type: NodeGroupType) -> bpy.types.NodeTree:
    ns: dict = {}
    exec(src, ns)  # noqa: S102
    fns = [v for v in ns.values() if callable(v) and hasattr(v, "__wrapped__")]
    assert len(fns) == 1, f"expected one generated function, got {len(fns)}"
    subgraph = pf.nodes.function_to_compute_graph(fns[0])
    return as_nodegroup(subgraph, group_type)


def _single_node(tree: bpy.types.NodeTree, bl_idname: str) -> bpy.types.Node:
    nodes = [n for n in tree.nodes if n.bl_idname == bl_idname]
    assert len(nodes) == 1, (
        f"expected one {bl_idname}, got {[n.bl_idname for n in tree.nodes]}"
    )
    return nodes[0]


@pytest.mark.parametrize(
    ("group_type", "bl_idname"),
    [
        ("TextureNodeTree", "TextureNodeMixRGB"),
        ("ShaderNodeTree", "ShaderNodeMixRGB"),
    ],
)
def test_legacy_mix_rgb_use_clamp_emits_clamp_result(group_type, bl_idname):
    tree = _make_tree(group_type)
    node = tree.nodes.new(bl_idname)
    node.use_clamp = True
    _wire_output(tree, node, "NodeSocketColor")

    src = _transpile(tree)
    assert "clamp_result=True" in src
    assert "use_clamp" not in src


def test_texture_math_use_clamp_emits_clamp():
    tree = _make_tree("TextureNodeTree")
    node = tree.nodes.new("TextureNodeMath")
    node.operation = "ADD"
    node.use_clamp = True
    _wire_output(tree, node, "NodeSocketFloat")

    src = _transpile(tree)
    assert "clamp(" in src
    assert "use_clamp" not in src


def test_texture_mix_rgb_use_clamp_round_trips():
    tree = _make_tree("TextureNodeTree")
    node = tree.nodes.new("TextureNodeMixRGB")
    node.use_clamp = True
    node.blend_type = "MULTIPLY"
    _wire_output(tree, node, "NodeSocketColor")

    realized = _realize(_transpile(tree), NodeGroupType.TEXTURE)
    rebuilt = _single_node(realized, "TextureNodeMixRGB")
    assert rebuilt.use_clamp is True
    assert rebuilt.blend_type == "MULTIPLY"


def test_texture_mix_rgb_default_omits_implied_noop_kwargs():
    tree = _make_tree("TextureNodeTree")
    node = tree.nodes.new("TextureNodeMixRGB")
    _wire_output(tree, node, "NodeSocketColor")

    src = _transpile(tree)
    # clamp_factor=True / data_type=RGBA are inherent to the legacy node and
    # match the mix_rgb defaults; default use_clamp=False matches clamp_result.
    for implied in ("use_clamp", "clamp_result", "clamp_factor", "data_type"):
        assert implied not in src

    realized = _realize(src, NodeGroupType.TEXTURE)
    assert _single_node(realized, "TextureNodeMixRGB").use_clamp is False


def test_compositor_mix_rgb_use_clamp_round_trips():
    tree = _make_tree("CompositorNodeTree")
    node = tree.nodes.new("CompositorNodeMixRGB")
    node.use_clamp = True
    _wire_output(tree, node, "NodeSocketColor")

    src = _transpile(tree)
    assert "clamp_result=True" in src
    assert "use_clamp" not in src

    realized = _realize(src, NodeGroupType.COMPOSITOR)
    rebuilt = _single_node(realized, "CompositorNodeMixRGB")
    assert rebuilt.use_clamp is True


def test_compositor_curve_vec_round_trips_without_fac():
    tree = _make_tree("CompositorNodeTree")
    node = tree.nodes.new("CompositorNodeCurveVec")
    points = node.mapping.curves[0].points
    points[0].location = (0.0, 0.25)
    points[1].location = (1.0, 0.75)
    node.mapping.update()
    _wire_output(tree, node, "NodeSocketVector")

    src = _transpile(tree)
    assert "vector_curve" in src
    assert "curves=" in src
    # the compositor node has no Fac socket; fidelity means relying on the
    # wrapper's fac=1.0 no-op default, not emitting kwargs the node lacks
    assert "fac" not in src
    assert "mapping" not in src

    realized = _realize(src, NodeGroupType.COMPOSITOR)
    rebuilt = _single_node(realized, "CompositorNodeCurveVec")
    rebuilt_x = [tuple(p.location) for p in rebuilt.mapping.curves[0].points]
    np.testing.assert_allclose(rebuilt_x, [(0.0, 0.25), (1.0, 0.75)], atol=1e-4)
