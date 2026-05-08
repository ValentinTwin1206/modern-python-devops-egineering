# historic_calculator (Python 2.4)

A small command-line utility that reduces a comma-separated vector to its `max`, `min`, `mean`, or `sum`. This release runs on Python 2.4 with setuptools 0.6c11. Setuptools resolves the Numeric dependency at install time through `install_requires=`.

## Required Developer Tools

- A Linux host with a working C toolchain.
- Python 2.4.
- Setuptools 0.6c11.
- Numeric 24.0b2 installed and registered as a setuptools distribution.
- Docker (for the chapter helper path).

### With Docker

Build the development image through the chapter helper:

```sh
../build.sh build --path section-03/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```sh
../build.sh build --path section-03/Dockerfile.devEnv
```

Build and run the deployment image:

```sh
../build.sh build --path section-03/Dockerfile
```

### On Host

Fetch and build Python 2.4 from source:

```sh
wget https://www.python.org/ftp/python/2.4/Python-2.4.tgz
tar -xzf Python-2.4.tgz
./configure --prefix=/usr/local && make && make install
```

Fetch and install setuptools 0.6c11:

```sh
wget https://files.pythonhosted.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz
tar -xzf setuptools-0.6c11.tar.gz
cd setuptools-0.6c11 && python setup.py install
```

Fetch Numeric 24.0b2:

```sh
wget -O Numeric-24.0b2.tar.gz "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"
tar -xzf Numeric-24.0b2.tar.gz
```

Patch Numeric to use setuptools so it registers as a real distribution:

```sh
sed -i 's/from distutils.core import setup/from setuptools import setup/' Numeric-24.0b2/setup.py
```

Install Numeric:

```sh
cd Numeric-24.0b2 && python setup.py install
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

Rebuild the source distribution after edits:

```sh
python setup.py sdist
```

Reinstall locally to refresh the entry point:

```sh
python setup.py install
```
