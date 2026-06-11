# Image Processor

This section introduces *Image Processor* as a sample project that demonstrates how Conda manages both the Python interpreter and the package set, including native binary dependencies. It runs a small image-processing pipeline with `numpy` and `opencv` inside an environment defined by `environment.yml`, and shows how the project can be distributed as a Conda package built from [recipe/meta.yaml](recipe/meta.yaml).

## Project Components

The table below lists the main files that support the Conda example project.

| Component | Description |
| --------- | ----------- |
| [src/image_processor/main.py](src/image_processor/main.py) | This module generates a synthetic grayscale image, blurs it, runs Canny edge detection, and writes the result to disk. It is intentionally short so the focus stays on the binary dependencies the environment supplies. |
| [environment.yml](environment.yml) | This file declares the Conda environment for the example project. It pins the interpreter, NumPy, and OpenCV from `conda-forge`, and records extra Python tools installed through `pip`. |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image is based on `continuumio/miniconda3` and creates the named environment with `conda env create`. It provides a reproducible Conda setup with OpenCV, NumPy, and dev tools pre-configured. |
| [recipe/meta.yaml](recipe/meta.yaml) | This file is the Conda recipe consumed by `conda-build`. It is the sole packaging declaration for the project: it copies the `image_processor` package into the env's site-packages, registers the `image-processor` entry point, and pulls OpenCV and NumPy from `conda-forge` at install time. |

## End-User Guide

This section shows how an end user installs and runs `image-processor` from a published Conda channel.

### Requirements

- Miniconda or Anaconda.
- Access to a public Conda channel that publishes `image-processor`.

### Installation

Add `image-processor` to your project's `environment.yml` file:

```yaml
name: image-processor-demo
channels:
	- {YOUR_CONDA_CHANNEL}
	- conda-forge
dependencies:
	- python=3.12
	- image-processor
```

> Use `{YOUR_CONDA_CHANNEL}` for the public channel that publishes `image-processor`.

Create and activate the environment from that file:

```bash
conda env create -f environment.yml && conda activate image-processor-demo
```

### Usage

With the `image-processor-demo` environment activated, run the demo pipeline with the bundled synthetic input and write `edges.png`:

```bash
image-processor --output edges.png
```

Run the pipeline against your own grayscale image:

```bash
image-processor --input path/to/image.png --output edges.png
```

## Developer Guide

### Setup Environment

The [Dockerfile.devEnv](Dockerfile.devEnv) contains all required development tools. Build artifacts are stored on the host in `.build/`. Run the following command on the host to open an interactive shell in the development image through the projects helper:

```bash
../build.sh build --path proj4_image_processor/Dockerfile.devEnv
```

### Sync Environment

Within the running container, update the Conda environment to match `environment.yml`, removing any packages that are no longer listed:

```bash
conda env update -f environment.yml --prune
```

### Run Tests

Within the running container, run the test suite with Karva:

```bash
PYTHONPATH=src karva test tests/
```

### Build Guide

Install the required packaging tools into the base environment:

```bash
conda install -n base -c conda-forge conda-build anaconda-client
```

Build the package from the project root:

```bash
conda build recipe/ --channel conda-forge
```

Authenticate with Anaconda.org:

```bash
anaconda login
```

Upload the built package to your public channel:

```bash
anaconda upload --user {YOUR_CONDA_CHANNEL} "$CONDA_PREFIX/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```
