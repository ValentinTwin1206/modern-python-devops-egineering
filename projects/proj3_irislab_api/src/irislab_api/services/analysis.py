"""Validate uploads, moderate them and adapt IrisLab's path-based API."""

import logging
import os
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO

from irislab import analyze
from irislab.iris import model_path
from paiguard import ModelNotFoundError, PaiGuard
from paiguard.rules import PaiNsfwDetection, PaiViolenceDetection
from PIL import Image, UnidentifiedImageError

from ..schemas.analysis import AnalysisResult

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000

logger = logging.getLogger("irislab_api")

# PaiGuard moderates every upload before IrisLab analyzes it. The models are
# loaded from PAIGUARD_MODEL_DIR when the first image is inspected.
guard = PaiGuard(
    rules=[
        PaiNsfwDetection(
            threshold=float(os.environ.get("IRISLAB_API_NSFW_THRESHOLD", "0.80"))
        ),
        PaiViolenceDetection(
            threshold=float(os.environ.get("IRISLAB_API_VIOLENCE_THRESHOLD", "0.85"))
        ),
    ]
)


class InvalidImageError(ValueError):
    """The upload is not a supported image."""


class UploadTooLargeError(ValueError):
    """The upload exceeds the size limit."""


class ContentRejectedError(ValueError):
    """PaiGuard did not allow the image."""


class ModerationUnavailableError(RuntimeError):
    """The PaiGuard models are not available."""


class AnalysisService:
    def analyze(self, upload: BinaryIO) -> AnalysisResult:
        data = upload.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise UploadTooLargeError("Image exceeds the 10 MiB upload limit")

        try:
            with Image.open(BytesIO(data)) as image:
                if image.format not in {"PNG", "JPEG"}:
                    raise InvalidImageError("Only PNG and JPEG images are supported")
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise InvalidImageError("Image exceeds the 20 megapixel limit")
                suffix = ".png" if image.format == "PNG" else ".jpg"
                image.verify()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
            raise InvalidImageError("Invalid PNG or JPEG image") from error

        self.moderate(data)

        path = model_path()
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError("IrisLab model is unavailable")
        with TemporaryDirectory(prefix="irislab-") as directory:
            path = Path(directory) / f"upload{suffix}"
            path.write_bytes(data)
            return AnalysisResult.model_validate(analyze(path, device="cpu"))

    def moderate(self, data: bytes) -> None:
        """Raise ContentRejectedError unless PaiGuard allows the image."""
        with Image.open(BytesIO(data)) as image:
            picture = image.convert("RGB")

        try:
            result = guard.inspect(picture)
        except ModelNotFoundError as error:
            logger.error("PaiGuard models are unavailable: %s", error)
            raise ModerationUnavailableError(
                "PaiGuard models are unavailable"
            ) from error

        if not result.is_safe:
            violations = ", ".join(result.violations)
            logger.warning("Upload rejected (%s): %s", result.decision, violations)
            raise ContentRejectedError(
                f"Image rejected by content moderation ({result.decision}): "
                f"{violations}"
            )
