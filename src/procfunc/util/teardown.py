"""Helpers to exit without triggering bpy's C-level teardown segfault.

bpy's cleanup segfaults (SIGSEGV / exit code 139) during normal Python
shutdown. ``os._exit`` skips Python teardown and atexit handlers, avoiding
the crash while preserving the real exit code.
"""

import os
import sys
import traceback
from contextlib import contextmanager


def exit_skipping_teardown(code: int = 0):
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
