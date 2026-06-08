import numpy as np

from image_processor.main import make_sample_image, process


def test_sample_image_shape_and_dtype() -> None:
    image = make_sample_image(size=64)
    assert image.shape == (64, 64)
    assert image.dtype == np.uint8


def test_process_returns_binary_edges() -> None:
    edges = process(make_sample_image(size=64))
    assert edges.shape == (64, 64)
    assert edges.dtype == np.uint8
    # Canny output is strictly 0 or 255.
    assert set(np.unique(edges)).issubset({0, 255})
