"""Tests for the pigment catalog and RDKit-backed details."""

import pytest

from redsticks.pigments import CATALOG, Pigment, pigment_details


def test_catalog_is_populated():
    assert len(CATALOG) >= 4
    assert all(isinstance(pigment, Pigment) for pigment in CATALOG)


def test_pigment_details_returns_chemistry():
    for pigment in CATALOG:
        canonical_smiles, formula, weight = pigment_details(pigment)
        assert canonical_smiles
        assert formula.startswith("C")
        assert weight > 100.0


def test_pigment_details_rejects_invalid_smiles():
    broken = Pigment("Broken", "not-a-smiles", (0, 0, 0))
    with pytest.raises(ValueError):
        pigment_details(broken)
