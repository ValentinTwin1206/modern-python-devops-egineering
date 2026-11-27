"""Shared model interfaces and utilities for local inference."""

import logging
import math
import os
from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image

logger = logging.getLogger("paiguard")

DEFAULT_MODEL_DIR = "/opt/paiguard/models"

FALCONSAI_FILES = ["config.json", "preprocessor_config.json", "model.safetensors"]
SIGLIP_ENCODER_FILES = ["config.json", "preprocessor_config.json", "model.safetensors"]
SIGLIP_HEAD_FILES = ["violence_head.onnx", "violence_head.onnx.data"]


class PaiModel(ABC):
    """Base interface for lazily loaded pAIguard scoring models."""

    @abstractmethod
    def load(self) -> None:
        """Load model assets and initialize the inference backend."""
        raise NotImplementedError

    @abstractmethod
    def score(self, image: Image.Image) -> float:
        """Return the model's score for an image."""
        raise NotImplementedError


def model_dir() -> Path:
    """Return the directory that contains all pAIguard models."""
    return Path(os.environ.get("PAIGUARD_MODEL_DIR", DEFAULT_MODEL_DIR)).expanduser()


def require_files(directory: Path, names: list[str]) -> None:
    """Raise FileNotFoundError when a required model file is missing or empty."""
    for name in names:
        path = directory / name
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(
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
