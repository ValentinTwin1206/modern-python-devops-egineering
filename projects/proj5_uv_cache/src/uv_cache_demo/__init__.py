"""A source-built package with bundled synthetic embeddings for the cache demo."""

import json
from importlib.resources import files

import numpy as np
from numpy.typing import NDArray


def cache_message() -> str:
    """Return a message that verifies the installed package works."""
    return "Local wheel imported successfully"


def fixture_shape() -> tuple[int, int]:
    """Check the installed fixture's size and return its matrix dimensions."""
    data = files(__package__).joinpath("data")
    spec = json.loads(data.joinpath("fixture.json").read_text())
    with data.joinpath("embeddings.bin").open("rb") as stream:
        size = stream.seek(0, 2)
    if spec["dtype"] != "uint8" or size != spec["rows"] * spec["dimensions"]:
        raise ValueError("The bundled embedding matrix does not match its specification")
    return spec["rows"], spec["dimensions"]


def load_embeddings() -> NDArray[np.uint8]:
    """Load the validated matrix from the installed package's bundled data."""
    shape = fixture_shape()
    payload = files(__package__).joinpath("data/embeddings.bin").read_bytes()
    return np.frombuffer(payload, dtype=np.uint8).reshape(shape)
