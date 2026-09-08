"""Lipstick shade suggestion from an eye-color image."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from redsticks._native import harmony_score

from .pigments import CATALOG, pigment_details

_SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg"}


class UnsupportedImageError(ValueError):
    """Raised when the input image is missing or not a PNG/JPEG file."""


@dataclass(frozen=True, slots=True)
class SuggestionResult:
    """Public suggestion result returned by :func:`suggest`."""

    shade_name: str
    hex: str
    rgb: tuple[int, int, int]
    eye_rgb: tuple[int, int, int]
    harmony: int
    pigment_formula: str
    pigment_weight: float

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Eye color: rgb{self.eye_rgb}",
                f"Suggested shade: {self.shade_name}",
                f"Shade color: {self.hex}",
                f"Harmony: {self.harmony}/100",
                f"Pigment formula: {self.pigment_formula}",
                f"Pigment weight: {self.pigment_weight:.2f}",
            ]
        )

    __repr__ = __str__


def suggest(image_path: str | Path) -> SuggestionResult:
    """Suggest the lipstick shade that best matches the eye color in an image.

    Pillow extracts the dominant color of the image, the native C++ library
    scores every catalog shade against it in CIELAB space, and RDKit supplies
    the chemistry details of the winning pigment.
    """

    path = Path(image_path)
    if path.suffix.lower() not in _SUPPORTED_SUFFIXES or not path.is_file():
        raise UnsupportedImageError(f"Expected an existing PNG or JPEG file, got: {path}")

    with Image.open(path) as image:
        quantized = image.convert("RGB").quantize(colors=8)
        counts = quantized.getcolors()
        palette = quantized.getpalette()
    _, dominant_index = max(counts)
    eye_rgb = tuple(palette[dominant_index * 3 : dominant_index * 3 + 3])

    scored = [
        (harmony_score(*map(float, eye_rgb), *map(float, pigment.rgb)), pigment)
        for pigment in CATALOG
    ]
    best_score, best_pigment = max(scored, key=lambda pair: pair[0])

    _, formula, weight = pigment_details(best_pigment)
    return SuggestionResult(
        shade_name=best_pigment.name,
        hex="#{:02X}{:02X}{:02X}".format(*best_pigment.rgb),
        rgb=best_pigment.rgb,
        eye_rgb=eye_rgb,
        harmony=max(0, min(100, round(best_score))),
        pigment_formula=formula,
        pigment_weight=weight,
    )
