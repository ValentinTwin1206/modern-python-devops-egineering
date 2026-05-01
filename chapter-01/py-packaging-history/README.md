# Python Packaging History

This directory follows one small package across six packaging eras. Each
subdirectory is a self-contained snapshot with its own source tree,
dependency files, Docker setup, and a README describing the tooling and
installation style of that period.

## Folder Index

| Folder | Year | Era | Packaging shape | Details |
| ------ | ---- | --- | --------------- | ------- |
| [`py16/`](./py16/) | 2000 | Python 1.6 | `setup.py` with stdlib `distutils` | [README](./py16/README.md) |
| [`py23/`](./py23/) | 2003 | Python 2.3 | `setup.py` with metadata-only dependency hints | [README](./py23/README.md) |
| [`py24/`](./py24/) | 2004 | Python 2.4 | `setup.py` with early `setuptools` | [README](./py24/README.md) |
| [`py27/`](./py27/) | 2010 | Python 2.7 | `setup.py` plus pinned `requirements.txt` | [README](./py27/README.md) |
| [`py35/`](./py35/) | 2016 | Python 3.5 / 2016 workflow | `setup.py` + `setup.cfg` + `requirements*.txt` | [README](./py35/README.md) |
| [`py311/`](./py311/) | 2022 | Python 3.11 / 2022 workflow | `pyproject.toml` only | [README](./py311/README.md) |

## What Changes Across Folders

The application stays conceptually the same: a small historical calculator.
What changes is the packaging surface around it: where metadata lives, how
dependencies are declared, and which files must stay in sync.

## Where To Start

Open the README inside the era you want to inspect.

- Oldest baseline: [py16 README](./py16/README.md)
- First `setuptools` step: [py24 README](./py24/README.md)
- `requirements.txt` era: [py27 README](./py27/README.md)
- Declarative `setup.cfg` era: [py35 README](./py35/README.md)
- PEP 621 / `pyproject.toml` era: [py311 README](./py311/README.md)

For the full progression, read the folders in order from [`py16/`](./py16/)
through [`py311/`](./py311/).
