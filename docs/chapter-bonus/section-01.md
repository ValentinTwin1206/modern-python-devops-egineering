# Python 1.6

This section introduces Python 1.6 packaging with `distutils` and uses a
small command-line project to show how early Python packages were described,
built, and installed.

## Applied Project

### Project Setup

The applied project is Historic Calculator, release 1.0.0. This snapshot is set in 2000, the release year of Python 1.6, and contains the `historic_calculator` package plus the `hist_calc` command-line script.

### Run the Project

Application commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_historic_calculator/2000/README.md).

## Background

This project belongs to the Python 1.6 era in 2000, when `distutils` graduated from a separately installable package into the Python standard library. It was Python's first standard packaging toolkit and gave Python projects a common `setup.py` interface for:

- Declaring package metadata
- Listing source files
- Building source distributions
- Installing packages into a Python environment

The `setup.py` file records the shipped package and script directly:

```python
setup(
	name="historic_calculator",
	version="1.0.0",
	package_dir={"": "src"},
	packages=["historic_calculator"],
	scripts=["bin/hist_calc"],
)
```

- `name` gives the distribution its package name.
- `version` records the release number that build and install commands use.
- `package_dir` maps packages to the `src` directory instead of the project root.
- `packages` lists the Python package included in the distribution.
- `scripts` installs the `bin/hist_calc` launcher as an executable script.

## Dependency Management

### Overview

`distutils` was an important step toward standardized packaging, but the model still had important limits:

- ⚠️ It did not resolve or install runtime dependencies.
- ⚠️ Tools such as wheels, build isolation, lock files, and modern dependency resolvers did not exist yet.
- ⚠️ Users still had to prepare much of the environment by hand.

### Runtime and build dependencies

Use `Dockerfile.devEnv` for the Python 1.6 development environment. It keeps the historical interpreter and build tooling isolated from the host machine.

Numerical 15.3 is the runtime component that provides array-style calculations for this project. It is the predecessor of NumPy, but it is not declared in a way that `distutils` can install automatically. A user must install Numerical before installing Historic Calculator, which shows the manual dependency workflow of the time.

Fetch and unpack Numerical 15.3:

```bash
wget -O Numerical-15.3.tgz "https://sourceforge.net/projects/numpy/files/OldFiles/Numerical-15.3.tgz/download"
tar -xzf Numerical-15.3.tgz
```

Build and install Numerical from its own `setup.py`:

```bash
cd Numerical-15.3 && python setup.py install
```

The install copies Numeric and its compiled extensions into the Python 1.6 prefix, typically `/usr/local/lib/python1.6/site-packages/`. That target existed, but automatic dependency discovery and installation did not.

### Build the package

Build the source distribution:

```bash
python setup.py sdist
```

### Install the package

Install the package and the `hist_calc` launcher system wide:

```bash
python setup.py install
```

> This command registers `hist_calc` through `scripts=`. If Numerical is missing, running `hist_calc` fails with `ImportError`.
