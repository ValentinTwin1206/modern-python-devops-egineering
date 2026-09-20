"""Command-line interface for RedSticks."""

from __future__ import annotations

import logging
from typing import Sequence

# third-party imports
import click
from rich import box
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.text import Text

# own imports
from .suggest import EyeColorDetectionError, SuggestionResult, suggest

logger = logging.getLogger("redsticks")


def _render_suggestion(result: SuggestionResult) -> Table:
    """Build a Rich table for a suggestion result."""

    shade_value = Text(f"{result.shade_name} {result.hex} ")
    shade_value.append("      ", style=f"on {result.hex}")

    table = Table(
        title="RedSticks Suggestion",
        box=box.SQUARE,
        show_lines=True,
    )

    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Eye color", result.eye_color.value)
    table.add_row("Eye RGB", str(result.eye_rgb))
    table.add_row(
        "Extraction",
        f"{result.source} ({result.confidence:.0%} confidence)",
    )
    table.add_row("Eyes detected", str(result.eyes_detected))
    table.add_row("Suggested shade", shade_value)
    table.add_row("Harmony", f"{result.harmony}/100")
    table.add_row(
        "Pigment",
        f"{result.pigment_formula}\n"
        f"{result.pigment_weight:.2f} g/mol",
    )

    return table


@click.command()
@click.option(
    "--image",
    required=True,
    type=click.Path(dir_okay=False, path_type=str),
    help="Path to a PNG or JPEG portrait image.",
)
@click.option(
    "--gpu",
    is_flag=True,
    help=(
        "Request GPU acceleration where supported. "
        "The iris landmark detector may run on CPU."
    ),
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable debug logging.",
)
def cli(image: str, gpu: bool, verbose: bool) -> None:
    """Suggest a lipstick shade that harmonizes with eye color."""

    console = Console()
    error_console = Console(stderr=True)

    log_level = logging.DEBUG if verbose else logging.INFO

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
        result = suggest(
            image,
            device="cuda" if gpu else "cpu",
        )
    except EyeColorDetectionError as error:
        raise click.ClickException(str(error)) from error
    except ValueError as error:
        raise click.ClickException(str(error)) from error

    logger.info(
        "Eye color classified as %s",
        result.eye_color.value,
    )
    logger.info("Showing 'redsticks' suggestion")

    console.print(_render_suggestion(result))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the RedSticks command-line interface."""

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