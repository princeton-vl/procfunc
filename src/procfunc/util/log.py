import logging
import os
import sys
from contextlib import contextmanager
from typing import Literal

logger = logging.getLogger(__name__)


class Suppress:
    def __enter__(self, logfile=os.devnull):
        open(logfile, "w").close()
        self.old = os.dup(1)
        sys.stdout.flush()
        os.close(1)
        os.open(logfile, os.O_WRONLY)
        self.level = logging.root.manager.disable
        logging.disable(logging.CRITICAL)

    def __exit__(self, type, value, traceback):
        os.close(1)
        os.dup(self.old)
        os.close(self.old)
        logging.disable(self.level)


class LogLevel:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.orig_level = None

    def __enter__(self):
        self.orig_level = self.logger.level
        self.logger.setLevel(self.level)

    def __exit__(self, *_):
        self.logger.setLevel(self.orig_level)


def clamp_with_log(val, logger, name, level=logging.WARNING, min=None, max=None):
    if min is not None and val < min:
        logger.log(level, f"{name} had {val} but will be clamped to {min=}")
        val = min
    if max is not None and val > max:
        logger.log(level, f"{name} had {val} but will be clamped to {max=}")
        val = max
    return val


def raise_error_or_warn(
    msg: str,
    mode: Literal["throw", "warn", "ignore"],
    warning_logger: logging.Logger | None,
    error_class: type = ValueError,
):
    if warning_logger is None:
        warning_logger = logger

    match mode:
        case "throw":
            raise error_class(msg)
        case "warn":
            warning_logger.warning(msg)
        case "ignore":
            pass
        case _:
            raise ValueError(f"Unknown mode: {mode}")


@contextmanager
def add_exception_context_msg(
    prefix: str = "",
    postfix: str = "",
    unparseable_exception_throw: Literal["throw", "warn", "ignore"] = "throw",
):
    try:
        yield
    except Exception as e:
        is_arg_msg = (
            isinstance(e.args, tuple) and len(e.args) > 0 and isinstance(e.args[0], str)
        )

        orig_msg = e.args[0] if is_arg_msg else f"{type(e).__name__}: {str(e)}"

        msg = orig_msg
        if prefix:
            msg = f"{prefix} {msg}"
        if postfix and not msg.endswith(postfix):
            msg = f"{msg} {postfix}"

        if is_arg_msg:
            e.args = (msg, *e.args[1:])
            raise e from e
        else:
            raise ValueError(msg) from e
