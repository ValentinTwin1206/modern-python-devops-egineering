"""Lipstick shade suggestion from an eye-color image."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

from redsticks._native import harmony_score
from .eye_color import EyeColor, classify_eye_color
from .iris import extract_iris


_SUPPORTED_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
}

logger = logging.getLogger("redsticks")


class EyeColorDetectionError(ValueError):
    """Raised when an image does not contain a reliable iris."""


@dataclass(frozen=True, slots=True)
class SuggestionResult:
    """Public suggestion returned by :func:`suggest`."""

    shade_name: str
    hex: str
    rgb: tuple[int, int, int]

    eye_rgb: tuple[int, int, int]
    eye_color: EyeColor

    harmony: int

    pigment_formula: str
    pigment_weight: float

    source: str
    confidence: float
    eyes_detected: int


@dataclass(frozen=True, slots=True)
class Pigment:
    """Lipstick shade backed by a cosmetic pigment molecule."""

    name: str
    smiles: str
    rgb: tuple[int, int, int]


CATALOG: tuple[Pigment, ...] = (
    Pigment(
        "Classic Red (Red 7 Lake)",
        "Cc1ccc(S(=O)(=O)O)c(N=Nc2c(O)c(C(=O)O)cc3ccccc23)c1",
        (200, 16, 46),
    ),
    Pigment(
        "Coral Flame (Red 6)",
        "Cc1ccc(S(=O)(=O)O)c(N=Nc2c(O)c(C(=O)O)cc3ccccc23)c1S(=O)(=O)O",
        (255, 88, 76),
    ),
    Pigment(
        "Carmine Crush (Carminic Acid)",
        "Cc1c(C(=O)O)c(O)cc2c1C(=O)c1c(O)c(C3OC(CO)C(O)C(O)C3O)c(O)c(O)c1C2=O",
        (150, 0, 24),
    ),
    Pigment(
        "Pink Pop (Eosin / Red 21)",
        "O=C(O)c1ccccc1-c1c2cc(Br)c(=O)c(Br)c-2oc2c(Br)c(O)c(Br)cc12",
        (255, 64, 129),
    ),
    Pigment(
        "Nude Amber (Beta-Carotene)",
        "CC1=C(C(C)(C)CCC1)/C=C/C(C)=C/C=C/C(C)=C/C=C/C=C(C)/C=C/C=C(C)/C=C/C1=C(C)CCCC1(C)C",
        (222, 152, 111),
    ),
    Pigment(
        "Deep Rosewood (Alizarin)",
        "O=C1c2ccccc2C(=O)c2c1ccc(O)c2O",
        (155, 62, 74),
    ),
)


def _pigment_details(pigment: Pigment) -> tuple[str, float]:
    """Return molecular formula and weight."""

    molecule = Chem.MolFromSmiles(
        pigment.smiles
    )

    if molecule is None:
        raise ValueError(
            f"Invalid pigment SMILES for {pigment.name!r}"
        )

    return (
        rdMolDescriptors.CalcMolFormula(molecule),
        float(Descriptors.MolWt(molecule)),
    )


#
# Public API
# # # # # # # 
def suggest(image_path: Path, device: str = "cpu") -> SuggestionResult:
    """Suggest a lipstick shade from iris pigmentation."""

    # Unsupported file format
    if image_path.suffix.lower() not in _SUPPORTED_SUFFIXES:
        raise ValueError(f"The file format '{image_path.suffix.lower()}' is not supported.")

    # File not accessible
    if not image_path.is_file():
        raise ValueError(f"The file '{image_path}' does not exist or is not accessible.")

    # Extract iris pigmentation from the image
    logger.info("Trying to extract iris from '%s' using '%s' device", image_path, device)
    with Image.open(image_path) as image:
        iris = extract_iris(image=image, device=device)

    if iris is None:
        raise EyeColorDetectionError("Could not reliably detect an iris. Use a portrait with clearly visible eye(s).")

    logger.info("Extracted iris from image with RGB '%s' and confidence %.2f", iris.rgb, iris.confidence)

    # Classify eye color (e.g. blue, green, brown)
    logger.info("Trying to classify eye color")
    eye_color = classify_eye_color(iris.pixels)
    logger.info("Classified eye color '%s' for RGB '%s'", eye_color.value, iris.rgb)

    # Leverage native extenstion for harmony scoring
    logger.info("Trying harmony scoring for '%d' pigments", len(CATALOG))
    scored = [
        (
            harmony_score(
                *map(float, iris.rgb),
                *map(float, pigment.rgb),
            ),
            pigment,
        )
        for pigment in CATALOG
    ]

    best_score, best_pigment = max(scored, key=lambda pair: pair[0])
    logger.debug(
        "Selected pigment '%s' with harmony score %.2f",
        best_pigment.name,
        best_score,
    )

    logger.debug("Calling _pigment_details() for %s", best_pigment.name)
    formula, weight = _pigment_details(
        best_pigment
    )

    return SuggestionResult(
        shade_name=best_pigment.name,
        hex="#{:02X}{:02X}{:02X}".format(
            *best_pigment.rgb
        ),
        rgb=best_pigment.rgb,
        eye_rgb=iris.rgb,
        eye_color=eye_color,
        harmony=max(
            0,
            min(
                100,
                round(best_score),
            ),
        ),
        pigment_formula=formula,
        pigment_weight=weight,
        source="iris-landmarks",
        confidence=iris.confidence,
        eyes_detected=iris.eyes_detected,
    )