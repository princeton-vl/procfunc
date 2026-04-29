import os

import pytest

from procfunc.util import teardown

_exitstatus = 0


def pytest_sessionfinish(session, exitstatus):
    global _exitstatus
    _exitstatus = int(exitstatus)


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):
    # bpy's C-level teardown segfaults on normal Python shutdown, which would
    # mask the real pytest exit code in CI. Skip teardown once reporting is done.
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return
    teardown.exit_skipping_teardown(_exitstatus)
