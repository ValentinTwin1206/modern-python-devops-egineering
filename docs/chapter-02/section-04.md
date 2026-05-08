# Section 04: Python 2.7 with pip and `requirements.txt`

This page covers the fourth packaging snapshot in the Historic Calculator series. The example targets Python 2.7, released on July 3, 2010. It uses `setup.py` together with a pinned `requirements.txt`, which became the canonical reproducible install pattern of the era.

## Background

PEP 477 backported `ensurepip` to Python 2.7.9 in December 2014. `pip` ships with the interpreter from that release on. The idiomatic project layout pairs `setup.py` with `install_requires=` for abstract runtime dependencies and `requirements.txt` with `==` pins for concrete deployments. `pip install -r requirements.txt` resolves and installs from PyPI, and the same pinned file reproduces the dependency set across machines.

What the era still lacks is environment isolation by default, a modern resolver, and a true lockfile that captures the full transitive graph with hashes.

## Packaging matrix

| Field            | Value                                              |
| ---------------- | -------------------------------------------------- |
| Project version  | 4.0.0                                              |
| Python version   | 2.7                                                |
| NumPy            | 1.9.2, pinned in `requirements.txt`                |
| pip              | Bundled from 2.7.9 onward (PEP 477)                |
| Layout           | `setup.py` and `requirements.txt`                  |
| Distribution     | sdist                                              |

## Install

Install the pinned runtime dependencies:

```bash
pip install -r requirements.txt
```

Install the project itself:

```bash
python setup.py install
```

Verify NumPy:

```bash
python -c "import numpy; print numpy.__version__"
```

## Build

Build the source distribution:

```bash
python setup.py sdist
```

The era predates PEP 427 wheels, so the source distribution is the canonical artifact.

## Usage

Run the calculator with one of `max`, `min`, `mean`, or `sum`:

```bash
hist_calc max 1,-2,4
```

## See also

- Declarative metadata in `setup.cfg` in [Section 05](section-05.md).
- A `pyproject.toml`-only project in [Section 06](section-06.md).
