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
| [Dockerfile](Dockerfile) | This deployment image builds the project wheel and runs it inside a dedicated Conda environment. It shows how the same environment model can be used beyond local inspection. |
| [pyproject.toml](pyproject.toml) | This file defines the Python package metadata for the image processor. It is the source of the package that later gets installed into the Conda environment. |

## Required Developer Tools

- Docker or Podman.
- Miniconda or Anaconda (for the on-host path).
- `uv` for the project development workflow.

## Setup Environment

### With Docker

Build the development image through the chapter helper:

```bash
../build.sh build --path section-03/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path section-03/Dockerfile.devEnv
```

Build and run the deployment image:

```bash
../build.sh build --path section-03/Dockerfile
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

Build a wheel:

```bash
uv build --wheel
```
