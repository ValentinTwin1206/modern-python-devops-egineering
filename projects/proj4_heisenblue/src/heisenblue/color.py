"""Color utilities for mapping a fictional Blue Score to a blue gradient."""

from __future__ import annotations


LIGHT_BLUE = (214, 233, 255)
MID_BLUE = (77, 139, 214)
DEEP_BLUE = (11, 55, 125)


def _clamp_score(score: int) -> int:
    return max(0, min(100, int(score)))


def _interpolate_channel(start: int, end: int, fraction: float) -> int:
    return int(round(start + (end - start) * fraction))


def score_to_rgb(score: int) -> tuple[int, int, int]:
    """Map a score from 0 to 100 onto a simple two-stage blue gradient."""

    clamped = _clamp_score(score)
    if clamped <= 50:
        fraction = clamped / 50.0
        start, end = LIGHT_BLUE, MID_BLUE
    else:
        fraction = (clamped - 50) / 50.0
        start, end = MID_BLUE, DEEP_BLUE

    return (
        _interpolate_channel(start[0], end[0], fraction),
        _interpolate_channel(start[1], end[1], fraction),
        _interpolate_channel(start[2], end[2], fraction),
    )


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert an RGB tuple to an uppercase hexadecimal color string."""

    red, green, blue = rgb
    return f"#{red:02X}{green:02X}{blue:02X}"


def score_to_hex(score: int) -> str:
    """Convenience wrapper that converts a score directly to HEX."""

    return rgb_to_hex(score_to_rgb(score))