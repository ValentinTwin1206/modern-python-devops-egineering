# Python 2.4

This section introduces early `setuptools` on Python 2.4 and uses a small
command-line project to show how dependency declarations started to become
active during installation.

## Applied Project

### Project Setup

The applied project is Historic Calculator, release 3.0.0. This snapshot is set in 2004, the release year of Python 2.4, and contains the `historic_calculator` package plus the `hist_calc` command-line script.

### Run the Project

Application commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_historic_calculator/2004/README.md).

## Background

This project belongs to the early `setuptools` period around Python 2.4, released in 2004. `setuptools` changed packaging from passive metadata into active installation behavior and gave Python projects a richer `setup.py` interface for:

- Declaring enforceable runtime dependencies
- Generating console-script launchers
- Building source distributions and eggs
- Checking installed distribution metadata during installation

The `setup.py` file records the enforceable dependency and generated console script directly:

```python
setup(
    name="historic_calculator",
    version="3.0.0",
    description="A tiny vector calculator using Numeric and setuptools.",
    package_dir={"": "src"},
    packages=["historic_calculator"],
    install_requires=[
        "Numeric",
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
- `install_requires` asks `setuptools` to check for the Numeric runtime dependency during installation.
- `entry_points` registers the `hist_calc` command through the `console_scripts` mechanism.

## Dependency Management

### Overview

`setuptools` was an important step toward dependency-aware installation, but the early model still had important limits:

- ⚠️ It checked installed distribution metadata, not just importable modules.
- ⚠️ Numeric had to be installed with setuptools metadata before `install_requires` could recognize it.
- ⚠️ Tools such as wheels, build isolation, lock files, and modern dependency resolvers did not exist yet.

### Runtime and build dependencies

Use `Dockerfile.devEnv` for the Python 2.4 development environment. It keeps the historical interpreter, setuptools 0.6c11, and build tooling isolated from the host machine.

Numeric 24.0b2 is the runtime component that provides array-style calculations for this project. `setuptools` expects Numeric to be registered as an installed distribution, so this section patches Numeric to install with setuptools metadata before installing Historic Calculator.

Fetch and install setuptools 0.6c11:

```bash
wget https://files.pythonhosted.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz
tar -xzf setuptools-0.6c11.tar.gz
cd setuptools-0.6c11 && python setup.py install
```

Fetch Numeric 24.0b2:

```bash
wget -O Numeric-24.0b2.tar.gz "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"
tar -xzf Numeric-24.0b2.tar.gz
```

Patch Numeric to use setuptools, then install it:

```bash
sed -i 's/from distutils.core import setup/from setuptools import setup/' Numeric-24.0b2/setup.py
cd Numeric-24.0b2 && python setup.py install
```

### Build the package

Build the source distribution:

```bash
python setup.py sdist
```

### Install the package

Install the package and let setuptools verify dependencies:

```bash
python setup.py install
```

The install registers `hist_calc` on `PATH` through `console_scripts`, the entry point mechanism that arrived with setuptools.
