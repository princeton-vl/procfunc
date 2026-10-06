import bpy

import procfunc as pf
from procfunc import compute_graph as cg


@pf.nodes.node_function
def _amount_offset(
    geometry: pf.ProcNode[pf.MeshObject],
    amount: pf.ProcNode[float],
) -> pf.ProcNode[pf.MeshObject]:
    offset = pf.nodes.math.combine_xyz(x=amount)
    return pf.nodes.geo.set_position(geometry=geometry, offset=offset)


@pf.nodes.node_function
def _offset(geometry: pf.ProcNode[pf.MeshObject]) -> pf.ProcNode[pf.MeshObject]:
    return pf.nodes.geo.set_position(geometry=geometry, offset=(1.0, 0.0, 0.0))


_lazy_calls = []


@pf.nodes.node_function
def _lazy(
    geometry: pf.ProcNode[pf.MeshObject],
    amount: pf.ProcNode[float],
) -> pf.ProcNode[pf.MeshObject]:
    _lazy_calls.append(None)
    offset = pf.nodes.math.combine_xyz(x=amount)
    return pf.nodes.geo.set_position(geometry=geometry, offset=offset)


def _cube():
    return pf.nodes.geo.mesh_cube(size=(1.0, 1.0, 1.0)).mesh


def _geo_nodegroup(graph: cg.ComputeGraph) -> bpy.types.NodeTree:
    return pf.nodes.as_nodegroup(graph, pf.nodes.NodeGroupType.GEOMETRY)


def test_node_function_builds_graph_on_first_call_only():
    assert len(_lazy_calls) == 0
    first = _lazy(_cube(), 1.0).item()
    assert len(_lazy_calls) == 1
    second = _lazy(_cube(), 2.0).item()
    assert len(_lazy_calls) == 1
    assert first.subgraph is second.subgraph
    assert first.kwargs["amount"] == 1.0
    assert second.kwargs["amount"] == 2.0


def test_node_function_reuses_nodegroup():
    first = _geo_nodegroup(_offset(_cube()).item().subgraph)
    second = _geo_nodegroup(_offset(_cube()).item().subgraph)
    assert first == second


@pf.nodes.node_function
def _add_one(value: pf.ProcNode[float]) -> pf.ProcNode[float]:
    return value + 1.0


def test_node_function_separates_tree_types():
    graph = _add_one(pf.nodes.math.constant(2.0)).item().subgraph
    geo = _geo_nodegroup(graph)
    shader = pf.nodes.as_nodegroup(graph, pf.nodes.NodeGroupType.SHADER)
    assert geo.bl_idname != shader.bl_idname


def test_deleted_nodegroup_is_rebuilt():
    graph = _offset(_cube()).item().subgraph
    bpy.data.node_groups.remove(_geo_nodegroup(graph))
    rebuilt = _geo_nodegroup(graph)
    assert bpy.data.node_groups.get(rebuilt.name) == rebuilt


def test_nodegroup_rebuilt_after_file_reset():
    graph = _offset(_cube()).item().subgraph
    _geo_nodegroup(graph)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rebuilt = _geo_nodegroup(graph)
    assert bpy.data.node_groups.get(rebuilt.name) == rebuilt


def test_transformed_graph_gets_own_nodegroup():
    graph = _offset(_cube()).item().subgraph
    original = _geo_nodegroup(graph)
    transformed = cg.transform_compute_graph(graph, lambda node: node)
    assert _geo_nodegroup(transformed) != original


def test_cached_nodegroups_execute_correctly():
    meshes = [
        pf.nodes.to_mesh_object(_amount_offset(_cube(), amount)).item()
        for amount in (1.0, 3.0)
    ]
    xs = [min(v.co.x for v in m.data.vertices) for m in meshes]
    assert abs(xs[0] - 0.5) < 1e-6
    assert abs(xs[1] - 2.5) < 1e-6


def _first_procedural_node(graph: cg.ComputeGraph) -> cg.ProceduralNode:
    nodes = cg.traverse_depth_first(graph)
    return next(n for n in nodes if isinstance(n, cg.ProceduralNode))


def test_definitions_recorded_after_cached_call():
    _offset(_cube())
    with pf.context.override_globals(record_node_definitions=True):
        graph = _offset(_cube()).item().subgraph
    assert "definition" in _first_procedural_node(graph).metadata
