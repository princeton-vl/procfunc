"""Helpers to exit without triggering bpy's C-level teardown segfault.

bpy's cleanup segfaults (SIGSEGV / exit code 139) during normal Python
shutdown. ``os._exit`` skips Python teardown and atexit handlers, avoiding
the crash while preserving the real exit code. Anything the process would
otherwise have written on its way out is flushed here first.
"""

import os
import sys
import traceback
from contextlib import contextmanager


def _save_coverage() -> None:
    # coverage.py saves once the traced process returns, which os._exit never does
    try:
        import coverage

        cov = coverage.Coverage.current()
        if cov is not None:
            cov.save()
    except Exception:
        traceback.print_exc()


def exit_skipping_teardown(code: int = 0):
    _save_coverage()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)


@contextmanager
def skip_teardown_on_exit():
    """Run a block and unconditionally ``os._exit`` when it finishes.

    Catches ``SystemExit``, unhandled exceptions, and normal return;
    translates each into an ``os._exit`` with the appropriate code so
    bpy's teardown is skipped. Unhandled exceptions are printed with the
    standard Python traceback format to stderr before exiting, matching
    what you'd see from a natural crash.
    """
    try:
        yield
    except SystemExit as e:
        exit_skipping_teardown(e.code if isinstance(e.code, int) else 1)
    except BaseException:
        traceback.print_exc()
        exit_skipping_teardown(1)
    exit_skipping_teardown(0)
