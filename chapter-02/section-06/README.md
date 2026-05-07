# Historic Calculator (Python 3.11)

A small example application demonstrating the **2022-era** Python project
layout: a single declarative `pyproject.toml` (PEP 621), with NumPy and
the Click CLI framework on top of Python 3.11 (released
**October 24, 2022**).

  * **Python version:** 3.11
  * **Release date:** October 24, 2022
  * **NumPy:** 1.24.0 (pinned in `pyproject.toml`)
  * **Click:** 8.1.3 (pinned in `pyproject.toml`)
  * **pytest:** 7.2.0 (pinned in `pyproject.toml` optional `dev` extra)
  * **Associated PEPs:**
    * [PEP 517 — A build-system independent format for source trees](https://peps.python.org/pep-0517/)
    * [PEP 518 — Specifying Minimum Build System Requirements](https://peps.python.org/pep-0518/)
    * [PEP 621 — Storing project metadata in `pyproject.toml`](https://peps.python.org/pep-0621/)

## System Requirements

### Overview

  * [Docker](https://docs.docker.com/get-docker/) installed locally, or
    a Linux system with [Python 3.11](#install-python) available.
  * The pinned runtime dependencies and optional dev dependencies are
    declared directly in [`pyproject.toml`](pyproject.toml).

### Install Python

#### On The Host

If you want a native host install, check whether `python3 -V` already
resolves to a valid Python 3.11 interpreter first:

```sh
python3 -V
```

If it does not, build Python 3.11.0 from source:

* Download the source tarball.

  ```sh
  curl -O https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
  ```

* Extract the archive.

  ```sh
  tar -xzf Python-3.11.0.tgz
  cd Python-3.11.0
  ```

* Configure the build.

  ```sh
  ./configure --prefix=/usr/local --enable-optimizations
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
  python3 -V
  ```

#### With Docker

The official `python:3.11` image is the cleanest way to recreate a
period-appropriate environment today:

```sh
docker pull python:3.11
docker run --rm -it python:3.11 python -V
```

> You should see `Python 3.11.x`.

### Install dependencies

With Python 3.11 available, install the project and its pinned runtime
dependencies directly from `pyproject.toml`:

```sh
pip install .
```

For development (running the test suite), install the optional `dev`
dependency group instead:

```sh
pip install .[dev]
```

Verify that NumPy and Click were installed correctly:

```sh
python -c "import numpy, click; print(numpy.__version__, click.__version__)"
```

> You should see `1.24.0 8.1.3`.

## Dependency Management

### Matrix

| Dependency  | 1.0.0                 | 2.0.0                      | 3.0.0                           | 4.0.0                            | 5.0.0                                             | 6.0.0                                       |
| ----------- | --------------------- | -------------------------- | ------------------------------- | -------------------------------- | ------------------------------------------------- | ------------------------------------------- |
| Python      | 1.6                   | 2.3                        | 2.4                             | 2.7                              | 3.5                                               | 3.11                                        |
| Numeric     | 15.3 (manual install) | 24.0b2 (declared, manual)  | 24.0b2 (resolved at install)    | —                                | —                                                 | —                                           |
| NumPy       | —                     | —                          | —                               | 1.9.2 (pinned, pip-installed)    | 1.11.3 (pinned, pip-installed)                    | 1.24.0 (pinned in `pyproject.toml`)         |
| Click       | —                     | —                          | —                               | —                                | 6.6 (pinned, pip-installed)                       | 8.1.3 (pinned in `pyproject.toml`)          |
| setuptools  | —                     | —                          | 0.6c11 (bootstrap dependency)   | bundled                          | bundled                                           | build backend (>=61.0, declared)            |
| pip         | —                     | —                          | —                               | bundled (PEP 477)                | bundled                                           | bundled, PEP 517/518 frontend               |
| pytest      | —                     | —                          | —                               | —                                | 3.0.7 (dev, requirements-dev.txt)                 | 7.2.0 (dev extra in `pyproject.toml`)       |
| Layout      | `setup.py` only       | `setup.py` (distutils)     | `setup.py` (setuptools)         | `setup.py` + `requirements.txt`  | `setup.py` + `setup.cfg` + 2× `requirements*.txt` | `pyproject.toml` only                        |

### Background

By the early 2020s the long-running migration toward declarative
packaging was complete. **PEP 518 (2016)** introduced
`pyproject.toml` as the place to declare build-system requirements.
**PEP 517 (2017)** generalised the build front-end / back-end split so
pip could drive any compliant builder, not just setuptools.
**PEP 621 (Nov 2020)** standardised a `[project]` table for static
project metadata (name, version, dependencies, scripts, …). And
**setuptools 61.0 (March 2022)** finally implemented PEP 621 natively,
which is the moment a setuptools-based project can drop both
`setup.py` and `setup.cfg` and live entirely from `pyproject.toml`.

This project does exactly that: see [`pyproject.toml`](pyproject.toml).
The `[build-system]` table declares the build backend, the `[project]`
table holds all metadata previously kept in `setup.py` / `setup.cfg`,
the exact runtime pins live in `[project.dependencies]`, the optional
test tooling lives in `[project.optional-dependencies]`,
`[project.scripts]` registers the `hist_calc` console entry
point, and `[tool.pytest.ini_options]` replaces the old
`[tool:pytest]` section.

Crucially, 2022-era pip is fully capable of reading those dependency
tables during `pip install .` and `pip install .[dev]`, so a
setuptools-based project like this no longer needs `requirements.txt`
or `requirements-dev.txt` merely to express its direct dependencies.
What `pyproject.toml` still does **not** provide is a true lockfile:
there is no fully solved dependency graph with hashes and transitive
pins. That role still belongs to later, opinionated toolchains such as
`Pipfile.lock` (Pipenv, 2017), `poetry.lock` (Poetry, 2018),
`pdm.lock` (PDM, 2020), and `uv.lock` (uv, 2024).

What is finally missing in this layout — and what motivates the next
chapter — is environment isolation by default and a real lockfile.
`pip install` still mutates whatever site-packages it points at, and
the exact versions pinned in `pyproject.toml` are still only *direct*
dependency pins, not a fully solved graph including hashes.

That makes this the first chapter in the series where a setuptools-based
project keeps its direct runtime and dev dependency declarations entirely
inside `pyproject.toml`.

## Build

PEP 517 / PEP 518 / PEP 621 together let pip drive the setuptools
backend declared in `pyproject.toml` to produce a modern wheel without
ever invoking `setup.py`. The 2022-era `build` frontend is the
idiomatic builder:

```sh
pip install build
python -m build
```

> The resulting artifacts appear in `dist/`:
>
> * `historic_calculator-6.0.0-py3-none-any.whl` -- a pure-Python wheel
> * `historic_calculator-6.0.0.tar.gz` -- the matching source distribution
>
> Install either with `pip install dist/<filename>`.

## Installation

* Install the package and its pinned runtime dependencies. This
  registers the `hist_calc` console script on your `PATH`.

  ```sh
  pip install .
  ```

* For development, install the optional `dev` dependency group and run
  the test suite.

  ```sh
  pip install .[dev]
  pytest
  ```

* The previous two-step workflow is no longer required because the
  package metadata and direct dependency pins live in
  [`pyproject.toml`](pyproject.toml).

  This replaces the older `requirements*.txt` pair for this example.

## Usage

The package exposes a single Click-based command-line entry point that
applies a reduction to a comma-separated vector of numbers.

The general form is:

```sh
hist_calc COMMAND VECTOR
```

  * `COMMAND` is one of `max`, `min`, `mean`, or `sum`.
  * `VECTOR` is a comma-separated list of numbers, for example
    `1,-2,4`. Negative numbers and decimals are supported; spaces
    around the commas are allowed.

You can also discover commands and options via Click's auto-generated
help:

```sh
hist_calc --help
hist_calc max --help
```

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
command, or a malformed vector causes Click to print its usage banner
on standard error and exit with a non-zero status.

You can also use the package from your own scripts:

```python
from historic_calculator import run_calculator, make_vector

print(run_calculator("max", "1,-2,4"))

v = make_vector([1, 2, 3, 4])
print(v * 2)
```

## Testing

Install the dev dependencies and run pytest from the project root:

```sh
pip install .[dev]
pytest
```

> You should see `8 passed` from [`tests/test_main.py`](tests/test_main.py),
> covering the public Python API as well as the Click CLI via
> `click.testing.CliRunner`.
