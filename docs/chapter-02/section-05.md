# Python 3.5 with `setup.cfg` and split requirements

Python 3.5 was released in 2015, shortly before declarative setuptools configuration became the normal project shape. By 2016, many projects used `setup.cfg` for static metadata, kept `setup.py` as a compatibility shim, and split runtime and development dependencies across separate requirements files.

## Applied Project

### Project Setup

The applied project is version 5.0.0 of Historic Calculator. It moves most package metadata into `setup.cfg`, while `setup.py` becomes a small compatibility shim for tools that still expect that file.

The runtime components are pinned in `requirements.txt`: NumPy provides array-style calculations, and Click provides the structured `hist_calc` command-line interface. `requirements-dev.txt` extends the runtime set with development tooling such as pytest, showing the common split between application dependencies and test dependencies in this era.

!!! info "Historical development image"

	`Dockerfile.devEnv` builds a containerized approximation of the Python 3.5 development environment. It provides the interpreter, pip, setuptools, wheel support, and project files needed to explore the `setup.cfg` plus split requirements workflow without changing the host machine.

### Packaging Matrix

| Field            | Value                                                    |
| ---------------- | -------------------------------------------------------- |
| Project version  | 5.0.0                                                    |
| Python version   | 3.5                                                      |
| NumPy            | 1.11.3, pinned in `requirements.txt`                     |
| Click            | 6.6, pinned in `requirements.txt`                        |
| pytest           | 3.0.7, pinned in `requirements-dev.txt`                  |
| Layout           | `setup.py` shim plus declarative `setup.cfg`             |
| Distribution     | wheel and sdist                                          |

## Background

This project belongs to the Python 3.5 and 2016 packaging era, when declarative configuration became normal for setuptools projects. Setuptools 30.3.0 in December 2016 added `[metadata]` and `[options]` sections in `setup.cfg`. From that moment, almost everything previously written imperatively in `setup.py` could be expressed declaratively in `setup.cfg`, and `setup.py` collapsed into a one-line `setup()` shim that legacy tools can still invoke:

=== "`setup.cfg`"

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

=== "`requirements.txt`"

	```text
	numpy==1.11.3
	click==6.6
	```

=== "`requirements-dev.txt`"

	```text
	-r requirements.txt
	pytest==3.0.7
	```

=== "`setup.py`"

	The `setup.py` was still required because `pip` internally depended on it. Consequently, removing it would cause installs to fail entirely:

	```
    $ pip install -e .
    Obtaining file:///{PATH_TO_PROJECT_ROOT}/my-package
    ERROR: file:///{PATH_TO_PROJECT_ROOT}/my-package does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found.
    ```

	```python
	from setuptools import setup

	setup()
	```

The dependency story splits across two files. Runtime pins live in `requirements.txt`. Development pins live in `requirements-dev.txt` and usually start with `-r requirements.txt`. Together, they were the period's accepted answer to reproducible installs while a real lockfile standard was missing.

The CLI gains real structure. Click 1.0 shipped in April 2014 and was the dominant choice by 2016. Decorators replace hand-rolled `argparse` plumbing, and `console_scripts` registers `hist_calc` on `PATH`.

## Build and install

### Runtime and build dependencies

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

### Run Project

After installation, run the installed console script:

```bash
hist_calc max 1,-2,4
```

Without installation, run the CLI module from the source tree:

```bash
PYTHONPATH=src python -m historic_calculator.main max 1,-2,4
```

Additional build and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-02/section-05/README.md).
