"""Tests for the shade suggestion pipeline."""

import importlib

import pytest
from PIL import Image

suggest_module = importlib.import_module("redsticks.suggest")

from redsticks import SuggestionResult, UnsupportedImageError, suggest
from redsticks.pigments import CATALOG


def _write_eye_image(path, rgb):
    Image.new("RGB", (64, 64), rgb).save(path)


def test_suggest_returns_catalog_shade(tmp_path):
    image = tmp_path / "blue-eye.png"
    _write_eye_image(image, (70, 110, 180))

    result = suggest(image)

    assert isinstance(result, SuggestionResult)
    assert result.shade_name in {pigment.name for pigment in CATALOG}
    assert result.hex.startswith("#") and len(result.hex) == 7
    assert 0 <= result.harmony <= 100
    assert result.eye_rgb == (70, 110, 180)


def test_suggest_accepts_jpeg(tmp_path):
    image = tmp_path / "green-eye.jpg"
    _write_eye_image(image, (90, 140, 80))

    result = suggest(image)

    assert result.pigment_weight > 100.0


def test_suggest_rejects_unsupported_extension(tmp_path):
    bad = tmp_path / "eye.gif"
    _write_eye_image(bad, (70, 110, 180))

    with pytest.raises(UnsupportedImageError):
        suggest(bad)


def test_suggest_rejects_missing_file(tmp_path):
    with pytest.raises(UnsupportedImageError):
        suggest(tmp_path / "missing.png")


def test_suggest_falls_back_to_quantization_without_eyes(tmp_path):
    image = tmp_path / "eye.png"
    _write_eye_image(image, (70, 110, 180))

    result = suggest(image)

    assert result.source == "quantize"


def test_suggest_uses_ai_eye_color_when_available(tmp_path, monkeypatch):
    image = tmp_path / "eye.png"
    _write_eye_image(image, (70, 110, 180))
    monkeypatch.setattr(
        suggest_module, "extract_eye_rgb", lambda image, device="cpu": (10, 20, 30)
    )

    result = suggest(image)

    assert result.source == "ai"
    assert result.eye_rgb == (10, 20, 30)
