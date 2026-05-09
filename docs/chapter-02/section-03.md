# Section 03: Python 2.4 and early `setuptools`

This page covers the third packaging snapshot in the Historic Calculator series. The example targets Python 2.4, released on November 30, 2004, with setuptools 0.6c11. This is the first section where dependency declarations are actively enforced at install time.

## Used Project

| Component            | Description |
| -------------------- | ----------- |
| Historic Calculator  | Historic Calculator is the example package used to show the first real dependency-aware install workflow in the chapter. This snapshot demonstrates what changed when setuptools began enforcing requirements. |
| `setup.py`           | This `setup.py` file is driven by early setuptools rather than plain `distutils`. It introduces `install_requires` and entry-point declarations that make installation behavior more active. |
| Numeric              | Numeric is the runtime dependency used by the project in this era. Setuptools checks for it during installation, which is a meaningful step beyond metadata-only declarations. |
| `pkg_resources`      | `pkg_resources` is the setuptools runtime API for working with installed distributions. It matters here because it supports the requirement checks and installed-package metadata that setuptools relies on. |
| `console_scripts`    | `console_scripts` is the entry-point mechanism introduced by setuptools. It registers `hist_calc` on `PATH` without shipping a manually maintained script file. |

## Background

Setuptools introduces `install_requires=`. During `python setup.py install`, setuptools checks whether the current Python environment already contains a registered distribution that satisfies the declared requirement. A missing dependency now fails at install time instead of surfacing later as an `ImportError`.

The check uses `pkg_resources`. It does not look for an importable file. It looks for an installed distribution recorded in `site-packages`, for example through an `.egg-info` directory or `setuptools.pth`. That is why this section's setup patches Numeric to install with setuptools instead of plain `distutils`. Without the patch, `pkg_resources.require("Numeric")` does not see the package and tries to fetch it from PyPI.

A working environment looks like this:

```text
/usr/local/lib/python2.4/site-packages/
|-- Numeric/
|-- Numeric-24.0b2-py2.4.egg-info/
`-- setuptools.pth
```

## Packaging matrix

| Field            | Value                                              |
| ---------------- | -------------------------------------------------- |
| Project version  | 3.0.0                                              |
| Python version   | 2.4                                                |
| Numeric          | 24.0b2, resolved at install                        |
| setuptools       | 0.6c11, bootstrap dependency                       |
| Layout           | `setup.py` with setuptools                         |
| Distribution     | sdist or `bdist_egg`, no wheels                    |
| Console scripts  | `console_scripts` entry points                     |

## Build and install

Build the source distribution:

```bash
python setup.py sdist
```

Install the package and let setuptools verify dependencies:

```bash
python setup.py install
```

The install registers `hist_calc` on `PATH` through `console_scripts`, the entry point mechanism that arrived with setuptools.

## Usage

Run the calculator with one of `max`, `min`, `mean`, or `sum`:

```bash
hist_calc max 1,-2,4
```

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

## See also

- The 2010 pip plus `requirements.txt` workflow in [Section 04](section-04.md).
- Declarative metadata in `setup.cfg` in [Section 05](section-05.md).
