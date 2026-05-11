# Image Processor `conda` Environment

This section shows how Conda manages both the Python interpreter and the package set, including native binary dependencies. It runs a tiny image-processing pipeline (`numpy` + `opencv`) inside an environment defined by `environment.yml`.

OpenCV is a good showcase for Conda because it ships compiled C++ extensions and links to shared libraries (BLAS, libjpeg, libstdc++). Conda installs them as part of the environment, so you do not have to compile anything or chase missing system packages.

For background on Conda channels, the YAML schema, and the tradeoffs against `venv`, see the [MkDocs page](../../docs/chapter-01/section-03.md).

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
