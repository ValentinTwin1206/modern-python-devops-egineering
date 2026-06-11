"""Command-line entry point for pixelpack."""

from __future__ import annotations

from pathlib import Path

import click
from PIL import Image, ImageOps


@click.group()
@click.version_option(package_name="pixelpack")
def cli() -> None:
    """Tiny image-processing CLI built on Pillow."""


@cli.command()
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("destination", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--width", type=int, required=True, help="Target width in pixels.")
@click.option("--height", type=int, required=True, help="Target height in pixels.")
def resize(source: Path, destination: Path, width: int, height: int) -> None:
    """Resize SOURCE to WIDTHxHEIGHT and write it to DESTINATION."""
    with Image.open(source) as image:
        resized = image.resize((width, height))
        resized.save(destination)
    click.echo(f"wrote {destination} ({width}x{height})")


@cli.command()
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("destination", type=click.Path(dir_okay=False, path_type=Path))
def convert(source: Path, destination: Path) -> None:
    """Convert SOURCE to the image format implied by DESTINATION's suffix."""
    with Image.open(source) as image:
        image.save(destination)
    click.echo(f"wrote {destination}")


@cli.command()
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("destination", type=click.Path(dir_okay=False, path_type=Path))
def grayscale(source: Path, destination: Path) -> None:
    """Convert SOURCE to grayscale and write it to DESTINATION."""
    with Image.open(source) as image:
        gray = ImageOps.grayscale(image)
        gray.save(destination)
    click.echo(f"wrote {destination}")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
