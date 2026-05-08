# historic_calculator (Python 3.11)

A small Click-based command-line utility that reduces a comma-separated vector to its `max`, `min`, `mean`, or `sum`. This release runs on Python 3.11 and stores all metadata, dependency pins, and entry points in a single `pyproject.toml`.

## Required Developer Tools

- Python 3.11.
- `pip` and the `build` frontend.
- pytest (for the test suite).
- Docker (for the chapter helper path).

### With Docker

Build the development image through the chapter helper:

```sh
../build.sh build --path section-06/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```sh
../build.sh build --path section-06/Dockerfile.devEnv
```

Build and run the deployment image:

```sh
../build.sh build --path section-06/Dockerfile
```

### On Host

Use the official Python 3.11 image directly if possible:

```sh
docker run --rm -it python:3.11
```

Or build Python 3.11.0 from source on the host:

```sh
curl -O https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
tar -xzf Python-3.11.0.tgz
cd Python-3.11.0 && ./configure --prefix=/usr/local --enable-optimizations && make && sudo make install
```

Install the modern build frontend:

```sh
pip install build
```

## Usage Guide

Build the wheel and the source distribution:

```sh
python -m build
```

Install the project and its pinned runtime dependencies:

```sh
pip install .
```

Run a calculation:

```sh
hist_calc max 1,-2,4
```

Discover the Click help text:

```sh
hist_calc --help
```

## Development Guide

Install the project together with the optional `dev` group:

```sh
pip install .[dev]
```

Run the test suite:

```sh
pytest
```
