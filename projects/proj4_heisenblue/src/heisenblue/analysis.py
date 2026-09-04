"""High-level chemistry analysis API for HeisenBlue."""

from __future__ import annotations

from dataclasses import dataclass

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, rdMolDescriptors

from heisenblue._native import calculate_blue_score

from .color import score_to_hex, score_to_rgb


class InvalidSmilesError(ValueError):
    """Raised when a SMILES string cannot be parsed into a valid molecule."""


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Public analysis result returned by :func:`analyze`."""

    score: int
    hex: str
    rgb: tuple[int, int, int]
    formula: str
    molecular_weight: float
    smiles: str

    def __str__(self) -> str:
        lines = [
            f"Molecule: {self.smiles}",
            f"Formula: {self.formula}",
            f"Molecular weight: {self.molecular_weight:.2f}",
            f"Blue Score: {self.score}",
            f"Color: {self.hex}",
        ]
        return "\n".join(lines)

    __repr__ = __str__


def _build_result(smiles: str, molecular_weight: float, formula: str, score: int) -> AnalysisResult:
    rgb = score_to_rgb(score)
    return AnalysisResult(
        score=score,
        hex=score_to_hex(score),
        rgb=rgb,
        formula=formula,
        molecular_weight=molecular_weight,
        smiles=smiles,
    )


def analyze(smiles: str) -> AnalysisResult:
    """Analyze a molecule and assign a fictional Blue Score.

    RDKit handles all chemistry parsing and descriptor extraction. The native
    C++ extension receives only plain numeric descriptors and returns a
    deterministic score from 0 to 100.
    """

    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise InvalidSmilesError(f"Invalid SMILES string: {smiles!r}")

    normalized_smiles = Chem.MolToSmiles(molecule)
    molecular_weight = float(Descriptors.MolWt(molecule))
    formula = rdMolDescriptors.CalcMolFormula(molecule)
    aromatic_rings = int(rdMolDescriptors.CalcNumAromaticRings(molecule))
    heavy_atoms = int(molecule.GetNumHeavyAtoms())
    hetero_atoms = int(Lipinski.NumHeteroatoms(molecule))
    rotatable_bonds = int(rdMolDescriptors.CalcNumRotatableBonds(molecule))

    raw_score = calculate_blue_score(
        molecular_weight,
        aromatic_rings,
        heavy_atoms,
        hetero_atoms,
        rotatable_bonds,
    )
    score = max(0, min(100, int(round(raw_score))))
    return _build_result(normalized_smiles, molecular_weight, formula, score)