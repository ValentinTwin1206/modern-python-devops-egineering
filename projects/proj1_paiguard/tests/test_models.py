import os

import pytest
from PIL import Image

from paiguard import ModelNotFoundError, models
from paiguard.models import FalconsaiNsfwModel, SiglipViolenceModel


def test_model_dir_uses_default(monkeypatch):
    monkeypatch.delenv("PAIGUARD_MODEL_DIR", raising=False)

    assert str(models.model_dir()) == "/opt/paiguard/models"


def test_model_dir_reads_environment_variable(monkeypatch, tmp_path):
    monkeypatch.setenv("PAIGUARD_MODEL_DIR", str(tmp_path))

    assert models.model_dir() == tmp_path


def test_missing_nsfw_model_raises_useful_error(monkeypatch, tmp_path, image):
    monkeypatch.setenv("PAIGUARD_MODEL_DIR", str(tmp_path))

    with pytest.raises(ModelNotFoundError) as error:
        FalconsaiNsfwModel().score(image)

    assert str(tmp_path / "falconsai-nsfw" / "config.json") in str(error.value)
    assert "PAIGUARD_MODEL_DIR" in str(error.value)


def test_missing_violence_head_raises_useful_error(tmp_path, image):
    encoder_directory = tmp_path / "siglip2-base"
    encoder_directory.mkdir()
    for name in models.SIGLIP_ENCODER_FILES:
        (encoder_directory / name).write_bytes(b"x")

    model = SiglipViolenceModel(
        encoder_directory=encoder_directory,
        head_directory=tmp_path / "siglip2-heads",
    )

    with pytest.raises(ModelNotFoundError, match="violence_head.onnx"):
        model.score(image)


def test_empty_model_file_counts_as_missing(tmp_path):
    (tmp_path / "config.json").write_bytes(b"")

    with pytest.raises(ModelNotFoundError):
        models.require_files(tmp_path, ["config.json"])


def test_sigmoid_turns_logits_into_scores():
    assert models.sigmoid(0.0) == 0.5
    assert models.sigmoid(10.0) > 0.99
    assert models.sigmoid(-10.0) < 0.01


def test_find_label_index_reads_model_labels():
    assert models.find_label_index({0: "normal", 1: "nsfw"}, "nsfw") == 1
    assert models.find_label_index({"0": "NSFW", "1": "normal"}, "nsfw") == 0

    with pytest.raises(ValueError, match="no 'nsfw' label"):
        models.find_label_index({0: "cat", 1: "dog"}, "nsfw")


# The tests below run the real models. They are skipped unless the model
# files exist in PAIGUARD_MODEL_DIR. They never use the network.
real_models = pytest.mark.skipif(
    not (models.model_dir() / "falconsai-nsfw" / "model.safetensors").is_file()
    or not (models.model_dir() / "siglip2-base" / "model.safetensors").is_file()
    or not os.environ.get("PAIGUARD_MODEL_DIR"),
    reason="PAIGUARD_MODEL_DIR does not point to the real model files",
)


@real_models
def test_real_nsfw_model_scores_harmless_image():
    pytest.importorskip("torch")
    harmless = Image.new("RGB", (256, 256), (20, 100, 150))

    score = FalconsaiNsfwModel().score(harmless)

    assert 0.0 <= score < 0.5


@real_models
def test_real_violence_model_scores_harmless_image():
    pytest.importorskip("torch")
    harmless = Image.new("RGB", (256, 256), (20, 100, 150))

    score = SiglipViolenceModel().score(harmless)

    assert 0.0 <= score < 0.5
