"""AI-assisted eye-region color extraction using an open-weight model.

Downloads the open-weight face-parsing model `jonathandinu/face-parsing``
(SegFormer) from the Hugging Face Hub on first use, segments the image, and
returns the dominant color of the eye-region pixels only.

Returns `None` when the model is unavailable (e.g. offline and not cached)
or when no eye pixels are detected, so the caller can fall back to plain
color quantization.
"""

from __future__ import annotations

import logging

# Third-party libraries
import numpy as np
import torch
from PIL.Image import Image
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation

logger = logging.getLogger("redsticks")

_EYE_LABELS = {"l_eye", "r_eye", "left_eye", "right_eye"}
_MODEL_CACHE: dict[str, tuple[AutoImageProcessor, AutoModelForSemanticSegmentation]] = {}


def cuda_available() -> bool:
    """Return True when PyTorch sees a CUDA device."""
    return torch.cuda.is_available()


def _load_model():
    """Load and cache the segmentation model and its image processor."""

    model_id = "jonathandinu/face-parsing"
    if model_id not in _MODEL_CACHE:
        processor = AutoImageProcessor.from_pretrained(model_id)
        model = AutoModelForSemanticSegmentation.from_pretrained(model_id)
        model.eval()
        _MODEL_CACHE[model_id] = (processor, model)
    return _MODEL_CACHE[model_id]


def extract_eye_rgb(image: Image, device: str = "cpu") -> tuple[int, int, int] | None:
    """Return the dominant RGB color of the eye pixels in *image*.

    Returns `None` when the model cannot be downloaded or no eye pixels are
    detected, so callers can fall back to whole-image quantization.
    """

    try:
        processor, model = _load_model()
    except Exception as error:  # offline, missing weights, hub errors
        logger.info("Face-parsing model unavailable (%s); falling back", error)
        return None

    rgb_image = image.convert("RGB")
    model = model.to(device)
    inputs = processor(images=rgb_image, return_tensors="pt").to(device)

    with torch.no_grad():
        logits = model(**inputs).logits

    upsampled = torch.nn.functional.interpolate(
        logits,
        size=rgb_image.size[::-1],  # (height, width)
        mode="bilinear",
        align_corners=False,
    )
    label_map = upsampled.argmax(dim=1)[0].cpu()

    eye_ids = [
        idx for idx, label in model.config.id2label.items() if label in _EYE_LABELS
    ]
    mask = torch.zeros_like(label_map, dtype=torch.bool)
    for idx in eye_ids:
        mask |= label_map == int(idx)

    if not bool(mask.any()):
        logger.info("No eye pixels detected; falling back to quantization")
        return None

    pixels = np.asarray(rgb_image)[mask.numpy()]
    dominant = pixels.mean(axis=0).round().astype(int)
    return (int(dominant[0]), int(dominant[1]), int(dominant[2]))
