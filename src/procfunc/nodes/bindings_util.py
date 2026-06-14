import logging
from dataclasses import dataclass, field
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
    COLOR_RAMP = "ContextualColorRamp"
    VECTOR_CURVE = "ContextualVectorCurve"
    COMBINE_XYZ = "ContextualCombineXYZ"
    MAP_RANGE = "ContextualMapRange"
    HUE_SATURATION = "ContextualHueSaturation"
    COMPARE = "ContextualCompare"
    VALUE = "ContextualValue"
    RGB = "ContextualRGB"
    BOOLEAN = "ContextualBoolean"
    INT = "ContextualInt"
    VECTOR = "ContextualVector"
    ROTATION = "ContextualRotation"
    STRING = "ContextualString"

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
    input_keys_map: dict[str | tuple[str, int], tuple[str, int] | str] = field(
        default_factory=dict
    )
    output_keys_map: dict[str, str] = field(default_factory=dict)
    drop_keys: frozenset[str] = frozenset()

    def __post_init__(self):
        if any(v is None for v in self.input_keys_map.values()):
            raise ValueError(
                f"{self.node_type}: input_keys_map must not map keys to None; "
                "use drop_keys to discard a wrapper-pinned key"
            )


# Mapping to map unified version of nodes to context-specific blender versions
# Input keys are (ContextualNode, NodeGroupType) - the unifiied version + the context we need to use it in
# Output is the (NodeType, input map) - tells what specific node to construct, then how to change the inputs for that context, if applicable

CONTEXTUAL_NODE_MAPPING = [
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_COLOR,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeCombineColor",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_COLOR,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeCombineColor",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_COLOR,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeCombineColor",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_COLOR,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeCombineColor",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.SEPARATE_COLOR,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeSeparateColor",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.SEPARATE_COLOR,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeSeparateColor",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.SEPARATE_COLOR,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeSeparateColor",
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
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.GROUP,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeGroup",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.GROUP,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="GeometryNodeGroup",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MIX_RGB,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeMix",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MIX_RGB,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="ShaderNodeMix",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MIX_RGB,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeMixRGB",
        input_keys_map={
            "A": "Color1",
            "B": "Color2",
            "clamp_result": "use_clamp",
        },
        drop_keys=frozenset({"data_type"}),
    ),
    # Compare: geometry uses FunctionNodeCompare (full data_type support incl.
    # INT); other contexts reuse the Math node. LESS_THAN / GREATER_THAN map
    # directly to a Math operation here, while eq/ne/le/ge are lowered earlier to
    # a Math composition (see _lower_compare_outside_geometry in construct_nodes),
    # so this entry only ever realizes the LESS_THAN / GREATER_THAN operations.
    # The A/B -> Value socket remap matches the Math node's two "Value" inputs.
    # These entries precede the MATH ones so that transpiling a shared Math node
    # maps it to MATH, not COMPARE (last duplicate wins).
    NodeContextResolution(
        contextual_node=ContextualNode.COMPARE,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeCompare",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMPARE,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeMath",
        input_keys_map={("A", 0): ("Value", 0), ("B", 0): ("Value", 1)},
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMPARE,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeMath",
        input_keys_map={("A", 0): ("Value", 0), ("B", 0): ("Value", 1)},
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMPARE,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeMath",
        input_keys_map={("A", 0): ("Value", 0), ("B", 0): ("Value", 1)},
    ),
    # Constant float/int (Value) and color (RGB) inputs. ShaderNodeValue is
    # accepted in geometry trees; ShaderNodeRGB is not, so geometry color
    # constants use FunctionNodeInputColor (its color lives on the node `value`
    # property, not an output default). Texture trees have no such node and are
    # intentionally unmapped (they error clearly; use a node-group input).
    NodeContextResolution(
        contextual_node=ContextualNode.VALUE,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeValue",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.VALUE,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="ShaderNodeValue",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.VALUE,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeValue",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.RGB,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeRGB",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.RGB,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeInputColor",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.RGB,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeRGB",
    ),
    # Remaining constant types. Geometry trees use the dedicated
    # FunctionNodeInput* nodes (constant on a node property, see CONSTANT_NODES).
    # Outside geometry: int degrades to the float Value node (shader/compositor
    # sockets are float anyway), vector/rotation lower to a CombineXYZ with the
    # components as socket defaults, and bool/string are intentionally unmapped.
    NodeContextResolution(
        contextual_node=ContextualNode.INT,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeInputInt",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.INT,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeValue",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.INT,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeValue",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.BOOLEAN,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeInputBool",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.VECTOR,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeInputVector",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.VECTOR,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeCombineXYZ",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.VECTOR,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeCombineXYZ",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.ROTATION,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeInputRotation",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.ROTATION,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeCombineXYZ",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.ROTATION,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeCombineXYZ",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.STRING,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="FunctionNodeInputString",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeMath",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="ShaderNodeMath",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeMath",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MATH,
        node_group_type=NodeGroupType.TEXTURE,
        node_type="TextureNodeMath",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COLOR_RAMP,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeValToRGB",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COLOR_RAMP,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="ShaderNodeValToRGB",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COLOR_RAMP,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeValToRGB",
        output_keys_map={"Color": "Image"},
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.VECTOR_CURVE,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeVectorCurve",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.VECTOR_CURVE,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="ShaderNodeVectorCurve",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.VECTOR_CURVE,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeCurveVec",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_XYZ,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeCombineXYZ",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_XYZ,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="ShaderNodeCombineXYZ",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.COMBINE_XYZ,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeCombineXYZ",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MAP_RANGE,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeMapRange",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MAP_RANGE,
        node_group_type=NodeGroupType.GEOMETRY,
        node_type="ShaderNodeMapRange",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.MAP_RANGE,
        node_group_type=NodeGroupType.COMPOSITOR,
        # CompositorNodeMapRange exposes only float Value and use_clamp; it has
        # no interpolation_type and no vector data_type. The wrapper omits
        # those attrs when at default, so setattr only fails (with its own
        # "no attribute" error) when a user actually requested a non-default.
        node_type="CompositorNodeMapRange",
        input_keys_map={"clamp": "use_clamp"},
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.HUE_SATURATION,
        node_group_type=NodeGroupType.SHADER,
        node_type="ShaderNodeHueSaturation",
    ),
    NodeContextResolution(
        contextual_node=ContextualNode.HUE_SATURATION,
        node_group_type=NodeGroupType.COMPOSITOR,
        node_type="CompositorNodeHueSat",
        input_keys_map={"Color": "Image"},
    ),
]


def resolve_contextual_node(
    node: list[NodeContextResolution], group: NodeGroupType
) -> NodeContextResolution:
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

    return item


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
        f"procfunc requires an explicit vector input - node will not default to using texture coordinate or world coordinate like blender. "
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
