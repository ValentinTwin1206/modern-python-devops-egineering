# Section 02: Python 2.3 and PEP 314 metadata

This page covers the second packaging snapshot in the Historic Calculator series. The example targets Python 2.3, released on July 29, 2003, and uses the `distutils` workflow extended by PEP 314 metadata.

## Used Project

PEP 314 added a `requires=` field to `setup.py`. The field records informational metadata only. `distutils` still does not resolve or install dependencies. Users install Numeric themselves before installing `historic_calculator`.

| Component            | Description |
| -------------------- | ----------- |
| Historic Calculator  | Historic Calculator is the chapter-wide example package used to compare packaging eras. In this section it represents the Python 2.3 period, where metadata improved but installation remained mostly manual. |
| `setup.py`           | This `setup.py` file still uses `distutils`, but now includes PEP 314 metadata. It can describe requirements in package metadata, even though the installer does not act on them automatically. |
| Numeric              | Numeric is the array library required by the project in this snapshot. The metadata can mention it, but users still have to install it themselves before installing the package. |
| `bin/hist_calc`      | This script remains the command-line entry point for the calculator. It shows that legacy script installation predates modern entry-point registration. |

## Background

PEP 314 produced Metadata 1.1, which introduced `Requires`, `Provides`, and `Obsoletes`. The metadata is stored in the package, but no tool acts on it during install. The practical workflow remains the same as in [Section 01](section-01.md): fetch the dependency tarball by hand, install it, then install the project.

## Packaging matrix

| Field            | Value                                                      |
| ---------------- | ---------------------------------------------------------- |
| Project version  | 2.0.0                                                      |
| Python version   | 2.3                                                        |
| Numeric          | 24.0b2, declared in `requires=`, installed manually        |
| Layout           | `setup.py` only                                            |
| Distribution     | sdist                                                      |
| Console scripts  | `scripts=` in `setup.py`                                   |

## Build and install

Build the source distribution:

```bash
python setup.py sdist
```

Install the package system wide:

```bash
python setup.py install
```

## Usage

Run the calculator with one of `max`, `min`, `mean`, or `sum`:

```bash
hist_calc max 1,-2,4
```

## See also

- Real install-time dependency resolution with early setuptools in [Section 03](section-03.md).
- The 2010-era pip plus `requirements.txt` workflow in [Section 04](section-04.md).
