# Historic Calculator (Python 2.3)

A small example application demonstrating Python 2.3 together with the
Numeric extension, the direct ancestor of today's NumPy. This section
shows a `distutils` project after PEP 314 added metadata fields such as
`requires=`, while dependency installation was still a manual step.

- **Python version:** 2.3
- **Release date:** July 29, 2003
- **Associated PEP:** [PEP 314 - Metadata for Python Software Packages v1.1](https://peps.python.org/pep-0314/)

## System Requirements

- A Linux system with glibc 2.2 or 2.3.
- A C compiler, `make`, and development headers for the C library,
  `readline`, and `zlib`.
- Python 2.3 installed on the system.
- Numeric 24.0b2 installed on the system.

## Docker Images

The development image builds Python 2.3 and copies the project into the
image without installing Numeric or the package:

```sh
docker build -f Dockerfile.devEnv -t historic-calculator-py23-dev .
```

The runtime image builds Python 2.3, installs Numeric 24.0b2, installs
the package, and opens an interactive shell:

```sh
docker build -t historic-calculator-py23 .
docker run --rm -it historic-calculator-py23
```

## Dependency Management

PEP 314 lets `setup.py` record informational dependency metadata through
`requires=["Numeric==24.2"]`. `distutils` does not resolve or install
that dependency. Users still install Numeric themselves before installing
`historic_calculator`.

## Build

Python 2.3 predates wheels, so the era-appropriate distribution format
is a source distribution:

```sh
python setup.py sdist
```

The resulting tarball appears under `dist/` and is installed by unpacking
it and running `python setup.py install`.

## Installation

Install the package from this directory:

```sh
python setup.py install
```

This places `historic_calculator` on Python's import path and installs a
`hist_calc` launcher through the `scripts=` argument in `setup.py`.

## Usage

Run the command-line calculator with an operation and a comma-separated
vector:

```sh
hist_calc max 1,-2,4
hist_calc min 1,-2,4
hist_calc mean 1.5,2.5,3.5
hist_calc sum 10,20,30,40
```

You can also import the package from Python code:

```python
from historic_calculator.main import run_calculator, make_vector

print run_calculator("max", "1,-2,4")

v = make_vector([1, 2, 3, 4])
print v * 2
```
