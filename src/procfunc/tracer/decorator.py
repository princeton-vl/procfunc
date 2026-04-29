import functools
import inspect
import logging
from typing import Callable

from .patch import PatchFunctionTarget, TraceLevel
from .trace import add_wrap_target

logger = logging.getLogger(__name__)


def register_trace_target(
    func: Callable,
    trace_level: TraceLevel,
    allow_exec: bool,
    custom_trace_wrapper_create: Callable | None,
    mutates: list[str] | None = None,
    normalize: bool = True,
):
    """Helper function to register a function for tracing with consistent frame inspection"""

    if ".<locals>." in getattr(func, "__qualname__", ""):
        raise ValueError(
            f"Cannot register {func.__qualname__!r} as a trace target: local functions "
            "(defined inside another function) are not in module globals and cannot be "
            "traced. Move it to module level or remove the procfunc decorator."
        )

    f = inspect.currentframe()
    while f.f_code.co_name != "<module>":
        assert hasattr(f, "f_back")
        f = f.f_back
        assert hasattr(f, "f_code")

    frame = f.f_globals
    sourcename = f.f_code.co_filename.split("/")[-1][:-3]  # remove .py

    assert hasattr(func, "__name__")
    assert isinstance(func.__name__, str)

    # Local functions (defined inside another function) are never in the module
    # globals frame, so registering them would leave a stale entry that causes
    # KeyError on every subsequent pf.trace() call.
    if ".<locals>." in getattr(func, "__qualname__", ""):
        return

    add_wrap_target(
        PatchFunctionTarget(
            frame=frame,
            name=func.__name__,
            trace_level=trace_level,
            allow_exec=allow_exec,
            custom_trace_wrapper_create=custom_trace_wrapper_create,
            source_name=sourcename,
            mutates=mutates,
            normalize=normalize,
        )
    )


def _make_decorator(
    trace_level: TraceLevel = TraceLevel.GENERATORS,
):
    """
    Main decorator to mark a function and control its behaviour during tracing

    Args:
        trace_level: The level at which this function should be traced
        allow_exec: If True, the function may be executed. Use False for any functions that create meshes or have side-effects
        custom_trace_wrapper_create: Custom wrapper creation function for special tracing behavior
    """

    def decorator(
        func: Callable | None = None,
        *,
        allow_exec: bool = False,
        custom_trace_wrapper_create: Callable | None = None,
        mutates: list[str] | None = None,
        normalize: bool = True,
    ) -> Callable:
        @functools.wraps(func)
        def decorate(
            func: Callable,
        ):
            logger.debug(
                f"Decorating {func.__name__} with {trace_level=} {custom_trace_wrapper_create=}"
            )
            # When called as decorator, we need to go back 2 frames
            register_trace_target(
                func,
                trace_level,
                allow_exec,
                custom_trace_wrapper_create,
                mutates=mutates,
                normalize=normalize,
            )
            return func

        # handle EITHER @decorator or @decorator(args)
        if func is not None:
            return decorate(func)
        else:
            return decorate

    return decorator


grammar = _make_decorator(trace_level=TraceLevel.GRAMMAR)
random_control = _make_decorator(trace_level=TraceLevel.RANDOM_CONTROL)
random_param = _make_decorator(trace_level=TraceLevel.RANDOM_PARAMS)
generator = _make_decorator(trace_level=TraceLevel.GENERATORS)
primitive = _make_decorator(trace_level=TraceLevel.PRIMITIVES)

__all__ = [
    "register_trace_target",
    "grammar",
    "random_control",
    "random_param",
    "generator",
    "primitive",
]
