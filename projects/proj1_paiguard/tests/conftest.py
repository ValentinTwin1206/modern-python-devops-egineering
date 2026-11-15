import pytest
from PIL import Image


class FakeModel:
    """A model that returns a fixed score and records its calls."""

    def __init__(self, score):
        self.fixed_score = score
        self.calls = 0

    def score(self, image):
        self.calls += 1
        return self.fixed_score


@pytest.fixture
def image():
    """A small harmless RGB image."""
    return Image.new("RGB", (32, 32), (20, 100, 150))


@pytest.fixture
def fake_model():
    """Factory for creating fake models with a fixed score."""
    return FakeModel
