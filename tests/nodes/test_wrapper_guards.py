import pytest

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc.nodes import bindings_util as bu


@pytest.fixture
def strict_vector_mode():
    prev = pf.context.globals.warn_mode_avoid_implicit_vector
    pf.context.globals.warn_mode_avoid_implicit_vector = "throw"
    yield
    pf.context.globals.warn_mode_avoid_implicit_vector = prev


def _proc_node(socket) -> cg.ProceduralNode:
    node = socket.item()
    while not isinstance(node, cg.ProceduralNode):
        node = node.args[0]
    return node


def test_noise_wired_vector_accepted(strict_vector_mode):
    res = pf.nodes.texture.noise(vector=pf.nodes.math.combine_xyz(1, 2, 3))
    assert "Vector" in _proc_node(res.fac).kwargs


def test_noise_constant_vector_wired(strict_vector_mode):
    res = pf.nodes.texture.noise(vector=(1.0, 2.0, 3.0))
    assert _proc_node(res.fac).kwargs["Vector"] == (1.0, 2.0, 3.0)


def test_noise_zero_vector_is_a_real_value(strict_vector_mode):
    res = pf.nodes.texture.noise(vector=(0.0, 0.0, 0.0))
    assert _proc_node(res.fac).kwargs["Vector"] == (0.0, 0.0, 0.0)


def test_noise_explicit_none_vector_raises_in_strict_mode(strict_vector_mode):
    with pytest.raises(ValueError, match="vector"):
        pf.nodes.texture.noise(vector=None, scale=5.0)


def test_noise_explicit_none_vector_omits_socket_in_ignore_mode():
    prev = pf.context.globals.warn_mode_avoid_implicit_vector
    pf.context.globals.warn_mode_avoid_implicit_vector = "ignore"
    try:
        res = pf.nodes.texture.noise(vector=None, scale=5.0)
        assert "Vector" not in _proc_node(res.fac).kwargs
    finally:
        pf.context.globals.warn_mode_avoid_implicit_vector = prev


def test_noise_1d(strict_vector_mode):
    res = pf.nodes.texture.noise(vector=None, noise_dimensions="1D", w=0.5)
    node = _proc_node(res.fac)
    assert node.kwargs["W"] == 0.5
    assert "Vector" not in node.kwargs

    with pytest.raises(ValueError, match="Vector"):
        pf.nodes.texture.noise(noise_dimensions="1D", w=0.5, vector=(1.0, 2.0, 3.0))

    with pytest.raises(ValueError, match="vector"):
        pf.nodes.texture.noise(vector=None, noise_dimensions="1D")


@pytest.fixture
def strict_normal_mode():
    prev = pf.context.globals.warn_mode_avoid_normal_bump
    pf.context.globals.warn_mode_avoid_normal_bump = "throw"
    yield
    pf.context.globals.warn_mode_avoid_normal_bump = prev


def test_principled_bsdf_defaults_pass_strict_mode(strict_normal_mode):
    node = pf.nodes.shader.principled_bsdf(base_color=(1, 0, 0, 1)).item()
    assert "Normal" not in node.kwargs
    assert "Coat Normal" not in node.kwargs
    assert "Tangent" not in node.kwargs


def test_principled_bsdf_explicit_normal_raises_in_strict_mode(strict_normal_mode):
    with pytest.raises(ValueError, match="normal"):
        pf.nodes.shader.principled_bsdf(normal=(0.0, 0.0, 1.0))

    with pytest.raises(ValueError, match="normal"):
        pf.nodes.shader.principled_bsdf(coat_normal=(0.0, 0.0, 1.0))


def test_principled_bsdf_normal_wired_in_warn_mode():
    prev = pf.context.globals.warn_mode_avoid_normal_bump
    pf.context.globals.warn_mode_avoid_normal_bump = "warn"
    try:
        node = pf.nodes.shader.principled_bsdf(normal=(0.0, 0.0, 1.0)).item()
        assert node.kwargs["Normal"] == (0.0, 0.0, 1.0)
    finally:
        pf.context.globals.warn_mode_avoid_normal_bump = prev


def test_voronoi_wired_vector_accepted(strict_vector_mode):
    res = pf.nodes.texture.voronoi(vector=pf.nodes.math.combine_xyz(1, 2, 3))
    assert "Vector" in _proc_node(res.distance).kwargs


def test_voronoi_zero_vector_is_a_real_value(strict_vector_mode):
    res = pf.nodes.texture.voronoi(vector=(0.0, 0.0, 0.0))
    assert _proc_node(res.distance).kwargs["Vector"] == (0.0, 0.0, 0.0)


def test_voronoi_explicit_none_vector_raises_in_strict_mode(strict_vector_mode):
    with pytest.raises(ValueError, match="vector"):
        pf.nodes.texture.voronoi(vector=None)


def test_voronoi_1d(strict_vector_mode):
    res = pf.nodes.texture.voronoi(vector=None, voronoi_dimensions="1D", w=0.5)
    node = _proc_node(res.distance)
    assert node.kwargs["W"] == 0.5
    assert "Vector" not in node.kwargs

    with pytest.raises(ValueError, match="Vector"):
        pf.nodes.texture.voronoi(vector=(1.0, 2.0, 3.0), voronoi_dimensions="1D", w=0.5)


def test_voronoi_smooth_f1_wired_vector_accepted(strict_vector_mode):
    res = pf.nodes.texture.voronoi_smooth_f1(vector=pf.nodes.math.combine_xyz(1, 2, 3))
    assert "Vector" in _proc_node(res.distance).kwargs


def test_voronoi_distance_wired_vector_accepted(strict_vector_mode):
    res = pf.nodes.texture.voronoi_distance(vector=pf.nodes.math.combine_xyz(1, 2, 3))
    assert "Vector" in _proc_node(res).kwargs


def test_context_resolution_rejects_none_mapped_keys():
    with pytest.raises(ValueError, match="drop_keys"):
        bu.NodeContextResolution(
            contextual_node=bu.ContextualNode.MIX_RGB,
            node_group_type=bu.NodeGroupType.TEXTURE,
            node_type="TextureNodeMixRGB",
            input_keys_map={"data_type": None},
        )


def test_color_ramp_hue_interpolation_requires_hue_mode():
    with pytest.raises(ValueError, match="hue_interpolation"):
        pf.nodes.color.color_ramp(mode="RGB", hue_interpolation="CW")
