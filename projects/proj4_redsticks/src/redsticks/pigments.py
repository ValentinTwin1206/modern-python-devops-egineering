"""Cosmetic pigment catalog backed by RDKit chemistry."""

from __future__ import annotations

from dataclasses import dataclass

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors


@dataclass(frozen=True, slots=True)
class Pigment:
    """A lipstick shade backed by a real cosmetic pigment molecule."""

    name: str
    smiles: str
    rgb: tuple[int, int, int]


#: Catalog of lipstick shades and their backing pigment molecules.
CATALOG: tuple[Pigment, ...] = (
    Pigment("Classic Red (Red 7 Lake)", "Cc1ccc(S(=O)(=O)O)c(N=Nc2c(O)c(C(=O)O)cc3ccccc23)c1", (200, 16, 46)),
    Pigment("Coral Flame (Red 6)", "Cc1ccc(S(=O)(=O)O)c(N=Nc2c(O)c(C(=O)O)cc3ccccc23)c1S(=O)(=O)O", (255, 88, 76)),
    Pigment("Carmine Crush (Carminic Acid)", "Cc1c(C(=O)O)c(O)cc2c1C(=O)c1c(O)c(C3OC(CO)C(O)C(O)C3O)c(O)c(O)c1C2=O", (150, 0, 24)),
    Pigment("Pink Pop (Eosin / Red 21)", "O=C(O)c1ccccc1-c1c2cc(Br)c(=O)c(Br)c-2oc2c(Br)c(O)c(Br)cc12", (255, 64, 129)),
    Pigment("Nude Amber (Beta-Carotene)", "CC1=C(C(C)(C)CCC1)/C=C/C(C)=C/C=C/C(C)=C/C=C/C=C(C)/C=C/C=C(C)/C=C/C1=C(C)CCCC1(C)C", (222, 152, 111)),
    Pigment("Deep Rosewood (Alizarin)", "O=C1c2ccccc2C(=O)c2c1ccc(O)c2O", (155, 62, 74)),
)


def pigment_details(pigment: Pigment) -> tuple[str, str, float]:
    """Return the canonical SMILES, formula, and molecular weight of a pigment."""

    molecule = Chem.MolFromSmiles(pigment.smiles)
    if molecule is None:
        raise ValueError(f"Invalid pigment SMILES for {pigment.name!r}")
    return (
        Chem.MolToSmiles(molecule),
        rdMolDescriptors.CalcMolFormula(molecule),
        float(Descriptors.MolWt(molecule)),
    )
