"""Shared fixtures: keep the default test suite off the AI model path."""

import importlib

import pytest

suggest_module = importlib.import_module("redsticks.suggest")


@pytest.fixture(autouse=True)
def no_ai_model(monkeypatch):
    """Force the quantization fallback so tests never download model weights.

    Individual tests re-patch ``extract_eye_rgb`` on the suggest module to
    simulate the AI path.
    """

    monkeypatch.setattr(suggest_module, "extract_eye_rgb", lambda image, device="cpu": None)
