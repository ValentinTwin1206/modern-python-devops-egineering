"""NSFW image model adapters."""

import logging
from pathlib import Path

from PIL import Image

from .base import (
    FALCONSAI_FILES,
    PaiModel,
    find_label_index,
    import_inference_libraries,
    model_dir,
    require_files,
)

logger = logging.getLogger("paiguard")


class FalconsaiNsfwModel(PaiModel):
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
