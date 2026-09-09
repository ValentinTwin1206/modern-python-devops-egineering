"""Lipstick shade suggestion from an eye-color image."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from redsticks._native import harmony_score

from .iris import extract_eye_rgb
from .pigments import CATALOG, pigment_details

_SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg"}


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
    source: str = "quantize"

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Eye color: rgb{self.eye_rgb}",
                f"Eye color source: {self.source}",
                f"Suggested shade: {self.shade_name}",
                f"Shade color: {self.hex}",
                f"Harmony: {self.harmony}/100",
                f"Pigment formula: {self.pigment_formula}",
                f"Pigment weight: {self.pigment_weight:.2f}",
            ]
        )

    __repr__ = __str__


def suggest(image_path: str | Path, *, device: str = "cpu") -> SuggestionResult:
    """Suggest the lipstick shade that best matches the eye color in an image."""

    path = Path(image_path)
    if path.suffix.lower() not in _SUPPORTED_SUFFIXES or not path.is_file():
        raise ValueError(f"Expected an existing PNG or JPEG file, got: {path}")

    source = "ai"
    with Image.open(path) as image:
        eye_rgb = extract_eye_rgb(image, device=device)
        if eye_rgb is None:
            source = "quantize"
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
        source=source,
    )
