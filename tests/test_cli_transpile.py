import bpy
import pytest

from procfunc.transpiler import main as transpiler_main

MAT_NAMES = ["cli_glob_mat_a", "cli_glob_mat_b", "cli_other_mat"]


@pytest.fixture
def named_materials():
    for name in MAT_NAMES:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        # keep the materials alive across .blend save/load round trips
        mat.use_fake_user = True
    yield MAT_NAMES
    for name in MAT_NAMES:
        mat = bpy.data.materials.get(name)
        if mat is not None:
            bpy.data.materials.remove(mat)


def test_find_target_str_exact(named_materials):
    res = transpiler_main._find_target_str("cli_glob_mat_a", bpy.data.materials)
    assert res == [bpy.data.materials["cli_glob_mat_a"]]


def test_find_target_str_index(named_materials):
    mat = bpy.data.materials["cli_glob_mat_b"]
    idx = list(bpy.data.materials).index(mat)
    res = transpiler_main._find_target_str(str(idx), bpy.data.materials)
    assert res == [mat]


def test_find_target_str_glob(named_materials):
    res = transpiler_main._find_target_str("cli_glob_mat_*", bpy.data.materials)
    assert sorted(m.name for m in res) == ["cli_glob_mat_a", "cli_glob_mat_b"]


def test_find_target_str_glob_rejects_nontrailing(named_materials):
    with pytest.raises(ValueError, match="trailing"):
        transpiler_main._find_target_str("*_mat_a", bpy.data.materials)
    with pytest.raises(ValueError, match="trailing"):
        transpiler_main._find_target_str("cli_*_a*", bpy.data.materials)


def test_find_target_str_missing_name(named_materials):
    with pytest.raises(ValueError, match="Found 0 targets"):
        transpiler_main._find_target_str("does_not_exist", bpy.data.materials)


def test_cli_transpile_output_print(tmp_path, named_materials, capsys):
    blend = tmp_path / "cli_print.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))

    parser = transpiler_main.get_parser()
    args = parser.parse_args(
        [str(blend), "--materials", "cli_glob_mat_a", "--output", "print"]
    )
    transpiler_main.run(args)

    out = capsys.readouterr().out
    assert "cli_glob_mat_a" in out
    assert "def " in out


def test_cli_transpile_glob_end_to_end(tmp_path, named_materials):
    blend = tmp_path / "cli_glob.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))

    out_py = tmp_path / "out.py"
    parser = transpiler_main.get_parser()
    args = parser.parse_args(
        [str(blend), "--materials", "cli_glob_mat_*", "--output", str(out_py)]
    )
    transpiler_main.run(args)

    src = out_py.read_text()
    assert "cli_glob_mat_a" in src
    assert "cli_glob_mat_b" in src
    assert "cli_other_mat" not in src
