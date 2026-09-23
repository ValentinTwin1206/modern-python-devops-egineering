"""Scientific iris-color analysis from an eye image."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from irislab._native import delta_e

from .eye_color import (
    ColorFeatures,
    EyeColor,
    classify_eye_color,
    extract_color_features,
)
from .iris import extract_iris


_SUPPORTED_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
}

logger = logging.getLogger("irislab")


class EyeColorDetectionError(ValueError):
    """Raised when an image does not contain a reliably detectable iris."""


@dataclass(frozen=True, slots=True)
class ReferenceColor:
    """Reference color used for perceptual color comparison."""

    name: str
    eye_color: EyeColor
    rgb: tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class ColorAnalysisResult:
    """Result returned by :func:`analyze`."""

    eye_color: EyeColor
    eye_rgb: tuple[int, int, int]

    lab: tuple[float, float, float]
    hsv: tuple[float, float, float]
    chroma: float
    hue: float

    closest_profile: str
    profile_rgb: tuple[int, int, int]
    delta_e: float

    source: str
    confidence: float
    eyes_detected: int


#
# These colors are intentionally reference samples for the demonstration,
# not canonical definitions of human iris pigmentation.
#
REFERENCE_COLORS: tuple[ReferenceColor, ...] = (
    ReferenceColor(
        name="Blue-01",
        eye_color=EyeColor.BLUE,
        rgb=(92, 126, 145),
    ),
    ReferenceColor(
        name="Green-01",
        eye_color=EyeColor.GREEN,
        rgb=(104, 126, 83),
    ),
    ReferenceColor(
        name="Gray-01",
        eye_color=EyeColor.GRAY,
        rgb=(126, 132, 130),
    ),
    ReferenceColor(
        name="Hazel-01",
        eye_color=EyeColor.HAZEL,
        rgb=(126, 108, 65),
    ),
    ReferenceColor(
        name="Amber-01",
        eye_color=EyeColor.AMBER,
        rgb=(168, 112, 42),
    ),
    ReferenceColor(
        name="Brown-01",
        eye_color=EyeColor.BROWN,
        rgb=(91, 63, 42),
    ),
)


def _find_closest_profile(
    features: ColorFeatures,
) -> tuple[ReferenceColor, float]:
    """Find the reference profile with the smallest CIELAB distance."""

    scored: list[tuple[float, ReferenceColor]] = []

    for profile in REFERENCE_COLORS:
        profile_features = extract_color_features(
            profile.rgb
        )

        distance = float(
            delta_e(
                *map(float, features.lab),
                *map(float, profile_features.lab),
            )
        )

        scored.append(
            (
                distance,
                profile,
            )
        )

    distance, profile = min(
        scored,
        key=lambda pair: pair[0],
    )

    return profile, distance


def analyze(
    image_path: Path,
    device: str = "cpu",
) -> ColorAnalysisResult:
    """Analyze iris pigmentation in an image.

    The image is processed by the local iris-segmentation pipeline.
    Representative iris color features are calculated in Python and
    compared against reference profiles using the native C++ CIELAB
    distance implementation.
    """

    suffix = image_path.suffix.lower()

    if suffix not in _SUPPORTED_SUFFIXES:
        raise ValueError(
            f"The file format '{suffix}' is not supported."
        )

    if not image_path.is_file():
        raise ValueError(
            f"The file '{image_path}' does not exist or is not accessible."
        )

    logger.info(
        "Extracting iris from '%s' using '%s'",
        image_path,
        device,
    )

    with Image.open(image_path) as image:
        iris = extract_iris(
            image=image,
            device=device,
        )

    if iris is None:
        raise EyeColorDetectionError(
            "Could not reliably detect an iris. "
            "Use an image with clearly visible eye(s)."
        )

    logger.info(
        "Extracted iris RGB %s with confidence %.2f",
        iris.rgb,
        iris.confidence,
    )

    #
    # Semantic classification based on the complete iris pixel population.
    #
    eye_color = classify_eye_color(
        iris.pixels
    )

    #
    # Quantitative color features based on the representative iris RGB.
    #
    features = extract_color_features(
        iris.rgb
    )

    logger.debug(
        (
            "Representative iris color: "
            "RGB=%s LAB=(%.2f, %.2f, %.2f) "
            "HSV=(%.2f, %.2f, %.2f) "
            "C*=%.2f h=%.2f"
        ),
        features.rgb,
        *features.lab,
        *features.hsv,
        features.chroma,
        features.hue,
    )

    #
    # Native C++ perceptual color comparison.
    #
    logger.info(
        "Comparing iris color against %d reference profiles",
        len(REFERENCE_COLORS),
    )

    closest_profile, distance = _find_closest_profile(
        features
    )

    logger.info(
        "Closest reference profile is '%s' with ΔE %.2f",
        closest_profile.name,
        distance,
    )

    return ColorAnalysisResult(
        eye_color=eye_color,
        eye_rgb=features.rgb,
        lab=features.lab,
        hsv=features.hsv,
        chroma=features.chroma,
        hue=features.hue,
        closest_profile=closest_profile.name,
        profile_rgb=closest_profile.rgb,
        delta_e=distance,
        source="iris-segmentation",
        confidence=iris.confidence,
        eyes_detected=iris.eyes_detected,
    )