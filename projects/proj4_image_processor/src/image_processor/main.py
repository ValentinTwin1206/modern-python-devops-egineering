"""Minimal image-processing pipeline for the Conda showcase.

Demonstrates why Conda is a strong fit for projects with native binary
dependencies: OpenCV ships compiled C++ extensions and links against shared
libraries that Conda can install reliably across platforms.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def make_sample_image(size: int = 256) -> np.ndarray:
    """Generate a deterministic grayscale gradient with a bright square."""
    image = np.tile(np.linspace(0, 255, size, dtype=np.uint8), (size, 1))
    image[size // 4 : 3 * size // 4, size // 4 : 3 * size // 4] = 230
    return image


def process(image: np.ndarray) -> np.ndarray:
    """Blur the image and return Canny edges as an 8-bit array."""
    blurred = cv2.GaussianBlur(image, ksize=(5, 5), sigmaX=1.2)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    return edges


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the demo edge-detection pipeline.")
    parser.add_argument("--input", type=Path, help="Optional path to a grayscale image.")
    parser.add_argument("--output", type=Path, default=Path("edges.png"))
    args = parser.parse_args()

    if args.input is not None:
        image = cv2.imread(str(args.input), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise SystemExit(f"Could not read image: {args.input}")
    else:
        image = make_sample_image()

    edges = process(image)
    cv2.imwrite(str(args.output), edges)
    print(f"Wrote {args.output} ({edges.shape[1]}x{edges.shape[0]})")


if __name__ == "__main__":
    main()
