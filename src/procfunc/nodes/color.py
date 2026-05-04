from typing import Literal, NamedTuple

import numpy as np

from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import ContextualNode
from procfunc.nodes.bpy_node_info import NodeDataType

TColorMixType = Literal[
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


def mix_rgb(
    factor: nt.SocketOrVal[float] = 0.5,
    a: nt.SocketOrVal[pt.Color] = (0.5, 0.5, 0.5, 1),
    b: nt.SocketOrVal[pt.Color] = (0.5, 0.5, 0.5, 1),
    blend_type: TColorMixType = "MIX",
    clamp_result: bool = False,
    clamp_factor: bool = True,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a Mix Node with datatype Color

    NOTE: separated from float/vector mix() due to extra arguments

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/mix.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeMix",
        inputs={"Factor": factor, "A": a, "B": b},
        attrs={
            "blend_type": blend_type,
            "clamp_result": clamp_result,
            "clamp_factor": clamp_factor,
            "data_type": NodeDataType.RGBA,
        },
    )


def rgb_curve(
    fac: nt.SocketOrVal[float] = 1.0,
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    curves: list[np.ndarray] | None = None,
) -> nt.ProcNode:
    """
    Uses a RGBCurve Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/rgb_curves.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeRGBCurve",
        inputs={"Fac": fac, "Color": color},
        attrs={"curves": curves},
    )


def combine_rgb(
    red: nt.SocketOrVal[float] = 0.0,
    green: nt.SocketOrVal[float] = 0.0,
    blue: nt.SocketOrVal[float] = 0.0,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
) -> nt.ProcNode[pt.Color]:
    """
    Uses a CombineColor Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/combine_color.html
    """
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMBINE_COLOR.value,
        inputs={"Red": red, "Green": green, "Blue": blue},
        attrs={"mode": mode},
    )


def combine_hsv(
    hue: nt.SocketOrVal[float] = 0.0,
    saturation: nt.SocketOrVal[float] = 0.0,
    value: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a CombineColor Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/combine_color.html
    """
    # Blender socket identifiers stay as Red/Green/Blue regardless of mode
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMBINE_COLOR.value,
        inputs={"Red": hue, "Green": saturation, "Blue": value},
        attrs={"mode": "HSV"},
    )


def combine_hsl(
    hue: nt.SocketOrVal[float] = 0.0,
    saturation: nt.SocketOrVal[float] = 0.0,
    lightness: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a CombineHSV Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/combine_color.html
    """
    # Blender socket identifiers stay as Red/Green/Blue regardless of mode
    return nt.ProcNode.from_nodetype(
        node_type=ContextualNode.COMBINE_COLOR.value,
        inputs={"Red": hue, "Green": saturation, "Blue": lightness},
        attrs={"mode": "HSL"},
    )


class SeparateRgbResult(NamedTuple):
    red: nt.ProcNode[float]
    green: nt.ProcNode[float]
    blue: nt.ProcNode[float]
    alpha: nt.ProcNode[float]


def separate_rgb(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
) -> SeparateRgbResult:
    """
    Uses a SeparateColor Shader Node in RGB mode.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/separate_color.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type=ContextualNode.SEPARATE_COLOR.value,
        inputs={"Color": color},
        attrs={"mode": "RGB"},
    )
    return SeparateRgbResult(
        red=res._output_socket("red"),
        green=res._output_socket("green"),
        blue=res._output_socket("blue"),
        alpha=res._output_socket("alpha"),
    )


class SeparateHsvResult(NamedTuple):
    hue: nt.ProcNode[float]
    saturation: nt.ProcNode[float]
    value: nt.ProcNode[float]
    alpha: nt.ProcNode[float]


def separate_hsv(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
) -> SeparateHsvResult:
    """
    Uses a SeparateColor Shader Node in HSV mode.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/separate_color.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type=ContextualNode.SEPARATE_COLOR.value,
        inputs={"Color": color},
        attrs={"mode": "HSV"},
    )
    return SeparateHsvResult(
        hue=res._output_socket("red"),
        saturation=res._output_socket("green"),
        value=res._output_socket("blue"),
        alpha=res._output_socket("alpha"),
    )


class SeparateHslResult(NamedTuple):
    hue: nt.ProcNode[float]
    saturation: nt.ProcNode[float]
    lightness: nt.ProcNode[float]
    alpha: nt.ProcNode[float]


def separate_hsl(
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
) -> SeparateHslResult:
    """
    Uses a SeparateColor Shader Node in HSL mode.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/separate_color.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type=ContextualNode.SEPARATE_COLOR.value,
        inputs={"Color": color},
        attrs={"mode": "HSL"},
    )
    return SeparateHslResult(
        hue=res._output_socket("red"),
        saturation=res._output_socket("green"),
        lightness=res._output_socket("blue"),
        alpha=res._output_socket("alpha"),
    )


# ---- ColorRamp -------------------------------------------------------------


class ColorRampResult(NamedTuple):
    color: nt.ProcNode[pt.Color]
    alpha: nt.ProcNode[float]


TRampInterpolationType = Literal["EASE", "CARDINAL", "LINEAR", "B_SPLINE", "CONSTANT"]


def color_ramp(
    fac: nt.SocketOrVal[float] = 0.5,
    points: list[tuple[float, pt.Color]] | None = None,
    mode: Literal["RGB", "HSV", "HSL"] = "RGB",
    interpolation: TRampInterpolationType = "LINEAR",
) -> ColorRampResult:
    """
    Uses a ValToRGB (ColorRamp) Shader Node with points support.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/color_ramp.html
    """

    res = nt.ProcNode.from_nodetype(
        node_type="ShaderNodeValToRGB",
        inputs={"Fac": fac},
        attrs={
            "points": points,
            "color_mode": mode,
            "interpolation": interpolation,
        },
    )
    return ColorRampResult(
        color=res._output_socket("Color"),
        alpha=res._output_socket("Alpha"),
    )


def blackbody(temperature: nt.SocketOrVal[float] = 1500.0) -> nt.ProcNode[pt.Color]:
    """
    Uses a Blackbody Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/blackbody.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBlackbody",
        inputs={"Temperature": temperature},
        attrs={},
    )


def bright_contrast(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1),
    bright: nt.SocketOrVal[float] = 0.0,
    contrast: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.Color]:
    """
    Uses a BrightContrast Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/bright_contrast.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeBrightContrast",
        inputs={"Color": color, "Bright": bright, "Contrast": contrast},
        attrs={},
    )


def gamma(
    color: nt.SocketOrVal[pt.Color] = (1, 1, 1, 1), gamma: nt.SocketOrVal[float] = 1.0
) -> nt.ProcNode[pt.Color]:
    """
    Uses a Gamma Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/gamma.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeGamma",
        inputs={"Color": color, "Gamma": gamma},
        attrs={},
    )


def hue_saturation(
    hue: nt.SocketOrVal[float] = 0.5,
    saturation: nt.SocketOrVal[float] = 1.0,
    value: nt.SocketOrVal[float] = 1.0,
    fac: nt.SocketOrVal[float] = 1.0,
    color: nt.SocketOrVal[pt.Color] = (0.8, 0.8, 0.8, 1),
) -> nt.ProcNode[pt.Color]:
    """
    Uses a HueSaturation Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/color/hue_saturation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeHueSaturation",
        inputs={
            "Hue": hue,
            "Saturation": saturation,
            "Value": value,
            "Fac": fac,
            "Color": color,
        },
        attrs={},
    )


def rgb_to_bw(
    color: nt.SocketOrVal[pt.Color] = (0.5, 0.5, 0.5, 1),
) -> nt.ProcNode[float]:
    """
    Uses a RGBToBW Shader Node.

    See: https://docs.blender.org/manual/en/4.2/render/shader_nodes/converter/rgb_to_bw.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="ShaderNodeRGBToBW",
        inputs={"Color": color},
        attrs={},
    )
