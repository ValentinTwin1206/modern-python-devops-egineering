"""Tests for model-independent iris sampling."""

import numpy as np
from PIL import Image

from redsticks.iris import (
    _filter_iris_pixels,
    _iris_candidate_mask_from_center,
    _robust_color,
    extract_iris,
)


def test_pupil_center_moves_iris_mask_with_gaze():
    image = np.full((40, 80, 3), (70, 130, 80), dtype=np.uint8)
    image[18:23, 50:55] = (15, 15, 15)
    eye_mask = np.zeros((40, 80), dtype=bool)
    eye_mask[10:30, 20:70] = True

    candidate = _iris_candidate_mask_from_center(image, eye_mask)

    assert candidate is not None
    ys, xs = np.where(candidate)
    assert xs.mean() > 45
    assert 15 < ys.mean() < 25


def test_filter_and_median_ignore_pupil_and_sclera():
    image = np.full((20, 30, 3), (70, 130, 80), dtype=np.uint8)
    image[8:12, 13:17] = (10, 10, 10)
    image[0:2, :] = (245, 245, 245)
    mask = np.ones((20, 30), dtype=bool)

    pixels = _filter_iris_pixels(image, mask)

    assert _robust_color(pixels) == (70, 130, 80)


def test_extract_iris_returns_color_from_segmented_eye(monkeypatch):
    array = np.full((40, 80, 3), (60, 135, 75), dtype=np.uint8)
    array[18:23, 50:55] = (15, 15, 15)
    image = Image.fromarray(array)
    eye_mask = np.zeros((40, 80), dtype=bool)
    eye_mask[10:30, 20:70] = True

    monkeypatch.setattr(
        "redsticks.iris._segment_eyes",
        lambda image, device: [eye_mask],
    )

    result = extract_iris(image)

    assert result is not None
    assert result.rgb[1] > result.rgb[0]
    assert result.rgb[1] > result.rgb[2]
    assert result.eyes_detected == 1
