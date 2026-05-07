# Historic Calculator (Python 2.7)

A small example application demonstrating Python 2.7 (released
**July 3, 2010**, with `pip` first bundled in **2.7.9** on **December 10,
2014** via PEP 477's `ensurepip`) together with **NumPy** and the now
standard **pip + setuptools + `requirements.txt`** workflow.

  * **Python version:** 2.7
  * **Release date:** July 3, 2010 (with bundled `pip` from 2.7.9, December 10, 2014)
  * **NumPy:** 1.9.2 (pinned in `requirements.txt`)
  * **Associated PEP:** [PEP 477 — Backport `ensurepip` (`pip` bootstrap)
    to Python 2.7](https://peps.python.org/pep-0477/)

## System Requirements

### Overview

  * [Docker](https://docs.docker.com/get-docker/) installed locally, or
    a Linux system with [Python 2.7](#install-python) available.
  * The pinned runtime dependencies listed in
    [`requirements.txt`](requirements.txt), installed via pip.

### Install Python

#### On The Host

If you want a native host install, check whether `python -V` already
resolves to a valid Python 2.7 interpreter first:

```sh
python -V
```

If it does not, build Python 2.7.9 from source:

* Download the source tarball.

  ```sh
  curl -O https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
  ```

* Extract the archive.

  ```sh
  tar -xzf Python-2.7.9.tgz
  cd Python-2.7.9
  ```

* Configure the build.

  ```sh
  ./configure --prefix=/usr/local
  ```

* Compile Python.

  ```sh
  make
  ```

* Install it on the host.

  ```sh
  sudo make install
  ```

* Verify that the interpreter resolves correctly.

  ```sh
  python -V
  ```

#### With Docker

Docker first appeared during the Python 2.7 era, so the official image
is a practical way to recreate a period-appropriate environment today:

```sh
docker pull python:2.7
docker run --rm -it python:2.7 python -V
```

> You should see `Python 2.7.x`.

### Install dependencies

With Python 2.7 available, install the pinned runtime dependencies:

```sh
pip install -r requirements.txt
```

Verify that NumPy was installed correctly:

```sh
python -c "import numpy; print numpy.__version__"
```

> You should see `1.9.2`.

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

Python 2.7.9 (Dec 2014) was the first 2.x release to ship `pip` itself
via PEP 477's `ensurepip` module, completing the transition started by
setuptools a decade earlier: dependency installation is now a bundled,
first-class part of the language. The idiomatic project layout pairs a
`setup.py` (with `install_requires=` describing *abstract* runtime
dependencies) and a `requirements.txt` (pinning *concrete* versions for
reproducible deployments). `pip install -r requirements.txt` resolves
and installs from PyPI, and a single shared lockfile-style listing is
enough to reproduce the dependency set across machines.

What is still missing compared to today is environment isolation by
default (virtualenv exists since 2007 but is opt-in), proper
transitive-resolver semantics (pip's resolver was rewritten only in
2020), and lockfiles that capture the *full* resolved tree (Pipfile.lock
in 2017, then `pyproject.toml`/Poetry/uv after that).

## Build

The 2010-era Python 2.7 layout predates PEP 427 (wheels, 2012), so the
canonical distribution format here is a **source distribution** (sdist):

```sh
python setup.py sdist
```

> The resulting tarball appears in `dist/historic_calculator-4.0.0.tar.gz`.

## Installation

Install the package itself by running:

```sh
python setup.py install
```

> This registers the `hist_calc` console script on `PATH` via setuptools'
> `console_scripts` entry point.

## Usage

The package exposes a single command-line entry point that
applies a reduction to a comma-separated vector of numbers.

The general form is:

```sh
hist_calc COMMAND VECTOR
```

  * `COMMAND` is one of `max`, `min`, `mean`, or `sum`.
  * `VECTOR` is a comma-separated list of numbers, for example
    `1,-2,4`. Negative numbers and decimals are supported; spaces
    around the commas are allowed.

### Calculating the Vector Maximum

Use `max` to return the largest value in the vector.

```sh
hist_calc max 1,-2,4
```

This prints:

```sh
max(1,-2,4) = 4.0
```

### Calculating the Vector Minimum

Use `min` to return the smallest value in the vector.

```sh
hist_calc min 1,-2,4
```

This prints:

```sh
min(1,-2,4) = -2.0
```

### Calculating the Vector Mean

Use `mean` to return the arithmetic average of the vector.

```sh
hist_calc mean 1.5,2.5,3.5
```

This prints:

```sh
mean(1.5,2.5,3.5) = 2.5
```

### Calculating the Vector Sum

Use `sum` to return the total of all values in the vector.

```sh
hist_calc sum 10,20,30,40
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
