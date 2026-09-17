import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]


def write_entrypoint(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "entrypoint.py"
    script.write_text(
        "from procfunc.util.teardown import skip_teardown_on_exit\n\n" + body
    )
    return script


def run(cmd: list[str], tmp_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=_REPO,
        env={**os.environ, "COVERAGE_FILE": str(tmp_path / "data")},
        capture_output=True,
        text=True,
    )


def test_coverage_data_saved_before_exit(tmp_path: Path) -> None:
    pytest.importorskip("coverage")
    script = write_entrypoint(
        tmp_path, "with skip_teardown_on_exit():\n    print('ran')\n"
    )

    proc = run(
        [sys.executable, "-m", "coverage", "run", "--parallel-mode", str(script)],
        tmp_path,
    )

    assert proc.returncode == 0, proc.stderr
    assert sorted(tmp_path.glob("data.*")), proc.stderr


def test_exit_code_preserved_without_coverage(tmp_path: Path) -> None:
    script = write_entrypoint(
        tmp_path, "with skip_teardown_on_exit():\n    raise SystemExit(3)\n"
    )

    proc = run([sys.executable, str(script)], tmp_path)

    assert proc.returncode == 3, proc.stderr


def test_missing_optional_coverage_is_silent(tmp_path: Path) -> None:
    script = write_entrypoint(
        tmp_path,
        'import sys\nsys.modules["coverage"] = None\n\n'
        "with skip_teardown_on_exit():\n    print('ran')\n",
    )

    proc = run([sys.executable, str(script)], tmp_path)

    assert proc.returncode == 0, proc.stderr
    assert "Traceback" not in proc.stderr
    assert "ModuleNotFoundError" not in proc.stderr


@pytest.mark.parametrize("error_type", ["ImportError", "RuntimeError"])
def test_coverage_import_failure_preserves_exit_code(
    tmp_path: Path, error_type: str
) -> None:
    (tmp_path / "coverage.py").write_text(
        f"raise {error_type}('coverage import failed')\n"
    )
    script = write_entrypoint(
        tmp_path, "with skip_teardown_on_exit():\n    raise SystemExit(3)\n"
    )

    proc = run([sys.executable, str(script)], tmp_path)

    assert proc.returncode == 3, proc.stderr
    assert f"{error_type}: coverage import failed" in proc.stderr


def test_coverage_save_failure_is_reported(tmp_path: Path) -> None:
    script = write_entrypoint(
        tmp_path,
        "import sys\nimport types\n\n"
        "def fail():\n    raise RuntimeError('coverage save failed')\n\n"
        "current = types.SimpleNamespace(save=fail)\n"
        "coverage_type = types.SimpleNamespace(current=lambda: current)\n"
        'sys.modules["coverage"] = types.SimpleNamespace(Coverage=coverage_type)\n\n'
        "with skip_teardown_on_exit():\n    print('ran')\n",
    )

    proc = run([sys.executable, str(script)], tmp_path)

    assert proc.returncode == 0
    assert "RuntimeError: coverage save failed" in proc.stderr
