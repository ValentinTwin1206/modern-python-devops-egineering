"""Command-line interface for HeisenBlue."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .analysis import InvalidSmilesError, analyze
from .render import render


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="heisenblue",
        description="Analyze a molecule with RDKit and assign a fictional Blue Score.",
    )
    parser.add_argument("smiles", help="SMILES string to analyze")
    parser.add_argument("--output", help="Optional PNG output path")
    parser.add_argument(
        "--show-molecule",
        action="store_true",
        help="Include a simple RDKit molecular depiction in the PNG output.",
    )
    return parser


def _format_result_block(smiles: str, formula: str, molecular_weight: float, score: int, color_hex: str) -> str:
    return "\n".join(
        [
            "HEISENBLUE",
            "===========",
            f"SMILES: {smiles}",
            f"Formula: {formula}",
            f"Molecular weight: {molecular_weight:.2f}",
            f"Blue Score: {score}",
            f"Color: {color_hex}",
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the HeisenBlue command-line interface."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        result = analyze(args.smiles)
    except InvalidSmilesError as error:
        print(str(error), file=sys.stderr)
        return 2

    print(
        _format_result_block(
            result.smiles,
            result.formula,
            result.molecular_weight,
            result.score,
            result.hex,
        )
    )

    if args.output:
        render(result, args.output, show_molecule=args.show_molecule)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())