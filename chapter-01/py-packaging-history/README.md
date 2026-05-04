# Python Packaging History

This directory follows one small package across six packaging eras. Each
subdirectory is a self-contained snapshot with its own source tree,
dependency files, Docker setup, and a README describing the tooling and
installation style of that period.

## Folder Index

| Folder | Year | Era | Packaging shape | Details |
| ------ | ---- | --- | --------------- | ------- |
| [`01-py16/`](./01-py16/) | 2000 | Python 1.6 | `setup.py` with stdlib `distutils` | [README](./01-py16/README.md) |
| [`02-py23/`](./02-py23/) | 2003 | Python 2.3 | `setup.py` with metadata-only dependency hints | [README](./02-py23/README.md) |
| [`03-py24/`](./03-py24/) | 2004 | Python 2.4 | `setup.py` with early `setuptools` | [README](./03-py24/README.md) |
| [`04-py27/`](./04-py27/) | 2010 | Python 2.7 | `setup.py` plus pinned `requirements.txt` | [README](./04-py27/README.md) |
| [`05-py35/`](./05-py35/) | 2016 | Python 3.5 / 2016 workflow | `setup.py` + `setup.cfg` + `requirements*.txt` | [README](./05-py35/README.md) |
| [`06-py311/`](./06-py311/) | 2022 | Python 3.11 / 2022 workflow | `pyproject.toml` only | [README](./06-py311/README.md) |

## What Changes Across Folders

The application stays conceptually the same: a small historical calculator.
What changes is the packaging surface around it: where metadata lives, how
dependencies are declared, and which files must stay in sync.

