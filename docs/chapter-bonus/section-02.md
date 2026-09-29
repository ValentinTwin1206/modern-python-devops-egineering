# Python 2.3

This section introduces Python 2.3 packaging metadata with PEP 314 and uses a
small command-line project to show how early metadata fields described
dependencies without installing them automatically.

## Applied Project

### Project Setup

The applied project is Historic Calculator, release 2.0.0. This snapshot is set in 2003, the release year of Python 2.3, and contains the `historic_calculator` package plus the `hist_calc` command-line script.

### Run the Project

Application commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_historic_calculator/2003/README.md).

## Background

This project belongs to the Python 2.3 era in 2003, when packaging metadata became more expressive but installation stayed mostly manual. PEP 314 produced Metadata 1.1 and gave Python projects standard fields for describing package relationships:

- Declaring required packages
- Declaring the package or feature a distribution provides
- Declaring older packages or versions a distribution replaces

The `setup.py` file records those metadata fields directly:

```python
setup(
	name="historic_calculator",
	version="2.0.0",
	description="A historical Python 2.3 application",
	package_dir={"": "src"},
	packages=["historic_calculator"],
	requires=["Numeric (==24.0b2)"],
	provides=["historic_calculator (2.0.0)"],
	obsoletes=["historic_calculator (<2.0.0)"],
	scripts=["bin/hist_calc"],
)
```

- `name` gives the distribution its package name.
- `version` records the release number that build and install commands use.
- `description` adds a short human-readable project summary to the package metadata.
- `package_dir` maps packages to the `src` directory instead of the project root.
- `packages` lists the Python package included in the distribution.
- `requires` records the Numeric dependency as package metadata.
- `provides` declares the distribution name and version this package provides.
- `obsoletes` marks older Historic Calculator releases as replaced by this release.
- `scripts` installs the `bin/hist_calc` launcher as an executable script.

## Dependency Management

### Overview

PEP 314 metadata was an important step toward standardized dependency descriptions, but the model still had important limits:

- ⚠️ It did not resolve or install runtime dependencies.
- ⚠️ Tools such as wheels, build isolation, lock files, and modern dependency resolvers did not exist yet.
- ⚠️ Users still had to prepare much of the environment by hand.

### Runtime and build dependencies

Use `Dockerfile.devEnv` for the Python 2.3 development environment. It keeps the historical interpreter and build tooling isolated from the host machine.

Numeric 24.0b2 is the runtime component that provides array-style calculations for this project. It is the predecessor of NumPy, and this release can name it in `requires`, but `distutils` still treats that information as descriptive only. A user must install Numeric before installing Historic Calculator, which shows the gap between dependency metadata and dependency installation.

Fetch and unpack Numeric 24.0b2:

```bash
wget -O Numeric-24.0b2.tar.gz "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"
tar -xzf Numeric-24.0b2.tar.gz
```

Build and install Numeric from its own `setup.py`:

```bash
cd Numeric-24.0b2 && python setup.py install
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
