"""Inspect synthetic embeddings and save a headless numerical report."""

import argparse
import json
from importlib.resources import files
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from numpy.typing import NDArray
from scipy.spatial.distance import cdist


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
    with files(__package__).joinpath("data/embeddings.bin").open("rb") as stream:
        return np.memmap(stream, dtype=np.uint8, mode="r", shape=shape)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reports/embeddings.png"))
    parser.add_argument("--query", type=int, default=0, help="Query row (default: 0)")
    args = parser.parse_args()

    embeddings = load_embeddings()
    rows, dimensions = embeddings.shape
    if not 0 <= args.query < rows:
        parser.error(f"--query must be between 0 and {rows - 1}")
    if rows < 2 or dimensions < 1:
        parser.error("The report needs at least two rows and one feature")

    # Map the installed data and convert only a bounded chunk to float64.
    # Keep one result per row, rather than a full float64 or N x N matrix.
    query = embeddings[args.query : args.query + 1].astype(np.float64)
    norms = np.empty(rows, dtype=np.float64)
    distances = np.empty(rows, dtype=np.float64)
    total = 0.0
    squared_total = 0.0
    chunk_rows = max(1, (8 * 1024 * 1024) // (dimensions * 8))
    for start in range(0, rows, chunk_rows):
        stop = min(start + chunk_rows, rows)
        values = embeddings[start:stop].astype(np.float64)
        norms[start:stop] = np.linalg.norm(values, axis=1)
        distances[start:stop] = cdist(query, values, metric="cosine")[0]
        total += float(values.sum())
        squared_total += float(np.einsum("ij,ij->", values, values))
    if np.any(norms == 0):
        parser.error("Cosine distance is undefined for zero-length embeddings")
    mean = total / embeddings.size
    std = np.sqrt(max(0.0, squared_total / embeddings.size - mean**2))
    candidates = np.arange(rows) != args.query
    neighbor_rows = np.flatnonzero(candidates)
    nearest = neighbor_rows[np.argsort(distances[candidates], kind="stable")[:5]]

    print(f"Bundled matrix: {rows:,} rows x {dimensions} features ({embeddings.dtype})")
    print(f"Feature values: mean={mean:.3f}, std={std:.3f}")
    print(f"Vector norms: min={norms.min():.3f}, mean={norms.mean():.3f}, max={norms.max():.3f}")
    print(f"Nearest rows to query {args.query} (synthetic data; no semantic meaning):")
    for row in nearest:
        print(f"  row {row}: cosine distance={distances[row]:.6f}")

    figure = Figure(figsize=(10, 4), layout="constrained")
    FigureCanvasAgg(figure)
    norm_plot, distance_plot = figure.subplots(1, 2)
    norm_plot.hist(norms, bins=50)
    norm_plot.set(title="Synthetic embedding norms", xlabel="L2 norm", ylabel="Rows")
    distance_plot.hist(distances[candidates], bins=50)
    distance_plot.set(
        title=f"Distances from row {args.query}", xlabel="Cosine distance", ylabel="Rows"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, format="png", dpi=120)
    print(f"Saved report: {args.output}")


if __name__ == "__main__":
    main()
