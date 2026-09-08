"""Tests for the native CIELAB harmony scoring."""

from redsticks._native import harmony_score

BLUE_EYE = (70.0, 110.0, 180.0)
WARM_RED = (200.0, 16.0, 46.0)
COOL_BLUE = (40.0, 80.0, 200.0)


def test_score_is_bounded():
    score = harmony_score(*BLUE_EYE, *WARM_RED)
    assert 0.0 <= score <= 100.0


def test_score_is_deterministic():
    first = harmony_score(*BLUE_EYE, *WARM_RED)
    second = harmony_score(*BLUE_EYE, *WARM_RED)
    assert first == second


def test_complementary_shade_beats_same_hue():
    complementary = harmony_score(*BLUE_EYE, *WARM_RED)
    same_hue = harmony_score(*BLUE_EYE, *COOL_BLUE)
    assert complementary > same_hue
