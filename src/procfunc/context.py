import copy
import multiprocessing
import os
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from typing import Any, Literal


@dataclass
class ProcfuncContext:
    """Global context for Procfunc configuration and system information."""

    num_cpu_cores: int
    current_trace_level: int | None  # compared against to TraceLevel int values

    warn_mode_avoid_normal_bump: Literal["ignore", "warn", "throw"]
    """
    Set to 'throw' for infinigen best practices. Using a normal map / bump map / BSDF vector input _can_ be useful,
    but its always better to do it via the Displacement output of the shader (so that it at least can also be done as displacement)
    """

    warn_mode_avoid_implicit_vector: Literal["ignore", "warn", "throw"]
    """
    Set to 'throw' for default infinigen usage - we force the user to specify exactly what vector to sample
    This prevents materials from being incorrect when on a moving object, or ignoring uv coordinates
    """

    warn_mode_avoid_io_nodes: Literal["ignore", "warn", "throw"]
    """
    Set to 'throw' for infinigen, prevents floating Value Vector Color nodes, or strange output nodes like AOV in shader
    Intent is to force nodegroups to be more functional - all inputs and outputs go through nodegroup interface
    """

    warn_mode_empty_geonodes: Literal["ignore", "warn", "throw"]
    """
    Controls behavior when a geometry node graph produces no mesh geometry (e.g. unconnected inputs).
    'ignore' silently returns an empty mesh, 'warn' logs a warning, 'throw' raises an error.
    """

    def __post_init__(self):
        """Initialize computed fields after dataclass creation."""
        if self.num_cpu_cores <= 0:
            self.num_cpu_cores = multiprocessing.cpu_count()

    def set_strict(self):
        """Set all warning modes to 'throw'"""
        self.warn_mode_avoid_normal_bump = "throw"
        self.warn_mode_avoid_implicit_vector = "throw"
        self.warn_mode_avoid_io_nodes = "throw"
        self.warn_mode_empty_geonodes = "throw"

    def set_warn(self):
        """Set all warning modes to 'warn'"""
        self.warn_mode_avoid_normal_bump = "warn"
        self.warn_mode_avoid_implicit_vector = "warn"
        self.warn_mode_avoid_io_nodes = "warn"
        self.warn_mode_empty_geonodes = "warn"


# Global context instance

warn_modes = ["ignore", "warn", "throw"]

_warn_mode_avoid_normal_bump = os.environ.get(
    "PROCFUNC_WARN_MODE_AVOID_NORMAL_BUMP", "ignore"
)
assert _warn_mode_avoid_normal_bump in warn_modes

warn_mode_avoid_implicit_vector = os.environ.get(
    "PROCFUNC_WARN_MODE_AVOID_IMPLICIT_VECTOR", "ignore"
)
assert warn_mode_avoid_implicit_vector in warn_modes

warn_mode_avoid_io_nodes = os.environ.get("PROCFUNC_WARN_MODE_AVOID_IO_NODES", "ignore")
assert warn_mode_avoid_io_nodes in warn_modes

_warn_mode_empty_geonodes = os.environ.get("PROCFUNC_WARN_MODE_EMPTY_GEONODES", "warn")
assert _warn_mode_empty_geonodes in warn_modes

globals = ProcfuncContext(
    num_cpu_cores=int(os.environ.get("PROCFUNC_NUM_CPU_CORES", 0)),
    warn_mode_avoid_normal_bump=_warn_mode_avoid_normal_bump,  # type: ignore[invalid-assignment]
    warn_mode_avoid_implicit_vector=warn_mode_avoid_implicit_vector,  # type: ignore[invalid-assignment]
    warn_mode_avoid_io_nodes=warn_mode_avoid_io_nodes,  # type: ignore[invalid-assignment]
    warn_mode_empty_geonodes=_warn_mode_empty_geonodes,  # type: ignore[invalid-assignment]
    current_trace_level=None,
)


@contextmanager
def override_globals(
    new_context: ProcfuncContext | None = None,
    **overrides: Any,
):
    """
    Override the context for a block of code

    Args:
        new_context: If provided, will override the entire context with this new context
        overrides: If provided, will override specific keys with these values
    """
    orig = copy.deepcopy(globals)

    if new_context is not None:
        for key, value in asdict(new_context).items():
            setattr(globals, key, value)

    if overrides is not None:
        for key, value in overrides.items():
            setattr(globals, key, value)

    yield

    for key, value in asdict(orig).items():
        setattr(globals, key, value)
