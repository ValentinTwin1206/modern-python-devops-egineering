# historic_calculator (Python 2.3)

A small command-line utility that reduces a comma-separated vector to its `max`, `min`, `mean`, or `sum`. This release runs on Python 2.3. The `setup.py` declares its dependency on Numeric through PEP 314 metadata, but `distutils` does not install it for you.

## Required Developer Tools

- A Linux host with a working C toolchain.
- Python 2.3.
- Numeric 24.0b2 installed before this package.
- Docker (for the projects helper path).

### With Docker

Build the development image through the projects helper:

```sh
../../build.sh build --path proj5_historic_calculator/2003/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```sh
../../build.sh build --path proj5_historic_calculator/2003/Dockerfile.devEnv
```

Build and run the deployment image:

```sh
../../build.sh build --path proj5_historic_calculator/2003/Dockerfile
```

### On Host

Fetch and build Python 2.3 from source:

```sh
wget https://www.python.org/ftp/python/2.3/Python-2.3.tgz
tar -xzf Python-2.3.tgz
```

Install Python:

```sh
./configure --prefix=/usr/local && make && make install
```

Fetch, unpack, and install Numeric 24.0b2:

```sh
wget -O Numeric-24.0b2.tar.gz "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"
tar -xzf Numeric-24.0b2.tar.gz
python setup.py install
```

## Usage Guide

Build the source distribution:

```sh
python setup.py sdist
```

Install the package and the `hist_calc` launcher:

```sh
python setup.py install
```

Run a calculation:

```sh
hist_calc max 1,-2,4
```

## Development Guide

Rebuild the source distribution after edits:

```sh
python setup.py sdist
```

Reinstall locally:

```sh
python setup.py install
```
