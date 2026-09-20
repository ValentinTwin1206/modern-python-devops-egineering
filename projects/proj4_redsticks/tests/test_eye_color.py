"""Tests for semantic eye-color classification."""

import pytest

from redsticks.eye_color import describe_eye_color


@pytest.mark.parametrize(
    ("rgb", "expected"),
    [
        ((80, 76, 57), "Green"),
        ((72, 57, 46), "Brown"),
        ((108, 68, 39), "Brown"),
    ],
)
def test_dark_chromatic_eye_colors_are_not_classified_as_gray(rgb, expected):
    assert describe_eye_color(rgb) == expected


def test_neutral_eye_color_remains_gray():
    assert describe_eye_color((128, 128, 128)) == "Gray"