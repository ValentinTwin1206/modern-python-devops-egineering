# Python 3.11

This section introduces the modern Python 3.11 packaging workflow built around
`pyproject.toml`, using a small command-line project to show how build-system
settings, project metadata, dependencies, optional dependency groups, and
console scripts can live in one standard file.

## Applied Project

### Project Setup

The applied project is Historic Calculator, release 6.0.0. This snapshot is set in 2022, the release year of Python 3.11, and contains the `historic_calculator` package plus the `hist_calc` command-line script.

### Run the Project

Application commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj6_historic_calculator/2022/README.md).

## Background

This project belongs to the Python 3.11 era in 2022, when the modern `pyproject.toml`-only layout became practical for setuptools projects. PEP 517, PEP 518, PEP 621, and setuptools 61.0 gave projects one standard file for:

- Declaring build-system requirements and the build backend
- Recording project metadata
- Declaring runtime and optional dependencies
- Registering console-script entry points
- Configuring package discovery and test tooling

The `pyproject.toml` file records build-system settings and project metadata in one place:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "historic_calculator"
version = "6.0.0"
description = "A tiny vector calculator using NumPy and Click."
requires-python = ">=3.11"
dependencies = [
	"numpy==1.24.0",
	"click==8.1.3",
]

[project.optional-dependencies]
dev = [
	"pytest==7.2.0",
]

[project.scripts]
hist_calc = "historic_calculator.main:cli"
```

- `[build-system]` declares the build backend and the packages needed to run it.
- `[project]` stores the distribution name, version, description, Python requirement, and runtime dependencies.
- `dependencies` pins the runtime packages installed with the project.
- `[project.optional-dependencies]` defines the optional `dev` group for local development and tests.
- `[project.scripts]` registers the `hist_calc` command through `console_scripts`.

## Dependency Management

### Overview

`pyproject.toml` made modern Python packaging much more standardized, but the model still has important limits:

- ⚠️ It is project metadata, not a true lockfile with the fully solved transitive graph and hashes.
- ⚠️ Reproducible application environments still need a locking tool or workflow.
- ⚠️ Build frontends and installers must still coordinate with the chosen backend.

### Runtime and build dependencies

Use `Dockerfile.devEnv` for the Python 3.11 development environment. It keeps the modern interpreter, build frontend, and project tooling isolated from the host machine.

NumPy and Click remain runtime components for calculations and command-line behavior. The optional `dev` group contains pytest, and the `build` frontend creates wheel and source distribution artifacts through the PEP 517 build interface.

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
