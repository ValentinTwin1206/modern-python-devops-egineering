"""Shared fixtures: keep the default test suite off the AI model path."""

import importlib

import pytest
from PIL import Image

suggest_module = importlib.import_module("redsticks.suggest")
from redsticks.iris import IrisResult


@pytest.fixture(autouse=True)
def no_ai_model(monkeypatch):
    """Use the test image color without loading model weights.

    Individual tests re-patch ``extract_iris`` to simulate detection failure
    or a particular model result.
    """

    def fake_extract_iris(image: Image.Image, device: str = "cpu") -> IrisResult:
        rgb = image.convert("RGB").getpixel((0, 0))
        return IrisResult(rgb=rgb, confidence=0.9, eyes_detected=1)

    monkeypatch.setattr(suggest_module, "extract_iris", fake_extract_iris)
