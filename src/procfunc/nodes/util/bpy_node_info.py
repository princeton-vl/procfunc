"""
The bpy api represents the concept of int vs float vs string vs color vs boolean in many different ways

The different contexts in which these types are distinguished are:
- SocketType: the strings which show up when calling type() on a socket # TODO we may be able to avoid this by just always calling .type
- SocketDType: the strings which show up when calling socket.type
- NodeDataType: TODO specify where exactly these come from

We also care about mapping these types to and from real equivelant python types like int, str, float, Color, Vector, etc.

"""

from enum import Enum

from mathutils import Color, Euler, Quaternion, Vector

from procfunc import types as pt
from procfunc.nodes import types as nt


class NodeDataType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    RGBA = "RGBA"
    FLOAT_VECTOR = "FLOAT_VECTOR"
    FLOAT_VECTOR_2D = "FLOAT2"
    ROTATION = "ROTATION"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    FLOAT_MATRIX = "FLOAT_MATRIX"
    OBJECT = "OBJECT"
    GEOMETRY = "GEOMETRY"
    SHADER = "SHADER"
    COLLECTION = "COLLECTION"
    MATERIAL = "MATERIAL"
    IMAGE = "IMAGE"

    @classmethod
    def from_str(cls, s: str) -> "NodeDataType":
        try:
            return cls(s)
        except ValueError:
            raise ValueError(
                f"{s=} is not a valid {NodeDataType.__name__}, must be one of {list(cls)}"
            )


class SocketType(Enum):
    FLOAT = "NodeSocketFloat"
    INT = "NodeSocketInt"
    VECTOR = "NodeSocketVector"
    ROTATION = "NodeSocketRotation"
    COLOR = "NodeSocketColor"
    BOOLEAN = "NodeSocketBool"
    STRING = "NodeSocketString"
    GEOMETRY = "NodeSocketGeometry"
    SHADER = "NodeSocketShader"
    OBJECT = "NodeSocketObject"
    COLLECTION = "NodeSocketCollection"
    TEXTURE = "NodeSocketTexture"
    MATERIAL = "NodeSocketMaterial"
    MATRIX = "NodeSocketMatrix"
    IMAGE = "NodeSocketImage"


class SocketDType(Enum):
    VALUE = "VALUE"
    INT = "INT"
    VECTOR = "VECTOR"
    FLOAT_COLOR = "FLOAT_COLOR"
    RGBA = "RGBA"
    BOOLEAN = "BOOLEAN"
    ROTATION = "ROTATION"
    MATRIX = "MATRIX"
    OBJECT = "OBJECT"
    SHADER = "SHADER"
    COLLECTION = "COLLECTION"
    MATERIAL = "MATERIAL"
    GEOMETRY = "GEOMETRY"
    STRING = "STRING"
    IMAGE = "IMAGE"


class AttributeType(Enum):
    """bpy `data_type` strings on attribute nodes; differs from NodeDataType for
    color/rotation/matrix. Members with no NodeDataType equivalent are omitted."""

    FLOAT = "FLOAT"
    INT = "INT"
    FLOAT_VECTOR = "FLOAT_VECTOR"
    FLOAT_COLOR = "FLOAT_COLOR"
    FLOAT2 = "FLOAT2"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    QUATERNION = "QUATERNION"
    FLOAT4X4 = "FLOAT4X4"


# Map socket types to data types (from node_info.py)
SOCKET_DTYPE_TO_DATATYPE: dict[SocketDType, NodeDataType] = {
    SocketDType.VALUE: NodeDataType.FLOAT,
    SocketDType.INT: NodeDataType.INT,
    SocketDType.VECTOR: NodeDataType.FLOAT_VECTOR,
    SocketDType.FLOAT_COLOR: NodeDataType.RGBA,
    SocketDType.RGBA: NodeDataType.RGBA,
    SocketDType.BOOLEAN: NodeDataType.BOOLEAN,
    SocketDType.ROTATION: NodeDataType.ROTATION,
    SocketDType.OBJECT: NodeDataType.OBJECT,
    SocketDType.SHADER: NodeDataType.SHADER,
    SocketDType.COLLECTION: NodeDataType.COLLECTION,
    SocketDType.MATERIAL: NodeDataType.MATERIAL,
    SocketDType.GEOMETRY: NodeDataType.GEOMETRY,
    SocketDType.STRING: NodeDataType.STRING,
    SocketDType.IMAGE: NodeDataType.IMAGE,
    SocketDType.MATRIX: NodeDataType.FLOAT_MATRIX,
}
DATATYPE_TO_SOCKET_DTYPE: dict[NodeDataType, SocketDType] = {
    v: k for k, v in SOCKET_DTYPE_TO_DATATYPE.items()
}

ATTRIBUTE_TYPE_TO_DATATYPE: dict[AttributeType, NodeDataType] = {
    AttributeType.FLOAT: NodeDataType.FLOAT,
    AttributeType.INT: NodeDataType.INT,
    AttributeType.FLOAT_VECTOR: NodeDataType.FLOAT_VECTOR,
    AttributeType.FLOAT_COLOR: NodeDataType.RGBA,
    AttributeType.FLOAT2: NodeDataType.FLOAT_VECTOR_2D,
    AttributeType.STRING: NodeDataType.STRING,
    AttributeType.BOOLEAN: NodeDataType.BOOLEAN,
    AttributeType.QUATERNION: NodeDataType.ROTATION,
    AttributeType.FLOAT4X4: NodeDataType.FLOAT_MATRIX,
}
DATATYPE_TO_ATTRIBUTE_TYPE: dict[NodeDataType, AttributeType] = {
    v: k for k, v in ATTRIBUTE_TYPE_TO_DATATYPE.items()
}


def datatype_from_bpy_str(s: str) -> NodeDataType:
    """Resolve a bpy `data_type`/`input_type` string to the canonical NodeDataType,
    normalizing per-family spellings (e.g. matrix is 'FLOAT4X4' on attribute nodes,
    'MATRIX' on Switch). The conventions are non-overlapping."""
    try:
        return NodeDataType(s)
    except ValueError:
        pass
    try:
        return SOCKET_DTYPE_TO_DATATYPE[SocketDType(s)]
    except (ValueError, KeyError):
        pass
    try:
        return ATTRIBUTE_TYPE_TO_DATATYPE[AttributeType(s)]
    except (ValueError, KeyError):
        pass
    raise ValueError(
        f"{s=} is not a recognized bpy data_type in any known naming convention"
    )


SOCKET_CLASS_TO_DATATYPE: dict[str, NodeDataType] = {
    SocketType.FLOAT.value: NodeDataType.FLOAT,
    SocketType.INT.value: NodeDataType.INT,
    SocketType.VECTOR.value: NodeDataType.FLOAT_VECTOR,
    SocketType.COLOR.value: NodeDataType.RGBA,
    SocketType.BOOLEAN.value: NodeDataType.BOOLEAN,
    SocketType.ROTATION.value: NodeDataType.ROTATION,
    SocketType.STRING.value: NodeDataType.STRING,
    SocketType.GEOMETRY.value: NodeDataType.GEOMETRY,
    SocketType.SHADER.value: NodeDataType.SHADER,
    SocketType.OBJECT.value: NodeDataType.OBJECT,
    SocketType.COLLECTION.value: NodeDataType.COLLECTION,
    SocketType.MATERIAL.value: NodeDataType.MATERIAL,
    SocketType.MATRIX.value: NodeDataType.FLOAT_MATRIX,
    SocketType.IMAGE.value: NodeDataType.IMAGE,
}
DATATYPE_TO_SOCKET_CLASS: dict[NodeDataType, SocketType] = {
    v: SocketType(k) for k, v in SOCKET_CLASS_TO_DATATYPE.items()
}

NODEGROUPTYPE_TO_INSTANCE_NODE = {
    "GeometryNodeTree": "GeometryNodeGroup",
    "ShaderNodeTree": "ShaderNodeGroup",
    "CompositorNodeTree": "CompositorNodeGroup",
    "TextureNodeTree": "TextureNodeGroup",
}

# Compositor nodes that poll False inside a standalone node group: they resolve
# render data and so must live on a scene's compositing node tree. A compositor
# graph containing any of these is constructed directly on the active scene's
# node_tree (bpy.context.scene.node_tree), replacing its previous contents,
# rather than via bpy.data.node_groups.new.
SCENE_BOUND_NODE_TYPES = frozenset(
    {"CompositorNodeRLayers", "CompositorNodeCryptomatteV2"}
)

PYTHON_TYPE_TO_SOCKET_TYPE = {
    int: SocketType.INT,
    float: SocketType.FLOAT,
    Color: SocketType.COLOR,
    Vector: SocketType.VECTOR,
    Euler: SocketType.ROTATION,
    Quaternion: SocketType.ROTATION,
    str: SocketType.STRING,
    bool: SocketType.BOOLEAN,
    pt.MeshObject: SocketType.GEOMETRY,
    pt.CurveObject: SocketType.GEOMETRY,
    pt.VolumeObject: SocketType.GEOMETRY,
    nt.Geometry: SocketType.GEOMETRY,
    pt.Collection: SocketType.COLLECTION,
    pt.Material: SocketType.MATERIAL,
    nt.Shader: SocketType.SHADER,
    pt.Matrix: SocketType.MATRIX,
    pt.Object: SocketType.OBJECT,
    pt.Image: SocketType.IMAGE,
}
SOCKET_TYPE_TO_PYTHON_TYPE = {
    SocketType.FLOAT: float,
    SocketType.INT: int,
    SocketType.VECTOR: pt.Vector,
    SocketType.ROTATION: pt.Euler,
    SocketType.COLOR: pt.Color,
    SocketType.BOOLEAN: bool,
    SocketType.STRING: str,
    SocketType.GEOMETRY: None,  # TODO: infer which type of geometry it is? currently we make no annotation
    SocketType.COLLECTION: pt.Collection,
    SocketType.MATERIAL: pt.Material,
    SocketType.SHADER: nt.Shader,
    SocketType.OBJECT: pt.Object,
    SocketType.TEXTURE: pt.Texture,
    SocketType.MATRIX: pt.Matrix,
    SocketType.IMAGE: pt.Image,
}


def value_type_to_socket_type(py_type: type) -> "SocketType | None":
    """PYTHON_TYPE_TO_SOCKET_TYPE lookup honoring subclasses (e.g. an Object subclass resolves to its registered base)."""
    for base in py_type.__mro__:
        if base in PYTHON_TYPE_TO_SOCKET_TYPE:
            return PYTHON_TYPE_TO_SOCKET_TYPE[base]
    return None


# Socket types that can be implicitly converted between each other
COMPATIBLE_SCALARLIKE_SOCKETTYPES = {
    SocketType.FLOAT.value,
    SocketType.INT.value,
    SocketType.BOOLEAN.value,
    SocketType.VECTOR.value,
    SocketType.COLOR.value,
}

COMPATIBLE_VECTORLIKE_SOCKETTYPES = {
    SocketType.VECTOR.value,
    SocketType.ROTATION.value,
}


def are_socket_types_compatible(output_type: str, input_type: str) -> bool:
    """Check if two socket types are compatible for connection."""
    if output_type == input_type:
        return True

    if all(t in COMPATIBLE_SCALARLIKE_SOCKETTYPES for t in (output_type, input_type)):
        return True
    if all(t in COMPATIBLE_VECTORLIKE_SOCKETTYPES for t in (output_type, input_type)):
        return True
    return False


DATATYPE_TO_PY_TYPE = {
    NodeDataType.INT: int,
    NodeDataType.FLOAT: float,
    NodeDataType.RGBA: pt.Color,
    NodeDataType.FLOAT_VECTOR: pt.Vector,
    NodeDataType.STRING: str,
    NodeDataType.BOOLEAN: bool,
    NodeDataType.FLOAT_MATRIX: pt.Matrix,
    NodeDataType.OBJECT: pt.Object,
    NodeDataType.GEOMETRY: pt.MeshObject,
    NodeDataType.ROTATION: pt.Euler,
    NodeDataType.SHADER: nt.Shader,
    NodeDataType.COLLECTION: pt.Collection,
    NodeDataType.MATERIAL: pt.Material,
}


class NodeGroupType(Enum):
    GEOMETRY = "GeometryNodeTree"
    SHADER = "ShaderNodeTree"
    COMPOSITOR = "CompositorNodeTree"
    TEXTURE = "TextureNodeTree"


UNIVERSAL_ATTR_NAMES = set(
    [
        "show_preview",
        "__module__",
        "is_registered_node_type",
        "bl_rna",
        "poll",
        "name",
        "internal_links",
        "dimensions",
        "parent",
        "bl_width_max",
        "label",
        "input_template",
        "show_texture",
        "rna_type",
        "width_hidden",
        "show_options",
        "location",
        "outputs",
        "use_custom_color",
        "__doc__",
        "width",
        "bl_width_default",
        "inputs",
        "bl_idname",
        "socket_value_update",
        "bl_width_min",
        "color",
        "bl_height_max",
        "__slots__",
        "select",
        "mute",
        "bl_height_default",
        "bl_static_type",
        "bl_height_min",
        "height",
        "bl_label",
        "bl_icon",
        "hide",
        "output_template",
        "poll_instance",
        "draw_buttons_ext",
        "type",
        "bl_description",
        "draw_buttons",
        "update",
    ]
)

SPECIAL_CASE_ATTR_NAMES = set(
    [
        "color_ramp",
        "mapping",
        "texture_mapping",
        "color_mapping",
        "image_user",
        "interface",
        "node_tree",
        "tag_need_exec",
        "index_switch_items",
    ]
)

CONSTANT_NODES = {
    "FunctionNodeInputBool": "boolean",
    "FunctionNodeInputVector": "vector",
    "FunctionNodeInputColor": "value",
    "FunctionNodeInputInt": "integer",
    "FunctionNodeInputRotation": "rotation_euler",
    "FunctionNodeInputString": "string",
}
