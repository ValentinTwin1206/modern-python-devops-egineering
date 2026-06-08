# Python 2.7

This section introduces the Python 2.7 packaging workflow built around `pip`,
`setup.py`, and `requirements.txt`, using a small command-line project to show
how pinned dependency files improved reproducibility.

## Applied Project

### Project Setup

The applied project is Historic Calculator, release 4.0.0. This snapshot is set in 2010, the release year of Python 2.7, and contains the `historic_calculator` package plus the `hist_calc` command-line script.

### Run the Project

Application commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_historic_calculator/2010/README.md).

## Background

This project belongs to the Python 2.7 era that began in 2010, when `pip` and `requirements.txt` became the practical packaging workflow for many teams. The common layout paired `setup.py` with a pinned requirements file for:

- Declaring abstract package metadata and entry points
- Recording install-time runtime dependencies
- Pinning a concrete dependency set for repeatable installs
- Building source distributions for release

=== "`setup.py`"

	The `setup.py` file keeps the package metadata, abstract runtime dependency, and console-script registration:

	```python
	setup(
		name="historic_calculator",
		version="4.0.0",
		description="A tiny vector calculator using NumPy and setuptools.",
		package_dir={"": "src"},
		packages=["historic_calculator"],
		install_requires=[
			"numpy",
		],
		entry_points={
			"console_scripts": [
				"hist_calc = historic_calculator.main:main_cli",
			],
		},
	)
	```

	- `name` gives the distribution its package name.
	- `version` records the release number that build and install commands use.
	- `description` adds a short human-readable project summary to the package metadata.
	- `package_dir` maps packages to the `src` directory instead of the project root.
	- `packages` lists the Python package included in the distribution.
	- `install_requires` records the abstract NumPy runtime dependency.
	- `entry_points` registers the `hist_calc` command through `console_scripts`.

=== "`requirements.txt`"

	The concrete deployment pin lives in `requirements.txt`:

	```text
	numpy==1.9.2
	```

	- `numpy==1.9.2` pins the exact NumPy release used by this project snapshot.

## Dependency Management

### Overview

`pip` and `requirements.txt` made dependency installation more practical, but the model still had important limits:

- ⚠️ `requirements.txt` was a pinned install input, not a complete lockfile with hashes.
- ⚠️ Environment isolation was still a separate concern and was not provided by `pip` itself.
- ⚠️ Older pip behavior lacked the modern resolver used by current Python workflows.

### Runtime and build dependencies

Use `Dockerfile.devEnv` for the Python 2.7 development environment. It keeps the historical interpreter, pip-era tooling, and build tooling isolated from the host machine.

NumPy replaces the earlier Numeric packages as the runtime component for array-style calculations. `requirements.txt` pins the exact NumPy version, so `pip install -r requirements.txt` can reproduce the dependency set more reliably than the manual download steps used in earlier sections.

Install the pinned runtime dependencies:

```bash
pip install -r requirements.txt
```

This installs the concrete dependency set for the Python 2.7 workflow before the project package is installed.

### Build the package

Build the source distribution:

```bash
python setup.py sdist
```

The era predates PEP 427 wheels, so the source distribution is the canonical artifact.

### Install the package

Install the project itself:

```bash
python setup.py install
```
