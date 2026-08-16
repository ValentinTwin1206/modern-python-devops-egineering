from __future__ import annotations

import pytest

from heisenblue.analysis import InvalidSmilesError, analyze


def test_analyze_valid_smiles_returns_expected_fields() -> None:
    result = analyze("CCO")

    assert result.smiles == "CCO"
    assert result.formula == "C2H6O"
    assert result.molecular_weight == pytest.approx(46.069, rel=1e-3)
    assert result.score == 24
    assert result.hex == "#94BCEB"
    assert result.rgb == (148, 188, 235)


def test_analyze_invalid_smiles_raises_useful_error() -> None:
    with pytest.raises(InvalidSmilesError, match="Invalid SMILES string"):
        analyze("not-a-smiles")


def test_analyze_returns_deterministic_blue_score() -> None:
    first = analyze("c1ccccc1")
    second = analyze("c1ccccc1")

    assert first.score == second.score


def test_blue_score_is_clamped_to_valid_range() -> None:
    result = analyze("CCN(CC)CCOc1ccc2nc(S(N)(=O)=O)sc2c1")

    assert 0 <= result.score <= 100