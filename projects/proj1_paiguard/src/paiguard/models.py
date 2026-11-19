"""
Model adapters used by the moderation rules.

The model files are never downloaded by pAIguard. They must already exist in
the model directory, which is read from the PAIGUARD_MODEL_DIR environment
variable. Each adapter loads its model on the first call to `score()`.
"""

import logging
import math
import os
from pathlib import Path

from PIL import Image

logger = logging.getLogger("paiguard")

DEFAULT_MODEL_DIR = "/opt/paiguard/models"

FALCONSAI_FILES = ["config.json", "preprocessor_config.json", "model.safetensors"]
SIGLIP_ENCODER_FILES = ["config.json", "preprocessor_config.json", "model.safetensors"]
SIGLIP_HEAD_FILES = ["violence_head.onnx", "violence_head.onnx.data"]


class ModelNotFoundError(Exception):
    """Raised when required model files are missing on disk."""


def model_dir() -> Path:
    """Return the directory that contains all pAIguard models."""
    return Path(os.environ.get("PAIGUARD_MODEL_DIR", DEFAULT_MODEL_DIR)).expanduser()


def require_files(directory: Path, names: list[str]) -> None:
    """Raise ModelNotFoundError when one of the files is missing or empty."""
    for name in names:
        path = directory / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ModelNotFoundError(
                f"Model file not found: {path}. Download the pAIguard models "
                "and point PAIGUARD_MODEL_DIR to their directory."
            )


def import_inference_libraries():
    """Import the optional inference libraries of the `models` extra."""
    try:
        import numpy
        import onnxruntime
        import torch
        import transformers
    except ImportError as error:
        raise ImportError(
            "The pAIguard models need extra packages. "
            'Install them with: pip install "paiguard[models]"'
        ) from error

    return numpy, onnxruntime, torch, transformers


def sigmoid(logit: float) -> float:
    """Convert a logit into a score between 0 and 1."""
    return 1.0 / (1.0 + math.exp(-logit))


def find_label_index(id2label: dict, label: str) -> int:
    """Return the output index that belongs to the given label name."""
    for index, name in id2label.items():
        if name.lower() == label:
            return int(index)

    raise ValueError(f"The model has no '{label}' label: {id2label}")


class FalconsaiNsfwModel:
    """
    Falconsai/nsfw_image_detection: a ViT classifier with the labels
    `normal` and `nsfw`. The score is the softmax value of `nsfw`.
    """

    def __init__(self, directory: Path | None = None):
        self.directory = directory
        self.processor = None
        self.model = None
        self.nsfw_index = None

    def load(self) -> None:
        directory = self.directory or model_dir() / "falconsai-nsfw"
        require_files(directory, FALCONSAI_FILES)

        _, _, _, transformers = import_inference_libraries()

        logger.info("Loading NSFW model from %s", directory)
        self.processor = transformers.AutoImageProcessor.from_pretrained(
            directory, local_files_only=True
        )
        self.model = transformers.AutoModelForImageClassification.from_pretrained(
            directory, local_files_only=True
        )
        self.model.eval()
        self.nsfw_index = find_label_index(self.model.config.id2label, "nsfw")

    def score(self, image: Image.Image) -> float:
        if self.model is None:
            self.load()

        _, _, torch, _ = import_inference_libraries()

        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            logits = self.model(**inputs).logits

        probabilities = torch.softmax(logits, dim=-1)
        return float(probabilities[0, self.nsfw_index])


class SiglipViolenceModel:
    """
    Violence head of khasinski/siglip2-moderation-heads.

    The frozen image encoder of google/siglip2-base-patch16-256 turns the
    image into a normalized embedding. The small ONNX head turns the
    embedding into a logit, and a sigmoid turns the logit into the score.
    """

    def __init__(
        self,
        encoder_directory: Path | None = None,
        head_directory: Path | None = None,
    ):
        self.encoder_directory = encoder_directory
        self.head_directory = head_directory
        self.processor = None
        self.encoder = None
        self.head = None

    def load(self) -> None:
        encoder_directory = self.encoder_directory or model_dir() / "siglip2-base"
        head_directory = self.head_directory or model_dir() / "siglip2-heads"
        require_files(encoder_directory, SIGLIP_ENCODER_FILES)
        require_files(head_directory, SIGLIP_HEAD_FILES)

        _, onnxruntime, _, transformers = import_inference_libraries()

        logger.info("Loading violence model from %s", encoder_directory)
        self.processor = transformers.AutoImageProcessor.from_pretrained(
            encoder_directory, local_files_only=True
        )
        # Only the image encoder is needed, not the text encoder.
        self.encoder = transformers.SiglipVisionModel.from_pretrained(
            encoder_directory, local_files_only=True
        )
        self.encoder.eval()
        self.head = onnxruntime.InferenceSession(
            str(head_directory / "violence_head.onnx"),
            providers=["CPUExecutionProvider"],
        )

    def score(self, image: Image.Image) -> float:
        if self.head is None:
            self.load()

        numpy, _, torch, _ = import_inference_libraries()

        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            embedding = self.encoder(**inputs).pooler_output

        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        embedding = embedding.numpy().astype(numpy.float32)

        logits = self.head.run(None, {"embedding": embedding})[0]
        return sigmoid(float(logits[0, 0]))
