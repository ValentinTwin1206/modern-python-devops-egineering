# Python 2.4 and early `setuptools`

Python 2.4 was released in 2004, just as early setuptools began changing packaging from passive metadata into active installation behavior. The distinct shift was `install_requires`: dependencies could now be checked during installation instead of failing later as runtime imports.

## Applied Project

### Project Setup

The applied project is version 3.0.0 of Historic Calculator. It still uses `setup.py`, but this snapshot switches from plain `distutils` to early setuptools so the package can declare `install_requires` and register the `hist_calc` command through `console_scripts`.

Numeric 24.0b2 remains the runtime component for array-style calculations, but setuptools expects it to be registered as an installed distribution. That makes `pkg_resources` important: it checks installed package metadata, not just importable files, before allowing Historic Calculator to install.

!!! info "Historical development image"

    `Dockerfile.devEnv` builds a containerized approximation of the Python 2.4 and early setuptools development environment. It provides Python 2.4, setuptools 0.6c11, and the tooling needed to explore dependency-aware installation without changing the host machine.

### Packaging Matrix

| Field            | Value                                              |
| ---------------- | -------------------------------------------------- |
| Project version  | 3.0.0                                              |
| Python version   | 2.4                                                |
| Numeric          | 24.0b2, resolved at install                        |
| setuptools       | 0.6c11, bootstrap dependency                       |
| Layout           | `setup.py` with setuptools                         |
| Distribution     | sdist or `bdist_egg`, no wheels                    |
| Console scripts  | `console_scripts` entry points                     |

## Background

This project belongs to the early setuptools period around Python 2.4, released in 2004. The special change is that `install_requires=` makes dependency declarations active during installation. During `python setup.py install`, setuptools checks whether the current Python environment already contains a registered distribution that satisfies the declared requirement.

The `setup.py` file records the enforceable dependency and the generated console script:

```python
setup(
    name="historic_calculator",
    version="3.0.0",
    install_requires=["Numeric"],
    entry_points={
        "console_scripts": [
            "hist_calc = historic_calculator.main:main_cli",
        ],
    },
)
```

The check uses `pkg_resources`. It does not look for an importable file. It looks for an installed distribution recorded in `site-packages`, for example through an `.egg-info` directory or `setuptools.pth`. That is why this section's setup patches Numeric to install with setuptools instead of plain `distutils`. Without the patch, `pkg_resources.require("Numeric")` does not see the package and tries to fetch it from PyPI.

A working environment looks like this:

```text
/usr/local/lib/python2.4/site-packages/
|-- Numeric/
|-- Numeric-24.0b2-py2.4.egg-info/
`-- setuptools.pth
```

## Build and install

### Runtime and build dependencies

This snapshot needs Python 2.4, setuptools 0.6c11, and Numeric 24.0b2 registered as a setuptools distribution. Setuptools checks `install_requires=`, but it can only satisfy the requirement when Numeric is visible through installed distribution metadata.

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

## Defensive imports

Setuptools blocks the install when a dependency is missing, so the runtime usually has a complete environment. Defensive code is still useful for scripts that bypass the install path. Guard the import explicitly and exit with an actionable message:

```python
import sys

try:
    import Numeric
except ImportError:
    print >> sys.stderr, "Numeric 24.0b2 is required."
    raise SystemExit(1)
```

### Run Project

After installation, run the installed launcher:

```bash
hist_calc max 1,-2,4
```

Without installation, run the calculator from the source tree:

```bash
PYTHONPATH=src python -c "from historic_calculator.main import run_calculator; print run_calculator('max', '1,-2,4')"
```

Additional build and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-02/section-03/README.md).
