"""Image moderation and request logging middleware backed by pAIguard."""

from io import BytesIO
import logging
import os

from fastapi import Request as FastAPIRequest, responses
from paiguard import ModelNotFoundError, PaiGuard
from paiguard.rules import PaiNsfwDetection, PaiViolenceDetection
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger("iris-lab")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000


def _safe_request_path(path: str) -> str:
    prefix = "/licenses/"
    token = path[len(prefix):] if path.startswith(prefix) else ""
    return f"{prefix}{{token}}" if token and "/" not in token else path


async def security_middleware(request: FastAPIRequest, call_next):
    """Moderate analysis uploads and log requests and responses."""
    path = request.url.path
    form = None
    if request.method == "POST" and path == "/api/v1/analyses":
        # Buffering lets Starlette replay the body so FastAPI can parse UploadFile.
        # The request cap allows at most 64 KiB of multipart overhead.
        max_body_bytes = MAX_UPLOAD_BYTES + 64 * 1024
        content_length = request.headers.get("content-length")
        if (
            content_length
            and content_length.isdecimal()
            and int(content_length) > max_body_bytes
        ):
            return responses.JSONResponse(
                status_code=413,
                content={"detail": "Image exceeds the 10 MiB upload limit"},
            )
        body = await request.body()
        if len(body) > max_body_bytes:
            return responses.JSONResponse(
                status_code=413,
                content={"detail": "Image exceeds the 10 MiB upload limit"},
            )

        try:
            form = await request.form()
        except Exception:
            # Let FastAPI return its normal multipart validation error.
            form = None

        if form is not None:
            upload = form.get("image")
            if hasattr(upload, "read"):
                data = await upload.read(MAX_UPLOAD_BYTES + 1)
                await form.close()
                form = None
                if len(data) <= MAX_UPLOAD_BYTES:
                    try:
                        with Image.open(BytesIO(data)) as image:
                            if (
                                image.format in {"PNG", "JPEG"}
                                and image.width * image.height <= MAX_IMAGE_PIXELS
                            ):
                                picture = image.convert("RGB")
                            else:
                                picture = None
                    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                        picture = None
                    if picture is not None:
                        try:
                            result = request.app.state.moderation_guard.inspect(picture)
                        except ModelNotFoundError as error:
                            logger.error("pAIguard models are unavailable: %s", error)
                            return responses.JSONResponse(
                                status_code=503,
                                content={"detail": "pAIguard models are unavailable"},
                            )
                        if not result.is_safe:
                            violations = ", ".join(result.violations)
                            logger.warning(
                                "Upload rejected (%s): %s",
                                result.decision,
                                violations,
                            )
                            return responses.JSONResponse(
                                status_code=422,
                                content={
                                    "detail": (
                                        "Image rejected by content moderation "
                                        f"({result.decision}): {violations}"
                                    )
                                },
                            )
            if form is not None:
                await form.close()
                form = None

    client_ip = request.client.host if request.client else "unknown"
    safe_path = _safe_request_path(path)
    logger.info("Request: %s %s from %s", request.method, safe_path, client_ip)
    try:
        response = await call_next(request)
        logger.info("Response: %s %s -> %s", request.method, safe_path, response.status_code)
        return response
    finally:
        if form is not None:
            await form.close()


def create_moderation_guard() -> PaiGuard:
    """Create the pAIguard instance used by the moderation middleware."""
    return PaiGuard(
        rules=[
            PaiNsfwDetection(
                threshold=float(os.environ.get("IRISLAB_API_NSFW_THRESHOLD", "0.80"))
            ),
            PaiViolenceDetection(
                threshold=float(os.environ.get("IRISLAB_API_VIOLENCE_THRESHOLD", "0.85"))
            ),
        ]
    )
