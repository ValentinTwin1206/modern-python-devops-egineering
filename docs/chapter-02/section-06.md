# Section 06: Python 3.11 with `pyproject.toml` only

This page covers the final packaging snapshot in the Historic Calculator series. The example targets Python 3.11, released on October 24, 2022. It uses a single declarative `pyproject.toml` under PEP 621. There is no `setup.py` and no `setup.cfg`.

## Background

Three PEPs and one setuptools release combine into the modern shape:

| PEP or release           | Year | Contribution                                                  |
| ------------------------ | ---- | ------------------------------------------------------------- |
| PEP 518                  | 2016 | `pyproject.toml` for build-system requirements.               |
| PEP 517                  | 2017 | Build front-end and back-end split.                           |
| PEP 621                  | 2020 | Standard `[project]` table for static project metadata.       |
| setuptools 61.0          | 2022 | Native PEP 621 support, allowing setup.py and setup.cfg removal. |

The result is one file per project. `[build-system]` declares the backend. `[project]` holds metadata, runtime dependencies, optional dependency groups, and console scripts. `[tool.pytest.ini_options]` replaces `[tool:pytest]`. Modern pip can read those tables directly during `pip install .` and `pip install .[dev]`.

What `pyproject.toml` still does not provide is a true lockfile with the fully solved transitive graph and hashes. That role belongs to later toolchains such as `Pipfile.lock`, `poetry.lock`, `pdm.lock`, and `uv.lock`.

## Packaging matrix

| Field            | Value                                                |
| ---------------- | ---------------------------------------------------- |
| Project version  | 6.0.0                                                |
| Python version   | 3.11                                                 |
| NumPy            | 1.24.0, pinned in `pyproject.toml`                   |
| Click            | 8.1.3, pinned in `pyproject.toml`                    |
| pytest           | 7.2.0, in the `dev` optional group                   |
| Layout           | `pyproject.toml` only                                |
| Distribution     | wheel and sdist via the `build` frontend             |

## Build

Install the modern build frontend:

```bash
pip install build
```

Build the wheel and the source distribution:

```bash
python -m build
```

Both artifacts appear in `dist/`.

## Install

Install the package and its pinned runtime dependencies:

```bash
pip install .
```

Install the optional `dev` group for testing:

```bash
pip install .[dev]
```

Run the test suite:

```bash
pytest
```

## Usage

Click auto-generates help text:

```bash
hist_calc --help
```

Run a calculation:

```bash
hist_calc max 1,-2,4
```

## See also

- The split runtime and dev requirements layout in [Section 05](section-05.md).
- Modern environment isolation through Dev Containers in [Chapter 01, Section 05](../chapter-01/section-05.md).
