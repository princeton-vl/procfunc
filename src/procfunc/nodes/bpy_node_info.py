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


class SocketDType(Enum):
    VALUE = "VALUE"
    INT = "INT"
    VECTOR = "VECTOR"
    FLOAT_COLOR = "FLOAT_COLOR"
    RGBA = "RGBA"
    BOOLEAN = "BOOLEAN"
    ROTATION = "ROTATION"
    OBJECT = "OBJECT"
    SHADER = "SHADER"
    COLLECTION = "COLLECTION"
    MATERIAL = "MATERIAL"
    GEOMETRY = "GEOMETRY"
    STRING = "STRING"


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
}
DATATYPE_TO_SOCKET_DTYPE: dict[NodeDataType, SocketDType] = {
    v: k for k, v in SOCKET_DTYPE_TO_DATATYPE.items()
}

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
}

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
    ]
)

CONSTANT_NODES = {
    "ShaderNodeValue": "DEFAULT_VALUE",
    "FunctionNodeInputBool": "boolean",
    "FunctionNodeInputVector": "vector",
    "FunctionNodeInputColor": "color",
    "FunctionNodeInputInt": "integer",
    # TODO: unsure what the attr names are for these
    # "FunctionNodeInputRotation": "rotation",
    # "FunctionNodeInputSpecialCharacters": "specialcharacters",
    # "FunctionNodeInputString": "string",
    # "FunctionNodeInputActiveCamera": "active_camera",
}
