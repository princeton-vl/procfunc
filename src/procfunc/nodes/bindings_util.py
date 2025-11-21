import logging
from dataclasses import dataclass
from enum import Enum
from typing import Self

import procfunc as pf
from procfunc.nodes.bpy_node_info import NodeDataType, NodeGroupType
from procfunc.util.log import raise_error_or_warn

logger = logging.getLogger(__name__)


@dataclass
class RuntimeResolveDataType:
    data_types: list[NodeDataType]
    dependent_input_names: list[str]


class ContextualNode(Enum):
    """Special node types that map to different implementations based on context."""

    COMBINE_COLOR = "ContextualCombineColor"
    SEPARATE_COLOR = "ContextualSeparateColor"
    GROUP = "ContextualGroup"
    MIX_RGB = "ContextualMixRGB"
    MATH = "ContextualMath"

    @classmethod
    def parse_name(cls, from_name: str) -> Self | None:
        try:
            return cls(from_name)
        except ValueError:
            return None


@dataclass
class NodeContextResolution:
    contextual_node: ContextualNode
    node_group_type: NodeGroupType
    node_type: str
    input_keys_map: dict[str, tuple[str, int] | str | None] | None


# Mapping to map unified version of nodes to context-specific blender versions
# Input keys are (ContextualNode, NodeGroupType) - the unifiied version + the context we need to use it in
# Output is the (NodeType, input map) - tells what specific node to construct, then how to change the inputs for that context, if applicable

CONTEXTUAL_NODE_MAPPING = [
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_COLOR,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeCombineColor",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_COLOR,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeCombineColor",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_COLOR,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeCombineColor",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.SEPARATE_COLOR,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeSeparateColor",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.SEPARATE_COLOR,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeSeparateColor",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.SEPARATE_COLOR,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeSeparateColor",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.SEPARATE_COLOR,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeSeparateColor",
        input_keys_map={"Color": "Image"},
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.GROUP,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeGroup",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.GROUP,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeGroup",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.GROUP,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="GeometryNodeGroup",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MIX_RGB,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeMixRGB",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MIX_RGB,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeMixRGB",
        input_keys_map={"Fac": "Factor"},
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MIX_RGB,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="ShaderNodeMixRGB",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeMath",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeMath",
        input_keys_map=None,
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeMath",
        input_keys_map=None,
    ),
]


def resolve_contextual_node(
    node: list[NodeContextResolution], group: NodeGroupType
) -> tuple[str, dict[str, str]]:
    item = next(
        (
            item
            for item in CONTEXTUAL_NODE_MAPPING
            if (item.node_group_type == group and item.contextual_node == node)
        ),
        None,
    )

    if item is None:
        raise ValueError(f"No contextual node found for {node} in {group}")

    return item.node_type, item.input_keys_map


def raise_shader_normal_error(node_func_name: str, logger: logging.Logger):
    """Helper to handle normal socket usage in shaders based on context setting."""

    message = (
        f"Using 'normal' input in {node_func_name} is not recommended. "
        f"Use displacement instead. To suppress this message, set "
        f"pf.context.globals.warn_mode_avoid_normal_bump = 'ignore'"
    )

    raise_error_or_warn(message, pf.context.globals.warn_mode_avoid_normal_bump, logger)


def raise_explicit_noise_vector_error(node_func_name: str, logger: logging.Logger):
    """Helper to handle missing vector input in noise functions based on context setting."""
    message = (
        f"The 'vector' input is required for {node_func_name}. "
        f"Infinigen requires an explicit vector input - node will not default to using texture coordinate or world coordinate like blender. "
        f"To suppress this message, set pf.context.globals.warn_mode_avoid_implicit_vector = 'ignore'"
    )
    raise_error_or_warn(
        message, pf.context.globals.warn_mode_avoid_implicit_vector, logger
    )


def raise_io_error(node_func_name: str, logger: logging.Logger):
    """Helper to handle IO nodes based on context setting."""
    message = (
        f"IO nodes are not allowed in nodegroups but we found {node_func_name} in the nodegroup. Use the nodegroup interface instead. "
        "To suppress this message, set pf.context.globals.warn_mode_avoid_io_nodes = 'ignore'"
    )
    raise_error_or_warn(message, pf.context.globals.warn_mode_avoid_io_nodes, logger)
