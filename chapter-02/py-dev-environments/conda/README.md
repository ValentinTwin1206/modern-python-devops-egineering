# `conda` Example

This folder shows how to use **`conda`** to create an isolated
environment for a project.

## What Is `conda`?

`conda` is more than a virtual-environment tool: it is a full
**package and environment manager**. Unlike `pip`, `conda` can also
install non-Python software (compiled C/Fortran libraries, command-line
tools, even alternative Python interpreters) and it manages the Python
version itself, not just packages on top of an existing Python.

It is the standard choice in data science and scientific computing
because libraries like NumPy, SciPy, PyTorch, or geospatial tooling
depend on heavy native components (BLAS, CUDA, GDAL, …) that are
painful to install with `pip` alone.

## How It Works

1. You install a conda distribution once. The two common choices are
   **Miniconda** (small, just `conda` and Python) and **Anaconda**
   (large, ships hundreds of preinstalled packages).
2. You describe an environment in a YAML file
   ([`environment.yml`](environment.yml)): which Python version, which
   channels to fetch from, and which packages.
3. `conda env create -f environment.yml` reads the file, downloads
   prebuilt binary packages from those channels, and assembles them
   into an environment under `envs/<name>/`.
4. `conda activate <name>` switches your shell to use that environment.

## Create The Environment

From this folder, on a machine that has Miniconda or Anaconda installed:

```sh
conda env create -f environment.yml
conda activate my-package
```

Your prompt should now show `(my-package)` and `which python` should
point inside the conda envs folder.

## Manage Dependencies

Add a package to the environment:

```sh
conda install -c conda-forge <package>
```

Snapshot the current environment back to a file:

```sh
conda env export --from-history > environment.yml
```

To leave the environment:

```sh
conda deactivate
```

## Run The Example

This example follows the rule "conda must not use pip unless
necessary", so the project is not installed with `pip install .`.
Instead, the package source lives in [`src/`](src/) and is added to
`PYTHONPATH`:

```sh
PYTHONPATH=src python -m my_package.main
```

You should see `Hello from conda environment`.

## Run It With Docker

A working [`Dockerfile`](Dockerfile) is included. It uses the official
[`continuumio/miniconda3`](https://hub.docker.com/r/continuumio/miniconda3)
base image instead of `python:3.11-slim`, because conda needs to manage
the Python interpreter itself:

```sh
docker build -t pyenv-conda .
docker run --rm pyenv-conda
```

## Pros

- **Manages non-Python packages** — install BLAS, CUDA, GDAL, R, etc.,
  not just PyPI packages.
- **Manages Python itself** — switch interpreters per environment.
- **Prebuilt binaries** for scientific libraries, no compiler needed.
- **Cross-platform** — same `environment.yml` works on Linux, macOS,
  and Windows.

## Cons

- **Heavyweight** — even Miniconda is hundreds of MB before you create
  any environments.
- **Slower resolution** — solving an `environment.yml` is much slower
  than `pip install`, especially with the classic solver. Use
  [Mamba](https://mamba.readthedocs.io/) for a much faster experience.
- **Two ecosystems** — conda packages and pip packages live in the
  same environment but are not aware of each other; mixing them is
  possible but error-prone.
- **Channel governance** — the default channels have commercial usage
  limits; most teaching examples (including this one) use the
  community-run [`conda-forge`](https://conda-forge.org/) channel.

## When To Use It

Use `conda` when:

- Your project relies on heavy native libraries (NumPy with MKL,
  PyTorch with CUDA, GDAL/PROJ, …).
- You need to manage the Python interpreter itself, not just packages
  on top of it.
- You work in data science, scientific computing, or bioinformatics
  where conda is already the team standard.

For pure-Python web or CLI projects, [`venv`](../venv/) or
[`pipenv`](../pipenv/) are usually simpler and lighter.
