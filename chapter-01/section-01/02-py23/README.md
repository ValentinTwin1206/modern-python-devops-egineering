# historic_calculator

A small example application demonstrating Python 2.3 (released
**July 29, 2003**) together with the Numeric extension — the direct
ancestor of today's NumPy.

  * **Python version:** 2.3
  * **Release date:** July 29, 2003
  * **Associated PEP:** [PEP 314 — Metadata for Python Software
    Packages v1.1](https://peps.python.org/pep-0314/)

## System Requirements

### Overview

  * A Linux system with glibc 2.2 or 2.3.
  * The GNU C compiler (`gcc`) 2.95 or later, and `make`.
  * Development headers for the C library, `readline`, and `zlib`:
      - on Debian: `libc6-dev`, `libreadline-dev`, `zlib1g-dev`
      - on Red Hat: `glibc-devel`, `readline-devel`, `zlib-devel`
  * Root privileges (or write access to a custom `--prefix`) to
    install into `/usr/local`.
  * [Python 2.3](#install-python) installed on the system
  * [Numeric 24.0b2](#install-numeric) installed on the system

### Install Python

Download and unpack the Python 2.3 source archive:

```sh
cd /usr/src
wget https://www.python.org/ftp/python/2.3/Python-2.3.tgz
tar -xzf Python-2.3.tgz
```

Configure, build, and install the interpreter:

```sh
cd Python-2.3
./configure --prefix=/usr/local
make
make install
```

Verify that Python was installed correctly:

```sh
/usr/local/bin/python -V
```

> You should see `Python 2.3`.

### Install Numeric

Download and unpack the Numeric 24.0b2 source archive:

```sh
cd /usr/src
wget -O Numeric-24.0b2.tar.gz \
  "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"
tar -xzf Numeric-24.0b2.tar.gz
```

Build and install the Numeric extension:

```sh
cd Numeric-24.0b2
python setup.py build
python setup.py install
```

Verify that Numeric was installed correctly:

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

PEP 314 (shipped with Python 2.3) extends `distutils` with the
`requires=`, `provides=`, and `obsoletes=` keywords. For the first time
a project can *write down* its runtime dependencies — here
`requires=["Numeric"]` — and `python setup.py install` records that
information in the generated `PKG-INFO` so humans and tools can read it.

The critical caveat is that this metadata is purely informational:
`distutils` itself never resolves it, never fetches anything, and never
fails the install if `Numeric` is absent. Compared to py16 we have moved
from "undocumented" to "documented", but the human is still the
package manager.

## Installation

From the directory containing this `README.md`:

```sh
python setup.py install
```

> This places the `historic_calculator` module on Python's search path system-wide.

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
python historic_calculator/main.py max 1,-2,4
```

This prints:

```sh
max(1,-2,4) = 4.0
```

### Calculating the Vector Minimum

Use `min` to return the smallest value in the vector.

```sh
python historic_calculator/main.py min 1,-2,4
```

This prints:

```sh
min(1,-2,4) = -2.0
```

### Calculating the Vector Mean

Use `mean` to return the arithmetic average of the vector.

```sh
python historic_calculator/main.py mean 1.5,2.5,3.5
```

This prints:

```sh
mean(1.5,2.5,3.5) = 2.5
```

### Calculating the Vector Sum

Use `sum` to return the total of all values in the vector.

```sh
python historic_calculator/main.py sum 10,20,30,40
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
from historic_calculator.main import run_calculator, make_vector

print run_calculator("max", "1,-2,4")

v = make_vector([1, 2, 3, 4])
print v * 2
```
