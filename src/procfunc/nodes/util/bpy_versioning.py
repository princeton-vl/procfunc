"""Supported bpy version utilities."""

import bpy

_MIN_SUPPORTED_VERSION = (3, 6)
_MAX_SUPPORTED_VERSION = (5, 2)


def bpy_version(version: tuple[int, ...] | None = None) -> tuple[int, int]:
    actual = version or bpy.app.version
    result = actual[:2]
    if not _MIN_SUPPORTED_VERSION <= result <= _MAX_SUPPORTED_VERSION:
        raise ValueError(
            f"Unsupported bpy {actual}; supported versions are "
            f"{_MIN_SUPPORTED_VERSION[0]}.{_MIN_SUPPORTED_VERSION[1]} through "
            f"{_MAX_SUPPORTED_VERSION[0]}.{_MAX_SUPPORTED_VERSION[1]}"
        )
    return result


def _fmt(version: tuple[int, ...]) -> str:
    return ".".join(str(v) for v in version)


def unsupported_message(
    feature: str,
    since: tuple[int, int] | None = None,
    removed_in: tuple[int, int] | None = None,
) -> str:
    if since is not None and removed_in is not None:
        needs = f"bpy {_fmt(since)} through {_fmt(removed_in)} (exclusive)"
    elif since is not None:
        needs = f"bpy {_fmt(since)} or newer"
    elif removed_in is not None:
        needs = f"bpy older than {_fmt(removed_in)}"
    else:
        raise ValueError("unsupported_message needs `since` and/or `removed_in`")
    return (
        f"{feature} requires {needs}, but this session is running "
        f"bpy {_fmt(bpy.app.version)}"
    )
