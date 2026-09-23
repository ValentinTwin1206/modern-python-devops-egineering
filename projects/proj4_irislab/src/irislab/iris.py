"""Iris localization and color extraction using MediaPipe Face Landmarker.

MediaPipe runs a local face-landmark model to locate the irises. RedSticks
then samples pixels from each iris and calculates a representative RGB color.

No cloud inference is used.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

# Configure native MediaPipe/TensorFlow logging before importing MediaPipe.
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

from absl import logging as absl_logging
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL.Image import Image


logger = logging.getLogger("redsticks")

absl_logging.set_verbosity(absl_logging.ERROR)
absl_logging.set_stderrthreshold(absl_logging.ERROR)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

_MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "face_landmarker.task"
)


# ---------------------------------------------------------------------------
# MediaPipe iris landmarks
# ---------------------------------------------------------------------------

# Face Landmarker provides five landmarks per iris:
#
#   center + four points around the iris.
#
# We deliberately use the four boundary landmarks for calculating the iris
# radius. The center landmark is not needed for the radius calculation.

_RIGHT_IRIS = (469, 470, 471, 472)
_LEFT_IRIS = (474, 475, 476, 477)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EyeIris:
    """Color information extracted from one iris."""

    rgb: tuple[int, int, int]
    pixels: np.ndarray
    pixel_count: int


@dataclass(frozen=True, slots=True)
class IrisResult:
    """Combined result from one or both detected irises."""

    rgb: tuple[int, int, int]
    pixels: np.ndarray
    confidence: float
    eyes_detected: int


# ---------------------------------------------------------------------------
# Model creation
# ---------------------------------------------------------------------------


def _create_detector(device: str = "cpu") -> vision.FaceLandmarker:
    """Create the local MediaPipe Face Landmarker for the requested device."""

    if not _MODEL_PATH.is_file():
        raise FileNotFoundError(
            "MediaPipe Face Landmarker model not found: "
            f"{_MODEL_PATH}\n"
            "Expected the model at "
            "'models/face_landmarker.task'."
        )

    if device == "cuda":
        logger.info("Using MediaPipe GPU delegate")
        base_options = python.BaseOptions(
            model_asset_path=str(_MODEL_PATH),
            delegate=python.BaseOptions.Delegate.GPU,
        )
    else:
        logger.debug("Using MediaPipe CPU delegate")
        base_options = python.BaseOptions(
            model_asset_path=str(_MODEL_PATH),
            delegate=python.BaseOptions.Delegate.CPU,
        )

    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    )

    return vision.FaceLandmarker.create_from_options(options)


# ---------------------------------------------------------------------------
# Iris pixel extraction
# ---------------------------------------------------------------------------


def _extract_iris_pixels(
    image: np.ndarray,
    landmarks,
    indices: tuple[int, ...],
) -> np.ndarray:
    """Extract useful pigmentation pixels from one iris."""

    height, width = image.shape[:2]

    points = np.asarray(
        [
            (
                landmarks[index].x * width,
                landmarks[index].y * height,
            )
            for index in indices
        ],
        dtype=np.float32,
    )

    center = points.mean(axis=0)

    distances = np.linalg.norm(
        points - center,
        axis=1,
    )

    radius = float(np.median(distances))

    if radius < 2.0:
        return np.empty(
            (0, 3),
            dtype=np.uint8,
        )

    yy, xx = np.ogrid[
        :height,
        :width,
    ]

    distance = np.sqrt(
        (xx - center[0]) ** 2
        + (yy - center[1]) ** 2
    )

    # Sample an annulus rather than the entire iris.
    #
    # Inner exclusion:
    #     avoids most of the pupil.
    #
    # Outer exclusion:
    #     avoids the iris/sclera boundary.
    mask = (
        (distance >= radius * 0.38)
        & (distance <= radius * 0.82)
    )

    pixels = image[mask]

    if len(pixels) == 0:
        return pixels

    values = pixels.astype(np.float32)

    maximum = values.max(axis=1)
    minimum = values.min(axis=1)

    brightness = values.mean(axis=1)
    chroma = maximum - minimum

    # Remove:
    #
    # - very dark pupil / eyelashes
    # - strong specular highlights
    # - bright neutral sclera pixels
    valid = (
        (brightness > 30.0)
        & (maximum < 245.0)
        & ~(
            (brightness > 175.0)
            & (chroma < 45.0)
        )
    )

    return pixels[valid]


def _extract_eye(
    image: np.ndarray,
    landmarks,
    indices: tuple[int, ...],
) -> EyeIris | None:
    """Extract color information from one iris."""

    pixels = _extract_iris_pixels(
        image,
        landmarks,
        indices,
    )

    if len(pixels) < 20:
        return None

    median = np.median(
        pixels.astype(np.float32),
        axis=0,
    )

    median = np.clip(
        np.rint(median),
        0,
        255,
    ).astype(np.uint8)

    rgb = (
        int(median[0]),
        int(median[1]),
        int(median[2]),
    )

    return EyeIris(
        rgb=rgb,
        pixels=pixels,
        pixel_count=len(pixels),
    )


#
# Public API
# # # # # # # 
def extract_iris(image: Image, device: str = "cpu") -> IrisResult | None:
    """Locate the irises and extract their pigmentation.

    MediaPipe performs local ML inference using the Face Landmarker model.

    ``device="cuda"`` selects MediaPipe's GPU delegate. The model must be
    run in an environment with a supported MediaPipe GPU backend.
    """

    rgb_image = image.convert("RGB")

    # Copy intentionally:
    #
    # MediaPipe expects a contiguous writable uint8 image buffer.
    image_array = np.asarray(
        rgb_image,
        dtype=np.uint8,
    ).copy()

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=image_array,
    )

    def detect_with_device(selected_device: str):
        with _create_detector(selected_device) as detector:
            return detector.detect(mp_image)

    try:
        result = detect_with_device(device)

    except Exception as error:
        if device != "cuda":
            logger.error(
                "MediaPipe Face Landmarker failed: %s",
                error,
            )
            return None

        logger.warning(
            "MediaPipe GPU delegate unavailable (%s); retrying with CPU",
            error,
        )

        try:
            result = detect_with_device("cpu")
        except Exception as cpu_error:
            logger.error(
                "MediaPipe Face Landmarker failed on CPU fallback: %s",
                cpu_error,
            )
            return None

    if not result.face_landmarks:
        logger.info(
            "No face detected by MediaPipe"
        )
        return None

    landmarks = result.face_landmarks[0]

    # A refined Face Landmarker model should expose the iris landmarks.
    if len(landmarks) < 478:
        logger.error(
            "Face Landmarker returned only %d landmarks; "
            "iris landmarks require the refined 478-landmark model",
            len(landmarks),
        )
        return None

    eyes: list[EyeIris] = []

    for name, indices in (
        ("left", _LEFT_IRIS),
        ("right", _RIGHT_IRIS),
    ):
        eye = _extract_eye(
            image_array,
            landmarks,
            indices,
        )

        if eye is None:
            logger.info(
                "Could not extract reliable %s iris pixels",
                name,
            )
            continue

        logger.info(
            "%s iris: RGB %s from %d pixels",
            name.capitalize(),
            eye.rgb,
            eye.pixel_count,
        )

        eyes.append(eye)

    if not eyes:
        logger.info(
            "No reliable iris pixels detected"
        )
        return None

    # Keep the complete pixel population.
    #
    # eye_color.py uses this distribution for semantic classification rather
    # than attempting to classify the representative RGB value alone.
    pixels = np.concatenate(
        [eye.pixels for eye in eyes],
        axis=0,
    )

    median = np.median(
        pixels.astype(np.float32),
        axis=0,
    )

    median = np.clip(
        np.rint(median),
        0,
        255,
    ).astype(np.uint8)

    rgb = (
        int(median[0]),
        int(median[1]),
        int(median[2]),
    )

    # This is an extraction-quality indicator, not a calibrated ML
    # probability.
    confidence = (
        0.95
        if len(eyes) == 2
        else 0.70
    )

    logger.info(
        "Detected %d iris(es) with representative RGB %s",
        len(eyes),
        rgb,
    )

    return IrisResult(
        rgb=rgb,
        pixels=pixels,
        confidence=confidence,
        eyes_detected=len(eyes),
    )
