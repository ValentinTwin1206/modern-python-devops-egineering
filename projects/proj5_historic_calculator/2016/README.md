# historic_calculator (Python 3.5)

A small Click-based command-line utility that reduces a comma-separated vector to its `max`, `min`, `mean`, or `sum`. This release runs on Python 3.5. Project metadata lives in `setup.cfg` with a one-line `setup.py` shim, and dependencies split between `requirements.txt` and `requirements-dev.txt`.

## Required Developer Tools

- Python 3.5.
- `pip`, setuptools, and `wheel`.
- pytest (for the test suite).
- Docker (for the projects helper path).

### With Docker

Build the development image through the projects helper:

```sh
../../build.sh build --path proj5_historic_calculator/2016/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```sh
../../build.sh build --path proj5_historic_calculator/2016/Dockerfile.devEnv
```

Build and run the deployment image:

```sh
../../build.sh build --path proj5_historic_calculator/2016/Dockerfile
```

### On Host

Use the official Python 3.5 image directly if possible:

```sh
docker run --rm -it python:3.5
```

Or build Python 3.5.2 from source on the host:

```sh
curl -O https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
tar -xzf Python-3.5.2.tgz
cd Python-3.5.2 && ./configure --prefix=/usr/local && make && sudo make install
```

Install the pinned runtime dependencies:

```sh
pip install -r requirements.txt
```

Install the development dependencies:

```sh
pip install -r requirements-dev.txt
```

## Usage Guide

Build the wheel and the source distribution:

```sh
pip install wheel
python setup.py bdist_wheel sdist
```

Install the project:

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

Install the project in editable mode:

```sh
pip install -e .
```

Run the test suite:

```sh
pytest
```
