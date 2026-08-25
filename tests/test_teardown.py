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


def test_coverage_data_saved_before_exit(tmp_path):
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


def test_exit_code_preserved_without_coverage(tmp_path):
    script = write_entrypoint(
        tmp_path, "with skip_teardown_on_exit():\n    raise SystemExit(3)\n"
    )

    proc = run([sys.executable, str(script)], tmp_path)

    assert proc.returncode == 3, proc.stderr
