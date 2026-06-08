# Image Processor `conda` Environment

This section shows how Conda manages both the Python interpreter and the package set, including native binary dependencies. It runs a tiny image-processing pipeline (`numpy` + `opencv`) inside an environment defined by `environment.yml`.

OpenCV is a good showcase for Conda because it ships compiled C++ extensions and links to shared libraries (BLAS, libjpeg, libstdc++). Conda installs them as part of the environment, so you do not have to compile anything or chase missing system packages.

For background on Conda channels, the YAML schema, and the tradeoffs against `venv`, see the [MkDocs page](../../docs/chapter-01/section-03.md).

## Project Components

The table below lists the main files that support the Conda example project.

| Component | Description |
| --------- | ----------- |
| [src/image_processor/main.py](src/image_processor/main.py) | This module generates a synthetic grayscale image, blurs it, runs Canny edge detection, and writes the result to disk. It is intentionally short so the focus stays on the binary dependencies the environment supplies. |
| [environment.yml](environment.yml) | This file declares the Conda environment for the example project. It pins the interpreter, NumPy, and OpenCV from `conda-forge`, and records extra Python tools installed through `pip`. |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image is based on `continuumio/miniconda3` and creates the named environment with `conda env create`. It provides a reproducible Conda setup with OpenCV, NumPy, and dev tools pre-configured. |
| [pyproject.toml](pyproject.toml) | This file defines the Python package metadata for the image processor. It is the source of the package that later gets installed into the Conda environment. |
| [recipe/meta.yaml](recipe/meta.yaml) | This file is the Conda recipe consumed by `conda-build`. It declares the package metadata, the build script, and the runtime dependencies, and pulls OpenCV and NumPy from `conda-forge` so the produced Conda package resolves the binary stack at install time. |

## Required Developer Tools

- Docker or Podman.
- Miniconda or Anaconda (for the on-host path).
- `uv` for the project development workflow.
- `conda-build` (for building the Conda package).

### With Docker

Build the development image through the projects helper:

```bash
../build.sh build --path proj3_image_processor/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path proj3_image_processor/Dockerfile.devEnv
```

### On Host

Install Miniconda using the official installer:

```bash
curl -fsSL -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

Run the installer:

```bash
bash miniconda.sh -b -p "$HOME/miniconda"
```

Accept the Anaconda channel terms of service:

```bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
```

Create the environment:

```bash
conda env create -f environment.yml
```

Activate it:

```bash
conda activate image-processor
```

## Usage Guide

Run the demo pipeline with the bundled synthetic input and write `edges.png`:

```bash
PYTHONPATH=src python -m image_processor.main --output edges.png
```

Run the pipeline against your own grayscale image:

```bash
PYTHONPATH=src python -m image_processor.main --input path/to/image.png --output edges.png
```

Snapshot the environment requirements back to YAML:

```bash
conda env export --from-history > environment.yml
```

## Development Guide

Sync the development environment with `uv`:

```bash
uv sync
```

Run the tests:

```bash
PYTHONPATH=src uv run karva test tests/
```

Run the linter:

```bash
uv run ruff check .
```

## Distribute as a Conda Package

The project can also be distributed as a Conda package. That way the binary OpenCV stack and NumPy come from `conda-forge` at install time instead of being pulled in by `pip`. The recipe lives in [recipe/meta.yaml](recipe/meta.yaml) and the build process turns the source tree plus that recipe into a `.conda` archive that any Conda-based environment can install.

Install `conda-build` into the base environment:

```bash
conda install -n base -c conda-forge conda-build
```

Build the package from the project root. The recipe references the project source through a relative `path: ..`, so the command must run from the project root and pass the recipe directory as the argument:

```bash
conda build recipe/ --channel conda-forge
```

`conda-build` resolves the host and runtime dependencies, runs the project's PEP 517 build backend through `pip`, executes the recipe's `test` block, and writes a `.conda` archive into the local Conda build cache. The path to the artifact is printed at the end of the build, typically:

```text
$CONDA_PREFIX/conda-bld/noarch/image-processor-1.0.0-py_0.conda
```

Verify the freshly built package by installing it into a clean throwaway environment from the local build cache and from `conda-forge`:

```bash
conda create -n image-processor-test -c local -c conda-forge image-processor
```

Activate the test environment and run the CLI:

```bash
conda activate image-processor-test && image-processor --help
```

Once the package looks good, upload it to a Conda channel. Anaconda.org is the most common destination. Install the uploader and authenticate:

```bash
conda install -n base -c conda-forge anaconda-client && anaconda login
```

Upload the build artifact:

```bash
anaconda upload "$CONDA_PREFIX/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

Users can then install the package from your channel without touching `pip`:

```bash
conda install -c <your-channel> -c conda-forge image-processor
```
