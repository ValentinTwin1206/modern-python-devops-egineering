"""PNG rendering helpers for HeisenBlue analysis results."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw, ImageFont
from rdkit import Chem
from rdkit.Chem import Draw

from .analysis import AnalysisResult


PathLike = Union[str, Path]


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def render(result: AnalysisResult, output_path: PathLike, show_molecule: bool = False) -> None:
    """Render a compact PNG summary for an analysis result."""

    width = 900
    height = 620 if show_molecule else 420
    image = Image.new("RGB", (width, height), color=(245, 248, 252))
    draw = ImageDraw.Draw(image)

    title_font = _load_font(28)
    body_font = _load_font(20)
    small_font = _load_font(16)

    draw.text((40, 30), "HEISENBLUE", fill=(15, 32, 64), font=title_font)
    draw.text((40, 85), f"SMILES: {result.smiles}", fill=(30, 45, 75), font=body_font)
    draw.text((40, 125), f"Formula: {result.formula}", fill=(30, 45, 75), font=body_font)
    draw.text(
        (40, 165),
        f"Molecular weight: {result.molecular_weight:.2f}",
        fill=(30, 45, 75),
        font=body_font,
    )
    draw.text((40, 205), f"Blue Score: {result.score}", fill=(30, 45, 75), font=body_font)
    draw.text((40, 245), f"HEX color: {result.hex}", fill=(30, 45, 75), font=body_font)

    swatch_box = (520, 70, 840, 280)
    draw.rounded_rectangle(swatch_box, radius=24, fill=result.rgb, outline=(25, 45, 85), width=3)
    draw.text((615, 295), result.hex, fill=(15, 32, 64), font=small_font)

    if show_molecule:
        molecule = Chem.MolFromSmiles(result.smiles)
        if molecule is not None:
            depiction = Draw.MolToImage(molecule, size=(360, 220))
            image.paste(depiction, (40, 330))
            draw.text((40, 560), "RDKit depiction", fill=(70, 84, 112), font=small_font)

    image.save(Path(output_path), format="PNG")