
###MODULE procfunc.nodes.math


def clamp(
    value: pf.SocketOrVal[float] = 1.0,
    min: pf.SocketOrVal[float] = 0.0,
    max: pf.SocketOrVal[float] = 1.0,
    clamp_type: str = "MINMAX",
) -> pf.ProcNode[float]:
    pass
# Math Nodes


# Basic Math Operations
def add(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def subtract(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def multiply(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def multiply_add(
    a: pf.SocketOrVal[float] = 0.5,
    b: pf.SocketOrVal[float] = 0.5,
    addend: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def divide(
    numerator: pf.SocketOrVal[float] = 0.5, denominator: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def power(
    base: pf.SocketOrVal[float] = 0.5, exponent: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def logarithm(
    value: pf.SocketOrVal[float] = 0.5, base: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def sqrt(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def inverse_sqrt(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def absolute(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def exponent(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
# Comparison Operations
def minimum(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def maximum(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def less_than(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def greater_than(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def sign(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def compare(
    a: pf.SocketOrVal[float] = 0.5,
    b: pf.SocketOrVal[float] = 0.5,
    epsilon: pf.SocketOrVal[float] = 0.001,
) -> pf.ProcNode[float]:
    pass
def smooth_minimum(
    a: pf.SocketOrVal[float] = 0.5,
    b: pf.SocketOrVal[float] = 0.5,
    distance: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def smooth_maximum(
    a: pf.SocketOrVal[float] = 0.5,
    b: pf.SocketOrVal[float] = 0.5,
    distance: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def round(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def floor(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def ceil(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def truncate(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def fraction(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def modulo(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def floor_mod(
    a: pf.SocketOrVal[float] = 0.5, b: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def wrap(
    value: pf.SocketOrVal[float] = 0.5,
    max_val: pf.SocketOrVal[float] = 1.0,
    min_val: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def snap(
    value: pf.SocketOrVal[float] = 0.5, increment: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[float]:
    pass
def pingpong(
    value: pf.SocketOrVal[float] = 0.5, scale: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[float]:
    pass
# Trigonometric Operations
def sin(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def cos(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def tan(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def asin(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def acos(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def atan(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def atan2(
    y: pf.SocketOrVal[float] = 0.5, x: pf.SocketOrVal[float] = 0.5
) -> pf.ProcNode[float]:
    pass
def sinh(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def cosh(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def tanh(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
# Conversion Operations
def deg_to_rad(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
def rad_to_deg(value: pf.SocketOrVal[float] = 0.5) -> pf.ProcNode[float]:
    pass
# Vector Math Operations
def vector_add(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_subtract(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_multiply(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_multiply_add(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    addend: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_divide(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_cross_product(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_project(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    onto: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[float]:
    pass
def vector_reflect(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_refract(
    incident: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    ior: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_faceforward(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    surface: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_dot_product(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_distance(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_length(vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0)) -> pf.ProcNode[float]:
    pass
def vector_scale(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0), scale: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_normalize(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_wrap(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    max_val: pf.SocketOrVal[mathutils.Vector] = (1, 1, 1),
    min_val: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_snap(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (1, 1, 1),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_floor(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_ceil(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_modulo(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (1, 1, 1),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_fraction(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_round(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_truncate(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_absolute(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_minimum(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_maximum(
    a: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_sine(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_cosine(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_tangent(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_rotate_axis_angle(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    center: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    axis: pf.SocketOrVal[mathutils.Vector] = (0, 0, 1),
    angle: pf.SocketOrVal[float] = 0.0,
    invert: bool = False,
) -> pf.ProcNode[mathutils.Vector]:
    pass
def vector_rotate_euler(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    center: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    rotation: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    invert: bool = False,
) -> pf.ProcNode[mathutils.Vector]:
    pass
# NOTE: mode XYZ have been dropped. transpiler specialcases will map these back to vector_rotate_euler calls.


def vector_transform(
    vector: pf.SocketOrVal[mathutils.Vector] = (0.5, 0.5, 0.5),
    convert_from: str = "WORLD",
    convert_to: str = "OBJECT",
    vector_type: str = "VECTOR",
) -> pf.ProcNode[mathutils.Vector]:
    pass

###MODULE procfunc.nodes.shader


def add_shader(
    shader_0: pf.ProcNode[pf.Shader] | None = None,
    shader_1: pf.ProcNode[pf.Shader] | None = None,
) -> pf.ProcNode:
    pass
class AmbientOcclusionResult(NamedTuple):
    color: pf.ProcNode[mathutils.Color]
    ao: pf.ProcNode[float]

def ambient_occlusion(
    color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    distance: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    inside: bool = False,
    only_local: bool = False,
    samples: int = 16,
) -> AmbientOcclusionResult:
    pass
class AttributeResult(NamedTuple):
    color: pf.ProcNode[mathutils.Color]
    vector: pf.ProcNode[mathutils.Vector]
    fac: pf.ProcNode[float]
    alpha: pf.ProcNode[float]


def attribute(
    attribute_name: str = "",
    attribute_type: Literal[
        "GEOMETRY", "OBJECT", "INSTANCER", "VIEW_LAYER"
    ] = "GEOMETRY",
) -> AttributeResult:
    pass
def background(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    strength: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode:
    pass
def bevel(
    radius: pf.SocketOrVal[float] = 0.05,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    samples: int = 4,
) -> pf.ProcNode:
    pass
def blackbody(temperature: pf.SocketOrVal[float] = 1500.0) -> pf.ProcNode:
    pass
def bright_contrast(
    color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    bright: pf.SocketOrVal[float] = 0.0,
    contrast: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode:
    pass
def anisotropic_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.5,
    anisotropy: pf.SocketOrVal[float] = 0.0,
    rotation: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    tangent: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    distribution: Literal[
        "BECKMANN", "GGX", "ASHIKHMIN_SHIRLEY", "MULTI_GGX"
    ] = "MULTI_GGX",
) -> pf.ProcNode:
    pass
def diffuse_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
) -> pf.ProcNode:
    pass
def glass_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.5,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    distribution: Literal["BECKMANN", "GGX", "MULTI_GGX"] = "MULTI_GGX",
) -> pf.ProcNode:
    pass
def hair_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    offset: pf.SocketOrVal[float] = 0.0,
    roughness_u: pf.SocketOrVal[float] = 0.1,
    roughness_v: pf.SocketOrVal[float] = 1.0,
    tangent: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    component: Literal["Reflection", "Transmission"] = "Reflection",
) -> pf.ProcNode:
    pass
def principled_hair_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (0.017513, 0.005763, 0.002059, 1),
    roughness: pf.SocketOrVal[float] = 0.3,
    radial_roughness: pf.SocketOrVal[float] = 0.3,
    coat: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.55,
    offset: pf.SocketOrVal[float] = 0.034907,
    random_roughness: pf.SocketOrVal[float] = 0.0,
    random: pf.SocketOrVal[float] = 0.0,
    model: Literal["CHIANG", "HUANG"] = "CHIANG",
    parametrization: Literal["ABSORPTION", "MELANIN", "COLOR"] = "COLOR",
) -> pf.ProcNode:
    pass
TSubsurfaceMethod = Literal["BURLEY", "RANDOM_WALK", "RANDOM_WALK_SKIN"]


def principled_bsdf(
    base_color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    metallic: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    ior: pf.SocketOrVal[float] = 1.5,
    alpha: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[mathutils.Vector] = (0.0, 0.0, 0.0),

    # subsurface scattering
    subsurface_method: TSubsurfaceMethod = "RANDOM_WALK",
    subsurface_weight: pf.SocketOrVal[float] = 0.0,
    subsurface_radius: pf.SocketOrVal[mathutils.Vector] = (1, 0.2, 0.1),
    subsurface_scale: pf.SocketOrVal[float] = 0.05,
    subsurface_ior: pf.SocketOrVal[float] | None = None,
    subsurface_anisotropy: pf.SocketOrVal[float] | None = None,

    # specular
    distribution: Literal["GGX", "MULTI_GGX"] = "MULTI_GGX",
    specular_ior_level: pf.SocketOrVal[float] = 0.5,
    specular_tint: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    anisotropic: pf.SocketOrVal[float] = 0.0,
    anisotropic_rotation: pf.SocketOrVal[float] = 0.0,
    tangent: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),

    transmission_weight: pf.SocketOrVal[float] = 0.0,
    
    coat_weight: pf.SocketOrVal[float] = 0.0,
    coat_roughness: pf.SocketOrVal[float] = 0.03,
    coat_ior: pf.SocketOrVal[float] = 1.5,
    coat_tint: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    coat_normal: pf.SocketOrVal[mathutils.Vector] = (0.0, 0.0, 0.0),
    
    sheen_weight: pf.SocketOrVal[float] = 0.0,
    sheen_roughness: pf.SocketOrVal[float] = 0.5,
    sheen_tint: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    
    emission_color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    emission_strength: pf.SocketOrVal[float] = 0.0,
    
    thin_film_thickness: pf.SocketOrVal[float] = 0.0,
    thin_film_ior: pf.SocketOrVal[float] = 1.33,
) -> pf.ProcNode:
    pass
def ray_portal_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    position: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    direction: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
) -> pf.ProcNode:
    pass
def refraction_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.45,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    distribution: Literal["BECKMANN", "GGX"] = "BECKMANN",
) -> pf.ProcNode:
    pass
def sheen_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.5,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    distribution: Literal["ASHIKHMIN", "MICROFIBER"] = "MICROFIBER",
) -> pf.ProcNode:
    pass
def toon_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    size: pf.SocketOrVal[float] = 0.5,
    smooth: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    component: str = "DIFFUSE",
) -> pf.ProcNode:
    pass
def translucent_bsdf(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    normal: pf.SocketOrVal[mathutils.Vector] = None,
) -> pf.ProcNode:
    pass
def transparent_bsdf(color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1)) -> pf.ProcNode:
    pass
def bump(
    strength: pf.SocketOrVal[float] = 1.0,
    distance: pf.SocketOrVal[float] = 1.0,
    height: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    invert: bool = False,
) -> pf.ProcNode:
    pass
class CameraDataResult(NamedTuple):
    view_vector: pf.ProcNode[mathutils.Vector]
    view_z_depth: pf.ProcNode[float]
    view_distance: pf.ProcNode[float]


def camera_data() -> CameraDataResult:
    pass
def displacement(
    height: pf.SocketOrVal[float] = 0.0,
    midlevel: pf.SocketOrVal[float] = 0.5,
    scale: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
) -> pf.ProcNode[mathutils.Vector]:
    pass
def eevee_specular(
    base_color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    specular: pf.SocketOrVal[mathutils.Color] = (0.03, 0.03, 0.03, 1),
    roughness: pf.SocketOrVal[float] = 0.2,
    emissive_color: pf.SocketOrVal[mathutils.Color] = (0, 0, 0, 1),
    transparency: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[mathutils.Vector] = None,
    clear_coat: pf.SocketOrVal[float] = 0.0,
    clear_coat_roughness: pf.SocketOrVal[float] = 0.0,
    clear_coat_normal: pf.SocketOrVal[mathutils.Vector] = None,
) -> pf.ProcNode:
    pass
def emission(
    color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    strength: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode:
    pass
def fresnel(
    ior: pf.SocketOrVal[float] = 1.5, normal: pf.SocketOrVal[mathutils.Vector] = None
) -> pf.ProcNode:
    pass
def gamma(
    color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1), gamma: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode:
    pass
class HairInfoResult(NamedTuple):
    is_strand: pf.ProcNode[float]
    intercept: pf.ProcNode[float]
    length: pf.ProcNode[float]
    thickness: pf.ProcNode[float]
    tangent_normal: pf.ProcNode[mathutils.Vector]
    random: pf.ProcNode[float]


def hair_info() -> HairInfoResult:
    pass
def holdout() -> pf.ProcNode:
    pass
def hue_saturation(
    hue: pf.SocketOrVal[float] = 0.5,
    saturation: pf.SocketOrVal[float] = 1.0,
    value: pf.SocketOrVal[float] = 1.0,
    fac: pf.SocketOrVal[float] = 1.0,
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
) -> pf.ProcNode:
    pass
def invert(
    fac: pf.SocketOrVal[float] = 1.0, color: pf.SocketOrVal[mathutils.Color] = (0, 0, 0, 1)
) -> pf.ProcNode:
    pass
class LayerWeightResult(NamedTuple):
    fresnel: pf.ProcNode[float]
    facing: pf.ProcNode[float]


def layer_weight(
    blend: pf.SocketOrVal[float] = 0.5, 
    normal: pf.SocketOrVal[mathutils.Vector] = (0.0, 0.0, 0.0)
) -> LayerWeightResult:
    pass
class LightFalloffResult(NamedTuple):
    quadratic: pf.ProcNode[float]
    linear: pf.ProcNode[float]
    constant: pf.ProcNode[float]


def light_falloff(
    strength: pf.SocketOrVal[float] = 100.0, smooth: pf.SocketOrVal[float] = 0.0
) -> LightFalloffResult:
    pass
class LightPathResult(NamedTuple):
    is_camera_ray: pf.ProcNode[float]
    is_shadow_ray: pf.ProcNode[float]
    is_diffuse_ray: pf.ProcNode[float]
    is_glossy_ray: pf.ProcNode[float]
    is_singular_ray: pf.ProcNode[float]
    is_reflection_ray: pf.ProcNode[float]
    is_transmission_ray: pf.ProcNode[float]
    ray_length: pf.ProcNode[float]
    ray_depth: pf.ProcNode[float]
    diffuse_depth: pf.ProcNode[float]
    glossy_depth: pf.ProcNode[float]
    transparent_depth: pf.ProcNode[float]
    transmission_depth: pf.ProcNode[float]


def light_path() -> LightPathResult:
    pass
def mapping(
    vector: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    location: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    rotation: pf.SocketOrVal[mathutils.Vector] = (0, 0, 0),
    scale: pf.SocketOrVal[mathutils.Vector] = (1, 1, 1),
    vector_type: Literal["POINT", "TEXTURE", "VECTOR", "NORMAL"] = "POINT",
) -> pf.ProcNode:
    pass
def mix_shader(
    factor: pf.SocketOrVal[float] = 0.5,
    a: pf.ProcNode[pf.Shader] | None = None,
    b: pf.ProcNode[pf.Shader] | None = None,
) -> pf.ProcNode[pf.Shader]:
    pass
class NormalResult(NamedTuple):
    normal: pf.ProcNode[mathutils.Vector]
    dot: pf.ProcNode[float]


def normal(normal: pf.SocketOrVal[mathutils.Vector] = (0, 0, 1)) -> NormalResult:
    pass
def normal_map(
    strength: pf.SocketOrVal[float] = 1.0,
    color: pf.SocketOrVal[mathutils.Color] = (0.5, 0.5, 1, 1),
    space: Literal["TANGENT", "OBJECT", "WORLD", "BLENDER_OBJECT", "BLENDER_WORLD"] = "TANGENT",
    uv_map: str = "",
) -> pf.ProcNode:
    pass
class ObjectInfoResult(NamedTuple):
    location: pf.ProcNode[mathutils.Vector]
    color: pf.ProcNode[mathutils.Color]
    alpha: pf.ProcNode[float]
    object_index: pf.ProcNode[int]
    material_index: pf.ProcNode[int]
    random: pf.ProcNode[float]


def object_info() -> ObjectInfoResult:
    pass
# NOTE: procfunc expects python code to `return LightResult()` instead



class ParticleInfoResult(NamedTuple):
    index: pf.ProcNode[int]
    random: pf.ProcNode[float]
    age: pf.ProcNode[float]
    lifetime: pf.ProcNode[float]
    location: pf.ProcNode[mathutils.Vector]
    size: pf.ProcNode[float]
    velocity: pf.ProcNode[mathutils.Vector]
    angular_velocity: pf.ProcNode[mathutils.Vector]


def particle_info() -> ParticleInfoResult:
    pass
class PointInfoResult(NamedTuple):
    position: pf.ProcNode[mathutils.Vector]
    radius: pf.ProcNode[float]
    random: pf.ProcNode[float]


def point_info() -> PointInfoResult:
    pass
def rgb() -> pf.ProcNode:
    pass
def rgb_to_bw(color: pf.SocketOrVal[mathutils.Color] = (0.5, 0.5, 0.5, 1)) -> pf.ProcNode:
    pass
def script(
    bytecode: str = "",
    bytecode_hash: str = "",
    filepath: str = "",
    mode: str = "INTERNAL",
    script: Any = None,
    use_auto_update: bool = False,
) -> pf.ProcNode:
    pass
def shader_to_rgb(shader: pf.ProcNode[pf.Shader] | None = None) -> pf.ProcNode:
    pass
def squeeze(
    value: pf.SocketOrVal[float] = 0.0,
    width: pf.SocketOrVal[float] = 1.0,
    center: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode:
    pass
def subsurface_scattering(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    scale: pf.SocketOrVal[float] = 0.05,
    radius: pf.SocketOrVal[mathutils.Vector] = (1, 0.2, 0.1),
    ior: pf.SocketOrVal[float] = 1.4,
    roughness: pf.SocketOrVal[float] = 1.0,
    anisotropy: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[mathutils.Vector] = (0.0, 0.0, 0.0),
    falloff: Literal['BURLEY', 'RANDOM_WALK', 'RANDOM_WALK_SKIN'] = "RANDOM_WALK",
) -> pf.ProcNode:
    pass
def tangent(
    axis: Literal["X", "Y", "Z"] = "Z", 
    direction_type: Literal["RADIAL", "UV_MAP"] = "RADIAL", 
    uv_map: str = ""
) -> pf.ProcNode:
    pass
class TextureResult(NamedTuple):
    fac: pf.ProcNode[float]
    color: pf.ProcNode[mathutils.Color]


def brick(
    vector: pf.SocketOrVal[mathutils.Vector],
    color1: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    color2: pf.SocketOrVal[mathutils.Color] = (0.2, 0.2, 0.2, 1),
    mortar: pf.SocketOrVal[mathutils.Color] = (0, 0, 0, 1),
    scale: pf.SocketOrVal[float] = 5.0,
    mortar_size: pf.SocketOrVal[float] = 0.02,
    mortar_smooth: pf.SocketOrVal[float] = 0.1,
    bias: pf.SocketOrVal[float] = 0.0,
    brick_width: pf.SocketOrVal[float] = 0.5,
    row_height: pf.SocketOrVal[float] = 0.25,
    offset: float = 0.5,
    offset_frequency: int = 2,
    squash: float = 1.0,
    squash_frequency: int = 2,
) -> TextureResult:
    pass
def checker(
    vector: pf.SocketOrVal[mathutils.Vector],
    color1: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    color2: pf.SocketOrVal[mathutils.Color] = (0.2, 0.2, 0.2, 1),
    scale: pf.SocketOrVal[float] = 5.0,
) -> TextureResult:
    pass
class CoordResult(NamedTuple):
    generated: pf.ProcNode[mathutils.Vector]
    normal: pf.ProcNode[mathutils.Vector]
    uv: pf.ProcNode[mathutils.Vector]
    object: pf.ProcNode[mathutils.Vector]
    camera: pf.ProcNode[mathutils.Vector]
    window: pf.ProcNode[mathutils.Vector]


def coord(from_instancer: bool = False, object: Any = None) -> CoordResult:
    pass
class GeometryResult(NamedTuple):
    position: pf.ProcNode[mathutils.Vector]
    normal: pf.ProcNode[mathutils.Vector]
    tangent: pf.ProcNode[mathutils.Vector]
    true_normal: pf.ProcNode[mathutils.Vector]
    incoming: pf.ProcNode[mathutils.Vector]
    parametric: pf.ProcNode[mathutils.Vector]
    backfacing: pf.ProcNode[float]
    pointiness: pf.ProcNode[float]
    random_per_island: pf.ProcNode[float]


def geometry() -> GeometryResult:
    pass
TTextureInterpolationType = Literal["Linear", "Closest", "Cubic", "Smart"] # TODO

def environment(
    vector: pf.SocketOrVal[mathutils.Vector],
    image: Any = None,
    interpolation: TTextureInterpolationType = "Linear",
    projection: Literal["EQUIRECTANGULAR", "MIRROR_BALL"] = "EQUIRECTANGULAR",
) -> pf.ProcNode[mathutils.Color]:
    pass
def gradient(
    vector: pf.SocketOrVal[mathutils.Vector],
    gradient_type: Literal['LINEAR', 'QUADRATIC', 'EASING', 'DIAGONAL', 'SPHERICAL', 'QUADRATIC_SPHERE', 'RADIAL'] = "LINEAR"
) -> TextureResult:
    pass
def ies(
    vector: pf.SocketOrVal[mathutils.Vector],
    strength: pf.SocketOrVal[float] = 1.0,
    filepath: str = "",
    ies: Any = None,
    mode: Literal["INTERNAL", "EXTERNAL"] = "INTERNAL",
) -> pf.ProcNode:
    pass
def image(
    vector: pf.SocketOrVal[mathutils.Vector],
    extension: Literal["REPEAT", "EXTEND", "CLIP", "MIRROR"] = "REPEAT",
    image: Any = None,
    interpolation: TTextureInterpolationType = "Linear",
    projection: Literal["FLAT", "BOX", "SPHERE", "CUBE"] = "FLAT",
    projection_blend: float = 0.0,
) -> TextureResult:
    pass
def magic(
    vector: pf.SocketOrVal[mathutils.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    distortion: pf.SocketOrVal[float] = 1.0,
    turbulence_depth: int = 2,
) -> TextureResult:
    pass
TNoiseType = Literal[
    "MULTIFRACTAL",
    "FBM",
    "RIDGED_MULTIFRACTAL",
    "HYBRID_MULTIFRACTAL",
    "HETERO_TERRAIN",
]
TNoiseDimensions = Literal["1D", "2D", "3D", "4D"]
def noise(
    vector: pf.SocketOrVal[mathutils.Vector] = (0.0, 0.0, 0.0),
    scale: pf.SocketOrVal[float] = 5.0,
    detail: pf.SocketOrVal[float] = 2.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    lacunarity: pf.SocketOrVal[float] = 2.0,
    offset: pf.SocketOrVal[float] = 0.0,
    gain: pf.SocketOrVal[float] = 1.0,
    distortion: pf.SocketOrVal[float] = 0.0,
    noise_dimensions: TNoiseDimensions = "3D",
    noise_type: TNoiseType = "FBM",
    normalize: bool = True,
    w: pf.SocketOrVal[float] = 0.0,
) -> TextureResult:
    pass
class PointDensityResult(NamedTuple):
    color: pf.ProcNode[mathutils.Color]
    density: pf.ProcNode[float]


def point_density(
    vector: pf.SocketOrVal[mathutils.Vector],
    interpolation: Literal["Closest", "Linear", "Cubic"] = "Linear",
    object: Any = None,
    particle_color_source: Literal["PARTICLE_AGE", "PARTICLE_SPEED", "PARTICLE_VELOCITY"] = "PARTICLE_AGE",
    particle_system: Any = None,
    point_source: Literal["OBJECT", "PARTICLE_SYSTEM"] = "PARTICLE_SYSTEM",
    radius: float = 0.3,
    resolution: int = 100,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
    vertex_attribute_name: str = "",
    vertex_color_source: Literal["VERTEX_COLOR", "VERTEX_NORMAL", "VERTEX_WEIGHT"] = "VERTEX_COLOR",
) -> PointDensityResult:
    pass
def sky(
    air_density: float = 1.0,
    altitude: float = 0.0,
    dust_density: float = 1.0,
    ground_albedo: float = 0.3,
    ozone_density: float = 1.0,
    sky_type: Literal["NISHITA", "HOSEK_WILKIE", "PREETHAM"] = "NISHITA",
    sun_direction: tuple = (0.0, 0.0, 1.0),
    sun_disc: bool = True,
    sun_elevation: float = 0.261799,
    sun_intensity: float = 1.0,
    sun_rotation: float = 0.0,
    sun_size: float = 0.009512,
    turbidity: float = 2.2,
) -> pf.ProcNode[mathutils.Color]:
    pass
class VoronoiResult(NamedTuple):
    color: pf.ProcNode[mathutils.Color]
    distance: pf.ProcNode[float]
    position: pf.ProcNode[mathutils.Vector]
    w: pf.ProcNode[float] | None


TDistanceMetric = Literal["EUCLIDEAN", "MANHATTAN", "CHEBYCHEV", "MINKOWSKI"]


def voronoi(
    vector: pf.SocketOrVal[mathutils.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    detail: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    lacunarity: pf.SocketOrVal[float] = 2.0,
    randomness: pf.SocketOrVal[float] = 1.0,
    exponent: pf.SocketOrVal[float] = 0.0,
    distance: TDistanceMetric = "EUCLIDEAN",
    feature: Literal["F1", "F2"] = "F1",
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = 0.0,
) -> VoronoiResult:
    pass
def voronoi_distance(
    vector: pf.SocketOrVal[mathutils.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    detail: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    lacunarity: pf.SocketOrVal[float] = 2.0,
    randomness: pf.SocketOrVal[float] = 1.0,
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def voronoi_smooth_f1(
    vector: pf.SocketOrVal[mathutils.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    detail: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    lacunarity: pf.SocketOrVal[float] = 2.0,
    smoothness: pf.SocketOrVal[float] = 0.5,
    randomness: pf.SocketOrVal[float] = 1.0,
    distance: TDistanceMetric = "EUCLIDEAN",
    normalize: bool = False,
    voronoi_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = 0.0,
) -> VoronoiResult:
    pass
def voronoi_n_spheres_distance(
    vector: pf.SocketOrVal[mathutils.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    randomness: pf.SocketOrVal[float] = 1.0,
    normalize: bool = False,
) -> pf.ProcNode[float]:
    pass
def wave(
    vector: pf.SocketOrVal[mathutils.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    distortion: pf.SocketOrVal[float] = 0.0,
    detail: pf.SocketOrVal[float] = 2.0,
    detail_scale: pf.SocketOrVal[float] = 1.0,
    detail_roughness: pf.SocketOrVal[float] = 0.5,
    phase_offset: pf.SocketOrVal[float] = 0.0,
    bands_direction: Literal["X", "Y", "Z", "SPHERICAL"] = "X",
    rings_direction: Literal["X", "Y", "Z", "SPHERICAL"] = "X",
    wave_profile: Literal["SIN", "SAW", "TRI"] = "SIN",
    wave_type: Literal["BANDS", "RINGS"] = "BANDS",
) -> TextureResult:
    pass
def white_noise(
    vector: pf.SocketOrVal[mathutils.Vector] | None = None,
    noise_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = None,
) -> TextureResult:
    pass
def uv_along_stroke(use_tips: bool = False) -> pf.ProcNode:
    pass
def uv_map(from_instancer: bool = False, uv_map: str = "") -> pf.ProcNode:
    pass
class ColorRampResult(NamedTuple):
    color: pf.ProcNode[mathutils.Color]
    alpha: pf.ProcNode[float]


TRampInterpolationType = Literal[
    "EASE", "CARDINAL", "LINEAR", "B_SPLINE", "CONSTANT"
]

# Manual
def color_ramp(
    fac: pf.SocketOrVal[float] = 0.5,
    points: list[tuple[float, mathutils.Color]] | None = None,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
    interpolation: TRampInterpolationType = "LINEAR",
) -> ColorRampResult:
    pass
def value() -> pf.ProcNode:
    pass
def vector_displacement(
    vector: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    midlevel: pf.SocketOrVal[float] = 0.0,
    scale: pf.SocketOrVal[float] = 1.0,
    space: Literal["TANGENT", "OBJECT", "WORLD"] = "TANGENT",
) -> pf.ProcNode:
    pass
def vertex_color(layer_name: str = "") -> pf.ProcNode:
    pass
def volume_absorption(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    density: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode:
    pass
def volume_info() -> pf.ProcNode:
    pass
def volume_principled(
    color: pf.SocketOrVal[mathutils.Color] = (0.5, 0.5, 0.5, 1),
    color_attribute: pf.SocketOrVal[str] = "",
    density: pf.SocketOrVal[float] = 1.0,
    density_attribute: pf.SocketOrVal[str] = "density",
    anisotropy: pf.SocketOrVal[float] = 0.0,
    absorption_color: pf.SocketOrVal[mathutils.Color] = (0, 0, 0, 1),
    emission_strength: pf.SocketOrVal[float] = 0.0,
    emission_color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    blackbody_intensity: pf.SocketOrVal[float] = 0.0,
    blackbody_tint: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    temperature: pf.SocketOrVal[float] = 1000.0,
    temperature_attribute: pf.SocketOrVal[str] = "temperature",
) -> pf.ProcNode:
    pass
def volume_scatter(
    color: pf.SocketOrVal[mathutils.Color] = (0.8, 0.8, 0.8, 1),
    density: pf.SocketOrVal[float] = 1.0,
    anisotropy: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode:
    pass
def wavelength(wavelength: pf.SocketOrVal[float] = 500.0) -> pf.ProcNode:
    pass
def wireframe(
    size: pf.SocketOrVal[float] = 0.01, use_pixel_size: bool = False
) -> pf.ProcNode:
    pass
# ============================================================================
# The following functions are duplicated from func.py for use in shader-only
# contexts (material tasks). The originals remain in func.py for geo node use.
# ============================================================================

TConstant = TypeVar("TConstant", int, float, bool, mathutils.Vector, pf.Euler, mathutils.Color)


def constant(
    value: TConstant,
) -> pf.ProcNode[TConstant]:
    pass
TMix = TypeVar(
    "TMix", pf.SocketOrVal[float], pf.SocketOrVal[mathutils.Vector]
)


def mix(
    a: TMix | None = None,
    b: TMix | None = None,
    factor: pf.SocketOrVal[float] = 0.5,
    clamp_factor: bool = True,
    factor_mode: Literal["UNIFORM", "NON_UNIFORM"] = "UNIFORM",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode[TMix]:
    pass
TColorMixType = Literal[
    'MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD',
    'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION',
    'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE'
]


def mix_rgb(
    factor: pf.SocketOrVal[float] = 0.5,
    a: pf.SocketOrVal[mathutils.Color] = (0.5, 0.5, 0.5, 1),
    b: pf.SocketOrVal[mathutils.Color] = (0.5, 0.5, 0.5, 1),
    blend_type: TColorMixType = "MIX",
    clamp_result: bool = False,
    clamp_factor: bool = True
) -> pf.ProcNode[mathutils.Color]:
    pass
def rgb_curve(
    fac: pf.SocketOrVal[float] = 1.0,
    color: pf.SocketOrVal[mathutils.Color] = (1, 1, 1, 1),
    curves: list[np.ndarray] | None = None,
) -> pf.ProcNode:
    pass
TInterpolationType = Literal["LINEAR", "STEPPED_LINEAR", "SMOOTHSTEP", "SMOOTHERSTEP"]


def map_range(
    value: pf.SocketOrVal[float] = 1.0,
    from_max: pf.SocketOrVal[float] = 1.0,
    from_min: pf.SocketOrVal[float] = 0.0,
    to_max: pf.SocketOrVal[float] = 1.0,
    to_min: pf.SocketOrVal[float] = 0.0,
    clamp: bool = True,
    interpolation_type: TInterpolationType = "LINEAR",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> pf.ProcNode:
    pass