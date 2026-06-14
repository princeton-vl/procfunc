import numpy as np
import pytest

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc import transforms as tr
from procfunc import types as t
from procfunc.util import pytree


def _toy_shader_graph(
    name: str = "material_toy", scale: float | None = None
) -> cg.ComputeGraph:
    vec = cg.FunctionCallNode(pf.nodes.shader.coord, (), {})
    vec_attr = cg.GetAttributeNode(vec, "generated")
    kwargs = {"vector": vec_attr}
    if scale is not None:
        kwargs["scale"] = scale
    noise = cg.FunctionCallNode(pf.nodes.texture.noise, (), kwargs)
    return cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"surface": noise}),
        name=name,
        metadata={},
    )


def _toy_rng_graph() -> cg.ComputeGraph:
    def toy_generator(rng):
        size = pf.random.uniform(rng, 0.1, 1.0)
        return pf.ops.primitives.mesh_cube(size=size)

    return pf.trace(
        toy_generator,
        rng=np.random.default_rng(0),
        trace_level=pf.tracer.TraceLevel.RANDOM_PARAMS,
    )


def _toy_rng_method_graph() -> cg.ComputeGraph:
    def toy_generator(rng):
        size = rng.uniform(0.1, 1.0)
        return pf.ops.primitives.mesh_cube(size=size)

    return pf.trace(
        toy_generator,
        rng=np.random.default_rng(0),
        trace_level=pf.tracer.TraceLevel.RANDOM_PARAMS,
    )


def test_extract_shader_vectors_as_inputs():
    graph = _toy_shader_graph()
    res = tr.extract_shader_vectors_as_inputs(graph)

    inputs = res.inputs.obj()
    assert "vector" in inputs
    inp = inputs["vector"]
    assert isinstance(inp, cg.InputPlaceholderNode)
    assert inp.input_name == "vector"

    noise = res.outputs.dict()["surface"]
    assert noise.kwargs["vector"] is inp


def test_extract_shader_vectors_noop_without_vectors():
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"result": cg.ConstantNode(value=1.0)}),
        name="no_vectors",
        metadata={},
    )
    res = tr.extract_shader_vectors_as_inputs(graph)
    assert "vector" not in res.inputs.obj()


def test_remove_v1_name_from_graph():
    graph = _toy_shader_graph(name="nodegroup_foo")
    assert tr.remove_v1_name_from_graph(None, graph).name == "foo"
    graph = _toy_shader_graph(name="shader_bar")
    assert tr.remove_v1_name_from_graph(None, graph).name == "bar"


def test_coerce_shaders_to_materialresult():
    graph = _toy_shader_graph()
    res = tr.coerce_shaders_to_materialresult(None, graph)
    assert res.outputs.toplevel_type() is t.Material


def test_eliminate_duplicate_subgraphs():
    def make_subgraph(name):
        return cg.ComputeGraph(
            inputs=pytree.PyTree({}),
            outputs=pytree.PyTree({"result": cg.ConstantNode(value=1.0)}),
            name=name,
            metadata={},
        )

    call_a = cg.SubgraphCallNode(subgraph=make_subgraph("dup_a"), args=(), kwargs={})
    call_b = cg.SubgraphCallNode(
        subgraph=make_subgraph("dup_b_longer"), args=(), kwargs={}
    )
    top = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"a": call_a, "b": call_b}),
        name="top",
        metadata={},
    )
    tr.eliminate_duplicate_subgraphs([top])
    assert call_a.subgraph is call_b.subgraph


def test_eliminate_duplicate_result_types():
    graphs = [_toy_shader_graph()]
    assert tr.eliminate_duplicate_result_types(graphs) is graphs


def test_fill_graph_defaults_with_call_node():
    inp = cg.InputPlaceholderNode(name="x", default_value=None)
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({"x": inp}),
        outputs=pytree.PyTree({"result": inp}),
        name="fillme",
        metadata={},
    )
    call = cg.SubgraphCallNode(subgraph=graph, args=(), kwargs={"x": 2.0})
    tr.fill_graph_defaults_with_call_node(call, graph)
    assert inp.kwargs["default_value"] == 2.0


def test_replace_ids():
    const = cg.ConstantNode(value=1.0)
    parent = cg.FunctionCallNode(pf.nodes.math.add, (), {"a": const, "b": 2.0})
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"result": parent}),
        name="replace",
        metadata={},
    )
    tr.replace_ids(graph, {id(const)}, 5.0)
    assert parent.kwargs["a"] == 5.0


def test_colors_to_hsv_definition():
    node = cg.FunctionCallNode(
        pf.nodes.math.add, (), {"a": pf.Color((1.0, 0.0, 0.0)), "b": 2.0}
    )
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"result": node}),
        name="colors",
        metadata={},
    )
    res = tr.colors_to_hsv_definition(graph)
    converted = res.outputs.dict()["result"].kwargs["a"]
    assert isinstance(converted, cg.FunctionCallNode)
    assert converted.func is pf.color.hsv_to_rgba


def test_colors_to_hsv_definition_positional():
    node = cg.FunctionCallNode(pf.nodes.math.add, (pf.Color((1.0, 0.0, 0.0)), 2.0), {})
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"result": node}),
        name="colors",
        metadata={},
    )
    res = tr.colors_to_hsv_definition(graph)
    converted = res.outputs.dict()["result"].args[0]
    assert isinstance(converted, cg.FunctionCallNode)
    assert converted.func is pf.color.hsv_to_rgba
    assert res.outputs.dict()["result"].args[1] == 2.0


def test_distribution_to_mode():
    graph = _toy_rng_method_graph()
    res = tr.distribution_to_mode(graph)

    assert res.name == graph.name + "_mode"
    (cube,) = res.outputs.values()
    assert cube.kwargs["size"] == pytest.approx(0.55)

    (orig_cube,) = graph.outputs.values()
    assert isinstance(orig_cube.kwargs["size"], cg.MethodCallNode)


def test_distribution_to_mode_kwargs_form():
    """rng.uniform(low=..., high=...) traced with keyword args must resolve
    the same as positional args."""

    def toy_generator(rng):
        size = rng.uniform(low=0.1, high=1.0)
        return pf.ops.primitives.mesh_cube(size=size)

    graph = pf.trace(
        toy_generator,
        rng=np.random.default_rng(0),
        trace_level=pf.tracer.TraceLevel.RANDOM_PARAMS,
    )
    res = tr.distribution_to_mode(graph)
    (cube,) = res.outputs.values()
    assert cube.kwargs["size"] == pytest.approx(0.55)


def test_distribution_to_mode_normal_kwargs_form():
    def toy_generator(rng):
        size = rng.normal(loc=2.0, scale=0.5)
        return pf.ops.primitives.mesh_cube(size=size)

    graph = pf.trace(
        toy_generator,
        rng=np.random.default_rng(0),
        trace_level=pf.tracer.TraceLevel.RANDOM_PARAMS,
    )
    res = tr.distribution_to_mode(graph)
    (cube,) = res.outputs.values()
    assert cube.kwargs["size"] == pytest.approx(2.0)


def test_outlier_distribution_kwargs_form():
    def toy_generator(rng):
        size = rng.uniform(low=0.1, high=1.0)
        return pf.ops.primitives.mesh_cube(size=size)

    graph = pf.trace(
        toy_generator,
        rng=np.random.default_rng(0),
        trace_level=pf.tracer.TraceLevel.RANDOM_PARAMS,
    )
    res = tr.outlier_distribution(graph)
    (cube,) = res.outputs.values()
    size = cube.kwargs["size"]
    assert isinstance(size, cg.FunctionCallNode)
    assert size.func is pf.random.uniform_tails
    assert size.kwargs["low"] == pytest.approx(0.1)
    assert size.kwargs["high"] == pytest.approx(1.0)


def test_outlier_distribution():
    graph = _toy_rng_method_graph()
    res = tr.outlier_distribution(graph, pct=0.1)

    assert res.name == graph.name + "_outlier"
    (cube,) = res.outputs.values()
    size = cube.kwargs["size"]
    assert isinstance(size, cg.FunctionCallNode)
    assert size.func is pf.random.uniform_tails
    assert size.kwargs["low"] == 0.1
    assert size.kwargs["high"] == 1.0
    assert size.kwargs["tail_pct"] == 0.1


def test_extract_parameter_distributions():
    assert tr.extract_parameter_distributions(_toy_shader_graph()) == []
    distribs = tr.extract_parameter_distributions(_toy_rng_graph())
    assert len(distribs) == 1
    assert distribs[0].func is pf.random.uniform


def test_extract_parameter_distributions_rng_method():
    distribs = tr.extract_parameter_distributions(_toy_rng_method_graph())
    assert len(distribs) == 1
    assert isinstance(distribs[0], cg.MethodCallNode)
    assert distribs[0].method_name == "uniform"


def test_extract_materials():
    graph = _toy_shader_graph()
    assert tr.extract_materials_from_graph(graph) == {}
    graphs = [graph]
    assert tr.extract_materials_from_graphs(graphs) is graphs


def test_map_graph_list():
    graphs = [_toy_shader_graph()]
    seen = []
    res = tr.map_graph_list(lambda g: seen.append(g) or g)(graphs)
    assert res == graphs
    assert seen == graphs


def test_map_subgraphs():
    sub = _toy_shader_graph(name="sub")
    call = cg.SubgraphCallNode(subgraph=sub, args=(), kwargs={})
    top = cg.ComputeGraph(
        inputs=pytree.PyTree({}),
        outputs=pytree.PyTree({"result": call}),
        name="top",
        metadata={},
    )
    seen = []
    tr.map_subgraphs(lambda _node, g: seen.append(g) or g)([top])
    assert sub in seen


def test_infer_nodegroup_distributions():
    res = tr.infer_nodegroup_distributions([_toy_shader_graph()])
    assert res == []


def _toy_subgraph_calls(a_values, dynamic_b: bool):
    sub_inputs = {
        "a": cg.InputPlaceholderNode(name="a", default_value=None, metadata={}),
        "b": cg.InputPlaceholderNode(name="b", default_value=None, metadata={}),
    }
    sub = cg.ComputeGraph(
        inputs=pytree.PyTree(sub_inputs),
        outputs=pytree.PyTree({"out": sub_inputs["a"]}),
        name="toy_sub",
        metadata={},
    )
    tops = []
    for i, a in enumerate(a_values):
        b = cg.FunctionCallNode(pf.nodes.shader.coord, (), {}) if dynamic_b else 3.0
        call = cg.SubgraphCallNode(subgraph=sub, args=(), kwargs={"a": a, "b": b})
        tops.append(
            cg.ComputeGraph(
                inputs=pytree.PyTree({}),
                outputs=pytree.PyTree({"r": call}),
                name=f"top_{i}",
                metadata={},
            )
        )
    return tops


def test_infer_nodegroup_distributions_keeps_partially_dynamic():
    """A subgraph with one dynamic input and one inferable input must produce
    a distribution graph, not be dropped."""
    tops = _toy_subgraph_calls([1.0, 2.0], dynamic_b=True)
    res = tr.infer_nodegroup_distributions(tops)
    assert len(res) == 1
    inputs = res[0].inputs.dict()
    assert set(inputs) == {"rng", "b"}


def test_infer_nodegroup_distributions_drops_all_dynamic():
    """A subgraph where every input is dynamic has nothing inferred and is
    dropped."""
    sub_inputs = {
        "a": cg.InputPlaceholderNode(name="a", default_value=None, metadata={}),
    }
    sub = cg.ComputeGraph(
        inputs=pytree.PyTree(sub_inputs),
        outputs=pytree.PyTree({"out": sub_inputs["a"]}),
        name="toy_sub_dyn",
        metadata={},
    )
    tops = []
    for i in range(2):
        call = cg.SubgraphCallNode(
            subgraph=sub,
            args=(),
            kwargs={"a": cg.FunctionCallNode(pf.nodes.shader.coord, (), {})},
        )
        tops.append(
            cg.ComputeGraph(
                inputs=pytree.PyTree({}),
                outputs=pytree.PyTree({"r": call}),
                name=f"top_dyn_{i}",
                metadata={},
            )
        )
    assert tr.infer_nodegroup_distributions(tops) == []


def test_infer_distribution_hypercube():
    graphs = [
        _toy_shader_graph("material_a", scale=2.0),
        _toy_shader_graph("material_b", scale=5.0),
    ]
    res = tr.infer_distribution_hypercube(graphs)

    assert res.name == "material_distribution"
    assert isinstance(res.inputs.obj()["rng"], cg.InputPlaceholderNode)
    assert res.outputs.toplevel_type() is t.Material

    surface = res.outputs.dict()["surface"]
    assert isinstance(surface, cg.FunctionCallNode)
    assert surface.func is pf.nodes.texture.noise

    # identical kwargs are kept, differing kwargs become a uniform distribution
    assert isinstance(surface.kwargs["vector"], cg.GetAttributeNode)
    scale = surface.kwargs["scale"]
    assert isinstance(scale, cg.FunctionCallNode)
    assert scale.func is pf.random.uniform
    assert scale.args[0] is res.inputs.obj()["rng"]
    assert float(scale.args[1]) == 2.0
    assert float(scale.args[2]) == 5.0
