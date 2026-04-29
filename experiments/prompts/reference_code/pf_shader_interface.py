
###MODULE procfunc.nodes.math


def clamp(
    value: pf.SocketOrVal[float] = 1.0,
    min: pf.SocketOrVal[float] = 0.0,
    max: pf.SocketOrVal[float] = 1.0,
    clamp_type: Literal["MINMAX", "RANGE"] = "MINMAX",
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
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_subtract(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_multiply(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_multiply_add(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    addend: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_divide(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_cross_product(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_project(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    onto: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[float]:
    pass
def vector_reflect(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_refract(
    incident: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    ior: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_faceforward(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    surface: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    normal: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_dot_product(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_distance(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_length(vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0)) -> pf.ProcNode[float]:
    pass
def vector_scale(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0), scale: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_normalize(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_wrap(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    max_val: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
    min_val: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_snap(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_floor(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_ceil(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_modulo(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_fraction(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_round(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_truncate(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_absolute(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_minimum(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_maximum(
    a: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    b: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_sine(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_cosine(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_tangent(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_rotate_axis_angle(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    center: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    axis: pf.SocketOrVal[pf.Vector] = (0, 0, 1),
    angle: pf.SocketOrVal[float] = 0.0,
    invert: bool = False,
) -> pf.ProcNode[pf.Vector]:
    pass
def vector_rotate_euler(
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    center: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    invert: bool = False,
) -> pf.ProcNode[pf.Vector]:
    pass
# NOTE: mode XYZ have been dropped. transpiler specialcases will map these back to vector_rotate_euler calls.


def vector_transform(
    vector: pf.SocketOrVal[pf.Vector] = (0.5, 0.5, 0.5),
    convert_from: Literal["WORLD", "OBJECT", "CAMERA"] = "WORLD",
    convert_to: Literal["WORLD", "OBJECT", "CAMERA"] = "OBJECT",
    vector_type: Literal["POINT", "VECTOR", "NORMAL"] = "VECTOR",
) -> pf.ProcNode[pf.Vector]:
    pass

###MODULE procfunc.nodes.shader


def add_shader(
    shader_0: pf.ProcNode[pf.Shader] | None = None,
    shader_1: pf.ProcNode[pf.Shader] | None = None,
) -> pf.ProcNode[pf.Shader]:
    pass
class AmbientOcclusionResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    ao: pf.ProcNode[float]


def ambient_occlusion(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    distance: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    inside: bool = False,
    only_local: bool = False,
    samples: int = 16,
) -> AmbientOcclusionResult:
    pass
class AttributeResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    vector: pf.ProcNode[pf.Vector]
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
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    strength: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Shader]:
    pass
def bevel(
    radius: pf.SocketOrVal[float] = 0.05,
    normal: pf.SocketOrVal[pf.Vector] = None,
    samples: int = 4,
) -> pf.ProcNode[pf.Vector]:
    pass
def blackbody(temperature: pf.SocketOrVal[float] = 1500.0) -> pf.ProcNode[pf.Color]:
    pass
def bright_contrast(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    bright: pf.SocketOrVal[float] = 0.0,
    contrast: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.Color]:
    pass
def anisotropic_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.5,
    anisotropy: pf.SocketOrVal[float] = 0.0,
    rotation: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    tangent: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    distribution: Literal[
        "BECKMANN", "GGX", "ASHIKHMIN_SHIRLEY", "MULTI_GGX"
    ] = "MULTI_GGX",
) -> pf.ProcNode[pf.Shader]:
    pass
def diffuse_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
) -> pf.ProcNode[pf.Shader]:
    pass
def glass_bsdf(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.5,
    normal: pf.SocketOrVal[pf.Vector] = None,
    distribution: Literal["BECKMANN", "GGX", "MULTI_GGX"] = "MULTI_GGX",
) -> pf.ProcNode[pf.Shader]:
    pass
def hair_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    offset: pf.SocketOrVal[float] = 0.0,
    roughness_u: pf.SocketOrVal[float] = 0.1,
    roughness_v: pf.SocketOrVal[float] = 1.0,
    tangent: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    component: Literal["Reflection", "Transmission"] = "Reflection",
) -> pf.ProcNode[pf.Shader]:
    pass
def principled_hair_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.017513, 0.005763, 0.002059, 1),
    roughness: pf.SocketOrVal[float] = 0.3,
    radial_roughness: pf.SocketOrVal[float] = 0.3,
    coat: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.55,
    offset: pf.SocketOrVal[float] = 0.034907,
    random_roughness: pf.SocketOrVal[float] = 0.0,
    random: pf.SocketOrVal[float] = 0.0,
    model: Literal["CHIANG", "HUANG"] = "CHIANG",
    parametrization: Literal["ABSORPTION", "MELANIN", "COLOR"] = "COLOR",
) -> pf.ProcNode[pf.Shader]:
    pass
TSubsurfaceMethod = Literal["BURLEY", "RANDOM_WALK", "RANDOM_WALK_SKIN"]


def principled_bsdf(
    base_color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    metallic: pf.SocketOrVal[float] = 0.0,
    roughness: pf.SocketOrVal[float] = 0.5,
    ior: pf.SocketOrVal[float] = 1.5,
    alpha: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
    # subsurface scattering
    subsurface_method: TSubsurfaceMethod = "RANDOM_WALK",
    subsurface_weight: pf.SocketOrVal[float] = 0.0,
    subsurface_radius: pf.SocketOrVal[pf.Vector] = (1, 0.2, 0.1),
    subsurface_scale: pf.SocketOrVal[float] = 0.05,
    subsurface_ior: pf.SocketOrVal[float] | None = None,
    subsurface_anisotropy: pf.SocketOrVal[float] | None = None,
    # specular
    distribution: Literal["GGX", "MULTI_GGX"] = "MULTI_GGX",
    specular_ior_level: pf.SocketOrVal[float] = 0.5,
    specular_tint: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    anisotropic: pf.SocketOrVal[float] = 0.0,
    anisotropic_rotation: pf.SocketOrVal[float] = 0.0,
    tangent: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    transmission_weight: pf.SocketOrVal[float] = 0.0,
    coat_weight: pf.SocketOrVal[float] = 0.0,
    coat_roughness: pf.SocketOrVal[float] = 0.03,
    coat_ior: pf.SocketOrVal[float] = 1.5,
    coat_tint: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    coat_normal: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
    sheen_weight: pf.SocketOrVal[float] = 0.0,
    sheen_roughness: pf.SocketOrVal[float] = 0.5,
    sheen_tint: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    emission_color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    emission_strength: pf.SocketOrVal[float] = 0.0,
    thin_film_thickness: pf.SocketOrVal[float] = 0.0,
    thin_film_ior: pf.SocketOrVal[float] = 1.33,
) -> pf.ProcNode[pf.Shader]:
    pass
def ray_portal_bsdf(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    position: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    direction: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
) -> pf.ProcNode[pf.Shader]:
    pass
def refraction_bsdf(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    roughness: pf.SocketOrVal[float] = 0.0,
    ior: pf.SocketOrVal[float] = 1.45,
    normal: pf.SocketOrVal[pf.Vector] = None,
    distribution: Literal["BECKMANN", "GGX"] = "BECKMANN",
) -> pf.ProcNode[pf.Shader]:
    pass
def sheen_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    roughness: pf.SocketOrVal[float] = 0.5,
    normal: pf.SocketOrVal[pf.Vector] = None,
    distribution: Literal["ASHIKHMIN", "MICROFIBER"] = "MICROFIBER",
) -> pf.ProcNode[pf.Shader]:
    pass
def toon_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    size: pf.SocketOrVal[float] = 0.5,
    smooth: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    component: Literal["DIFFUSE", "GLOSSY"] = "DIFFUSE",
) -> pf.ProcNode[pf.Shader]:
    pass
def translucent_bsdf(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    normal: pf.SocketOrVal[pf.Vector] = None,
) -> pf.ProcNode[pf.Shader]:
    pass
def transparent_bsdf(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
) -> pf.ProcNode[pf.Shader]:
    pass
def bump(
    strength: pf.SocketOrVal[float] = 1.0,
    distance: pf.SocketOrVal[float] = 1.0,
    height: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    invert: bool = False,
) -> pf.ProcNode[pf.Vector]:
    pass
class CameraDataResult(NamedTuple):
    view_vector: pf.ProcNode[pf.Vector]
    view_z_depth: pf.ProcNode[float]
    view_distance: pf.ProcNode[float]


def camera_data() -> CameraDataResult:
    pass
def displacement(
    height: pf.SocketOrVal[float] = 0.0,
    midlevel: pf.SocketOrVal[float] = 0.5,
    scale: pf.SocketOrVal[float] = 1.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
) -> pf.ProcNode[pf.Vector]:
    pass
def eevee_specular(
    base_color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    specular: pf.SocketOrVal[pf.Color] = (0.03, 0.03, 0.03, 1),
    roughness: pf.SocketOrVal[float] = 0.2,
    emissive_color: pf.SocketOrVal[pf.Color] = (0, 0, 0, 1),
    transparency: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = None,
    clear_coat: pf.SocketOrVal[float] = 0.0,
    clear_coat_roughness: pf.SocketOrVal[float] = 0.0,
    clear_coat_normal: pf.SocketOrVal[pf.Vector] = None,
) -> pf.ProcNode[pf.Shader]:
    pass
def emission(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    strength: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Shader]:
    pass
def fresnel(
    ior: pf.SocketOrVal[float] = 1.5, normal: pf.SocketOrVal[pf.Vector] = None
) -> pf.ProcNode[float]:
    pass
def gamma(
    color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1), gamma: pf.SocketOrVal[float] = 1.0
) -> pf.ProcNode[pf.Color]:
    pass
class HairInfoResult(NamedTuple):
    is_strand: pf.ProcNode[float]
    intercept: pf.ProcNode[float]
    length: pf.ProcNode[float]
    thickness: pf.ProcNode[float]
    tangent_normal: pf.ProcNode[pf.Vector]
    random: pf.ProcNode[float]


def hair_info() -> HairInfoResult:
    pass
def holdout() -> pf.ProcNode[pf.Shader]:
    pass
def hue_saturation(
    hue: pf.SocketOrVal[float] = 0.5,
    saturation: pf.SocketOrVal[float] = 1.0,
    value: pf.SocketOrVal[float] = 1.0,
    fac: pf.SocketOrVal[float] = 1.0,
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
) -> pf.ProcNode[pf.Color]:
    pass
def invert(
    fac: pf.SocketOrVal[float] = 1.0, color: pf.SocketOrVal[pf.Color] = (0, 0, 0, 1)
) -> pf.ProcNode[pf.Color]:
    pass
class LayerWeightResult(NamedTuple):
    fresnel: pf.ProcNode[float]
    facing: pf.ProcNode[float]


def layer_weight(
    blend: pf.SocketOrVal[float] = 0.5,
    normal: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
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
    vector: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    location: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    rotation: pf.SocketOrVal[pf.Vector] = (0, 0, 0),
    scale: pf.SocketOrVal[pf.Vector] = (1, 1, 1),
    vector_type: Literal["POINT", "TEXTURE", "VECTOR", "NORMAL"] = "POINT",
) -> pf.ProcNode[pf.Vector]:
    pass
def mix_shader(
    factor: pf.SocketOrVal[float] = 0.5,
    a: pf.ProcNode[pf.Shader] | None = None,
    b: pf.ProcNode[pf.Shader] | None = None,
) -> pf.ProcNode[pf.Shader]:
    pass
class NormalResult(NamedTuple):
    normal: pf.ProcNode[pf.Vector]
    dot: pf.ProcNode[float]


def normal(normal: pf.SocketOrVal[pf.Vector] = (0, 0, 1)) -> NormalResult:
    pass
def normal_map(
    strength: pf.SocketOrVal[float] = 1.0,
    color: pf.SocketOrVal[pf.Color] = (0.5, 0.5, 1, 1),
    space: Literal[
        "TANGENT", "OBJECT", "WORLD", "BLENDER_OBJECT", "BLENDER_WORLD"
    ] = "TANGENT",
    uv_map: str = "",
) -> pf.ProcNode[pf.Vector]:
    pass
class ObjectInfoResult(NamedTuple):
    location: pf.ProcNode[pf.Vector]
    color: pf.ProcNode[pf.Color]
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
    location: pf.ProcNode[pf.Vector]
    size: pf.ProcNode[float]
    velocity: pf.ProcNode[pf.Vector]
    angular_velocity: pf.ProcNode[pf.Vector]


def particle_info() -> ParticleInfoResult:
    pass
class PointInfoResult(NamedTuple):
    position: pf.ProcNode[pf.Vector]
    radius: pf.ProcNode[float]
    random: pf.ProcNode[float]


def point_info() -> PointInfoResult:
    pass
def rgb() -> pf.ProcNode[pf.Color]:
    pass
def rgb_to_bw(
    color: pf.SocketOrVal[pf.Color] = (0.5, 0.5, 0.5, 1),
) -> pf.ProcNode[float]:
    pass
def script(
    bytecode: str = "",
    bytecode_hash: str = "",
    filepath: str = "",
    mode: Literal["INTERNAL", "EXTERNAL"] = "INTERNAL",
    script: Any = None,
    use_auto_update: bool = False,
) -> pf.ProcNode[pf.Shader]:
    pass
def shader_to_rgb(
    shader: pf.ProcNode[pf.Shader] | None = None,
) -> pf.ProcNode[pf.Color]:
    pass
def squeeze(
    value: pf.SocketOrVal[float] = 0.0,
    width: pf.SocketOrVal[float] = 1.0,
    center: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[float]:
    pass
def subsurface_scattering(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    scale: pf.SocketOrVal[float] = 0.05,
    radius: pf.SocketOrVal[pf.Vector] = (1, 0.2, 0.1),
    ior: pf.SocketOrVal[float] = 1.4,
    roughness: pf.SocketOrVal[float] = 1.0,
    anisotropy: pf.SocketOrVal[float] = 0.0,
    normal: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
    falloff: Literal["BURLEY", "RANDOM_WALK", "RANDOM_WALK_SKIN"] = "RANDOM_WALK",
) -> pf.ProcNode[pf.Shader]:
    pass
def tangent(
    axis: Literal["X", "Y", "Z"] = "Z",
    direction_type: Literal["RADIAL", "UV_MAP"] = "RADIAL",
    uv_map: str = "",
) -> pf.ProcNode[pf.Vector]:
    pass
class TextureResult(NamedTuple):
    fac: pf.ProcNode[float]
    color: pf.ProcNode[pf.Color]


def brick(
    vector: pf.SocketOrVal[pf.Vector],
    color1: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    color2: pf.SocketOrVal[pf.Color] = (0.2, 0.2, 0.2, 1),
    mortar: pf.SocketOrVal[pf.Color] = (0, 0, 0, 1),
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
    vector: pf.SocketOrVal[pf.Vector],
    color1: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    color2: pf.SocketOrVal[pf.Color] = (0.2, 0.2, 0.2, 1),
    scale: pf.SocketOrVal[float] = 5.0,
) -> TextureResult:
    pass
class CoordResult(NamedTuple):
    generated: pf.ProcNode[pf.Vector]
    normal: pf.ProcNode[pf.Vector]
    uv: pf.ProcNode[pf.Vector]
    object: pf.ProcNode[pf.Vector]
    camera: pf.ProcNode[pf.Vector]
    window: pf.ProcNode[pf.Vector]


def coord(from_instancer: bool = False, object: Any = None) -> CoordResult:
    pass
class GeometryResult(NamedTuple):
    position: pf.ProcNode[pf.Vector]
    normal: pf.ProcNode[pf.Vector]
    tangent: pf.ProcNode[pf.Vector]
    true_normal: pf.ProcNode[pf.Vector]
    incoming: pf.ProcNode[pf.Vector]
    parametric: pf.ProcNode[pf.Vector]
    backfacing: pf.ProcNode[float]
    pointiness: pf.ProcNode[float]
    random_per_island: pf.ProcNode[float]


def geometry() -> GeometryResult:
    pass
TTextureInterpolationType = Literal["Linear", "Closest", "Cubic", "Smart"]  # TODO


def environment(
    vector: pf.SocketOrVal[pf.Vector],
    image: Any = None,
    interpolation: TTextureInterpolationType = "Linear",
    projection: Literal["EQUIRECTANGULAR", "MIRROR_BALL"] = "EQUIRECTANGULAR",
) -> pf.ProcNode[pf.Color]:
    pass
def gradient(
    vector: pf.SocketOrVal[pf.Vector],
    gradient_type: Literal[
        "LINEAR",
        "QUADRATIC",
        "EASING",
        "DIAGONAL",
        "SPHERICAL",
        "QUADRATIC_SPHERE",
        "RADIAL",
    ] = "LINEAR",
) -> TextureResult:
    pass
def ies(
    vector: pf.SocketOrVal[pf.Vector],
    strength: pf.SocketOrVal[float] = 1.0,
    filepath: str = "",
    ies: Any = None,
    mode: Literal["INTERNAL", "EXTERNAL"] = "INTERNAL",
) -> pf.ProcNode[float]:
    pass
def image(
    vector: pf.SocketOrVal[pf.Vector],
    extension: Literal["REPEAT", "EXTEND", "CLIP", "MIRROR"] = "REPEAT",
    image: Any = None,
    interpolation: TTextureInterpolationType = "Linear",
    projection: Literal["FLAT", "BOX", "SPHERE", "CUBE"] = "FLAT",
    projection_blend: float = 0.0,
) -> TextureResult:
    pass
def magic(
    vector: pf.SocketOrVal[pf.Vector],
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
    vector: pf.SocketOrVal[pf.Vector] = (0.0, 0.0, 0.0),
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
    color: pf.ProcNode[pf.Color]
    density: pf.ProcNode[float]


def point_density(
    vector: pf.SocketOrVal[pf.Vector],
    interpolation: Literal["Closest", "Linear", "Cubic"] = "Linear",
    object: Any = None,
    particle_color_source: Literal[
        "PARTICLE_AGE", "PARTICLE_SPEED", "PARTICLE_VELOCITY"
    ] = "PARTICLE_AGE",
    particle_system: Any = None,
    point_source: Literal["OBJECT", "PARTICLE_SYSTEM"] = "PARTICLE_SYSTEM",
    radius: float = 0.3,
    resolution: int = 100,
    space: Literal["OBJECT", "WORLD"] = "OBJECT",
    vertex_attribute_name: str = "",
    vertex_color_source: Literal[
        "VERTEX_COLOR", "VERTEX_NORMAL", "VERTEX_WEIGHT"
    ] = "VERTEX_COLOR",
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
) -> pf.ProcNode[pf.Color]:
    pass
class VoronoiResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    distance: pf.ProcNode[float]
    position: pf.ProcNode[pf.Vector]
    w: pf.ProcNode[float] | None


TDistanceMetric = Literal["EUCLIDEAN", "MANHATTAN", "CHEBYCHEV", "MINKOWSKI"]


def voronoi(
    vector: pf.SocketOrVal[pf.Vector],
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
    vector: pf.SocketOrVal[pf.Vector],
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
    vector: pf.SocketOrVal[pf.Vector],
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
    vector: pf.SocketOrVal[pf.Vector],
    scale: pf.SocketOrVal[float] = 5.0,
    randomness: pf.SocketOrVal[float] = 1.0,
    normalize: bool = False,
) -> pf.ProcNode[float]:
    pass
def wave(
    vector: pf.SocketOrVal[pf.Vector],
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
    vector: pf.SocketOrVal[pf.Vector] | None = None,
    noise_dimensions: TNoiseDimensions = "3D",
    w: pf.SocketOrVal[float] = None,
) -> TextureResult:
    pass
def uv_along_stroke(use_tips: bool = False) -> pf.ProcNode[pf.Vector]:
    pass
def uv_map(from_instancer: bool = False, uv_map: str = "") -> pf.ProcNode[pf.Vector]:
    pass
class ColorRampResult(NamedTuple):
    color: pf.ProcNode[pf.Color]
    alpha: pf.ProcNode[float]


TRampInterpolationType = Literal["EASE", "CARDINAL", "LINEAR", "B_SPLINE", "CONSTANT"]


# Manual
def color_ramp(
    fac: pf.SocketOrVal[float] = 0.5,
    points: list[tuple[float, pf.Color]] | None = None,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
    interpolation: TRampInterpolationType = "LINEAR",
) -> ColorRampResult:
    pass
def value() -> pf.ProcNode[float]:
    pass
def vector_displacement(
    vector: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    midlevel: pf.SocketOrVal[float] = 0.0,
    scale: pf.SocketOrVal[float] = 1.0,
    space: Literal["TANGENT", "OBJECT", "WORLD"] = "TANGENT",
) -> pf.ProcNode[pf.Vector]:
    pass
def vertex_color(layer_name: str = "") -> pf.ProcNode[pf.Color]:
    pass
def volume_absorption(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    density: pf.SocketOrVal[float] = 1.0,
) -> pf.ProcNode[pf.Shader]:
    pass
def volume_info() -> pf.ProcNode:
    pass
def volume_principled(
    color: pf.SocketOrVal[pf.Color] = (0.5, 0.5, 0.5, 1),
    color_attribute: pf.SocketOrVal[str] = "",
    density: pf.SocketOrVal[float] = 1.0,
    density_attribute: pf.SocketOrVal[str] = "density",
    anisotropy: pf.SocketOrVal[float] = 0.0,
    absorption_color: pf.SocketOrVal[pf.Color] = (0, 0, 0, 1),
    emission_strength: pf.SocketOrVal[float] = 0.0,
    emission_color: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    blackbody_intensity: pf.SocketOrVal[float] = 0.0,
    blackbody_tint: pf.SocketOrVal[pf.Color] = (1, 1, 1, 1),
    temperature: pf.SocketOrVal[float] = 1000.0,
    temperature_attribute: pf.SocketOrVal[str] = "temperature",
) -> pf.ProcNode[pf.Shader]:
    pass
def volume_scatter(
    color: pf.SocketOrVal[pf.Color] = (0.8, 0.8, 0.8, 1),
    density: pf.SocketOrVal[float] = 1.0,
    anisotropy: pf.SocketOrVal[float] = 0.0,
) -> pf.ProcNode[pf.Shader]:
    pass
def wavelength(wavelength: pf.SocketOrVal[float] = 500.0) -> pf.ProcNode[pf.Color]:
    pass
def wireframe(
    size: pf.SocketOrVal[float] = 0.01, use_pixel_size: bool = False
) -> pf.ProcNode[float]:
    pass