# historic-calculator

A small example application demonstrating Python 1.6 (released
**September 5, 2000**) together with the Numerical extension — an
early ancestor of today's NumPy, by way of Numeric.

  * **Python version:** 1.6
  * **Release date:** September 5, 2000
  * **Associated PEP:** none — `distutils` graduated from a separately
    installable package into the stdlib in this release

## System Requirements

### Overview

  * A Linux system with glibc 2.1 or 2.2.
  * The GNU C compiler (`gcc`) 2.95 or later, and `make`.
  * Development headers for the C library, `readline`, and `zlib`:
      - on Debian: `libc6-dev`, `libreadline-dev`, `zlib1g-dev`
      - on Red Hat: `glibc-devel`, `readline-devel`, `zlib-devel`
  * Root privileges (or write access to a custom `--prefix`) to
    install into `/usr/local`.
  * [Python 1.6](#install-python) installed on the system
  * [Numeric 15.3](#install-numeric) installed on the system

### Install Python

Download and unpack the Python 1.6 source archive:

```sh
cd /usr/src
wget https://www.python.org/ftp/python/src/python-1.6.tar.gz
tar -xzf python-1.6.tar.gz
```

Configure, build, and install the interpreter:

```sh
cd Python-1.6
./configure --prefix=/usr/local
make
make install
```

Verify that Python was installed correctly:

```sh
/usr/local/bin/python -V
```

> You should see `Python 1.6`.

### Install Numeric

Download and unpack the Numerical 15.3 source archive:

```sh
cd /usr/src
wget -O Numerical-15.3.tgz \
  "https://sourceforge.net/projects/numpy/files/OldFiles/Numerical-15.3.tgz/download"
tar -xzf Numerical-15.3.tgz
```

Build and install the Numerical extension:

```sh
cd Numerical-15.3
python setup.py build
python setup.py install
```

Verify that Numerical was installed correctly:

```sh
python -c "import Numeric; print Numeric.__version__"
```

## Dependency Management

### Matrix

| Dependency  | 1.0.0                 | 2.0.0                      | 3.0.0                           | 4.0.0                            | 5.0.0                                             | 6.0.0                                       |
| ----------- | --------------------- | -------------------------- | ------------------------------- | -------------------------------- | ------------------------------------------------- | ------------------------------------------- |
| Python      | 1.6                   | 2.3                        | 2.4                             | 2.7                              | 3.5                                               | 3.11                                        |
| Numeric     | 15.3 (manual install) | 24.0b2 (declared, manual)  | 24.0b2 (resolved at install)    | —                                | —                                                 | —                                           |
| NumPy       | —                     | —                          | —                               | 1.9.2 (pinned, pip-installed)    | 1.11.3 (pinned, pip-installed)                    | 1.24.0 (pinned, pip-installed)              |
| Click       | —                     | —                          | —                               | —                                | 6.6 (pinned, pip-installed)                       | 8.1.3 (pinned, pip-installed)               |
| setuptools  | —                     | —                          | 0.6c11 (bootstrap dependency)   | bundled                          | bundled                                           | build backend (>=61.0, declared)            |
| pip         | —                     | —                          | —                               | bundled (PEP 477)                | bundled                                           | bundled, PEP 517/518 frontend               |
| pytest      | —                     | —                          | —                               | —                                | 3.0.7 (dev, requirements-dev.txt)                 | 7.2.0 (dev extra in `pyproject.toml`)       |
| Layout      | `setup.py` only       | `setup.py` (distutils)     | `setup.py` (setuptools)         | `setup.py` + `requirements.txt`  | `setup.py` + `setup.cfg` + 2× `requirements*.txt` | `pyproject.toml` only                        |

### Background

In 2000 there is no such thing as a declarative dependency. The freshly
stdlib-ified `distutils` only describes what *your* package ships —
through `name`, `version`, and `packages` in `setup.py` — and has no
vocabulary for talking about what your package needs in order to run.
Consumers learn about Numerical from this README, fetch its tarball by
hand, and run `python setup.py install` themselves before installing
`historic-calculator`. There is no index, no resolver, and no enforcement:
if Numerical is missing, the failure surfaces only at `import` time.

## Installation

From the directory containing this `README.md`:

```sh
python setup.py install
```

> This places the `my_package` module on Python's search path system-wide.

## Usage

The package exposes a single command-line entry point that
applies a reduction to a comma-separated vector of numbers.

The general form is:

```sh
python main.py COMMAND VECTOR
```

  * `COMMAND` is one of `max`, `min`, `mean`, or `sum`.
  * `VECTOR` is a comma-separated list of numbers, for example
    `1,-2,4`. Negative numbers and decimals are supported; spaces
    around the commas are allowed.

### Calculating the Vector Maximum

Use `max` to return the largest value in the vector.

```sh
python my_package/main.py max 1,-2,4
```

This prints:

```sh
max(1,-2,4) = 4.0
```

### Calculating the Vector Minimum

Use `min` to return the smallest value in the vector.

```sh
python my_package/main.py min 1,-2,4
```

This prints:

```sh
min(1,-2,4) = -2.0
```

### Calculating the Vector Mean

Use `mean` to return the arithmetic average of the vector.

```sh
python my_package/main.py mean 1.5,2.5,3.5
```

This prints:

```sh
mean(1.5,2.5,3.5) = 2.5
```

### Calculating the Vector Sum

Use `sum` to return the total of all values in the vector.

```sh
python my_package/main.py sum 10,20,30,40
```

This prints:

```sh
sum(10,20,30,40) = 100.0
```

### Handling Invalid Input

Calling the script with the wrong number of arguments, an unknown
command, or a malformed vector prints a short usage banner on
standard error and exits with a non-zero status.

You can also use the package from your own scripts:

```python
from my_package.main import run_calculator, make_vector

print run_calculator("max", "1,-2,4")

v = make_vector([1, 2, 3, 4])
print v * 2
```
