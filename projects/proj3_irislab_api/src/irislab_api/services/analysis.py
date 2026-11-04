"""Validate uploads and adapt IrisLab's path-based API."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO

from irislab import analyze
from irislab.iris import model_path
from PIL import Image, UnidentifiedImageError

from ..schemas.analysis import AnalysisResult

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000


class InvalidImageError(ValueError):
    """The upload is not a supported image."""


class UploadTooLargeError(ValueError):
    """The upload exceeds the size limit."""


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

        path = model_path()
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError("IrisLab model is unavailable")
        with TemporaryDirectory(prefix="irislab-") as directory:
            path = Path(directory) / f"upload{suffix}"
            path.write_bytes(data)
            return AnalysisResult.model_validate(analyze(path, device="cpu"))
