# historic_calculator (Python 2.7)

A small command-line utility that reduces a comma-separated vector to its `max`, `min`, `mean`, or `sum`. This release runs on Python 2.7. Runtime dependencies are pinned in `requirements.txt` and installed with `pip`.

## Required Developer Tools

- Python 2.7 (preferably 2.7.9 or newer for bundled `pip`).
- `pip` and setuptools.
- Docker (for the chapter helper path).

### With Docker

Build the development image through the chapter helper:

```sh
../build.sh build --path section-04/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```sh
../build.sh build --path section-04/Dockerfile.devEnv
```

Build and run the deployment image:

```sh
../build.sh build --path section-04/Dockerfile
```

### On Host

Use the official Python 2.7 image directly if possible:

```sh
docker run --rm -it python:2.7
```

Or build Python 2.7 from source on the host:

```sh
curl -O https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
tar -xzf Python-2.7.9.tgz
cd Python-2.7.9 && ./configure --prefix=/usr/local && make && sudo make install
```

Install the pinned runtime dependencies:

```sh
pip install -r requirements.txt
```

## Usage Guide

Build the source distribution:

```sh
python setup.py sdist
```

Install the package and register the `hist_calc` console script:

```sh
python setup.py install
```

Run a calculation:

```sh
hist_calc max 1,-2,4
```

## Development Guide

Reinstall after edits:

```sh
python setup.py install
```

Refresh the pinned runtime dependencies:

```sh
pip install -r requirements.txt
```
