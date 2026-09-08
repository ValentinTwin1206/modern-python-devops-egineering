"""Command-line interface for redsticks."""

from __future__ import annotations

import logging
from typing import Sequence

# Third-party modules
import click
from PIL import Image
from rdkit import Chem
from rdkit.Chem import Draw
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.text import Text

# Own modules
from .pigments import CATALOG
from .suggest import SuggestionResult, UnsupportedImageError, suggest

logger = logging.getLogger("redsticks")


def render_suggestion(result: SuggestionResult) -> Table:
    """Build a Rich table for a suggestion result."""

    eye_hex = "#{:02X}{:02X}{:02X}".format(*result.eye_rgb)
    eye_swatch = Text("      ", style=f"on {eye_hex}")
    swatch = Text("      ", style=f"on {result.hex}")

    table = Table(title="RedSticks Suggestion")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_column("Preview")
    table.add_row(
        "Eye color",
        f"RGB {result.eye_rgb}\n{eye_hex}",
        eye_swatch,
    )
    table.add_row(
        "Suggested shade:",
        f"{result.shade_name}\n{result.hex}",
        swatch,
    )
    table.add_row("Harmony", f"{result.harmony}/100", "")
    table.add_row(
        "Pigment",
        f"{result.pigment_formula}\n{result.pigment_weight:.2f} g/mol",
        "",
    )
    return table


@click.command()
@click.option(
    "--image",
    required=True,
    type=click.Path(dir_okay=False, path_type=str),
    help="Path to a PNG or JPEG eye-color image.",
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, path_type=str),
    help="Optional PNG output path for a shade swatch with the pigment structure.",
)
def cli(image: str, output: str | None) -> None:
    """Suggest a lipstick shade that harmonizes with an eye-color image."""

    # Setup Logger
    console = Console()
    error_console = Console(stderr=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(console=error_console, show_path=False)],
    )

    # Run suggestion "algorithm"
    try:
        result: SuggestionResult = suggest(image)
    except UnsupportedImageError as error:
        raise click.ClickException(str(error)) from error

    console.print("REDSTICKS", style="bold")
    console.print(render_suggestion(result))

    logger.info(
        "Suggested shade %r with color %s for eye color rgb%s",
        result.shade_name,
        result.hex,
        result.eye_rgb,
    )

    if output:
        pigment = next(p for p in CATALOG if p.name == result.shade_name)
        depiction = Draw.MolToImage(Chem.MolFromSmiles(pigment.smiles), size=(256, 256))
        canvas = Image.new("RGB", (256, 320), result.rgb)
        canvas.paste(depiction, (0, 64))
        canvas.save(output, format="PNG")
        logger.info("Wrote shade swatch to %s", output)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the redsticks command-line interface."""

    try:
        cli.main(args=argv, standalone_mode=False)
    except click.ClickException as error:
        error.show()
        return 2
    except click.exceptions.Exit as error:
        return error.exit_code
    return 0


if __name__ == "__main__":
    cli()
