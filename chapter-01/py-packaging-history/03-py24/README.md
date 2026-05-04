# historic_calculator

A small example application demonstrating Python 2.4 (released
**November 30, 2004**) together with the **setuptools** packaging library
(released the same year) — the first tool to support real,
enforceable runtime dependency declarations through the
`install_requires=` keyword.

  * **Python version:** 2.4
  * **Release date:** November 30, 2004
  * **setuptools:** 0.6c11 (last release supporting Python 2.4)
  * **Numeric:** 24.0b2
  * **Associated PEP:** [PEP 314 — Metadata for Python Software
    Packages v1.1](https://peps.python.org/pep-0314/) (PEP 345 with
    `Requires-Dist` arrived later, in 2005; setuptools' `install_requires`
    was the de-facto standard well before then)

## System Requirements

### Overview

  * A Linux system with glibc 2.2 or 2.3.
  * The GNU C compiler (`gcc`) 2.95 or later, and `make`.
  * Development headers for the C library, `readline`, and `zlib`:
      - on Debian: `libc6-dev`, `libreadline-dev`, `zlib1g-dev`
      - on Red Hat: `glibc-devel`, `readline-devel`, `zlib-devel`
  * Root privileges (or write access to a custom `--prefix`) to
    install into `/usr/local`.
  * [Python 2.4](#install-python) installed on the system.
  * [setuptools 0.6c11](#install-setuptools) installed on the system.
  * [Numeric 24.0b2](#install-numeric) installed on the system.

### Install Python

Download and unpack the Python 2.4 source archive:

```sh
cd /usr/src
wget https://www.python.org/ftp/python/2.4/Python-2.4.tgz
tar -xzf Python-2.4.tgz
```

Configure, build, and install the interpreter:

```sh
cd Python-2.4
./configure --prefix=/usr/local
make
make install
```

Verify that Python was installed correctly:

```sh
/usr/local/bin/python -V
```

> You should see `Python 2.4`.

### Install setuptools

Download and unpack setuptools 0.6c11 — the last release that
supports Python 2.4:

```sh
cd /usr/src
wget https://files.pythonhosted.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz
tar -xzf setuptools-0.6c11.tar.gz
```

Install it with the just-built Python:

```sh
cd setuptools-0.6c11
python setup.py install
```

Verify that setuptools is available:

```sh
python -c "import setuptools; print setuptools.__version__"
```

### Install Numeric

Download and unpack the Numeric 24.0b2 source archive:

```sh
cd /usr/src
wget -O Numeric-24.0b2.tar.gz \
  "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"
tar -xzf Numeric-24.0b2.tar.gz
```

Patch Numeric's `setup.py` so it uses *setuptools* instead of plain
distutils. This is what registers Numeric as a setuptools distribution
in `pkg_resources` — without it, our project's `install_requires=
["Numeric"]` declaration would try to fetch `Numeric` from PyPI:

```sh
cd Numeric-24.0b2
sed -i 's/from distutils.core import setup/from setuptools import setup/' setup.py
```

Build and install the patched Numeric:

```sh
python setup.py install
```

Verify that Numeric was installed correctly:

```sh
python -c "import Numeric; print Numeric.__version__"
```

## Dependency Management

### Matrix

| Dependency  | 1.0.0                 | 2.0.0                      | 3.0.0                           | 4.0.0                            | 5.0.0                                             | 6.0.0                                       |
| ----------- | --------------------- | -------------------------- | ------------------------------- | -------------------------------- | ------------------------------------------------- | ------------------------------------------- |
| Python      | 1.6                   | 2.3                        | 2.4                             | 2.7                              | 3.5                                               | 3.11                                        |
| Numeric     | 15.3 (manual install) | 24.0b2 (declared, manual)  | 24.0b2 (resolved at install)    | —                                | —                                                 | —                                           |
| NumPy       | —                     | —                          | —                               | 1.9.2 (pinned, pip-installed)    | 1.11.3 (pinned, pip-installed)                    | 1.24.0 (pinned, pip-installed)              |
| Click       | —                     | —                          | —                               | —                                | 6.6 (pinned, pip-installed)                       | 8.1.3 (pinned, pip-installed)               |
| setuptools  | —                     | —                          | 0.6c11 (bootstrap dependency)   | bundled                          | bundled                                           | build backend (>=61.0, declared)            |
| pip         | —                     | —                          | —                               | bundled (PEP 477)                | bundled                                           | bundled, PEP 517/518 frontend               |
| pytest      | —                     | —                          | —                               | —                                | 3.0.7 (dev, requirements-dev.txt)                 | 7.2.0 (dev extra in `pyproject.toml`)       |
| Layout      | `setup.py` only       | `setup.py` (distutils)     | `setup.py` (setuptools)         | `setup.py` + `requirements.txt`  | `setup.py` + `setup.cfg` + 2× `requirements*.txt` | `pyproject.toml` only                        |

### Background

With `setuptools`, `install_requires=` becomes active rather than merely
descriptive. During `python setup.py install`, setuptools checks whether
the current Python 2.4 environment already contains a registered
`Numeric` distribution. That is the key shift in this chapter: a missing
dependency becomes an *install-time* failure instead of a later
`ImportError`. The cost is a bootstrap dependency of its own, because
setuptools still has to be installed separately in this era.

What `pkg_resources` looks for is not just an importable `Numeric.py`
somewhere on disk, but an installed distribution recorded in
`site-packages`. In practice the Python 2.4 environment needs to look
roughly like this:

```text
/usr/local/lib/python2.4/site-packages/
|-- Numeric/
|-- Numeric-24.0b2-py2.4.egg-info/
`-- setuptools.pth
```

That is why the README patches Numeric's own `setup.py` to use
`setuptools`: the install has to register Numeric as a distribution so
`pkg_resources` can see it.

In case that Numeric is missing, following command failed:

```sh
python setup.py install
```

```text
Processing dependencies for historic_calculator==3.0.0
Searching for Numeric
Reading http://pypi.python.org/simple/Numeric/
No local packages or download links found for Numeric
```

## Installation

From the directory containing this `README.md`:

```sh
python setup.py install
```

## Usage

The package exposes a single command-line entry point that
applies a reduction to a comma-separated vector of numbers.

The general form is:

```sh
python main.py COMMAND VECTOR
```

  * `COMMAND` is one of `max`, `min`, `mean`, or `sum`.
  * `VECTOR` is a comma-separated list of numbers, for example
    `1,-2,4`. Negative numbers and decimals are supported; spaces
    around the commas are allowed.

### Calculating the Vector Maximum

Use `max` to return the largest value in the vector.

```sh
python historic_calculator/main.py max 1,-2,4
```

This prints:

```sh
max(1,-2,4) = 4.0
```

### Calculating the Vector Minimum

Use `min` to return the smallest value in the vector.

```sh
python historic_calculator/main.py min 1,-2,4
```

This prints:

```sh
min(1,-2,4) = -2.0
```

### Calculating the Vector Mean

Use `mean` to return the arithmetic average of the vector.

```sh
python historic_calculator/main.py mean 1.5,2.5,3.5
```

This prints:

```sh
mean(1.5,2.5,3.5) = 2.5
```

### Calculating the Vector Sum

Use `sum` to return the total of all values in the vector.

```sh
python historic_calculator/main.py sum 10,20,30,40
```

This prints:

```sh
sum(10,20,30,40) = 100.0
```

### Handling Invalid Input

Calling the script with the wrong number of arguments, an unknown
command, or a malformed vector prints a short usage banner on
standard error and exits with a non-zero status.

You can also use the package from your own scripts:

```python
from historic_calculator.main import run_calculator, make_vector

print run_calculator("max", "1,-2,4")

v = make_vector([1, 2, 3, 4])
print v * 2
```

## If Numeric Is Missing

Because setuptools 0.6c11 checks `install_requires=` at install time,
the usual failure mode is that `python setup.py install` aborts before
the package is fully usable. But if you are writing your own scripts
for this era, it is still helpful to guard imports explicitly and print
an actionable error.

The simplest pattern is a plain `ImportError` check:

```python
import sys

try:
  import Numeric
except ImportError:
  print >> sys.stderr, "Numeric 24.0b2 is required. Install it before running historic_calculator."
  raise SystemExit(1)
```

If you want to mirror setuptools' view of the world more closely, check
whether `pkg_resources` can see a registered `Numeric` distribution
before importing it:

```python
import sys

import pkg_resources

try:
  pkg_resources.require("Numeric")
  import Numeric
except pkg_resources.DistributionNotFound:
  print >> sys.stderr, "Numeric is not registered in pkg_resources. Reinstall Numeric with the setuptools patch."
  raise SystemExit(1)
except ImportError:
  print >> sys.stderr, "Numeric is registered but cannot be imported. Check the Numeric install itself."
  raise SystemExit(1)
```

And if you want the CLI entry point to fail with a short message rather
than a traceback, wrap the import in a helper function:

```python
import sys


def require_numeric():
  try:
    import Numeric
  except ImportError:
    print >> sys.stderr, "Missing dependency: Numeric 24.0b2"
    print >> sys.stderr, "Install Numeric first, then rerun the command."
    raise SystemExit(1)
  return Numeric


Numeric = require_numeric()
```
