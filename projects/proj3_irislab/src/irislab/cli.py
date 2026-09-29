"""Command-line interface for IrisLab iris-color analysis."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

import click
from rich import box
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from .analyze import (
    ColorAnalysisResult,
    EyeColorDetectionError,
    analyze,
)


logger = logging.getLogger("irislab")


def _render_analysis(
    result: ColorAnalysisResult,
) -> Table:
    """Build a Rich table for an iris-color analysis result."""

    table = Table(
        title="IrisLab Iris Color Analysis",
        box=box.SQUARE,
        show_lines=True,
    )

    table.add_column("Metric")
    table.add_column("Value")

    table.add_row(
        "Classification",
        result.eye_color.value,
    )

    table.add_row(
        "RGB",
        str(result.eye_rgb),
    )

    table.add_row(
        "CIELAB",
        (
            f"L* {result.lab[0]:.2f}, "
            f"a* {result.lab[1]:.2f}, "
            f"b* {result.lab[2]:.2f}"
        ),
    )

    table.add_row(
        "HSV",
        (
            f"H {result.hsv[0]:.1f}°, "
            f"S {result.hsv[1]:.1f}%, "
            f"V {result.hsv[2]:.1f}%"
        ),
    )

    table.add_row(
        "Chroma",
        f"{result.chroma:.2f}",
    )

    table.add_row(
        "CIELAB hue",
        f"{result.hue:.1f}°",
    )

    table.add_row(
        "Closest profile",
        result.closest_profile,
    )

    table.add_row(
        "Profile RGB",
        str(result.profile_rgb),
    )

    table.add_row(
        "Color distance (ΔE)",
        f"{result.delta_e:.2f}",
    )

    table.add_row(
        "Extraction",
        (
            f"{result.source} "
            f"({result.confidence:.0%} confidence)"
        ),
    )

    table.add_row(
        "Eyes detected",
        str(result.eyes_detected),
    )

    return table


@click.command()
@click.option(
    "--image",
    required=True,
    type=click.Path(
        dir_okay=False,
        path_type=str,
    ),
    help="Path to a PNG or JPEG image containing visible eyes.",
)
@click.option(
    "--gpu",
    is_flag=True,
    help="Run iris segmentation with CUDA GPU acceleration.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable debug logging.",
)
def cli(
    image: str,
    gpu: bool,
    verbose: bool,
) -> None:
    """Analyze iris color from an image."""

    console = Console()
    error_console = Console(stderr=True)

    log_level = (
        logging.DEBUG
        if verbose
        else logging.INFO
    )

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[
            RichHandler(
                console=error_console,
                show_path=False,
            )
        ],
    )

    try:
        image_path = Path(image)
        device = "cuda" if gpu else "cpu"

        result = analyze(
            image_path=image_path,
            device=device,
        )

    except EyeColorDetectionError as error:
        raise click.ClickException(
            str(error)
        ) from error

    except ValueError as error:
        raise click.ClickException(
            str(error)
        ) from error

    logger.info(
        "Eye color classified as %s",
        result.eye_color.value,
    )

    console.print(
        _render_analysis(result)
    )


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """Run the IrisLab command-line interface."""

    try:
        cli.main(
            args=argv,
            standalone_mode=False,
        )

    except click.ClickException as error:
        error.show()
        return 2

    except click.exceptions.Exit as error:
        return error.exit_code

    return 0


if __name__ == "__main__":
    cli()