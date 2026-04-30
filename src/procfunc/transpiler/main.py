import argparse
import itertools
import logging
from pathlib import Path
from typing import Callable, Literal

import bpy
import pandas as pd

import procfunc as pf
from procfunc import compute_graph as cg
from procfunc import transforms as tr
from procfunc.nodes import NODE_OPERATOR_TABLE
from procfunc.util import pytree
from procfunc.util.teardown import skip_teardown_on_exit

from .bpy_to_computegraph import (
    ParseMemo,
    parse_material,
    parse_node_tree,
    parse_object,
)
from .codegen import default_func_resolution_map, to_python

logging.basicConfig(
    format="[%(asctime)s.%(msecs)03d] [%(module)s] [%(levelname)s] | %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

MODIFIERS_MANIFEST: pd.DataFrame | None = None
NODES_MANIFEST: pd.DataFrame | None = None


BPY_COLLECTIONS = [
    "scene",
    "object",
    "material",
    # "collections",
]

RETURN_TYPES = {
    "object": pf.MeshObject,
    "material": pf.Material,
    "collection": pf.Collection,
}


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", type=Path)

    parser.add_argument("--materials", type=str, default=[], nargs="+")
    parser.add_argument("--objects", type=str, default=[], nargs="+")
    parser.add_argument("--node_trees", type=str, default=[], nargs="+")

    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--transforms", type=str, default=[], nargs="+")

    parser.add_argument(
        "--object_mode",
        type=str,
        choices=["monkey", "active", "named"],
        default="monkey",
    )
    parser.add_argument("--no_version_comments", action="store_true")

    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )

    parser.add_argument("--add_line_comments", action="store_true")
    parser.add_argument("--include_object_materials", action="store_true")

    return parser


def parse_target(
    target: bpy.types.Object | bpy.types.Material | bpy.types.NodeTree,
    memo: ParseMemo,
    object_mode: Literal["monkey", "active", "named"] = "monkey",
    include_set_material: bool = True,
) -> cg.ComputeGraph:
    match target:
        # case pf.Scene:
        #    return parse_scene(bpy.context.scene, memo)
        case bpy.types.Object():
            return parse_object(
                target,
                memo,
                object_mode=object_mode,
                include_set_material=include_set_material,
            )
        case bpy.types.Material():
            return parse_material(target, memo)
        case bpy.types.NodeTree():
            graph, _ = parse_node_tree(target, memo)
            return graph
        case x:
            raise ValueError(f"Invalid {x=} {type(x)=}")


def _find_target_str(target: str, col: bpy.types.bpy_prop_collection) -> list:
    if target.isdigit():
        return [col[int(target)]]
    elif "*" in target:
        assert target.count("*") == 1
        assert target.endswith("*") == 0
        prefix = target.replace("*", "")
        return [v for k, v in col.items() if k.startswith(prefix)]
    else:
        matches = [v for k, v in col.items() if k == target]
        if len(matches) != 1:
            available = " ".join(col.keys())
            raise ValueError(
                f"Found {len(matches)} targets for {target=} in {available=}"
            )
        return [matches[0]]


def transpile_targets(
    targets: list[bpy.types.Object | bpy.types.Material | bpy.types.NodeTree],
    transforms: list[Callable[[list[cg.ComputeGraph]], list[cg.ComputeGraph]]],
    object_mode: Literal["monkey", "active", "named"] = "monkey",
    add_version_comment: bool = True,
    add_line_comments: bool = False,
    include_set_material: bool = True,
) -> str:
    memo = ParseMemo()

    result_graphs = [
        parse_target(
            target,
            memo,
            object_mode=object_mode,
            include_set_material=include_set_material,
        )
        for target in targets
    ]

    for tfunc in transforms:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Applying transform {tfunc} to {result_graphs=}")
        result_graphs = tfunc(result_graphs)

    vec = cg.FunctionCallNode(pf.nodes.coord, (), {})
    vec = cg.GetAttributeNode(vec, "generated")

    result_calls = []
    for result_graph in result_graphs:
        kwargs = {}
        if result_graph.name.startswith("material_"):
            kwargs["vector"] = vec

        return_type = RETURN_TYPES.get(type(result_graph), None)
        call_node = cg.SubgraphCallNode(
            subgraph=result_graph,
            args=(),
            kwargs=kwargs,
            metadata={"known_value_type": return_type},
        )
        result_calls.append(call_node)

    toplevel_name = "toplevel_invoke"
    graph = cg.ComputeGraph(
        inputs=pytree.PyTree(()),
        outputs=pytree.PyTree({"result": result_calls}),
        name=toplevel_name,
        metadata={},
    )
    assert isinstance(graph, cg.ComputeGraph), graph

    func_resolution, import_lines = default_func_resolution_map(graph)
    for oprow in NODE_OPERATOR_TABLE:
        func_resolution[oprow.pf_func] = oprow.operator_type

    python = to_python(
        graph,
        func_resolution=func_resolution,
        import_lines=import_lines,
        add_version_comment=add_version_comment,
        add_line_comments=add_line_comments,
    )

    return python


def inject_into_python_file(python: list[str], file: Path, target_name: str):
    """
    If def <target_name>(): is found in the python file, replace it with the python code.
    If not, add it to end of the file.
    """

    text = file.read_text()
    lines = text.splitlines()

    start_line = next(
        (i for i, line in enumerate(lines) if line.startswith(f"def {target_name}")),
        None,
    )

    if start_line is None:
        lines.append


def _targets_from_args(
    args: argparse.Namespace,
) -> list[bpy.types.Object | bpy.types.Material | bpy.types.NodeTree]:
    targets = []
    targets += [
        _find_target_str(target, bpy.data.materials) for target in args.materials
    ]
    for target in args.objects:
        if target == "ACTIVE":
            if bpy.context.active_object is None:
                raise ValueError(
                    "--objects ACTIVE specified but no active object in scene"
                )
            targets.append([bpy.context.active_object])
        else:
            targets.append(_find_target_str(target, bpy.data.objects))
    targets += [
        _find_target_str(target, bpy.data.node_groups) for target in args.node_trees
    ]

    return list(itertools.chain.from_iterable(targets))


_transforms_map = {
    "colors_to_hsv_definition": tr.map_graph_list(tr.colors_to_hsv_definition),
    "infer_distribution_hypercube": (
        lambda graphs: graphs + [tr.infer_distribution_hypercube(graphs)]
    ),
    "infer_nodegroup_distributions": (
        lambda graphs: tr.infer_nodegroup_distributions(graphs) + graphs
    ),
    "extract_materials": tr.extract_materials_from_graphs,
    # "infer_distribution_polytope": lambda graphs: graphs + [tr.infer_distribution_polytope(graphs)],
}


def main():
    parser = get_parser()
    args = parser.parse_args()

    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).setLevel(args.loglevel)

    pf.ops.file.load_blend(args.input)

    targets = _targets_from_args(args)

    if len(targets) == 0:
        raise ValueError(
            f"No targets found for {args.input} {args.materials=} {args.objects=} {args.node_trees=}"
        )

    logger.info(f"Found targets {[x.name for x in targets]}")

    transforms = [_transforms_map[x] for x in args.transforms]
    python = transpile_targets(
        targets,
        transforms,
        object_mode=args.object_mode,
        add_version_comment=not args.no_version_comments,
        add_line_comments=args.add_line_comments,
        include_set_material=args.include_object_materials,
    )

    match args.output:
        case "print":
            print(python)
        case None:
            pass
        case x if Path(x).suffix == ".py":
            x = Path(x)
            x.parent.mkdir(parents=True, exist_ok=True)
            print(f"Writing transpiled code to path {x}")
            with x.open("w") as f:
                f.write(python)
        case x if ":" in x:
            raise NotImplementedError("Not implemented")
            module_path, target_name = x.split(":")
            inject_into_python_file(python.splitlines(), Path(module_path), target_name)
        case _:
            raise ValueError(f"Invalid output type: {args.output}")


if __name__ == "__main__":
    with skip_teardown_on_exit():
        main()
