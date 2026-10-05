# historic_calculator (Python 1.6)

A small command-line utility that reduces a comma-separated vector to its `max`, `min`, `mean`, or `sum`. This release runs on Python 1.6 and uses the freshly stdlib-ified `distutils` for packaging.

## Required Developer Tools

- A Linux host with `gcc`, `make`, and the development headers for `glibc`, `readline`, and `zlib`.
- Python 1.6 built from source.
- The Numerical 15.3 extension.
- Docker (for the projects helper path).

### With Docker

`Dockerfile.devEnv` builds a containerized approximation of the Python 1.6 development environment. It compiles Python 1.6 on an old Debian base image and provides the tooling needed to explore the packaging workflow without changing the host machine. Build the development image through the projects helper:

```bash
../../build.sh build --path proj6_historic_calculator/2000/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../../build.sh build --path proj6_historic_calculator/2000/Dockerfile.devEnv
```

Build and run the deployment image:

```bash
../../build.sh build --path proj6_historic_calculator/2000/Dockerfile
```

### On Host

Fetch the Python source archive:

```sh
wget https://www.python.org/ftp/python/src/python-1.6.tar.gz
```

Unpack and enter the source tree:

```sh
tar -xzf python-1.6.tar.gz
```

Configure the build:

```sh
./configure --prefix=/usr/local
```

Compile and install Python:

```sh
make
make install
```

Fetch and unpack Numerical 15.3:

```sh
wget -O Numerical-15.3.tgz "https://sourceforge.net/projects/numpy/files/OldFiles/Numerical-15.3.tgz/download"
tar -xzf Numerical-15.3.tgz
```

Build and install Numerical:

```sh
python setup.py install
```

## Usage Guide

Build the source distribution from this directory:

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

Run the package directly from the source tree without installing:

```sh
PYTHONPATH=. python -c "from historic_calculator.main import run_calculator; print run_calculator('max', '1,-2,4')"
```

Rebuild the source distribution after edits:

```sh
python setup.py sdist
```
