from dataclasses import dataclass
from typing import Any, Generic, TypeVar

INTERPOLATION_TYPES = {
    "LINEAR",
    "BEZIER",
    # TODO more
}


T = TypeVar("T")


@dataclass
class Keyframes(Generic[T]):
    """
    Represents keyframe animation data for a parameter.

    Args:
        keyframes: List of (frame, value) tuples where value can be any type
        interpolation: Blender interpolation mode ('LINEAR', 'BEZIER', 'CONSTANT', etc.)
    """

    keyframes: list[tuple[int, T]]
    interpolation: str = "LINEAR"

    def __post_init__(self):
        if not self.keyframes:
            raise ValueError("Keyframes list cannot be empty")
        if self.interpolation not in INTERPOLATION_TYPES:
            raise ValueError(
                f"Invalid interpolation mode: {self.interpolation}, "
                f"current supported are {INTERPOLATION_TYPES}, adding more may be trivial"
            )


def apply_keyframes(
    target: Any,
    data_path_name: str,
    keyframes: Keyframes,
):
    """
    Apply keyframe animation to a node socket.

    Args:
        target_socket: The Blender node socket to animate
        keyframes: Keyframes object containing frame/value pairs and interpolation mode
    """
    if not hasattr(target, data_path_name):
        raise ValueError(
            f"Cannot apply keyframes to {target} - no {data_path_name} attribute"
        )

    setattr(target, data_path_name, keyframes.keyframes[0][1])

    # Apply all keyframes
    for frame, value in keyframes.keyframes:
        setattr(target, data_path_name, value)
        target.keyframe_insert(data_path=data_path_name, frame=frame)

    # Set interpolation mode for all keyframes
    if hasattr(target, "id_data") and hasattr(target.id_data, "animation_data"):
        anim_data = target.id_data.animation_data
        if anim_data and anim_data.action:
            for fcurve in anim_data.action.fcurves:
                # Check if this fcurve corresponds to our socket
                socket_path = target.path_from_id()
                if socket_path and socket_path in fcurve.data_path:
                    for keyframe in fcurve.keyframe_points:
                        keyframe.interpolation = keyframes.interpolation
