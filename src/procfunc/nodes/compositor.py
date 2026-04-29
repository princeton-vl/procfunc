"""
Auto-generated Compositor Node bindings for Blender
"""

from typing import Any, Literal, NamedTuple

from procfunc import types as pt
from procfunc.nodes import types as nt

TColorSpace = Literal[
    "ACES2065-1",
    "ACEScg",
    "AgX Base Display P3",
    "AgX Base Rec.1886",
    "AgX Base Rec.2020",
    "AgX Base sRGB",
    "AgX Log",
    "Display P3",
    "Filmic Log",
    "Filmic sRGB",
    "Khronos PBR Neutral sRGB",
    "Linear CIE-XYZ D65",
    "Linear CIE-XYZ E",
    "Linear DCI-P3 D65",
    "Linear FilmLight E-Gamut",
    "Linear Rec.2020",
    "Linear Rec.709",
    "Non-Color",
    "Rec.1886",
    "Rec.2020",
    "sRGB",
]
TBlendType = Literal[
    "MIX",
    "DARKEN",
    "MULTIPLY",
    "BURN",
    "LIGHTEN",
    "SCREEN",
    "DODGE",
    "ADD",
    "OVERLAY",
    "SOFT_LIGHT",
    "LINEAR_LIGHT",
    "DIFFERENCE",
    "EXCLUSION",
    "SUBTRACT",
    "DIVIDE",
    "HUE",
    "SATURATION",
    "COLOR",
    "VALUE",
]


class RenderLayersResult:
    # TODO: ban RenderLayersResult and make all compositiors just be functions with certain values as inputs

    def __init__(self, base: nt.ProcNode):
        self.base = base

    def __getattr__(self, name: str) -> nt.ProcNode:
        base = object.__getattribute__(self, "base")
        return base._output_socket(name)


# Manual
def render_layers() -> RenderLayersResult:
    """
    Uses a RenderLayers Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/scene/render_layers.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="CompositorNodeRLayers",  # dont change, this is the actual name of the node
        inputs={},
        attrs={},
    )
    return RenderLayersResult(res)


def alpha_over(
    fac: nt.SocketOrVal[float] = 1.0,
    image_0: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    image_1: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    premul: float = 0.0,
    use_premultiply: bool = False,
) -> nt.ProcNode:
    """
    Uses a AlphaOver Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/alpha_over.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeAlphaOver",
        inputs={"Fac": fac, ("Image", 0): image_0, ("Image", 1): image_1},
        attrs={"premul": premul, "use_premultiply": use_premultiply},
    )


def anti_aliasing(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    contrast_limit: float = 0.2,
    corner_rounding: float = 0.25,
    threshold: float = 1.0,
) -> nt.ProcNode:
    """
    Uses a AntiAliasing Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/anti_aliasing.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeAntiAliasing",
        inputs={"Image": image},
        attrs={
            "contrast_limit": contrast_limit,
            "corner_rounding": corner_rounding,
            "threshold": threshold,
        },
    )


def bilateralblur(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    determinator: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    iterations: int = 1,
    sigma_color: float = 0.3,
    sigma_space: float = 5.0,
) -> nt.ProcNode:
    """
    Uses a Bilateralblur Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/blur/bilateral_blur.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeBilateralblur",
        inputs={"Image": image, "Determinator": determinator},
        attrs={
            "iterations": iterations,
            "sigma_color": sigma_color,
            "sigma_space": sigma_space,
        },
    )


def blur(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    size: nt.SocketOrVal[float] = 1.0,
    aspect_correction: Literal["NONE", "Y", "X"] = "NONE",
    factor: float = 0.0,
    factor_x: float = 0.0,
    factor_y: float = 0.0,
    filter_type: Literal[
        "FLAT", "TENT", "QUAD", "CUBIC", "GAUSS", "FAST_GAUSS", "CATROM", "MITCH"
    ] = "GAUSS",
    size_x: int = 0,
    size_y: int = 0,
    use_bokeh: bool = False,
    use_extended_bounds: bool = False,
    use_gamma_correction: bool = False,
    use_relative: bool = False,
    use_variable_size: bool = False,
) -> nt.ProcNode:
    """
    Uses a Blur Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/blur/blur.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeBlur",
        inputs={"Image": image, "Size": size},
        attrs={
            "aspect_correction": aspect_correction,
            "factor": factor,
            "factor_x": factor_x,
            "factor_y": factor_y,
            "filter_type": filter_type,
            "size_x": size_x,
            "size_y": size_y,
            "use_bokeh": use_bokeh,
            "use_extended_bounds": use_extended_bounds,
            "use_gamma_correction": use_gamma_correction,
            "use_relative": use_relative,
            "use_variable_size": use_variable_size,
        },
    )


def bokeh_blur(
    image: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    bokeh: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    size: nt.SocketOrVal[float] = 1.0,
    bounding_box: nt.SocketOrVal[float] = 1.0,
    blur_max: float = 16.0,
    use_extended_bounds: bool = False,
    use_variable_size: bool = False,
) -> nt.ProcNode:
    """
    Uses a BokehBlur Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/blur/bokeh_blur.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeBokehBlur",
        inputs={
            "Image": image,
            "Bokeh": bokeh,
            "Size": size,
            "Bounding box": bounding_box,
        },
        attrs={
            "blur_max": blur_max,
            "use_extended_bounds": use_extended_bounds,
            "use_variable_size": use_variable_size,
        },
    )


def bokeh_image(
    angle: float = 0.0,
    catadioptric: float = 0.0,
    flaps: int = 5,
    rounding: float = 0.0,
    shift: float = 0.0,
) -> nt.ProcNode:
    """
    Uses a BokehImage Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/bokeh_image.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeBokehImage",
        inputs={},
        attrs={
            "angle": angle,
            "catadioptric": catadioptric,
            "flaps": flaps,
            "rounding": rounding,
            "shift": shift,
        },
    )


def box_mask(
    mask: nt.SocketOrVal[float] = 0.0,
    value: nt.SocketOrVal[float] = 1.0,
    mask_height: float = 0.1,
    mask_type: Literal["ADD", "SUBTRACT", "MULTIPLY", "NOT"] = "ADD",
    mask_width: float = 0.2,
    rotation: float = 0.0,
    x: float = 0.5,
    y: float = 0.5,
) -> nt.ProcNode:
    """
    Uses a BoxMask Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/mask/box_mask.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeBoxMask",
        inputs={"Mask": mask, "Value": value},
        attrs={
            "mask_height": mask_height,
            "mask_type": mask_type,
            "mask_width": mask_width,
            "rotation": rotation,
            "x": x,
            "y": y,
        },
    )


def bright_contrast(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    bright: nt.SocketOrVal[float] = 0.0,
    contrast: nt.SocketOrVal[float] = 0.0,
    use_premultiply: bool = True,
) -> nt.ProcNode:
    """
    Uses a BrightContrast Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/bright_contrast.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeBrightContrast",
        inputs={"Image": image, "Bright": bright, "Contrast": contrast},
        attrs={"use_premultiply": use_premultiply},
    )


def channel_matte(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    color_space: Literal["RGB", "HSV", "YUV", "YCC"] = "RGB",
    limit_channel: Literal["R", "G", "B"] = "R",
    limit_max: float = 1.0,
    limit_method: Literal["SINGLE", "MAX"] = "MAX",
    limit_min: float = 0.0,
    matte_channel: Literal["R", "G", "B"] = "G",
) -> nt.ProcNode:
    """
    Uses a ChannelMatte Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/channel_key.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeChannelMatte",
        inputs={"Image": image},
        attrs={
            "color_space": color_space,
            "limit_channel": limit_channel,
            "limit_max": limit_max,
            "limit_method": limit_method,
            "limit_min": limit_min,
            "matte_channel": matte_channel,
        },
    )


def chroma_matte(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    key_color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    gain: float = 1.0,
    lift: float = 0.0,
    shadow_adjust: float = 0.0,
    threshold: float = 0.174533,
    tolerance: float = 0.523599,
) -> nt.ProcNode:
    """
    Uses a ChromaMatte Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/chroma_key.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeChromaMatte",
        inputs={"Image": image, "Key Color": key_color},
        attrs={
            "gain": gain,
            "lift": lift,
            "shadow_adjust": shadow_adjust,
            "threshold": threshold,
            "tolerance": tolerance,
        },
    )


def color_balance(
    fac: nt.SocketOrVal[float] = 1.0,
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    correction_method: Literal[
        "LIFT_GAMMA_GAIN", "OFFSET_POWER_SLOPE"
    ] = "LIFT_GAMMA_GAIN",
    gain: tuple = (1.0, 1.0, 1.0),
    gamma: tuple = (1.0, 1.0, 1.0),
    lift: tuple = (1.0, 1.0, 1.0),
    offset: tuple = (0.0, 0.0, 0.0),
    offset_basis: float = 0.0,
    power: tuple = (1.0, 1.0, 1.0),
    slope: tuple = (1.0, 1.0, 1.0),
) -> nt.ProcNode:
    """
    Uses a ColorBalance Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/color_balance.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeColorBalance",
        inputs={"Fac": fac, "Image": image},
        attrs={
            "correction_method": correction_method,
            "gain": gain,
            "gamma": gamma,
            "lift": lift,
            "offset": offset,
            "offset_basis": offset_basis,
            "power": power,
            "slope": slope,
        },
    )


def color_correction(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    mask: nt.SocketOrVal[float] = 1.0,
    blue: bool = True,
    green: bool = True,
    highlights_contrast: float = 1.0,
    highlights_gain: float = 1.0,
    highlights_gamma: float = 1.0,
    highlights_lift: float = 0.0,
    highlights_saturation: float = 1.0,
    master_contrast: float = 1.0,
    master_gain: float = 1.0,
    master_gamma: float = 1.0,
    master_lift: float = 0.0,
    master_saturation: float = 1.0,
    midtones_contrast: float = 1.0,
    midtones_end: float = 0.7,
    midtones_gain: float = 1.0,
    midtones_gamma: float = 1.0,
    midtones_lift: float = 0.0,
    midtones_saturation: float = 1.0,
    midtones_start: float = 0.2,
    red: bool = True,
    shadows_contrast: float = 1.0,
    shadows_gain: float = 1.0,
    shadows_gamma: float = 1.0,
    shadows_lift: float = 0.0,
    shadows_saturation: float = 1.0,
) -> nt.ProcNode:
    """
    Uses a ColorCorrection Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/color_correction.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeColorCorrection",
        inputs={"Image": image, "Mask": mask},
        attrs={
            "blue": blue,
            "green": green,
            "highlights_contrast": highlights_contrast,
            "highlights_gain": highlights_gain,
            "highlights_gamma": highlights_gamma,
            "highlights_lift": highlights_lift,
            "highlights_saturation": highlights_saturation,
            "master_contrast": master_contrast,
            "master_gain": master_gain,
            "master_gamma": master_gamma,
            "master_lift": master_lift,
            "master_saturation": master_saturation,
            "midtones_contrast": midtones_contrast,
            "midtones_end": midtones_end,
            "midtones_gain": midtones_gain,
            "midtones_gamma": midtones_gamma,
            "midtones_lift": midtones_lift,
            "midtones_saturation": midtones_saturation,
            "midtones_start": midtones_start,
            "red": red,
            "shadows_contrast": shadows_contrast,
            "shadows_gain": shadows_gain,
            "shadows_gamma": shadows_gamma,
            "shadows_lift": shadows_lift,
            "shadows_saturation": shadows_saturation,
        },
    )


def color_matte(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    key_color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    color_hue: float = 0.01,
    color_saturation: float = 0.1,
    color_value: float = 0.1,
) -> nt.ProcNode:
    """
    Uses a ColorMatte Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/color_key.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeColorMatte",
        inputs={"Image": image, "Key Color": key_color},
        attrs={
            "color_hue": color_hue,
            "color_saturation": color_saturation,
            "color_value": color_value,
        },
    )


def color_spill(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    fac: nt.SocketOrVal[float] = 1.0,
    channel: Literal["R", "G", "B"] = "G",
    limit_channel: Literal["R", "G", "B"] = "R",
    limit_method: Literal["SIMPLE", "AVERAGE"] = "SIMPLE",
    ratio: float = 1.0,
    unspill_blue: float = 0.0,
    unspill_green: float = 0.0,
    unspill_red: float = 0.0,
    use_unspill: bool = False,
) -> nt.ProcNode:
    """
    Uses a ColorSpill Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/color_spill.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeColorSpill",
        inputs={"Image": image, "Fac": fac},
        attrs={
            "channel": channel,
            "limit_channel": limit_channel,
            "limit_method": limit_method,
            "ratio": ratio,
            "unspill_blue": unspill_blue,
            "unspill_green": unspill_green,
            "unspill_red": unspill_red,
            "use_unspill": use_unspill,
        },
    )


def comb_hsva(
    h: nt.SocketOrVal[float] = 0.0,
    s: nt.SocketOrVal[float] = 0.0,
    v: nt.SocketOrVal[float] = 0.0,
    a: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode:
    """
    Uses a CombHSVA Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCombHSVA",
        inputs={"H": h, "S": s, "V": v, "A": a},
        attrs={},
    )


def comb_rgba(
    r: nt.SocketOrVal[float] = 0.0,
    g: nt.SocketOrVal[float] = 0.0,
    b: nt.SocketOrVal[float] = 0.0,
    a: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode:
    """
    Uses a CombRGBA Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCombRGBA",
        inputs={"R": r, "G": g, "B": b, "A": a},
        attrs={},
    )


def comb_ycca(
    y: nt.SocketOrVal[float] = 0.0,
    cb: nt.SocketOrVal[float] = 0.5,
    cr: nt.SocketOrVal[float] = 0.5,
    a: nt.SocketOrVal[float] = 1.0,
    mode: Literal["ITUBT601", "ITUBT709", "JFIF"] = "ITUBT709",
) -> nt.ProcNode:
    """
    Uses a CombYCCA Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCombYCCA",
        inputs={"Y": y, "Cb": cb, "Cr": cr, "A": a},
        attrs={"mode": mode},
    )


def comb_yuva(
    y: nt.SocketOrVal[float] = 0.0,
    u: nt.SocketOrVal[float] = 0.0,
    v: nt.SocketOrVal[float] = 0.0,
    a: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode:
    """
    Uses a CombYUVA Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCombYUVA",
        inputs={"Y": y, "U": u, "V": v, "A": a},
        attrs={},
    )


def combine_color(
    red: nt.SocketOrVal[float] = 0.0,
    green: nt.SocketOrVal[float] = 0.0,
    blue: nt.SocketOrVal[float] = 0.0,
    alpha: nt.SocketOrVal[float] = 1.0,
    mode: Literal["RGB", "HSV", "HSL", "YCC", "YUV"] = "RGB",
    ycc_mode: Literal["ITUBT601", "ITUBT709", "JFIF"] = "ITUBT709",
) -> nt.ProcNode:
    """
    Uses a CombineColor Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCombineColor",
        inputs={"Red": red, "Green": green, "Blue": blue, "Alpha": alpha},
        attrs={"mode": mode, "ycc_mode": ycc_mode},
    )


def combine_xyz(
    x: nt.SocketOrVal[float] = 0.0,
    y: nt.SocketOrVal[float] = 0.0,
    z: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode:
    """
    Uses a CombineXYZ Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/vector/combine_xyz.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCombineXYZ",
        inputs={"X": x, "Y": y, "Z": z},
        attrs={},
    )


def composite(
    image: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    alpha: nt.SocketOrVal[float] = 1.0,
    use_alpha: bool = True,
) -> nt.ProcNode:
    """
    Uses a Composite Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/output/composite.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeComposite",
        inputs={"Image": image, "Alpha": alpha},
        attrs={"use_alpha": use_alpha},
    )


def convert_color_space(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    from_color_space: TColorSpace = "Linear Rec.709",
    to_color_space: TColorSpace = "Linear Rec.709",
) -> nt.ProcNode:
    """
    Uses a ConvertColorSpace Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/convert_colorspace.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeConvertColorSpace",
        inputs={"Image": image},
        attrs={"from_color_space": from_color_space, "to_color_space": to_color_space},
    )


def corner_pin(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    upper_left: nt.SocketOrVal[pt.Vector] = (0, 1, 0),
    upper_right: nt.SocketOrVal[pt.Vector] = (1, 1, 0),
    lower_left: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    lower_right: nt.SocketOrVal[pt.Vector] = (1, 0, 0),
) -> nt.ProcNode:
    """
    Uses a CornerPin Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/corner_pin.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCornerPin",
        inputs={
            "Image": image,
            "Upper Left": upper_left,
            "Upper Right": upper_right,
            "Lower Left": lower_left,
            "Lower Right": lower_right,
        },
        attrs={},
    )


def crop(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    max_x: int = 0,
    max_y: int = 0,
    min_x: int = 0,
    min_y: int = 0,
    rel_max_x: float = 0.0,
    rel_max_y: float = 0.0,
    rel_min_x: float = 0.0,
    rel_min_y: float = 0.0,
    relative: bool = False,
    use_crop_size: bool = False,
) -> nt.ProcNode:
    """
    Uses a Crop Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/crop.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCrop",
        inputs={"Image": image},
        attrs={
            "max_x": max_x,
            "max_y": max_y,
            "min_x": min_x,
            "min_y": min_y,
            "rel_max_x": rel_max_x,
            "rel_max_y": rel_max_y,
            "rel_min_x": rel_min_x,
            "rel_min_y": rel_min_y,
            "relative": relative,
            "use_crop_size": use_crop_size,
        },
    )


def cryptomatte(
    image: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    crypto_00: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    crypto_01: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    crypto_02: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    add: tuple = (0.0, 0.0, 0.0),
    matte_id: str = "",
    remove: tuple = (0.0, 0.0, 0.0),
) -> nt.ProcNode:
    """
    Uses a Cryptomatte Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/mask/cryptomatte.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCryptomatte",
        inputs={
            "Image": image,
            "Crypto 00": crypto_00,
            "Crypto 01": crypto_01,
            "Crypto 02": crypto_02,
        },
        attrs={"add": add, "matte_id": matte_id, "remove": remove},
    )


def curve_rgb(
    fac: nt.SocketOrVal[float] = 1.0,
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    black_level: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    white_level: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
) -> nt.ProcNode:
    """
    Uses a CurveRGB Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/rgb_curves.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCurveRGB",
        inputs={
            "Fac": fac,
            "Image": image,
            "Black Level": black_level,
            "White Level": white_level,
        },
        attrs={},
    )


def curve_vec(vector: nt.SocketOrVal[pt.Vector] = (0, 0, 0)) -> nt.ProcNode:
    """
    Uses a CurveVec Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/rgb_curves.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeCurveVec",
        inputs={"Vector": vector},
        attrs={},
    )


def d_blur(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    angle: float = 0.0,
    center_x: float = 0.5,
    center_y: float = 0.5,
    distance: float = 0.0,
    iterations: int = 1,
    spin: float = 0.0,
    zoom: float = 0.0,
) -> nt.ProcNode:
    """
    Uses a DBlur Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/blur/directional_blur.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDBlur",
        inputs={"Image": image},
        attrs={
            "angle": angle,
            "center_x": center_x,
            "center_y": center_y,
            "distance": distance,
            "iterations": iterations,
            "spin": spin,
            "zoom": zoom,
        },
    )


def defocus(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    z: nt.SocketOrVal[float] = 1.0,
    angle: float = 0.0,
    blur_max: float = 16.0,
    bokeh: Literal[
        "OCTAGON", "HEPTAGON", "HEXAGON", "PENTAGON", "SQUARE", "TRIANGLE", "CIRCLE"
    ] = "CIRCLE",
    f_stop: float = 128.0,
    scene: Any = None,
    threshold: float = 1.0,
    use_gamma_correction: bool = False,
    use_preview: bool = True,
    use_zbuffer: bool = False,
    z_scale: float = 1.0,
) -> nt.ProcNode:
    """
    Uses a Defocus Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/blur/defocus.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDefocus",
        inputs={"Image": image, "Z": z},
        attrs={
            "angle": angle,
            "blur_max": blur_max,
            "bokeh": bokeh,
            "f_stop": f_stop,
            "scene": scene,
            "threshold": threshold,
            "use_gamma_correction": use_gamma_correction,
            "use_preview": use_preview,
            "use_zbuffer": use_zbuffer,
            "z_scale": z_scale,
        },
    )


def denoise(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    normal: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    albedo: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    prefilter: Literal["NONE", "FAST", "ACCURATE"] = "ACCURATE",
    use_hdr: bool = True,
) -> nt.ProcNode:
    """
    Uses a Denoise Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/denoise.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDenoise",
        inputs={"Image": image, "Normal": normal, "Albedo": albedo},
        attrs={"prefilter": prefilter, "use_hdr": use_hdr},
    )


def despeckle(
    fac: nt.SocketOrVal[float] = 1.0,
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    threshold: float = 0.5,
    threshold_neighbor: float = 0.5,
) -> nt.ProcNode:
    """
    Uses a Despeckle Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/despeckle.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDespeckle",
        inputs={"Fac": fac, "Image": image},
        attrs={"threshold": threshold, "threshold_neighbor": threshold_neighbor},
    )


def diff_matte(
    image_1: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    image_2: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    falloff: float = 0.1,
    tolerance: float = 0.1,
) -> nt.ProcNode:
    """
    Uses a DiffMatte Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/difference_key.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDiffMatte",
        inputs={"Image 1": image_1, "Image 2": image_2},
        attrs={"falloff": falloff, "tolerance": tolerance},
    )


def dilate_erode(
    mask: nt.SocketOrVal[float] = 0.0,
    distance: int = 0,
    edge: float = 0.0,
    falloff: Literal[
        "SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE", "SHARP", "LINEAR"
    ] = "SMOOTH",
    mode: Literal["STEP", "THRESHOLD", "DISTANCE", "FEATHER"] = "STEP",
) -> nt.ProcNode:
    """
    Uses a DilateErode Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/dilate_erode.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDilateErode",
        inputs={"Mask": mask},
        attrs={"distance": distance, "edge": edge, "falloff": falloff, "mode": mode},
    )


def displace(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    vector: nt.SocketOrVal[pt.Vector] = (1, 1, 1),
    x_scale: nt.SocketOrVal[float] = 0.0,
    y_scale: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode:
    """
    Uses a Displace Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/displace.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDisplace",
        inputs={
            "Image": image,
            "Vector": vector,
            "X Scale": x_scale,
            "Y Scale": y_scale,
        },
        attrs={},
    )


def distance_matte(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    key_color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    channel: Literal["RGB", "YCC"] = "RGB",
    falloff: float = 0.1,
    tolerance: float = 0.1,
) -> nt.ProcNode:
    """
    Uses a DistanceMatte Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/distance_key.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDistanceMatte",
        inputs={"Image": image, "Key Color": key_color},
        attrs={"channel": channel, "falloff": falloff, "tolerance": tolerance},
    )


def double_edge_mask(
    inner_mask: nt.SocketOrVal[float] = 0.8,
    outer_mask: nt.SocketOrVal[float] = 0.8,
    edge_mode: Literal["BLEED_OUT", "KEEP_IN"] = "BLEED_OUT",
    inner_mode: Literal["ALL", "ADJACENT_ONLY"] = "ALL",
) -> nt.ProcNode:
    """
    Uses a DoubleEdgeMask Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/mask/double_edge_mask.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeDoubleEdgeMask",
        inputs={"Inner Mask": inner_mask, "Outer Mask": outer_mask},
        attrs={"edge_mode": edge_mode, "inner_mode": inner_mode},
    )


def ellipse_mask(
    mask: nt.SocketOrVal[float] = 0.0,
    value: nt.SocketOrVal[float] = 1.0,
    mask_height: float = 0.1,
    mask_type: Literal["ADD", "SUBTRACT", "MULTIPLY", "NOT"] = "ADD",
    mask_width: float = 0.2,
    rotation: float = 0.0,
    x: float = 0.5,
    y: float = 0.5,
) -> nt.ProcNode:
    """
    Uses a EllipseMask Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/mask/ellipse_mask.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeEllipseMask",
        inputs={"Mask": mask, "Value": value},
        attrs={
            "mask_height": mask_height,
            "mask_type": mask_type,
            "mask_width": mask_width,
            "rotation": rotation,
            "x": x,
            "y": y,
        },
    )


def exposure(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    exposure: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode:
    """
    Uses a Exposure Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/exposure.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeExposure",
        inputs={"Image": image, "Exposure": exposure},
        attrs={},
    )


def filter(
    fac: nt.SocketOrVal[float] = 1.0,
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    filter_type: Literal[
        "SOFTEN",
        "SHARPEN",
        "SHARPEN_DIAMOND",
        "LAPLACE",
        "SOBEL",
        "PREWITT",
        "KIRSCH",
        "SHADOW",
    ] = "SOFTEN",
) -> nt.ProcNode:
    """
    Uses a Filter Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/filter.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeFilter",
        inputs={"Fac": fac, "Image": image},
        attrs={"filter_type": filter_type},
    )


def flip(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1), axis: Literal["X", "Y", "XY"] = "X"
) -> nt.ProcNode:
    """
    Uses a Flip Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/flip.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeFlip",
        inputs={"Image": image},
        attrs={"axis": axis},
    )


def gamma(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1), gamma: nt.SocketOrVal[float] = 1.0
) -> nt.ProcNode:
    """
    Uses a Gamma Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/gamma.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeGamma",
        inputs={"Image": image, "Gamma": gamma},
        attrs={},
    )


def glare(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    angle_offset: float = 0.0,
    color_modulation: float = 0.25,
    fade: float = 0.9,
    glare_type: Literal[
        "BLOOM", "GHOSTS", "STREAKS", "FOG_GLOW", "SIMPLE_STAR"
    ] = "STREAKS",
    iterations: int = 3,
    mix: float = 0.0,
    quality: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM",
    size: int = 8,
    streaks: int = 4,
    threshold: float = 1.0,
    use_rotate_45: bool = True,
) -> nt.ProcNode:
    """
    Uses a Glare Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/glare.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeGlare",
        inputs={"Image": image},
        attrs={
            "angle_offset": angle_offset,
            "color_modulation": color_modulation,
            "fade": fade,
            "glare_type": glare_type,
            "iterations": iterations,
            "mix": mix,
            "quality": quality,
            "size": size,
            "streaks": streaks,
            "threshold": threshold,
            "use_rotate_45": use_rotate_45,
        },
    )


def group(node_tree: Any = None) -> nt.ProcNode:
    """
    Uses a Group Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/group.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeGroup",
        inputs={},
        attrs={"node_tree": node_tree},
    )


def hue_correct(
    fac: nt.SocketOrVal[float] = 1.0, image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1)
) -> nt.ProcNode:
    """
    Uses a HueCorrect Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/hue_correct.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeHueCorrect",
        inputs={"Fac": fac, "Image": image},
        attrs={},
    )


def hue_sat(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    hue: nt.SocketOrVal[float] = 0.5,
    saturation: nt.SocketOrVal[float] = 1.0,
    value: nt.SocketOrVal[float] = 1.0,
    fac: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode:
    """
    Uses a HueSat Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/hue_saturation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeHueSat",
        inputs={
            "Image": image,
            "Hue": hue,
            "Saturation": saturation,
            "Value": value,
            "Fac": fac,
        },
        attrs={},
    )


def id_mask(
    id_value: nt.SocketOrVal[float] = 1.0,
    index: int = 0,
    use_antialiasing: bool = False,
) -> nt.ProcNode:
    """
    Uses a IDMask Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/mask/id_mask.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeIDMask",
        inputs={"ID value": id_value},
        attrs={"index": index, "use_antialiasing": use_antialiasing},
    )


def image(
    frame_duration: int = 1,
    frame_offset: int = 0,
    frame_start: int = 1,
    image: Any = None,
    layer: Literal["PLACEHOLDER"] | None = None,
    view: Literal["ALL"] | None = None,
    use_auto_refresh: bool = True,
    use_cyclic: bool = False,
    use_straight_alpha_output: bool = False,
) -> nt.ProcNode:
    """
    Uses a Image Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/image.html
    """
    attrs = {
        "frame_duration": frame_duration,
        "frame_offset": frame_offset,
        "frame_start": frame_start,
        "image": image,
        "use_auto_refresh": use_auto_refresh,
        "use_cyclic": use_cyclic,
        "use_straight_alpha_output": use_straight_alpha_output,
    }
    if layer is not None:
        attrs["layer"] = layer
    if view is not None:
        attrs["view"] = view
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeImage",
        inputs={},
        attrs=attrs,
    )


def inpaint(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1), distance: int = 0
) -> nt.ProcNode:
    """
    Uses a Inpaint Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/inpaint.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeInpaint",
        inputs={"Image": image},
        attrs={"distance": distance},
    )


def invert(
    fac: nt.SocketOrVal[float] = 1.0,
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    invert_alpha: bool = False,
    invert_rgb: bool = True,
) -> nt.ProcNode:
    """
    Uses a Invert Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/invert_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeInvert",
        inputs={"Fac": fac, "Color": color},
        attrs={"invert_alpha": invert_alpha, "invert_rgb": invert_rgb},
    )


def keying(
    image: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    key_color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    garbage_matte: nt.SocketOrVal[float] = 0.0,
    core_matte: nt.SocketOrVal[float] = 0.0,
    blur_post: int = 0,
    blur_pre: int = 0,
    clip_black: float = 0.0,
    clip_white: float = 1.0,
    despill_balance: float = 0.5,
    despill_factor: float = 1.0,
    dilate_distance: int = 0,
    edge_kernel_radius: int = 3,
    edge_kernel_tolerance: float = 0.1,
    feather_distance: int = 0,
    feather_falloff: Literal[
        "SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE", "SHARP", "LINEAR"
    ] = "SMOOTH",
    screen_balance: float = 0.5,
) -> nt.ProcNode:
    """
    Uses a Keying Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/keying.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeKeying",
        inputs={
            "Image": image,
            "Key Color": key_color,
            "Garbage Matte": garbage_matte,
            "Core Matte": core_matte,
        },
        attrs={
            "blur_post": blur_post,
            "blur_pre": blur_pre,
            "clip_black": clip_black,
            "clip_white": clip_white,
            "despill_balance": despill_balance,
            "despill_factor": despill_factor,
            "dilate_distance": dilate_distance,
            "edge_kernel_radius": edge_kernel_radius,
            "edge_kernel_tolerance": edge_kernel_tolerance,
            "feather_distance": feather_distance,
            "feather_falloff": feather_falloff,
            "screen_balance": screen_balance,
        },
    )


def keying_screen(
    clip: Any = None, smoothness: float = 0.0, tracking_object: str = ""
) -> nt.ProcNode:
    """
    Uses a KeyingScreen Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/keying_screen.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeKeyingScreen",
        inputs={},
        attrs={
            "clip": clip,
            "smoothness": smoothness,
            "tracking_object": tracking_object,
        },
    )


def kuwahara(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    size: nt.SocketOrVal[float] = 6.0,
    eccentricity: float = 1.0,
    sharpness: float = 0.5,
    uniformity: int = 4,
    use_high_precision: bool = False,
    variation: Literal["CLASSIC", "ANISOTROPIC"] = "CLASSIC",
) -> nt.ProcNode:
    """
    Uses a Kuwahara Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/kuwahara.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeKuwahara",
        inputs={"Image": image, "Size": size},
        attrs={
            "eccentricity": eccentricity,
            "sharpness": sharpness,
            "uniformity": uniformity,
            "use_high_precision": use_high_precision,
            "variation": variation,
        },
    )


def lensdist(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    distortion: nt.SocketOrVal[float] = 0.0,
    dispersion: nt.SocketOrVal[float] = 0.0,
    use_fit: bool = False,
    use_jitter: bool = False,
    use_projector: bool = False,
) -> nt.ProcNode:
    """
    Uses a Lensdist Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/lens_distortion.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeLensdist",
        inputs={"Image": image, "Distortion": distortion, "Dispersion": dispersion},
        attrs={
            "use_fit": use_fit,
            "use_jitter": use_jitter,
            "use_projector": use_projector,
        },
    )


def levels(
    image: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    channel: Literal[
        "COMBINED_RGB", "RED", "GREEN", "BLUE", "LUMINANCE"
    ] = "COMBINED_RGB",
) -> nt.ProcNode:
    """
    Uses a Levels Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/utilities/levels.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeLevels",
        inputs={"Image": image},
        attrs={"channel": channel},
    )


def luma_matte(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    limit_max: float = 1.0,
    limit_min: float = 0.0,
) -> nt.ProcNode:
    """
    Uses a LumaMatte Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/keying/luminance_key.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeLumaMatte",
        inputs={"Image": image},
        attrs={"limit_max": limit_max, "limit_min": limit_min},
    )


def map_range(
    value: nt.SocketOrVal[float] = 1.0,
    from_min: nt.SocketOrVal[float] = 0.0,
    from_max: nt.SocketOrVal[float] = 1.0,
    to_min: nt.SocketOrVal[float] = 0.0,
    to_max: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode:
    """
    Uses a MapRange Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/utilities/map_range.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeMapRange",
        inputs={
            "Value": value,
            "From Min": from_min,
            "From Max": from_max,
            "To Min": to_min,
            "To Max": to_max,
        },
        attrs={},
    )


def map_uv(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    uv: nt.SocketOrVal[pt.Vector] = (1, 0, 0),
    alpha: int = 0,
    filter_type: Literal["NEAREST", "ANISOTROPIC"] = "ANISOTROPIC",
) -> nt.ProcNode:
    """
    Uses a MapUV Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/map_uv.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeMapUV",
        inputs={"Image": image, "UV": uv},
        attrs={"alpha": alpha, "filter_type": filter_type},
    )


def map_value(
    value: nt.SocketOrVal[float] = 1.0,
    max: tuple = (1.0,),
    min: tuple = (0.0,),
    offset: tuple = (0.0,),
    size: tuple = (1.0,),
    use_max: bool = False,
    use_min: bool = False,
) -> nt.ProcNode:
    """
    Uses a MapValue Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/utilities/map_value.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeMapValue",
        inputs={"Value": value},
        attrs={
            "max": max,
            "min": min,
            "offset": offset,
            "size": size,
            "use_max": use_max,
            "use_min": use_min,
        },
    )


def mask(
    mask: Any = None,
    motion_blur_samples: int = 16,
    motion_blur_shutter: float = 0.5,
    size_source: Literal["SCENE", "FIXED", "FIXED_SCENE"] = "SCENE",
    size_x: int = 256,
    size_y: int = 256,
    use_feather: bool = True,
    use_motion_blur: bool = False,
) -> nt.ProcNode:
    """
    Uses a Mask Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/mask.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeMask",
        inputs={},
        attrs={
            "mask": mask,
            "motion_blur_samples": motion_blur_samples,
            "motion_blur_shutter": motion_blur_shutter,
            "size_source": size_source,
            "size_x": size_x,
            "size_y": size_y,
            "use_feather": use_feather,
            "use_motion_blur": use_motion_blur,
        },
    )


def math(
    value_0: nt.SocketOrVal[float] = 0.5, value_1: nt.SocketOrVal[float] = 0.5
) -> nt.ProcNode:
    """
    Uses a Math Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/utilities/math.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeMath",
        inputs={("Value", 0): value_0, ("Value", 1): value_1},
        attrs={},
    )


def mix_rgb(
    fac: nt.SocketOrVal[float] = 1.0,
    image_0: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    image_1: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    blend_type: TBlendType = "MIX",
    use_alpha: bool = False,
) -> nt.ProcNode:
    """
    Uses a MixRGB Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/mix_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeMixRGB",
        inputs={"Fac": fac, ("Image", 0): image_0, ("Image", 1): image_1},
        attrs={"blend_type": blend_type, "use_alpha": use_alpha},
    )


class MovieClipResult(NamedTuple):
    image: nt.ProcNode[pt.Color]
    alpha: nt.ProcNode[float]
    offset_x: nt.ProcNode[float]
    offset_y: nt.ProcNode[float]
    scale: nt.ProcNode[float]
    angle: nt.ProcNode[float]


def movie_clip(clip: Any = None) -> MovieClipResult:
    """
    Uses a MovieClip Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/movie_clip.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="CompositorNodeMovieClip",
        inputs={},
        attrs={"clip": clip},
    )
    return MovieClipResult(
        node._output_socket("image"),
        node._output_socket("alpha"),
        node._output_socket("offset_x"),
        node._output_socket("offset_y"),
        node._output_socket("scale"),
        node._output_socket("angle"),
    )


def movie_distortion(
    image: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    clip: Any = None,
    distortion_type: Literal["UNDISTORT", "DISTORT"] = "UNDISTORT",
) -> nt.ProcNode:
    """
    Uses a MovieDistortion Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/movie_distortion.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeMovieDistortion",
        inputs={"Image": image},
        attrs={"clip": clip, "distortion_type": distortion_type},
    )


def normal(normal: nt.SocketOrVal[pt.Vector] = (0, 0, 1)) -> nt.ProcNode:
    """
    Uses a Normal Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/vector/normal.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeNormal",
        inputs={"Normal": normal},
        attrs={},
    )


def normalize(value: nt.SocketOrVal[float] = 1.0) -> nt.ProcNode:
    """
    Uses a Normalize Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/utilities/normalize.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeNormalize",
        inputs={"Value": value},
        attrs={},
    )


# Manual changes
def output_file(
    active_input_index: int = 0,
    base_path: str = "/tmp/",
    slot_paths: dict | None = None,
    format: dict | None = None,
    **kwargs,
) -> nt.ProcNode:
    """
    Uses a OutputFile Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/output/file_output.html
    """

    if format is None:
        format = {}

    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeOutputFile",
        inputs=kwargs,
        attrs={
            "active_input_index": active_input_index,
            "format": format,
            "base_path": base_path,
            "slot_paths": slot_paths,
        },
    )


def pixelate(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1), pixel_size: int = 1
) -> nt.ProcNode:
    """
    Uses a Pixelate Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/pixelate.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodePixelate",
        inputs={"Color": color},
        attrs={"pixel_size": pixel_size},
    )


def plane_track_deform(
    image: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    clip: Any = None,
    motion_blur_samples: int = 16,
    motion_blur_shutter: float = 0.5,
    plane_track_name: str = "",
    tracking_object: str = "",
    use_motion_blur: bool = False,
) -> nt.ProcNode:
    """
    Uses a PlaneTrackDeform Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/tracking/plane_track_deform.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodePlaneTrackDeform",
        inputs={"Image": image},
        attrs={
            "clip": clip,
            "motion_blur_samples": motion_blur_samples,
            "motion_blur_shutter": motion_blur_shutter,
            "plane_track_name": plane_track_name,
            "tracking_object": tracking_object,
            "use_motion_blur": use_motion_blur,
        },
    )


def posterize(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1), steps: nt.SocketOrVal[float] = 8.0
) -> nt.ProcNode:
    """
    Uses a Posterize Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/posterize.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodePosterize",
        inputs={"Image": image, "Steps": steps},
        attrs={},
    )


def premul_key(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    mapping: Literal["STRAIGHT_TO_PREMUL", "PREMUL_TO_STRAIGHT"] = "STRAIGHT_TO_PREMUL",
) -> nt.ProcNode:
    """
    Uses a PremulKey Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/alpha_convert.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodePremulKey",
        inputs={"Image": image},
        attrs={"mapping": mapping},
    )


def rgb() -> nt.ProcNode:
    """
    Uses a RGB Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/constant/rgb.html
    """
    return nt.ProcNode.from_nodetype(node_type="CompositorNodeRGB", inputs={}, attrs={})


def rgb_to_bw(image: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1)) -> nt.ProcNode:
    """
    Uses a RGBToBW Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/rgb_to_bw.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeRGBToBW",
        inputs={"Image": image},
        attrs={},
    )


def rotate(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    degr: nt.SocketOrVal[float] = 0.0,
    filter_type: Literal["NEAREST", "BILINEAR", "BICUBIC"] = "BILINEAR",
) -> nt.ProcNode:
    """
    Uses a Rotate Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/rotate.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeRotate",
        inputs={"Image": image, "Degr": degr},
        attrs={"filter_type": filter_type},
    )


def scale(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    x: nt.SocketOrVal[float] = 1.0,
    y: nt.SocketOrVal[float] = 1.0,
    frame_method: Literal["STRETCH", "FIT", "CROP"] = "STRETCH",
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    space: Literal["RELATIVE", "ABSOLUTE", "SCENE_SIZE", "RENDER_SIZE"] = "RELATIVE",
) -> nt.ProcNode:
    """
    Uses a Scale Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/scale.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeScale",
        inputs={"Image": image, "X": x, "Y": y},
        attrs={
            "frame_method": frame_method,
            "offset_x": offset_x,
            "offset_y": offset_y,
            "space": space,
        },
    )


class SceneTimeResult(NamedTuple):
    seconds: nt.ProcNode[float]
    frame: nt.ProcNode[float]


def scene_time() -> SceneTimeResult:
    """
    Uses a SceneTime Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/scene/scene_time.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSceneTime",
        inputs={},
        attrs={},
    )
    return SceneTimeResult(node._output_socket("seconds"), node._output_socket("frame"))


class SepHsvaResult(NamedTuple):
    h: nt.ProcNode[float]
    s: nt.ProcNode[float]
    v: nt.ProcNode[float]
    a: nt.ProcNode[float]


def sep_hsva(image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1)) -> SepHsvaResult:
    """
    Uses a SepHSVA Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/separate_color.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSepHSVA",
        inputs={"Image": image},
        attrs={},
    )
    return SepHsvaResult(
        node._output_socket("h"),
        node._output_socket("s"),
        node._output_socket("v"),
        node._output_socket("a"),
    )


class SepRgbaResult(NamedTuple):
    r: nt.ProcNode[float]
    g: nt.ProcNode[float]
    b: nt.ProcNode[float]
    a: nt.ProcNode[float]


def sep_rgba(image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1)) -> SepRgbaResult:
    """
    Uses a SepRGBA Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/separate_color.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSepRGBA",
        inputs={"Image": image},
        attrs={},
    )
    return SepRgbaResult(
        node._output_socket("r"),
        node._output_socket("g"),
        node._output_socket("b"),
        node._output_socket("a"),
    )


class SepYccaResult(NamedTuple):
    y: nt.ProcNode[float]
    cb: nt.ProcNode[float]
    cr: nt.ProcNode[float]
    a: nt.ProcNode[float]


def sep_ycca(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    mode: Literal["ITUBT601", "ITUBT709", "JFIF"] = "ITUBT709",
) -> SepYccaResult:
    """
    Uses a SepYCCA Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/separate_color.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSepYCCA",
        inputs={"Image": image},
        attrs={"mode": mode},
    )
    return SepYccaResult(
        node._output_socket("y"),
        node._output_socket("cb"),
        node._output_socket("cr"),
        node._output_socket("a"),
    )


class SepYuvaResult(NamedTuple):
    y: nt.ProcNode[float]
    u: nt.ProcNode[float]
    v: nt.ProcNode[float]
    a: nt.ProcNode[float]


def sep_yuva(image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1)) -> SepYuvaResult:
    """
    Uses a SepYUVA Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/separate_color.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSepYUVA",
        inputs={"Image": image},
        attrs={},
    )
    return SepYuvaResult(
        node._output_socket("y"),
        node._output_socket("u"),
        node._output_socket("v"),
        node._output_socket("a"),
    )


def set_alpha(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    alpha: nt.SocketOrVal[float] = 1.0,
    mode: Literal["APPLY", "REPLACE_ALPHA"] = "APPLY",
) -> nt.ProcNode:
    """
    Uses a SetAlpha Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/set_alpha.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSetAlpha",
        inputs={"Image": image, "Alpha": alpha},
        attrs={"mode": mode},
    )


def split(
    image_0: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    image_1: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    axis: Literal["X", "Y"] = "X",
    factor: int = 50,
) -> nt.ProcNode:
    """
    Uses a Split Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/utilities/split.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSplit",
        inputs={("Image", 0): image_0, ("Image", 1): image_1},
        attrs={"axis": axis, "factor": factor},
    )


def stabilize(
    image: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    clip: Any = None,
    filter_type: Literal["NEAREST", "BILINEAR", "BICUBIC"] = "BILINEAR",
    invert: bool = False,
) -> nt.ProcNode:
    """
    Uses a Stabilize Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/tracking/stabilize_2d.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeStabilize",
        inputs={"Image": image},
        attrs={"clip": clip, "filter_type": filter_type, "invert": invert},
    )


def sun_beams(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    ray_length: float = 0.0,
    source: tuple = (0.5, 0.5),
) -> nt.ProcNode:
    """
    Uses a SunBeams Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/sun_beams.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSunBeams",
        inputs={"Image": image},
        attrs={"ray_length": ray_length, "source": source},
    )


def switch(
    off: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    on: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    check: bool = False,
) -> nt.ProcNode:
    """
    Uses a Switch Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/utilities/switch.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSwitch",
        inputs={"Off": off, "On": on},
        attrs={"check": check},
    )


def switch_view(
    left: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    right: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
) -> nt.ProcNode:
    """
    Uses a SwitchView Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/utilities/switch.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeSwitchView",
        inputs={"left": left, "right": right},
        attrs={},
    )


def texture(
    offset: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    scale: nt.SocketOrVal[pt.Vector] = (1, 1, 1),
    node_output: int = 0,
    texture: Any = None,
) -> nt.ProcNode:
    """
    Uses a Texture Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/texture.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeTexture",
        inputs={"Offset": offset, "Scale": scale},
        attrs={"node_output": node_output, "texture": texture},
    )


def time(frame_end: int = 250, frame_start: int = 1) -> nt.ProcNode:
    """
    Uses a Time Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/scene/scene_time.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeTime",
        inputs={},
        attrs={"frame_end": frame_end, "frame_start": frame_start},
    )


def tonemap(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    adaptation: float = 1.0,
    contrast: float = 0.0,
    correction: float = 0.0,
    gamma: float = 1.0,
    intensity: float = 0.0,
    key: float = 0.18,
    offset: float = 1.0,
    tonemap_type: Literal["RD_PHOTORECEPTOR", "RH_SIMPLE"] = "RD_PHOTORECEPTOR",
) -> nt.ProcNode:
    """
    Uses a Tonemap Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/adjust/tone_map.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeTonemap",
        inputs={"Image": image},
        attrs={
            "adaptation": adaptation,
            "contrast": contrast,
            "correction": correction,
            "gamma": gamma,
            "intensity": intensity,
            "key": key,
            "offset": offset,
            "tonemap_type": tonemap_type,
        },
    )


def track_pos(
    clip: Any = None,
    frame_relative: int = 0,
    position: Literal[
        "ABSOLUTE", "RELATIVE_START", "RELATIVE_FRAME", "ABSOLUTE_FRAME"
    ] = "ABSOLUTE",
    track_name: str = "",
    tracking_object: str = "",
) -> nt.ProcNode:
    """
    Uses a TrackPos Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/tracking/track_position.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeTrackPos",
        inputs={},
        attrs={
            "clip": clip,
            "frame_relative": frame_relative,
            "position": position,
            "track_name": track_name,
            "tracking_object": tracking_object,
        },
    )


def transform(
    image: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
    x: nt.SocketOrVal[float] = 0.0,
    y: nt.SocketOrVal[float] = 0.0,
    angle: nt.SocketOrVal[float] = 0.0,
    scale: nt.SocketOrVal[float] = 1.0,
    filter_type: Literal["NEAREST", "BILINEAR", "BICUBIC"] = "NEAREST",
) -> nt.ProcNode:
    """
    Uses a Transform Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/transform.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeTransform",
        inputs={"Image": image, "X": x, "Y": y, "Angle": angle, "Scale": scale},
        attrs={"filter_type": filter_type},
    )


def translate(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    x: nt.SocketOrVal[float] = 0.0,
    y: nt.SocketOrVal[float] = 0.0,
    interpolation: Literal["Nearest", "Bilinear", "Bicubic"] = "Nearest",
    use_relative: bool = False,
    wrap_axis: Literal["NONE", "XAXIS", "YAXIS", "BOTH"] = "NONE",
) -> nt.ProcNode:
    """
    Uses a Translate Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/transform/translate.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeTranslate",
        inputs={"Image": image, "X": x, "Y": y},
        attrs={
            "interpolation": interpolation,
            "use_relative": use_relative,
            "wrap_axis": wrap_axis,
        },
    )


def val_to_rgb(fac: nt.SocketOrVal[float] = 0.5) -> nt.ProcNode:
    """
    Uses a ValToRGB Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/color_ramp.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeValToRGB",
        inputs={"Fac": fac},
        attrs={},
    )


def value() -> nt.ProcNode:
    """
    Uses a Value Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/input/constant/value.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeValue", inputs={}, attrs={}
    )


def vec_blur(
    image: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    z: nt.SocketOrVal[float] = 0.0,
    speed: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    factor: float = 0.25,
    samples: int = 32,
    speed_max: int = 0,
    speed_min: int = 0,
    use_curved: bool = False,
) -> nt.ProcNode:
    """
    Uses a VecBlur Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/filter/blur/vector_blur.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeVecBlur",
        inputs={"Image": image, "Z": z, "Speed": speed},
        attrs={
            "factor": factor,
            "samples": samples,
            "speed_max": speed_max,
            "speed_min": speed_min,
            "use_curved": use_curved,
        },
    )


def viewer(
    image: nt.SocketOrVal[pt.Color] = (0, 0, 0, 1),
    alpha: nt.SocketOrVal[float] = 1.0,
    use_alpha: bool = True,
) -> nt.ProcNode:
    """
    Uses a Viewer Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/output/viewer.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeViewer",
        inputs={"Image": image, "Alpha": alpha},
        attrs={"use_alpha": use_alpha},
    )


def zcombine(
    image_0: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    z_0: nt.SocketOrVal[float] = 1.0,
    image_1: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    z_1: nt.SocketOrVal[float] = 1.0,
    use_alpha: bool = False,
    use_antialias_z: bool = True,
) -> nt.ProcNode:
    """
    Uses a Zcombine Compositor Node.

    See: https://docs.blender.org/manual/en/4.2/compositing/types/color/mix/z_combine.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="CompositorNodeZcombine",
        inputs={
            ("Image", 0): image_0,
            ("Z", 0): z_0,
            ("Image", 1): image_1,
            ("Z", 1): z_1,
        },
        attrs={"use_alpha": use_alpha, "use_antialias_z": use_antialias_z},
    )
