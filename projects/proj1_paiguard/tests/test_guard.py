import pytest
from PIL import Image

from paiguard import InspectionResult, PaiGuard
from paiguard.rules import PaiNsfwDetection, PaiViolenceDetection


def make_guard(fake_model, nsfw_score, violence_score):
    return PaiGuard(
        rules=[
            PaiNsfwDetection(
                threshold=0.8, review_threshold=0.5, model=fake_model(nsfw_score)
            ),
            PaiViolenceDetection(
                threshold=0.8, review_threshold=0.5, model=fake_model(violence_score)
            ),
        ]
    )


def test_empty_guard_allows_image(image):
    result = PaiGuard().inspect(image)

    assert isinstance(result, InspectionResult)
    assert result.decision == "allow"
    assert result.is_safe is True
    assert result.violations == []
    assert result.results == []


def test_guard_allows_image_with_low_scores(image, fake_model):
    result = make_guard(fake_model, 0.1, 0.2).inspect(image)

    assert result.decision == "allow"
    assert result.is_safe is True
    assert result.violations == []
    assert len(result.results) == 2


def test_guard_asks_for_review_inside_review_band(image, fake_model):
    result = make_guard(fake_model, 0.1, 0.6).inspect(image)

    assert result.decision == "review"
    assert result.is_safe is False
    assert result.violations == ["violence"]


def test_guard_blocks_image_with_high_score(image, fake_model):
    result = make_guard(fake_model, 0.9, 0.1).inspect(image)

    assert result.decision == "block"
    assert result.is_safe is False
    assert result.violations == ["nsfw"]


def test_block_wins_over_review(image, fake_model):
    result = make_guard(fake_model, 0.6, 0.95).inspect(image)

    assert result.decision == "block"
    assert result.violations == ["nsfw", "violence"]


def test_guard_runs_all_rules_after_a_detection(image, fake_model):
    first = fake_model(0.99)
    second = fake_model(0.0)
    guard = PaiGuard(
        rules=[PaiNsfwDetection(model=first), PaiViolenceDetection(model=second)]
    )

    guard.inspect(image)

    assert first.calls == 1
    assert second.calls == 1


def test_guard_converts_image_to_rgb(fake_model):
    seen_modes = []

    class ModeModel:
        def score(self, image):
            seen_modes.append(image.mode)
            return 0.0

    guard = PaiGuard(rules=[PaiNsfwDetection(model=ModeModel())])

    guard.inspect(Image.new("RGBA", (8, 8)))

    assert seen_modes == ["RGB"]


def test_guard_rejects_non_image_input():
    with pytest.raises(TypeError, match="PIL.Image.Image"):
        PaiGuard().inspect("uploads/image.jpg")
