# Section 01: Python 1.6 and `distutils`

This page covers the earliest packaging shape in the Historic Calculator series. The example targets Python 1.6, released on September 5, 2000. It uses the standard-library `distutils` module and the Numerical extension that later evolved into NumPy.

The version 1.0.0 layout is the simplest one in the chapter. There is one `setup.py` file that calls `distutils.core.setup` with `name`, `version`, and `packages`. There is no dependency declaration vocabulary, no resolver, and no package index.

## Background

In 2000, `distutils` graduated from a separately installable package into the Python standard library. It only describes what your package ships. It has no way to talk about what your package needs at runtime.

A consumer reads this section's README, downloads the Numerical 15.3 source archive by hand, runs `python setup.py install` for it, and only then installs `historic_calculator`. A missing dependency surfaces as an `ImportError` at runtime rather than at install time.

## Packaging matrix

This is the first row of the chapter-wide packaging matrix.

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Project version  | 1.0.0                                |
| Python version   | 1.6                                  |
| Numerical        | 15.3, manually installed             |
| Layout           | `setup.py` only                      |
| Distribution     | sdist, no wheels, no eggs            |
| Console scripts  | `scripts=` in `setup.py`             |

## Build and install

Build the source distribution:

```bash
python setup.py sdist
```

Install the package system wide:

```bash
python setup.py install
```

The install registers a launcher script through the `scripts=` argument in `setup.py`. Console-script entry points only arrived later, with setuptools.

## Usage

The package exposes one command-line tool that reduces a comma-separated vector with `max`, `min`, `mean`, or `sum`:

```bash
hist_calc max 1,-2,4
```

Use it from Python code:

```python
from historic_calculator.main import run_calculator, make_vector

print run_calculator("max", "1,-2,4")
v = make_vector([1, 2, 3, 4])
print v * 2
```

## See also

- Metadata-only dependency hints arriving with PEP 314 in [Section 02](section-02.md).
- Real install-time dependency resolution with setuptools in [Section 03](section-03.md).
