#!/usr/bin/env python3
"""
visualize.py — Generate bar charts comparing dependency managers.

Reads results.json (JSONL format) produced by build_and_analyze.sh
and creates two bar charts:
  1. Installation time comparison (ms)
  2. Installed size / storage footprint comparison (MB)

Usage:
    python visualize.py [results.json]
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Material / Python palette
# Primary: Python blue #3776AB  Accent: amber #FFD43B
# Tool colours are chosen from the same cool-to-warm Material spectrum so
# they feel at home next to the site's indigo/amber scheme.
# ---------------------------------------------------------------------------
PALETTE = {
    "uv":      "#3776AB",   # Python blue  — primary / hero
    "pip":     "#546E7A",   # Blue-grey    — neutral baseline
    "poetry":  "#7B1FA2",   # Material Purple 700
}

TOOLS = ["pip", "uv", "poetry"]

# ---------------------------------------------------------------------------
# Global Matplotlib style — clean, minimal, Material-like
# ---------------------------------------------------------------------------
mpl.rcParams.update({
    "font.family":        "DejaVu Sans",
    "font.size":          10,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.spines.bottom": True,
    "axes.edgecolor":     "#CFD8DC",   # Blue-grey 100
    "axes.grid":          True,
    "axes.axisbelow":     True,
    "grid.color":         "#ECEFF1",   # Blue-grey 50
    "grid.linewidth":     0.8,
    "axes.labelcolor":    "#37474F",   # Blue-grey 800
    "xtick.color":        "#546E7A",
    "ytick.color":        "#546E7A",
    "xtick.bottom":       False,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
    "legend.framealpha":  0,
    "legend.edgecolor":   "#CFD8DC",
})


def load_results(path: str = "results.json") -> list[dict]:
    results = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def build_dep_set_labels(results: list[dict]) -> dict[int, str]:
    labels = {}
    for r in results:
        line = r["line"]
        if line not in labels:
            pkgs = r["dep_set"].split()
            short_names = []
            for p in pkgs[:3]:
                name = p.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0]
                short_names.append(name)
            suffix = f" +{len(pkgs) - 3}" if len(pkgs) > 3 else ""
            labels[line] = ", ".join(short_names) + suffix
    return labels


def _add_value_labels(ax, bars, fmt):
    """Place small value labels above each bar."""
    for bar in bars:
        val = bar.get_height()
        if val > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + ax.get_ylim()[1] * 0.008,
                fmt(val),
                ha="center", va="bottom",
                fontsize=7.5, color="#37474F",
            )


def plot_installation_time(results: list[dict], labels: dict[int, str], output: str):
    data: dict[int, dict] = defaultdict(dict)
    for r in results:
        data[r["line"]][r["tool"]] = r["install_time_ms"]

    lines_sorted = sorted(data.keys())
    x = np.arange(len(lines_sorted))
    width = 0.19
    n_tools = len(TOOLS)

    fig, ax = plt.subplots(figsize=(13, 6))

    for i, tool in enumerate(TOOLS):
        values = [data[line].get(tool, 0) for line in lines_sorted]
        offset = (i - n_tools / 2 + 0.5) * width
        bars = ax.bar(
            x + offset, values, width,
            label=tool,
            color=PALETTE[tool],
            edgecolor="white", linewidth=0.4,
            zorder=3,
        )
        _add_value_labels(ax, bars, lambda v: f"{v / 1000:.1f}s")

    ax.set_xlabel("Dependency Set", labelpad=8)
    ax.set_ylabel("Installation Time (s)")
    ax.set_title("Installation Time by Dependency Manager", fontsize=12, fontweight="bold",
                 color="#263238", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels([labels[ln] for ln in lines_sorted], rotation=18, ha="right")
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}s"))
    ax.legend(title="Tool", title_fontsize=9, fontsize=9, loc="upper left")

    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    print(f"  Saved: {output}")
    plt.close(fig)


def plot_storage_footprint(results: list[dict], labels: dict[int, str], output: str):
    data: dict[int, dict] = defaultdict(dict)
    for r in results:
        size = r.get("installed_size_bytes", 0) or r.get("layer_size_bytes", 0)
        data[r["line"]][r["tool"]] = size

    lines_sorted = sorted(data.keys())
    x = np.arange(len(lines_sorted))
    width = 0.19
    n_tools = len(TOOLS)

    fig, ax = plt.subplots(figsize=(13, 6))

    for i, tool in enumerate(TOOLS):
        values_mb = [data[line].get(tool, 0) / (1024 * 1024) for line in lines_sorted]
        offset = (i - n_tools / 2 + 0.5) * width
        bars = ax.bar(
            x + offset, values_mb, width,
            label=tool,
            color=PALETTE[tool],
            edgecolor="white", linewidth=0.4,
            zorder=3,
        )
        _add_value_labels(ax, bars, lambda v: f"{v:.0f}")

    ax.set_xlabel("Dependency Set", labelpad=8)
    ax.set_ylabel("Installed Size (MB)")
    ax.set_title("Storage Footprint by Dependency Manager", fontsize=12, fontweight="bold",
                 color="#263238", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels([labels[ln] for ln in lines_sorted], rotation=18, ha="right")
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:.0f} MB"))
    ax.legend(title="Tool", title_fontsize=9, fontsize=9, loc="upper left")

    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    print(f"  Saved: {output}")
    plt.close(fig)


def main():
    results_file = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    results_path = Path(results_file)

    if not results_path.exists():
        print(f"Error: '{results_path}' not found. Run build_and_analyze.sh first.")
        sys.exit(1)

    print(f"Loading results from: {results_path}")
    results = load_results(str(results_path))
    print(f"  Found {len(results)} entries")

    labels = build_dep_set_labels(results)

    output_dir = results_path.parent / "charts"
    output_dir.mkdir(exist_ok=True)

    print("Generating charts...")
    plot_installation_time(results, labels, str(output_dir / "install_time_comparison.png"))
    plot_storage_footprint(results, labels, str(output_dir / "storage_footprint_comparison.png"))
    print("Done.")


if __name__ == "__main__":
    main()
