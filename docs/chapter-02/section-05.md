# Section 05: Python 3.5 with `setup.cfg` and split requirements

This page covers the fifth packaging snapshot in the Historic Calculator series. The example targets Python 3.5, released on September 13, 2015. It uses the four-file project layout that dominated 2016: `setup.py`, `setup.cfg`, `requirements.txt`, and `requirements-dev.txt`. The CLI is built with Click, and pytest replaces ad hoc test runners.

## Background

Setuptools 30.3.0 in December 2016 added `[metadata]` and `[options]` sections in `setup.cfg`. From that moment, almost everything previously written imperatively in `setup.py` could be expressed declaratively in `setup.cfg`, and `setup.py` collapsed into a one-line `setup()` shim that legacy tools can still invoke.

The dependency story splits across two files. Runtime pins live in `requirements.txt`. Development pins live in `requirements-dev.txt` and usually start with `-r requirements.txt`. Together, they were the period's accepted answer to reproducible installs while a real lockfile standard was missing.

The CLI gains real structure. Click 1.0 shipped in April 2014 and was the dominant choice by 2016. Decorators replace hand-rolled `argparse` plumbing, and `console_scripts` registers `hist_calc` on `PATH`.

## Packaging matrix

| Field            | Value                                                    |
| ---------------- | -------------------------------------------------------- |
| Project version  | 5.0.0                                                    |
| Python version   | 3.5                                                      |
| NumPy            | 1.11.3, pinned in `requirements.txt`                     |
| Click            | 6.6, pinned in `requirements.txt`                        |
| pytest           | 3.0.7, pinned in `requirements-dev.txt`                  |
| Layout           | `setup.py` shim plus declarative `setup.cfg`             |
| Distribution     | wheel and sdist                                          |

## Build

Build a pure-Python wheel:

```bash
python setup.py bdist_wheel
```

Build a source distribution alongside it:

```bash
python setup.py sdist
```

PEP 427 wheels are fully usable in this era. `setup.cfg` already declares `[bdist_wheel] universal = 0`.

## Install

Install the runtime dependencies:

```bash
pip install -r requirements.txt
```

Install the project:

```bash
pip install .
```

Install the development dependencies and run the test suite:

```bash
pip install -r requirements-dev.txt
```

Run the tests:

```bash
pytest
```

## Usage

Click auto-generates help text. Discover commands and options:

```bash
hist_calc --help
```

Run a calculation:

```bash
hist_calc max 1,-2,4
```

## See also

- The earlier `setup.py` plus `requirements.txt` shape in [Section 04](section-04.md).
- A `pyproject.toml`-only project in [Section 06](section-06.md).
