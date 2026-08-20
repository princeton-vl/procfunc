import procfunc as pf
from procfunc import compute_graph as cg


def _proc_node(socket) -> cg.ProceduralNode:
    node = socket.item()
    while not isinstance(node, cg.ProceduralNode):
        node = node.args[0]
    return node


def test_definition_metadata_off_by_default():
    res = pf.nodes.texture.noise(vector=None, scale=5.0)
    assert "definition" not in _proc_node(res.fac).metadata


def test_context_construction_defaults_definition_metadata_off():
    new_context = pf.context.ProcfuncContext(1, None, "warn")
    with pf.context.override_globals(new_context=new_context):
        assert not pf.context.globals.record_node_definitions


def test_definition_metadata_recorded_when_enabled():
    with pf.context.override_globals(record_node_definitions=True):
        res = pf.nodes.texture.noise(vector=None, scale=5.0)
    file, lineno, procfunc_name = _proc_node(res.fac).metadata["definition"]
    assert file == __file__
    assert lineno > 0
    assert procfunc_name == "noise"
