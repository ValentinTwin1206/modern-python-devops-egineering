# `conda` Environment

This project shows how `conda` creates an isolated environment for the
shared tiny `bottle` web server. It includes the same `karva` and `ruff`
development tooling as the other Chapter 2 examples.

The `Dockerfile` is the important demonstration. It builds a container
where `conda` manages the Python interpreter and packages:

- It starts from `continuumio/miniconda3`.
- It installs Bash with APT.
- It creates an environment named `tiny-webserver` from
  `environment.yml`.
- It puts `/opt/conda/envs/tiny-webserver/bin` first on `PATH`.
- It exposes the source tree through `PYTHONPATH` instead of installing
  the project with `pip`.
- It activates the conda environment automatically for interactive
  shells.

Start the container with a bind mount so local edits appear under `/app`
at runtime:

```sh
cd chapter-02/section-02/conda
docker build -t pyenv-conda .
docker run --rm -it -v "$PWD":/app pyenv-conda
```

## Conda Environment Footprint

### Overview

`conda` is both a package manager and an environment manager. Unlike
`venv`, it can manage the Python interpreter version itself and install
non-Python dependencies from conda channels.

This makes it useful for scientific and data-heavy projects where Python
packages depend on native libraries such as BLAS, CUDA, GDAL, or system
tools that are awkward to assemble with `pip` alone.

### Environment Definition

The environment is described in [`environment.yml`](environment.yml):

```yaml
name: tiny-webserver
channels:
  - conda-forge
dependencies:
  - python=3.14
  - bottle=0.13.4
  - ruff=0.15.12
  - pip
  - pip:
      - karva>=0.0.1a5
```

Most packages come from `conda-forge`. `karva` is installed through
`pip` because it is distributed through PyPI.

### PATH And Execution

The Dockerfile puts the conda environment first on `PATH`:

```sh
which python
which conda
which karva
which ruff
```

The active Python comes from `/opt/conda/envs/tiny-webserver/bin`, not
from a system Python under `/usr/bin`.

## Dependency Workflow

### Create The Environment

Create the environment from this folder:

```sh
conda env create -f environment.yml
conda activate tiny-webserver
```

### Manage Packages

Add a conda package from `conda-forge`:

```sh
conda install -c conda-forge <package>
```

Snapshot the direct environment requirements back to the YAML file:

```sh
conda env export --from-history > environment.yml
```

### Run The Project

This example keeps the project source on `PYTHONPATH` instead of
installing the project into the environment:

```sh
PYTHONPATH=src python -m tiny_webserver.app
```

Run tests and linting:

```sh
PYTHONPATH=src karva test tests/
ruff check .
```

### Leave The Environment

Return the shell to its previous environment:

```sh
conda deactivate
```

## Tradeoffs

### Pros

`conda` manages Python versions, non-Python packages, and compiled
scientific dependencies in one environment file.

### Cons

`conda` is heavier than `venv`, has its own package ecosystem, and can
be slower to solve than simpler PyPI-only workflows.

## Useful Inspection Commands

Use these command patterns inside the container to inspect the active
environment.

### Resolved Commands

```sh
which python
which conda
which karva
which ruff
```

Expected output includes paths like:

```text
/opt/conda/envs/tiny-webserver/bin/python
/opt/conda/bin/conda
/opt/conda/envs/tiny-webserver/bin/karva
/opt/conda/envs/tiny-webserver/bin/ruff
```

### Active Environment

```sh
echo $CONDA_DEFAULT_ENV
conda env list
```

Expected output includes:

```text
tiny-webserver
```

### Package Locations

```sh
python -c "import bottle, tiny_webserver; print('bottle =', bottle.__file__); print('tiny_webserver =', tiny_webserver.__file__)"
```

Expected output includes paths under:

```text
/opt/conda/envs/tiny-webserver/
/app/src/tiny_webserver/
```
