#!/usr/bin/env python3

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tarfile
import tempfile
import uuid
from pathlib import Path

import typer
from rich.console import Console
from rich.tree import Tree

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(message)s",
)

logger = logging.getLogger(__name__)

console = Console()
app = typer.Typer(
    add_completion=False,
    help="Build a Docker image, extract its last OCI layer and display it as a tree.",
)


# -----------------------------------------------------------------------------
# Docker helpers
# -----------------------------------------------------------------------------

def build_image(dockerfile: Path, verbose: bool = False) -> str:
    """Build a temporary Docker image from the provided Dockerfile."""

    image_tag = f"last-layer-{uuid.uuid4().hex[:8]}"

    logger.info(f"Building Docker image '{image_tag}' from file '{dockerfile.resolve()}'...")

    cmd = [
        "docker",
        "build",
        "-f",
        str(dockerfile),
        "-t",
        image_tag,
        str(dockerfile.parent)
    ]

    if not verbose:
        cmd.append("-q")

    subprocess.run(cmd, check=True)

    logger.info("Docker image built successfully.")

    return image_tag


def remove_image(image: str, verbose: bool = False):
    """Remove the temporary Docker image and clean Docker resources."""

    logger.info("Cleaning Docker resources...")

    cmd = ["docker", "image", "rm", "-f", image]
    if not verbose:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(cmd, check=False)

    cmd = ["docker", "builder", "prune", "-f"]
    if not verbose:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(cmd, check=False)

    cmd = ["docker", "system", "prune", "-f"]
    if not verbose:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(cmd, check=False)

    logger.info("Docker cleanup finished.")


# -----------------------------------------------------------------------------
# OCI extraction
# -----------------------------------------------------------------------------

def extract_last_layer(image: str, workspace: Path) -> Path:
    """
    Save the Docker image, extract the OCI archive and return
    the extracted last layer directory.
    """

    tar_path = workspace / "image.tar"
    image_dir = workspace / "image"

    image_dir.mkdir()

    logger.info("Saving image as OCI archive...")
    logger.info("Archive : %s", tar_path)

    subprocess.run(
        [
            "docker",
            "save",
            image,
            "-o",
            str(tar_path),
        ],
        check=True,
    )

    logger.info("Extracting OCI archive...")

    with tarfile.open(tar_path) as tar:
        tar.extractall(image_dir)

    logger.info("Reading manifest...")

    manifest = json.loads((image_dir / "manifest.json").read_text())

    last_layer_blob = manifest[0]["Layers"][-1]

    logger.info("Last layer blob : %s", last_layer_blob)

    output = workspace / "last_layer"
    output.mkdir()

    logger.info("Extracting last layer...")

    with tarfile.open(image_dir / last_layer_blob) as tar:
        tar.extractall(output)

    logger.info("Last layer extracted to:")
    logger.info("    %s", output.resolve())

    return output


# -----------------------------------------------------------------------------
# Tree rendering
# -----------------------------------------------------------------------------

def add_nodes(tree: Tree, folder: Path, depth: int, max_depth: int):
    if depth > max_depth:
        return

    entries = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))

    for entry in entries:
        icon = "📁 " if entry.is_dir() else "📄 "

        branch = tree.add(icon + entry.name)

        if entry.is_dir():
            add_nodes(branch, entry, depth + 1, max_depth)


def show_tree(folder: Path, level: int):
    logger.info("")
    logger.info("=" * 70)
    logger.info("Last layer directory : %s", folder.resolve())
    logger.info("Tree depth           : %d", level)
    logger.info("=" * 70)
    logger.info("")

    tree = Tree(f"📦 {folder.name}")

    add_nodes(tree, folder, 1, level)

    console.print(tree)


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

@app.command()
def main(
    file: Path = typer.Option(
        None,
        "--file",
        help="Path to the Dockerfile.",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    clean: bool = typer.Option(
        False,
        "--clean",
        help="Delete the extracted last layer after displaying it.",
    ),
    level: int = typer.Option(
        99,
        "--level",
        help="Maximum tree depth (similar to tree -L).",
    ),
    last_layer_dir: Path | None = typer.Option(
        None,
        "--last-layer-dir",
        help="Display an already extracted last layer without building an image.",
        exists=True,
        file_okay=False,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose logging.",
    )
):
    """
    Build a Docker image from a Dockerfile, extract its last OCI layer
    and display the layer contents as a file tree.
    """

    if last_layer_dir is not None:
        logger.info("Displaying existing last layer directory.")
        show_tree(last_layer_dir, level)
        return

    if file is None:
        raise typer.BadParameter(
            "Either --file or --last-layer-dir must be provided."
        )

    image = None

    with tempfile.TemporaryDirectory(prefix="last-layer-") as tmp:
        workspace = Path(tmp)

        logger.info(f"Temporary workspace: {workspace}")

        try:
            image = build_image(file, verbose=verbose)

            last_layer = extract_last_layer(image, workspace)

            show_tree(last_layer, level)

            if clean:
                logger.info("Removing extracted last layer directory.")
                shutil.rmtree(last_layer)

            else:
                destination = Path.cwd() / "last_layer"

                if destination.exists():
                    shutil.rmtree(destination)

                shutil.copytree(last_layer, destination, symlinks=True)

                logger.info(f"Copied last layer to: {destination.resolve()}")

        finally:
            if image:
                remove_image(image, verbose=verbose)

    logger.info("Done.")


if __name__ == "__main__":
    app()