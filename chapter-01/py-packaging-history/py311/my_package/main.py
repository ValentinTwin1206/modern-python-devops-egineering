"""Vector calculator CLI built with Click and NumPy.

This is the 2022-era iteration of the historic-calculator example, with
a fully declarative ``pyproject.toml`` (PEP 621) and no ``setup.py`` or
``setup.cfg``.
"""
from __future__ import annotations

from typing import Iterable

import click
import numpy as np


def make_vector(values: Iterable[float]) -> np.ndarray:
    """Return a NumPy ``float64`` vector from an iterable of numbers."""
    return np.array(list(values), dtype=np.float64)


def parse_vector(text: str) -> np.ndarray:
    """Parse a comma-separated string of numbers into a NumPy vector."""
    parts = [part.strip() for part in text.split(",")]
    if not parts or any(part == "" for part in parts):
        raise ValueError("vector must contain at least one number")
    return make_vector(float(part) for part in parts)


_OPS = {
    "max": np.max,
    "min": np.min,
    "sum": np.sum,
    "mean": np.mean,
}


def run_calculator(command: str, vector_text: str) -> float:
    """Apply ``command`` to the parsed vector and return the result."""
    if command not in _OPS:
        raise ValueError(f"unknown command: {command}")
    return float(_OPS[command](parse_vector(vector_text)))


@click.group()
def cli() -> None:
    """Tiny vector calculator using NumPy."""


def _emit(command: str, vector_text: str) -> None:
    try:
        result = run_calculator(command, vector_text)
    except ValueError as err:
        raise click.BadParameter(str(err))
    click.echo(f"{command}({vector_text}) = {result}")


@cli.command("max")
@click.argument("vector")
def cmd_max(vector: str) -> None:
    """Largest value in VECTOR (e.g. 1,-2,4)."""
    _emit("max", vector)


@cli.command("min")
@click.argument("vector")
def cmd_min(vector: str) -> None:
    """Smallest value in VECTOR."""
    _emit("min", vector)


@cli.command("sum")
@click.argument("vector")
def cmd_sum(vector: str) -> None:
    """Sum of values in VECTOR."""
    _emit("sum", vector)


@cli.command("mean")
@click.argument("vector")
def cmd_mean(vector: str) -> None:
    """Arithmetic mean of values in VECTOR."""
    _emit("mean", vector)


if __name__ == "__main__":
    cli()
