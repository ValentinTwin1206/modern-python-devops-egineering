# Python 1.6 and `distutils`

Python 1.6 was released in 2000, when `distutils` became part of the Python standard library. It was the first standard packaging toolkit for Python projects: enough to describe files, build a source distribution, and run an install command, but not enough to resolve or install runtime dependencies.

## Applied Project

### Project Setup

The applied project is version 1.0.0 of Historic Calculator, a small command-line package used throughout Chapter 02 to compare packaging eras. In this snapshot, the project has one `setup.py` file that calls `distutils.core.setup` with the package name, version, shipped modules, and the `bin/hist_calc` script.

Numerical 15.3 is the runtime component that provides array-style calculations. It is the predecessor of NumPy, but it is not declared in a way that `distutils` can install automatically. A user must install Numerical first, then install Historic Calculator, which shows the manual dependency workflow of the time.

!!! info "Historical development image"

	`Dockerfile.devEnv` builds a containerized approximation of the Python 1.6 development environment. It compiles Python 1.6 on an old Debian base image and provides the tooling needed to explore the packaging workflow without changing the host machine.

### Packaging Matrix

This is the first row of the chapter-wide packaging matrix.

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Project version  | 1.0.0                                |
| Python version   | 1.6                                  |
| Numerical        | 15.3, manually installed             |
| Layout           | `setup.py` only                      |
| Distribution     | sdist, no wheels, no eggs            |
| Console scripts  | `scripts=` in `setup.py`             |

## Background

This project belongs to the Python 1.6 era in 2000, when `distutils` graduated from a separately installable package into the Python standard library. The important new idea was a standard way to describe and install a Python package, but `distutils` only describes what the package ships. It has no way to resolve or install runtime dependencies.

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

## Build and install

### Runtime and build dependencies

This snapshot needs Python 1.6, a working C toolchain, and Numerical 15.3 installed before the project itself. `distutils` can build and install the package, but it cannot install Numerical for you.

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

### Run Project

After installation, run the installed launcher:

```bash
hist_calc max 1,-2,4
```

Without installation, run the source-tree launcher directly:

```bash
PYTHONPATH=src python bin/hist_calc max 1,-2,4
```

Additional build and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-02/section-01/README.md).
