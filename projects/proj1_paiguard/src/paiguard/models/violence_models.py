"""Violence image model adapters."""

import logging
from pathlib import Path

from PIL import Image

from .base import (
    SIGLIP_ENCODER_FILES,
    SIGLIP_HEAD_FILES,
    PaiModel,
    import_inference_libraries,
    model_dir,
    require_files,
    sigmoid,
)

logger = logging.getLogger("paiguard")


class SiglipViolenceModel(PaiModel):
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
