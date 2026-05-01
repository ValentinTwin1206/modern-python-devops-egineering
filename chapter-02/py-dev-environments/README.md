# Python Development Environments

This directory is a teaching repository for the four most common ways to
isolate a Python project's dependencies from the system interpreter:
[`venv`](./venv/), [`virtualenv`](./virtualenv/), [`conda`](./conda/),
and [`pipenv`](./pipenv/). Every subdirectory is fully self-contained,
ships the same minimal example package, and uses only its own tooling.

## Subdirectories

| Tool | Folder | Dependency file(s) | Container base | Details |
| ---- | ------ | ------------------ | -------------- | ------- |
| `venv` | [`venv/`](./venv/) | `requirements.txt` | `python:3.11-slim` | [README](./venv/README.md) |
| `virtualenv` | [`virtualenv/`](./virtualenv/) | `requirements.txt` | `python:3.11-slim` | [README](./virtualenv/README.md) |
| `conda` | [`conda/`](./conda/) | `environment.yml` | `continuumio/miniconda3` | [README](./conda/README.md) |
| `pipenv` | [`pipenv/`](./pipenv/) | `Pipfile` + `Pipfile.lock` | `python:3.11-slim` | [README](./pipenv/README.md) |

## What Is A Virtual Environment?

A virtual environment is a self-contained Python installation with its
own `python` executable and its own `site-packages` directory. Anything
you install into a virtual environment stays inside that environment and
does not affect the system Python or any other project. This solves two
real-world problems:

1. **Isolation** — different projects can pin incompatible versions of
   the same library without colliding.
2. **Reproducibility** — recording exactly which packages are installed
   makes it possible to recreate the environment on another machine.

The four tools in this directory all solve those two problems but with
different trade-offs.

## Comparison

| Aspect | `venv` | `virtualenv` | `conda` | `pipenv` |
| ------ | ------ | ------------ | ------- | -------- |
| Ships with Python | yes (3.3+) | no, install with `pip` | no, separate distribution | no, install with `pip` |
| Manages Python itself | no | no | yes | no |
| Installs from | PyPI (via `pip`) | PyPI (via `pip`) | Anaconda channels (also pip-compatible) | PyPI (via `pip`) |
| Lockfile | none (only `requirements.txt`) | none (only `requirements.txt`) | `environment.yml` can pin everything | `Pipfile.lock` (true lockfile) |
| Handles non-Python deps | no | no | yes (C/Fortran libs, CUDA, R, …) | no |
| Best for | quick scripts, modern stdlib-only setups | older Python or extra features | data science, scientific stacks | application development with deterministic installs |

## Key Differences

- `venv` is part of the Python standard library since 3.3. No extra
  install step, no extra dependency, but also no extra features.
- `virtualenv` is the older, third-party tool that inspired `venv`. It
  is faster, supports more Python versions, and offers more options,
  at the cost of being an extra package you have to install.
- `conda` is a full **package and environment manager** that handles
  binary, non-Python dependencies as well. It is the standard choice
  in data science and scientific computing where libraries like NumPy,
  SciPy, or PyTorch ship compiled artifacts and depend on system
  libraries (BLAS, CUDA, GDAL, …).
- `pipenv` combines `pip` and `virtualenv` and adds a real lockfile.
  `Pipfile` is the human-edited list of direct dependencies;
  `Pipfile.lock` records the fully resolved tree with hashes for
  deterministic, secure installs.

## When To Use Which

- Use **`venv`** when you want zero extra setup, a recent Python, and
  only Python dependencies. This is the default modern choice for
  application code.
- Use **`virtualenv`** when you need to support older Pythons or want
  features `venv` does not have (faster creation, custom seeds, …).
- Use **`conda`** when your project depends on heavy native libraries
  (NumPy/SciPy with MKL, GPU stacks, geospatial tools) or when you
  need to manage the Python interpreter itself.
- Use **`pipenv`** when you want a deterministic application install
  with a true lockfile and do not want to step up to a full project
  manager such as Poetry, PDM, or uv.

## Repository Layout

Every subdirectory follows the same shape so the only thing that
changes between them is the environment tool itself:

```
<tool>/
├── src/my_package/main.py     # one trivial entry point
├── pyproject.toml             # PEP 621 metadata
├── <tool-specific deps>       # requirements.txt | environment.yml | Pipfile(+.lock)
├── Dockerfile                 # builds and runs the example
├── README.md                  # explains the tool in plain language
├── .dockerignore
└── .gitignore
```

Open the README inside each folder for the actual create / install /
run commands.

## Pinned Dependencies

Every environment installs the same external package set:

```
click==6.6
numpy==1.11.3
py==1.11.0
pytest==3.0.7
```

> Compatibility note: these versions are intentionally aligned with the
> [`py-packaging-history/py35`](../py-packaging-history/py35/) example.
> They predate `cp311` wheels for `numpy==1.11.3`, so installing them
> on `python:3.11-slim` requires building NumPy from source (this is
> why the Dockerfiles install `build-essential` before installing
> dependencies). Conda gets `numpy 1.11.3` from `conda-forge` as a
> prebuilt binary, which is one of the practical reasons to choose
> conda for old scientific stacks.
