# Historic Calculator (Python 3.5)

A small example application demonstrating the **2016-era** Python project
layout: `setup.py` + `setup.cfg` + `requirements.txt` +
`requirements-dev.txt`, with NumPy and the **Click** CLI framework on
top of Python 3.5 (released **September 13, 2015**).

This directory also includes a repo-local [`requirements.lock`](requirements.lock)
snapshot so the fully resolved environment is visible in one file.

  * **Python version:** 3.5
  * **Release date:** September 13, 2015 (still the dominant 3.x in 2016 -- 3.6 only arrived in late December 2016)
  * **NumPy:** 1.11.3 (pinned in `requirements.txt`)
  * **Click:** 6.6 (pinned in `requirements.txt`)
  * **pytest:** 3.0.7 (pinned in `requirements-dev.txt`)
  * **Associated PEP:** [PEP 440 — Version Identification and Dependency
    Specification](https://peps.python.org/pep-0440/), the version-string
    standard underpinning `==` pinning in `requirements*.txt`.

## System Requirements

### Overview

  * [Docker](https://docs.docker.com/get-docker/) installed locally, or
    a Linux system with [Python 3.5](#install-python) available.
  * The pinned runtime dependencies listed in
    [`requirements.txt`](requirements.txt) and the pinned developer
    dependencies in [`requirements-dev.txt`](requirements-dev.txt),
    installed via pip.

### Install Python

#### On The Host

If you want a native host install, check whether `python3 -V` already
resolves to a valid Python 3.5 interpreter first:

```sh
python3 -V
```

If it does not, build Python 3.5.2 from source:

* Download the source tarball.

  ```sh
  curl -O https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
  ```

* Extract the archive.

  ```sh
  tar -xzf Python-3.5.2.tgz
  cd Python-3.5.2
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
  python3 -V
  ```

#### With Docker

By 2016 Docker was a mainstream tool, and the official `python:3.5`
image is the cleanest way to recreate a period-appropriate environment
today:

```sh
docker pull python:3.5
docker run --rm -it python:3.5 python -V
```

> You should see `Python 3.5.x`.

### Install dependencies

With Python 3.5 available, install the pinned runtime dependencies:

```sh
pip install -r requirements.txt
```

For development (running the test suite), also install the dev
dependencies:

```sh
pip install -r requirements-dev.txt
```

Verify that NumPy and Click were installed correctly:

```sh
python -c "import numpy, click; print(numpy.__version__, click.__version__)"
```

> You should see `1.11.3 6.6`.

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

By 2016 the Python project layout had stabilised into the four-file
shape that is still recognisable today: a setuptools-driven `setup.py`,
a `setup.cfg` for declarative metadata and shared tool configuration
(`[bdist_wheel]`, `[tool:pytest]`, `flake8`, …), a pinned
`requirements.txt` for deployments, and a separate
`requirements-dev.txt` (typically using `-r requirements.txt`) for
developer-only dependencies such as the test runner. Distinguishing
runtime from development dependencies — and pinning each set with
`==` — was the period's accepted answer to reproducible installs in
the absence of a standard lockfile. For convenience, this repository also
ships a flat [`requirements.lock`](requirements.lock) that captures the
fully resolved external package set for this exact example environment.

A pivotal late-2016 release sharpened the picture: **setuptools 30.3.0
(December 8, 2016)** introduced the `[metadata]` and `[options]`
sections in `setup.cfg`, allowing nearly everything previously written
imperatively in `setup.py` — `name`, `version`, `description`,
`packages`, `install_requires`, `entry_points`, classifiers, and so on
— to be specified declaratively. From this point forward `setup.py`
is reduced to a one-line `setup()` shim purely so that older tooling
still has something to invoke. This project follows that pattern: see
[`setup.cfg`](setup.cfg) for the full metadata and
[`setup.py`](setup.py) for the shim.

The CLI story matured at the same time. Click 1.0 shipped in
**April 2014** and was the dominant choice for new command-line tools
by 2016, replacing hand-rolled `argparse` plumbing with composable
decorators and a `console_scripts` entry point that gets installed onto
the user's `PATH`.

What is still missing compared to today is `pyproject.toml` (PEP 518
was accepted in **May 2016** but not implemented in pip until 2017+),
a lockfile that captures the *full* resolved tree (Pipfile.lock arrives
in 2017, then Poetry, then uv), and pip's modern resolver (rewritten
in 2020).

## Build

Python 3.5 is the first section in this chapter where wheels (PEP 427,
2012) are fully usable: `setup.cfg` already declares
`[bdist_wheel] universal = 0`, and the `wheel` package is part of the
standard pip toolchain by 2016. Build a pure-Python wheel from the
directory containing this `README.md`:

```sh
pip install wheel
python setup.py bdist_wheel
```

> The resulting artifact appears in
> `dist/historic_calculator-5.0.0-py3-none-any.whl` and is installable
> directly with `pip install dist/historic_calculator-5.0.0-py3-none-any.whl`.

A source distribution is still available alongside the wheel:

```sh
python setup.py sdist
```

## Installation

* Install the pinned runtime dependencies first.

  ```sh
  pip install -r requirements.txt
  ```

* If you want the pre-resolved combined dependency set in one file,
  install the lock snapshot instead.

  ```sh
  pip install -r requirements.lock
  ```

* Install the package itself next. This registers the
  `hist_calc` console script on your `PATH`.

  ```sh
  pip install .
  ```

* For development, also install the dev dependencies and run the test
  suite.

  ```sh
  pip install -r requirements-dev.txt
  pytest
  ```

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
pip install -r requirements-dev.txt
pip install -e .
pytest
```

> You should see `8 passed` from [`tests/test_main.py`](tests/test_main.py),
> covering the public Python API as well as the Click CLI via
> `click.testing.CliRunner`.
