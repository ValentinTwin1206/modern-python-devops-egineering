import pytest

from paiguard.models import FalconsaiNsfwModel, SiglipViolenceModel
from paiguard.rules import PaiNsfwDetection, PaiRule, PaiViolenceDetection


def test_nsfw_rule_maps_model_score_to_result(image, fake_model):
    rule = PaiNsfwDetection(threshold=0.8, model=fake_model(0.93))

    result = rule.inspect(image)

    assert result.rule == "PaiNsfwDetection"
    assert result.category == "nsfw"
    assert result.score == 0.93
    assert result.detected is True
    assert result.needs_review is False
    assert result.details["threshold"] == 0.8
    assert result.details["model"] == "FakeModel"


def test_violence_rule_maps_model_score_to_result(image, fake_model):
    rule = PaiViolenceDetection(threshold=0.85, model=fake_model(0.12))

    result = rule.inspect(image)

    assert result.rule == "PaiViolenceDetection"
    assert result.category == "violence"
    assert result.score == 0.12
    assert result.detected is False
    assert result.needs_review is False


@pytest.mark.parametrize(
    ("score", "detected"),
    [(0.49, False), (0.50, True), (0.51, True)],
)
def test_threshold_is_configurable_and_inclusive(image, fake_model, score, detected):
    rule = PaiNsfwDetection(threshold=0.5, model=fake_model(score))

    assert rule.inspect(image).detected is detected


@pytest.mark.parametrize(
    ("score", "needs_review"),
    [(0.39, False), (0.40, True), (0.79, True), (0.80, False)],
)
def test_review_threshold_marks_scores_below_threshold(
    image, fake_model, score, needs_review
):
    rule = PaiViolenceDetection(
        threshold=0.8, review_threshold=0.4, model=fake_model(score)
    )

    assert rule.inspect(image).needs_review is needs_review


def test_no_review_without_review_threshold(image, fake_model):
    rule = PaiNsfwDetection(threshold=0.8, model=fake_model(0.79))

    assert rule.inspect(image).needs_review is False


def test_default_thresholds_and_models():
    nsfw = PaiNsfwDetection()
    violence = PaiViolenceDetection()

    assert nsfw.threshold == 0.80
    assert violence.threshold == 0.85
    assert isinstance(nsfw.model, FalconsaiNsfwModel)
    assert isinstance(violence.model, SiglipViolenceModel)
    # Creating a rule must not load the model.
    assert nsfw.model.model is None
    assert violence.model.head is None


def test_invalid_thresholds_are_rejected(fake_model):
    with pytest.raises(ValueError, match="between 0 and 1"):
        PaiNsfwDetection(threshold=1.5, model=fake_model(0.0))

    with pytest.raises(ValueError, match="review_threshold"):
        PaiNsfwDetection(threshold=0.5, review_threshold=0.6, model=fake_model(0.0))


def test_custom_rule_can_subclass_pai_rule():
    with pytest.raises(TypeError):
        PaiRule()
