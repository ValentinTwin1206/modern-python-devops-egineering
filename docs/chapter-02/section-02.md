# Python 2.3 and PEP 314 metadata

Python 2.3 was released in 2003, when packaging metadata started to describe more than shipped files. PEP 314 introduced metadata fields such as `Requires`, `Provides`, and `Obsoletes`, but those fields were still informational: installers recorded them without resolving dependencies automatically.

## Applied Project

### Project Setup

The applied project is version 2.0.0 of Historic Calculator. It keeps the same small `hist_calc` command-line interface, but the `setup.py` file now includes PEP 314 metadata through `requires=`, `provides=`, and `obsoletes=` fields.

Numeric 24.0b2 is the runtime component for array-style calculations. The metadata can mention Numeric, but `distutils` still treats that information as descriptive only. Users must install Numeric before installing Historic Calculator, so this section shows the gap between dependency metadata and dependency installation.

!!! info "Historical development image"

	`Dockerfile.devEnv` builds a containerized approximation of the Python 2.3 development environment. It provides Python 2.3 and the system tooling needed to explore the metadata-only packaging workflow without changing the host machine.

### Packaging Matrix

| Field            | Value                                                      |
| ---------------- | ---------------------------------------------------------- |
| Project version  | 2.0.0                                                      |
| Python version   | 2.3                                                        |
| Numeric          | 24.0b2, declared in `requires=`, installed manually        |
| Layout           | `setup.py` only                                            |
| Distribution     | sdist                                                      |
| Console scripts  | `scripts=` in `setup.py`                                   |

## Background

This project belongs to the Python 2.3 era in 2003, when packaging metadata became more expressive but installation stayed mostly manual. PEP 314 produced Metadata 1.1, which introduced `Requires`, `Provides`, and `Obsoletes`. The metadata is stored in the package, but no tool acts on it during install.

The `setup.py` file records those metadata fields directly:

```python
setup(
	name="historic_calculator",
	version="2.0.0",
	requires=["Numeric (==24.0b2)"],
	provides=["historic_calculator (2.0.0)"],
	obsoletes=["historic_calculator (<2.0.0)"],
	scripts=["bin/hist_calc"],
)
```

## Build and install

### Runtime and build dependencies

This snapshot needs Python 2.3 and Numeric 24.0b2 installed before the project itself. PEP 314 metadata can record the dependency, but `distutils` still does not download or install it.

Fetch, unpack, and install Numeric 24.0b2:

```bash
wget -O Numeric-24.0b2.tar.gz "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"
tar -xzf Numeric-24.0b2.tar.gz
python setup.py install
```

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

### Run Project

After installation, run the installed launcher:

```bash
hist_calc max 1,-2,4
```

Without installation, run the source-tree launcher directly:

```bash
PYTHONPATH=src python bin/hist_calc max 1,-2,4
```

Additional build and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-02/section-02/README.md).
