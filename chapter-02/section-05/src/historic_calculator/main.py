"""Vector calculator CLI built with Click and NumPy.

This is the 2016-era iteration of the historic_calculator example.

Notable upgrades over the py27 version:

  * Python 3.5+ syntax (``print()`` is a function, ``f-strings`` are not
    yet available -- those arrive with 3.6 in late 2016 -- so we use
    ``str.format``).
  * `Click <https://palletsprojects.com/p/click/>`_ for argument parsing
    instead of ``argparse``. Click 1.0 shipped in April 2014 and was the
    dominant choice for new CLIs by 2016.
  * A ``console_scripts`` entry point in ``setup.py`` exposes the CLI as
    a real ``historic_calculator`` command on the user's ``PATH`` after
    ``pip install``.
"""
import click
import numpy as np


def make_vector(values):
    """Return a NumPy ``float64`` vector from an iterable of numbers."""
    return np.array(list(values), dtype=np.float64)


def parse_vector(text):
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


def run_calculator(command, vector_text):
    """Apply ``command`` to the parsed vector and return the result."""
    if command not in _OPS:
        raise ValueError("unknown command: {0}".format(command))
    return _OPS[command](parse_vector(vector_text))


@click.group()
def cli():
    """Tiny vector calculator using NumPy."""


def _emit(command, vector_text):
    try:
        result = run_calculator(command, vector_text)
    except ValueError as err:
        raise click.BadParameter(str(err))
    click.echo("{0}({1}) = {2}".format(command, vector_text, result))


@cli.command("max")
@click.argument("vector")
def cmd_max(vector):
    """Largest value in VECTOR (e.g. 1,-2,4)."""
    _emit("max", vector)


@cli.command("min")
@click.argument("vector")
def cmd_min(vector):
    """Smallest value in VECTOR."""
    _emit("min", vector)


@cli.command("sum")
@click.argument("vector")
def cmd_sum(vector):
    """Sum of values in VECTOR."""
    _emit("sum", vector)


@cli.command("mean")
@click.argument("vector")
def cmd_mean(vector):
    """Arithmetic mean of values in VECTOR."""
    _emit("mean", vector)


if __name__ == "__main__":
    cli()
