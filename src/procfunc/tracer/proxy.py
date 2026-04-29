from dataclasses import dataclass

import numpy as np

from procfunc import compute_graph as cg


@dataclass
class RngProxy(cg.Proxy):
    """
    We will do specialcase handling to trace rng nodes through the graph

    This allows us to know what the results of choice() and other random control flow will be,
    BUT only if the user has kept the rng non-dirty, i.e. the rng used for choice descends from the root via only spawn() calls

    This is essential so that the result of choice() during tracing is the same as the result of choice() during generation
    """

    rng: np.random.Generator

    # true if any randomness has been taken from this rng besides splitting it via spawn
    dirty: bool = False

    def __init__(
        self,
        node: cg.Node,
        rng: np.random.Generator,
        dirty: bool = False,
    ):
        super().__init__(node)
        node.metadata["known_type"] = np.random.Generator
        node.metadata["varname"] = "rng"
        self.rng = rng
        self.dirty = dirty

    def spawn(self, n_children: int) -> "RngSpawnResultProxy":
        """
        Returns a mock node which can only be unpacked into its constitutent mock rngs
        """

        assert isinstance(n_children, int)

        spawn_node = cg.MethodCallNode(
            callee=self.node,
            method_name="spawn",
            args=(n_children,),
            kwargs={},
        )

        child_rngs = list(self.rng.spawn(n_children))

        return RngSpawnResultProxy(
            node=spawn_node,
            from_rng_proxy=self,
            child_rngs=child_rngs,
            dirty=self.dirty,
        )

    def __getattr__(self, name: str):
        is_dirty_op = (
            not name.startswith("_") and not name == "spawn" and hasattr(self.rng, name)
        )

        if is_dirty_op:
            self.dirty = True

        if not hasattr(self.rng, name):
            raise AttributeError(
                f"__getattr__ {name} is invalid because {type(self.rng)} has no attribute {name}"
            )

        return super().__getattr__(name)


@dataclass
class RngSpawnResultProxy(cg.Proxy):
    from_rng_proxy: "RngProxy"
    child_rngs: list[np.random.Generator]
    dirty: bool = False

    def __init__(
        self,
        node: cg.Node,
        from_rng_proxy: "RngProxy",
        child_rngs: list[np.random.Generator],
        dirty: bool = False,
    ):
        super().__init__(node)
        node.metadata["varname"] = "rngs"
        self.from_rng_proxy = from_rng_proxy
        self.child_rngs = child_rngs
        self.dirty = dirty
        if self.dirty:
            import warnings

            warnings.warn(
                "RngSpawnResultProxy has dirty=True, tracing results may be incomplete"
            )

    def __getitem__(self, idx: int) -> "RngProxy":
        if idx < 0 or idx >= len(self.child_rngs):
            raise IndexError(
                f"Index {idx} out of range for {len(self.child_rngs)} children"
            )

        getitem_node = cg.MethodCallNode(
            callee=self.node,
            method_name="__getitem__",
            args=(idx,),
            kwargs={},
            metadata={"known_value_type": np.random.Generator},
        )

        return RngProxy(
            node=getitem_node,
            rng=self.child_rngs[idx],
            dirty=self.dirty,
        )

    def __iter__(self):
        """
        specialcase to allow __iter__() since SpawnResult has known size

        allows x,y,z = rng.spawn(3) syntax to work in functions that need to be traceable
        """
        for i in range(len(self.child_rngs)):
            yield self.__getitem__(i)
