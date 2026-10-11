"""Inspect synthetic embeddings and save a headless numerical report."""

import argparse
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from scipy.spatial.distance import cdist

from uv_cache_demo import load_embeddings


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

    # Convert before arithmetic to avoid uint8 overflow. One query against all
    # rows keeps the distance output linear rather than building an N x N matrix.
    values = embeddings.astype(np.float64)
    norms = np.linalg.norm(values, axis=1)
    if np.any(norms == 0):
        parser.error("Cosine distance is undefined for zero-length embeddings")
    distances = cdist(values[args.query : args.query + 1], values, metric="cosine")[0]
    candidates = np.arange(rows) != args.query
    neighbor_rows = np.flatnonzero(candidates)
    nearest = neighbor_rows[np.argsort(distances[candidates], kind="stable")[:5]]

    print(f"Bundled matrix: {rows:,} rows x {dimensions} features ({embeddings.dtype})")
    print(f"Feature values: mean={values.mean():.3f}, std={values.std():.3f}")
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
