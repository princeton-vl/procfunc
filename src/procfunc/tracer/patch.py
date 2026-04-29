import enum
import functools
import logging
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, TypeAlias, TypeVar

from procfunc import compute_graph as cg
from procfunc.tracer.proxy import RngProxy
from procfunc.util import pytree

logger = logging.getLogger(__name__)

PATCHING_FLAG_ATTR = "_gen_tracing_is_patched"
_MODULE_CALLFUNC = "__call__"
_MODULE_GENFUNC = "_generate"

Tfunc = TypeVar("Tfunc")

TWrapperCreate: TypeAlias = Callable[["PatchFunctionTarget", "Patcher"], Callable]


class TraceLevel(enum.IntEnum):
    """
    Higher = coarser. Lower = finer.

    The resulting graph will contain nodes which are this level
    """

    GRAMMAR = 100  # _distribution functions
    RANDOM_CONTROL = 60  # pf.control.choice
    RANDOM_PARAMS = 50  # np.random calls, all other operations of numbers.
    GENERATORS = 40
    NODEGROUPS = 30  # @node_function
    PRIMITIVES = 20


@dataclass
class PatchFunctionTarget:
    frame: dict
    name: str
    trace_level: TraceLevel  # Compared to users requested trace level to decide whether this target will be a leaf. More
    normalize: bool = True
    allow_exec: bool = False
    custom_trace_wrapper_create: TWrapperCreate | None = None
    source_name: str | None = None  # used for logging/debugging
    mutates: list[str] | None = None  # list of argument names that the function mutates


@dataclass
class Patch:
    frame: dict[str, Any]
    fn_name: str
    orig_fn: Callable
    patched_fn: Callable

    def patch(self):
        raise NotImplementedError()

    def unpatch(self):
        raise NotImplementedError()


@dataclass
class PatchSetItem(Patch):
    def patch(self):
        self.frame[self.fn_name] = self.patched_fn

    def unpatch(self):
        self.frame[self.fn_name] = self.orig_fn


@dataclass
class PatchSetAttr(Patch):
    def patch(self):
        logger.debug(
            f"Patching {self.fn_name} in {id(self.frame)} from {self.orig_fn} to {self.patched_fn}"
        )
        setattr(self.frame, self.fn_name, self.patched_fn)

    def unpatch(self):
        setattr(self.frame, self.fn_name, self.orig_fn)


def _targets_from_module(
    module: ModuleType,
    seen: set[int],
    trace_level: TraceLevel,
    normalize: bool = False,
    allow_exec: bool = False,
) -> list[PatchFunctionTarget]:
    """
    Gather functions from modules like `math`, `numpy`, `blendfunc` wherein we want to wrap everything they contain

    We will use such functions as primitives - we will not trace their internals

    We will allow them to be executed if they are called with non-dynamic args

    Args:
        module: the module to gather targets from
        seen: a set of ids of functions that have already been processed and should be skipped
        normalize: whether to try to convert args to kwargs where available. fails for some modules such as numpy
        allow_exec: whether to allow the function to be executed if it is called with non-dynamic args

    Returns:
        a list of PatchFunctionTargets, one for each valid callable in the module. We ignore any function starting with _ or that is not in __all__.
    """

    results = []
    exports = getattr(module, "__all__", None)
    for name, value in module.__dict__.items():
        if (
            name.startswith("_")
            or issubclass(type(value), type)
            or not callable(value)
            or id(value) in seen
            or (exports is not None and name not in exports)
        ):
            continue

        seen.add(id(value))

        target = PatchFunctionTarget(
            frame=module.__dict__,
            name=name,
            source_name=module.__name__,
            normalize=normalize,
            allow_exec=allow_exec,
            trace_level=trace_level,
        )

        results.append(target)

    # logger.debug(
    #    f"Gathered {len(results)} targets from {module.__name__} with {normalize=} {allow_exec=}"
    # )

    return results


class Patcher:
    """
    A 'patch' is an invasive modification of another module (e.g numpy, math) which makes their functions behave differently for tracing

    This class creates patches and records them so that we can undo them later
    """

    def __init__(
        self,
        trace_level: TraceLevel,
        autopatch_wrap_modules: list[tuple[ModuleType, bool, TraceLevel]] | None = None,
        autopatch_remove_modules: list[ModuleType] | None = None,
        patch_functions: list[PatchFunctionTarget] | None = None,
        search_scopes: list[dict] | None = None,
    ):
        self.trace_level = trace_level
        if autopatch_wrap_modules is None:
            autopatch_wrap_modules = []
        if autopatch_remove_modules is None:
            autopatch_remove_modules = []
        if patch_functions is None:
            patch_functions = []
        if search_scopes is None:
            search_scopes = []

        self.patched: list[Patch] = []
        self.visited_frames: set[int] = set()

        modules_seen = set()

        autowrap_targets = []
        for m, allow_exec, mod_trace_level in autopatch_wrap_modules:
            autowrap_targets += _targets_from_module(
                m,
                modules_seen,
                trace_level=mod_trace_level,
                allow_exec=allow_exec,
            )

        ban_targets = []
        for m in autopatch_remove_modules:
            ban_targets += _targets_from_module(
                m, modules_seen, trace_level=TraceLevel.PRIMITIVES
            )

        self.patch_function_ids = {
            # keys ensure we can have separate unique values for same func in different frames
            id(target.frame[target.name]): target
            for target in autowrap_targets + patch_functions
        }
        self.ban_function_ids = {
            id(target.frame[target.name]): target for target in ban_targets
        }

        self._autopatch_wrap_modules = autopatch_wrap_modules
        self._autopatch_remove_modules = autopatch_remove_modules

        for scope in search_scopes:
            logger.debug(f"Adding search scope {id(scope)}")
            self.search_autowrap_targets(scope)

        logger.debug(
            f"{Patcher.__name__} found {len(self.patch_function_ids)=}, {len(self.ban_function_ids)=}"
        )

    def apply_preexecute_patches(
        self,
        func: Callable,
        trace_level: TraceLevel | None = None,
    ):
        for target in self.patch_function_ids.values():
            orig_fn = target.frame.get(target.name)
            if orig_fn is None:
                raise NotImplementedError(
                    f"{target.name} not found in frame (possibly a builtin)"
                )

            if getattr(orig_fn, PATCHING_FLAG_ATTR, False):
                continue

            func_wrapper = self.create_wrapper(orig_fn)
            patch = PatchSetItem(
                frame=target.frame,
                fn_name=target.name,
                orig_fn=orig_fn,
                patched_fn=func_wrapper,
            )
            self.patch(patch)

        for _id, target in self.ban_function_ids.items():
            orig_fn = target.frame.get(target.name)
            if orig_fn is None:
                raise NotImplementedError(
                    f"{target.name} not found in frame (possibly a builtin)"
                )
            patch = PatchSetItem(
                frame=target.frame,
                fn_name=target.name,
                orig_fn=orig_fn,
                patched_fn=_create_banned_func_wrapper(orig_fn),
            )
            self.patch(patch)

        for module, _allow_exec, _trace_level in self._autopatch_wrap_modules:
            self.search_autowrap_targets(module.__dict__)
        for module in self._autopatch_remove_modules:
            self.search_autowrap_targets(module.__dict__)

        self.search_autowrap_targets(func.__globals__)

        # func may be itself be a target we need to wrap
        func = self.create_wrapper(func)

        return func

        # call_wrapper = _create_module_call_wrapper(self)
        # module_call_patch = PatchSetAttr(
        #     frame=Module,
        #     fn_name=_MODULE_CALLFUNC,
        #     orig_fn=_ORIG_MODULE_CALL,
        #     patched_fn=call_wrapper,
        # )
        # self.patch(module_call_patch)

        # module_getattr_patch = PatchSetAttr(
        #    frame=Module,
        #    fn_name="__getattribute__",
        #    orig_fn=_ORIG_MODULE_GETATTR,
        #    patched_fn=_create_module_getattr_wrapper(),
        # )
        # patcher.patch(module_getattr_patch)

    def create_wrapper(
        self,
        func: Callable,
    ):
        if getattr(func, PATCHING_FLAG_ATTR, False):
            raise ValueError(
                f"Function {func.__name__} is already wrapped, should have already been skipped"
            )

        wrap_target = self.patch_function_ids.get(id(func))
        ban_target = self.ban_function_ids.get(id(func))

        is_wrap = wrap_target is not None
        is_ban = ban_target is not None

        # Can't wrap functions without __globals__ unless they're explicit targets
        if not hasattr(func, "__globals__") and not is_wrap and not is_ban:
            return func

        match is_wrap, is_ban:
            case (False, False):
                wrapper = _create_nonleaf_wrap_discover_wrapper(func, self)
            case (True, False):
                if wrap_target.custom_trace_wrapper_create is not None:
                    wrapper = wrap_target.custom_trace_wrapper_create(wrap_target, self)
                elif wrap_target.trace_level <= self.trace_level:
                    wrapper = _create_leaf_func_proxy_wrapper(wrap_target, self)
                else:
                    wrapper = _create_nonleaf_wrap_discover_wrapper(func, self)
            case False, True:
                wrapper = _create_banned_func_wrapper(func)
            case True, True:
                raise ValueError(
                    f"Got {func.__name__} which was both wrapped and banned? {wrap_target=} {ban_target=}"
                )

        # if logger.isEnabledFor(logging.DEBUG):
        #    logger.debug(
        #        f"Created wrapper for {func.__name__} {id(func)} -> {id(wrapper)} {is_wrap=} {is_ban=}"
        #    )

        return wrapper

    def search_autowrap_targets(self, frame: dict):
        # for efficiency - dont bother re-searching frames, since all the functions will be tagged/wrapped already
        if id(frame) in self.visited_frames:
            logger.debug(f"Already-visited frame {id(frame)}")
            return
        self.visited_frames.add(id(frame))

        for name, value in frame.items():
            skip = (
                getattr(value, PATCHING_FLAG_ATTR, False)
                or (name.startswith("__") and name.endswith("__"))
                or not callable(value)
            )
            if skip:
                continue

            patch = PatchSetItem(
                frame=frame,
                fn_name=name,
                orig_fn=value,
                patched_fn=self.create_wrapper(value),
            )
            self.patch(patch)

    def patch(
        self,
        patch: Patch,
    ):
        if hasattr(patch.orig_fn, PATCHING_FLAG_ATTR):
            logger.debug(f"skipping already patched {patch.orig_fn} {id(patch)}")
            return

        try:
            setattr(patch.patched_fn, PATCHING_FLAG_ATTR, True)
        except (TypeError, AttributeError) as _e:
            # logger.debug(
            #    f"Failed to setattr {PATCHING_FLAG_ATTR} on {patch.patched_fn} {type(patch.patched_fn)=} {e}"
            # )
            pass  # cant cache bools on some immutable types like Tuple

        patch.patch()
        self.patched.append(patch)

    def unpatch_all(self):
        for patch in self.patched:
            patch.unpatch()
        self.patched.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unpatch_all()
        return False


def _create_leaf_func_proxy_wrapper(
    target: PatchFunctionTarget,
    patcher: Patcher,
) -> cg.Node | Tfunc:
    func = target.frame[target.name]

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Executing leaf_wrapper! func={func.__name__}")

        # zero proxy args means the user is trying to call this function with real args during tracing
        # e.g they might do: bias = np.zeros(3)
        # some functions will allow this and just execute the function and return the result
        def _unwrap_proxy(v):
            return v.node if isinstance(v, cg.Proxy) else v

        if target.allow_exec:
            all_leaves, _ = pytree.flatten((args, kwargs))
            proxy_leaves = [v for v in all_leaves if isinstance(v, cg.Proxy)]
            if not proxy_leaves:
                return func(*args, **kwargs)
            rng_only = all(isinstance(v, RngProxy) for v in proxy_leaves)
            if rng_only and patcher.trace_level < TraceLevel.RANDOM_PARAMS:

                def _unbox_rng(v):
                    return v.rng if isinstance(v, RngProxy) else v

                concrete_args = tuple(
                    pytree.PyTree(a).map(_unbox_rng).obj() for a in args
                )
                concrete_kwargs = {
                    k: pytree.PyTree(v).map(_unbox_rng).obj() for k, v in kwargs.items()
                }
                return func(*concrete_args, **concrete_kwargs)

        if target.normalize:
            args, kwargs = cg.normalize_args_to_kwargs(func, args, kwargs)

        # Convert any Proxy args to their underlying nodes, including those nested in containers
        node_args = tuple(pytree.PyTree(a).map(_unwrap_proxy).obj() for a in args)
        node_kwargs = {
            k: pytree.PyTree(v).map(_unwrap_proxy).obj() for k, v in kwargs.items()
        }

        node = cg.FunctionCallNode(func=func, args=node_args, kwargs=node_kwargs)

        # Handle mutations by updating proxies for mutated arguments
        for param_name in target.mutates or []:
            if not (param_name in kwargs and isinstance(kwargs[param_name], cg.Proxy)):
                continue
            original_proxy = kwargs[param_name]
            mutated_node = cg.MutatedArgumentNode(
                mutator_call_node=node, original_node=original_proxy.node
            )
            logger.debug(
                f"MutatedArgumentNode created: {func.__name__}({param_name}=...) -> {mutated_node}"
            )
            original_proxy.node = mutated_node

        return cg.Proxy(node)

    if hasattr(func, "reduce"):
        # numpy.random.Generator breaks if these special reduce functions-inside-functions are not copied over?
        # TODO: handle the general case of metadata attrs on wrapped functions, I believe torch.fx does this
        wrapper.reduce = func.reduce

    setattr(wrapper, PATCHING_FLAG_ATTR, True)
    return wrapper


def _create_nonleaf_wrap_discover_wrapper(
    func: Callable,
    patcher: Patcher,
):
    # TODO: should record non-leaf functions in the graph while also executing their internals?

    if getattr(func, PATCHING_FLAG_ATTR, False):
        raise ValueError(f"Function {func.__name__} is already wrapped")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        frame = getattr(func, "__globals__", {})
        logger.debug(f"Searching autowrap targets for {func.__name__} {id(frame)}")
        patcher.search_autowrap_targets(frame)
        logger.debug(f"Finished autowrap targets for {func.__name__} {id(frame)}")

        # Wrap any callable args that are registered targets but weren't reachable
        # via module-dict patching (e.g. passed as function-valued arguments)
        def maybe_wrap(v):
            if not callable(v):
                return v
            if getattr(v, PATCHING_FLAG_ATTR, False):
                return v
            if id(v) in patcher.patch_function_ids:
                logger.debug(
                    f"maybe_wrap: wrapping callable arg {getattr(v, '__name__', v)!r} id={id(v)} found in patch_function_ids"
                )
                return patcher.create_wrapper(v)
            logger.debug(
                f"maybe_wrap: callable arg {getattr(v, '__name__', v)!r} id={id(v)} NOT in patch_function_ids (size={len(patcher.patch_function_ids)})"
            )
            return v

        args = tuple(maybe_wrap(a) for a in args)
        kwargs = {k: maybe_wrap(v) for k, v in kwargs.items()}

        return func(*args, **kwargs)

    setattr(wrapper, PATCHING_FLAG_ATTR, True)

    return wrapper


def _create_banned_func_wrapper(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        raise ValueError(
            f"Tracing failed - {func.__name__} is banned from use in traceable functions"
        )

    setattr(wrapped_func, PATCHING_FLAG_ATTR, True)

    return wrapped_func
