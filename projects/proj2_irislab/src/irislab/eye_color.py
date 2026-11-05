"""Perceptual color analysis and semantic classification of iris pixels.

The iris localization stage provides the pixel population belonging to one
or both irises. This module analyzes that population in perceptual color
spaces and classifies it into one of the six eye-color classes used by
IrisLab:

    Blue, Green, Gray, Hazel, Amber, Brown

Classification uses the iris pixel distribution rather than only a single
representative RGB value. This is especially important for Hazel and Amber
eyes, whose characteristic pigmentation can be lost when reduced to a
single median color.
"""

from __future__ import annotations

import colorsys
import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np


logger = logging.getLogger("irislab")


class EyeColor(str, Enum):
    """Semantic eye-color classes supported by IrisLab."""

    BLUE = "Blue"
    GREEN = "Green"
    GRAY = "Gray"
    HAZEL = "Hazel"
    AMBER = "Amber"
    BROWN = "Brown"


@dataclass(frozen=True, slots=True)
class ColorFeatures:
    """Perceptual color features for a representative iris color."""

    rgb: tuple[int, int, int]
    lab: tuple[float, float, float]
    hsv: tuple[float, float, float]
    chroma: float
    hue: float


def _rgb_to_lab(pixels: np.ndarray) -> np.ndarray:
    """Convert sRGB pixels with shape ``(N, 3)`` to CIELAB."""

    rgb = pixels.astype(np.float32) / 255.0

    # sRGB -> linear RGB
    rgb = np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4,
    )

    # Linear RGB -> XYZ using the D65 illuminant.
    transform = np.asarray(
        [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ],
        dtype=np.float32,
    )

    xyz = rgb @ transform.T

    # D65 reference white.
    xyz /= np.asarray(
        [0.95047, 1.00000, 1.08883],
        dtype=np.float32,
    )

    delta = 6.0 / 29.0
    delta3 = delta**3

    xyz = np.where(
        xyz > delta3,
        np.cbrt(xyz),
        xyz / (3.0 * delta**2) + 4.0 / 29.0,
    )

    x = xyz[:, 0]
    y = xyz[:, 1]
    z = xyz[:, 2]

    lab = np.column_stack(
        (
            116.0 * y - 16.0,
            500.0 * (x - y),
            200.0 * (y - z),
        )
    )

    return lab.astype(np.float32)


def extract_color_features(
    rgb: tuple[int, int, int],
) -> ColorFeatures:
    """Calculate perceptual features for one representative sRGB color."""

    if len(rgb) != 3:
        raise ValueError("Expected RGB color with exactly three components")

    if any(component < 0 or component > 255 for component in rgb):
        raise ValueError("RGB components must be between 0 and 255")

    pixels = np.asarray([rgb], dtype=np.uint8)
    lab_values = _rgb_to_lab(pixels)[0]

    lightness = float(lab_values[0])
    a = float(lab_values[1])
    b = float(lab_values[2])

    chroma = float(np.hypot(a, b))
    hue = float(
        (np.degrees(np.arctan2(b, a)) + 360.0) % 360.0
    )

    red, green, blue = (
        component / 255.0
        for component in rgb
    )

    hsv_h, hsv_s, hsv_v = colorsys.rgb_to_hsv(
        red,
        green,
        blue,
    )

    hsv = (
        hsv_h * 360.0,
        hsv_s * 100.0,
        hsv_v * 100.0,
    )

    return ColorFeatures(
        rgb=rgb,
        lab=(
            lightness,
            a,
            b,
        ),
        hsv=hsv,
        chroma=chroma,
        hue=hue,
    )


def classify_eye_color(pixels: np.ndarray) -> EyeColor:
    """Classify an iris pixel population into a semantic eye color.

    The classification uses CIELAB color distributions rather than only
    the representative RGB value calculated by ``iris.py``.

    Hazel is treated as a mixed-pigmentation class and therefore requires
    substantial green and warm pigmentation instead of merely a few warm
    pixels in an otherwise green iris.
    """

    pixels = np.asarray(pixels)

    if pixels.ndim != 2 or pixels.shape[1] != 3:
        raise ValueError(
            "Expected iris pixels with shape (N, 3)"
        )

    if len(pixels) < 20:
        raise ValueError(
            "At least 20 iris pixels are required for classification"
        )

    lab = _rgb_to_lab(pixels)

    lightness = lab[:, 0]
    a = lab[:, 1]
    b = lab[:, 2]

    chroma = np.sqrt(a * a + b * b)

    # CIELAB hue angle in degrees.
    hue = (
        np.degrees(np.arctan2(b, a)) + 360.0
    ) % 360.0

    # Remove the darkest and brightest tails that may still contain
    # pupil, eyelash, reflection, or sclera contamination.
    lower_lightness = np.percentile(lightness, 10)
    upper_lightness = np.percentile(lightness, 95)

    useful = (
        (lightness >= lower_lightness)
        & (lightness <= upper_lightness)
    )

    lightness = lightness[useful]
    a = a[useful]
    b = b[useful]
    chroma = chroma[useful]
    hue = hue[useful]

    if len(lightness) < 20:
        raise ValueError(
            "Not enough useful iris pixels for classification"
        )

    # ------------------------------------------------------------------
    # Pixel populations
    # ------------------------------------------------------------------

    # Low-chroma pixels are candidates for gray pigmentation.
    neutral = chroma < 8.0

    # Cool blue/cyan pigmentation.
    blue = (
        (hue >= 220.0)
        & (hue <= 300.0)
        & (chroma >= 5.0)
    )

    # Natural green eyes are often muted rather than strongly saturated.
    green = (
        (a < -1.0)
        & (b > 4.0)
        & (hue >= 90.0)
        & (hue <= 180.0)
        & (chroma >= 5.0)
    )

    # Golden/yellow-orange pigmentation.
    amber = (
        (hue >= 45.0)
        & (hue < 90.0)
        & (b >= 10.0)
        & (chroma >= 10.0)
    )

    # Darker red/orange warm pigmentation.
    brown = (
        (
            (hue < 55.0)
            | (hue >= 330.0)
        )
        & (chroma >= 7.0)
    )

    neutral_fraction = float(np.mean(neutral))
    blue_fraction = float(np.mean(blue))
    green_fraction = float(np.mean(green))
    amber_fraction = float(np.mean(amber))
    brown_fraction = float(np.mean(brown))

    warm_fraction = amber_fraction + brown_fraction

    median_lightness = float(np.median(lightness))
    median_chroma = float(np.median(chroma))
    median_a = float(np.median(a))
    median_b = float(np.median(b))

    logger.debug(
        (
            "Eye color features: "
            "L*=%.1f C*=%.1f a*=%.1f b*=%.1f | "
            "neutral=%.2f blue=%.2f green=%.2f "
            "amber=%.2f brown=%.2f warm=%.2f"
        ),
        median_lightness,
        median_chroma,
        median_a,
        median_b,
        neutral_fraction,
        blue_fraction,
        green_fraction,
        amber_fraction,
        brown_fraction,
        warm_fraction,
    )

    # Hazel requires substantial green pigmentation together with a
    # substantial warm population and a meaningful amber component.
    if (
        green_fraction >= 0.20
        and warm_fraction >= 0.25
        and amber_fraction >= 0.10
    ):
        result = EyeColor.HAZEL

    elif (
        blue_fraction >= 0.18
        and blue_fraction > green_fraction
        and blue_fraction > warm_fraction
    ):
        result = EyeColor.BLUE

    elif (
        green_fraction >= 0.15
        or (
            median_a < -1.0
            and median_b > 5.0
            and median_chroma >= 5.0
        )
    ):
        result = EyeColor.GREEN

    elif (
        amber_fraction >= 0.20
        or (
            median_b >= 12.0
            and median_b > abs(median_a) * 1.35
            and median_chroma >= 12.0
        )
    ):
        result = EyeColor.AMBER

    elif (
        neutral_fraction >= 0.55
        or median_chroma < 7.0
    ):
        result = EyeColor.GRAY

    elif (
        brown_fraction >= 0.15
        or warm_fraction >= 0.20
    ):
        result = EyeColor.BROWN

    else:
        result = EyeColor.GRAY

    logger.info(
        "Eye color classified as %s",
        result.value,
    )

    return result


def describe_eye_color(pixels: np.ndarray) -> str:
    """Return the human-readable semantic eye-color name."""

    return classify_eye_color(pixels).value