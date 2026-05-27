# Python 3.11 with `pyproject.toml` only

Python 3.11 was released in 2022, when the modern `pyproject.toml`-only packaging layout had become practical for setuptools projects. PEP 517, PEP 518, and PEP 621 made it possible to declare build requirements, project metadata, dependencies, and console scripts in one standard configuration file.

## Applied Project

### Project Setup

The applied project is version 6.0.0 of Historic Calculator. It removes `setup.py` and `setup.cfg`, then declares the build backend, project metadata, dependencies, optional development group, and `hist_calc` console script in `pyproject.toml`.

NumPy and Click remain runtime components for calculations and command-line behavior. The optional `dev` group contains pytest, and the `build` frontend creates wheel and source distribution artifacts through the PEP 517 build interface.

!!! info "Historical development image"

	`Dockerfile.devEnv` builds a containerized approximation of the Python 3.11 development environment. It provides the interpreter, modern build tooling, and project files needed to explore the `pyproject.toml`-only workflow without changing the host machine.

### Packaging Matrix

| Field            | Value                                                |
| ---------------- | ---------------------------------------------------- |
| Project version  | 6.0.0                                                |
| Python version   | 3.11                                                 |
| NumPy            | 1.24.0, pinned in `pyproject.toml`                   |
| Click            | 8.1.3, pinned in `pyproject.toml`                    |
| pytest           | 7.2.0, in the `dev` optional group                   |
| Layout           | `pyproject.toml` only                                |
| Distribution     | wheel and sdist via the `build` frontend             |

## Background

This project belongs to the Python 3.11 era in 2022, when the modern `pyproject.toml`-only layout became practical for setuptools projects. Three PEPs and one setuptools release combine into that shape:

| PEP or release           | Year | Contribution                                                  |
| ------------------------ | ---- | ------------------------------------------------------------- |
| PEP 518                  | 2016 | `pyproject.toml` for build-system requirements.               |
| PEP 517                  | 2017 | Build front-end and back-end split.                           |
| PEP 621                  | 2020 | Standard `[project]` table for static project metadata.       |
| setuptools 61.0          | 2022 | Native PEP 621 support, allowing setup.py and setup.cfg removal. |

The result is one file per project. `[build-system]` declares the backend. `[project]` holds metadata, runtime dependencies, optional dependency groups, and console scripts. `[tool.pytest.ini_options]` replaces `[tool:pytest]`. Modern pip can read those tables directly during `pip install .` and `pip install .[dev]`.

The `pyproject.toml` file records build-system settings and project metadata in one place:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "historic_calculator"
version = "6.0.0"
dependencies = [
	"numpy==1.24.0",
	"click==8.1.3",
]

[project.scripts]
hist_calc = "historic_calculator.main:cli"
```

What `pyproject.toml` still does not provide is a true lockfile with the fully solved transitive graph and hashes. That role belongs to later toolchains such as `Pipfile.lock`, `poetry.lock`, `pdm.lock`, and `uv.lock`.

## Build and install

### Runtime and build dependencies

Install the modern build frontend:

```bash
pip install build
```

Install the optional `dev` group when you need the test runner and local development tools:

```bash
pip install .[dev]
```

### Build the package

Build the wheel and the source distribution:

```bash
python -m build
```

Both artifacts appear in `dist/`.

### Install the package

Install the package and its pinned runtime dependencies:

```bash
pip install .
```

### Run Project

After installation, run the installed console script:

```bash
hist_calc max 1,-2,4
```

Without installation, run the CLI module from the source tree:

```bash
PYTHONPATH=src python -m historic_calculator.main max 1,-2,4
```

Additional build and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-02/section-06/README.md).
