# Python 3.5

This section introduces the Python 3.5 packaging workflow built around
declarative `setup.cfg`, a small `setup.py` compatibility shim, and split
runtime and development requirements.

## Applied Project

### Project Setup

The applied project is Historic Calculator, release 5.0.0. This snapshot is set in 2015, the release year of Python 3.5, and contains the `historic_calculator` package plus the `hist_calc` command-line script.

### Run the Project

Application commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_historic_calculator/2016/README.md).

## Background

This project belongs to the Python 3.5 and 2016 packaging era, when declarative configuration became normal for setuptools projects. Setuptools 30.3.0 added `[metadata]` and `[options]` sections in `setup.cfg`, giving projects a declarative place for:

- Recording package metadata
- Finding packages in a `src` layout
- Declaring runtime dependencies
- Registering console-script entry points
- Configuring wheel and test tooling

=== "`setup.cfg`"

	The `setup.cfg` file records the package metadata, dependencies, entry point, and tool settings:

	```ini
	[metadata]
	name = historic_calculator
	version = 5.0.0
	description = A tiny vector calculator using NumPy and Click.

	[options]
	package_dir =
		=src
	packages = find:
	install_requires =
		numpy
		click

	[options.packages.find]
	where = src
	exclude =
		tests
		tests.*

	[options.entry_points]
	console_scripts =
		hist_calc = historic_calculator.main:cli

	[bdist_wheel]
	universal = 0

	[tool:pytest]
	testpaths = tests
	addopts = -ra
	```

	- `[metadata]` stores the distribution name, version, and human-readable description.
	- `[options]` maps packages to the `src` directory, discovers packages, and declares runtime dependencies.
	- `[options.packages.find]` tells setuptools where to find packages and which test packages to exclude.
	- `[options.entry_points]` registers the `hist_calc` command through `console_scripts`.
	- `[bdist_wheel]` configures the wheel build.
	- `[tool:pytest]` records pytest discovery and reporting settings.

=== "`setup.py`"

	The compatibility `setup.py` stays small because the metadata moved into `setup.cfg`:

	```python
	from setuptools import setup

	setup()
	```

	- `setup()` lets older tools continue to invoke the setuptools build while reading configuration from `setup.cfg`.

=== "`requirements.txt`"

	The runtime dependency pins live in `requirements.txt`:

	```text
	numpy==1.11.3
	click==6.6
	```

	- `numpy==1.11.3` pins the NumPy release used for array-style calculations.
	- `click==6.6` pins the Click release used for the command-line interface.

=== "`requirements-dev.txt`"

	The development dependency pins live in `requirements-dev.txt`:

	```text
	-r requirements.txt
	pytest==3.0.7
	```

	- `-r requirements.txt` reuses the runtime dependency set.
	- `pytest==3.0.7` pins the test runner used by this project snapshot.

## Dependency Management

### Overview

Declarative configuration and split requirements made project setup clearer, but the model still had important limits:

- ⚠️ `requirements.txt` and `requirements-dev.txt` pinned direct install inputs, not a complete lockfile with hashes.
- ⚠️ Runtime dependencies were duplicated conceptually between package metadata and requirements files.
- ⚠️ `setup.py` was still required as a compatibility shim for many tools.

### Runtime and build dependencies

Use `Dockerfile.devEnv` for the Python 3.5 development environment. It keeps the historical interpreter, pip, setuptools, wheel support, and build tooling isolated from the host machine.

NumPy provides array-style calculations, and Click provides the structured `hist_calc` command-line interface. `requirements.txt` pins the runtime dependency set, while `requirements-dev.txt` extends it with pytest for local development and tests.

Install the runtime dependencies:

```bash
pip install -r requirements.txt
```

Install the development dependencies when you need the test runner and local development tools:

```bash
pip install -r requirements-dev.txt
```

### Build the package

Build a pure-Python wheel:

```bash
python setup.py bdist_wheel
```

Build a source distribution alongside it:

```bash
python setup.py sdist
```

PEP 427 wheels are fully usable in this era. `setup.cfg` already declares `[bdist_wheel] universal = 0`.

### Install the package

Install the project:

```bash
pip install .
```
