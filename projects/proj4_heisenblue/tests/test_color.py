from __future__ import annotations

from heisenblue.color import rgb_to_hex, score_to_hex, score_to_rgb


def test_score_zero_maps_to_light_blue() -> None:
    assert score_to_rgb(0) == (214, 233, 255)
    assert score_to_hex(0) == "#D6E9FF"


def test_score_fifty_maps_to_mid_blue() -> None:
    assert score_to_rgb(50) == (77, 139, 214)
    assert score_to_hex(50) == "#4D8BD6"


def test_score_hundred_maps_to_deep_blue() -> None:
    assert score_to_rgb(100) == (11, 55, 125)
    assert score_to_hex(100) == "#0B377D"


def test_rgb_to_hex_converts_uppercase_hex() -> None:
    assert rgb_to_hex((58, 115, 193)) == "#3A73C1"