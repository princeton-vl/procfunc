import numpy as np

from procfunc import types as t


def hsv_color(
    hsv: np.ndarray | tuple | None = None,
    *,
    hue: float | None = None,
    saturation: float | None = None,
    value: float | None = None,
) -> t.Color:
    if hsv is None and (hue is None or saturation is None or value is None):
        raise ValueError("provide hsv=... or all of hue/saturation/value")
    color = t.Color()
    if hsv is not None:
        color.hsv = hsv
    else:
        color.hsv = (hue, saturation, value)
    return color


hsv_to_rgba = hsv_color


def rgb_color(
    r: float | None = None,
    g: float | None = None,
    b: float | None = None,
    rgb: np.ndarray | None = None,
) -> t.Color:
    if rgb is None and (r is None or g is None or b is None):
        raise ValueError("provide rgb=... or all of r/g/b")
    return t.Color(rgb if rgb is not None else (r, g, b))


def _srgb_to_linearrgb(c):
    if c < 0:
        return 0
    elif c < 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** 2.4


def _hex_to_rgb(h: int):
    r = (h & 0xFF0000) >> 16
    g = (h & 0x00FF00) >> 8
    b = h & 0x0000FF
    return tuple([_srgb_to_linearrgb(c / 0xFF) for c in (r, g, b)])


def hex_color(h: int) -> t.Color:
    return t.Color(_hex_to_rgb(h))
