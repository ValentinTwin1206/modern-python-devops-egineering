from __future__ import annotations

import pytest

from heisenblue._native import calculate_blue_score


def test_calculate_blue_score_returns_stable_value() -> None:
    score = calculate_blue_score(46.069, 0, 3, 1, 0)

    assert score == pytest.approx(24.1560375)


def test_calculate_blue_score_is_clamped() -> None:
    score = calculate_blue_score(1200.0, 10, 80, 20, 0)

    assert score == pytest.approx(100.0)