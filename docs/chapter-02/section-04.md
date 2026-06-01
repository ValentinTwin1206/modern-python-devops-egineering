# Python 2.7 with pip and `requirements.txt`

Python 2.7 was released in 2010, during the period when `pip` and `requirements.txt` became the everyday installation workflow for Python projects. The key pattern was separating package metadata in `setup.py` from concrete pinned dependency sets in requirements files.

## Applied Project

### Project Setup

The applied project is version 4.0.0 of Historic Calculator. It still uses `setup.py` for package installation and source builds, but the dependency workflow moves to `pip` and a pinned `requirements.txt` file.

NumPy replaces the earlier Numeric packages as the runtime component for array-style calculations. `requirements.txt` pins the exact NumPy version, so `pip install -r requirements.txt` can reproduce the dependency set more reliably than the manual download steps used in earlier sections.

!!! info "Historical development image"

	`Dockerfile.devEnv` builds a containerized approximation of the Python 2.7 development environment. It provides the interpreter, pip-era tooling, and project files needed to explore the `setup.py` plus `requirements.txt` workflow without changing the host machine.

### Packaging Matrix

| Field            | Value                                              |
| ---------------- | -------------------------------------------------- |
| Project version  | 4.0.0                                              |
| Python version   | 2.7                                                |
| NumPy            | 1.9.2, pinned in `requirements.txt`                |
| pip              | Bundled from 2.7.9 onward (PEP 477)                |
| Layout           | `setup.py` and `requirements.txt`                  |
| Distribution     | sdist                                              |

## Background

This project belongs to the Python 2.7 era that began in 2010, when `pip` and `requirements.txt` became the practical packaging workflow for many teams. PEP 477 later backported `ensurepip` to Python 2.7.9 in December 2014, so `pip` shipped with the interpreter from that release on.

The idiomatic project layout pairs `setup.py` with `install_requires=` for abstract runtime dependencies and `requirements.txt` with `==` pins for concrete deployments. `pip install -r requirements.txt` resolves and installs from PyPI, and the same pinned file reproduces the dependency set across machines. What the era still lacks is environment isolation by default, a modern resolver, and a true lockfile that captures the full transitive graph with hashes:

=== "`setup.py`"

	The `setup.py` file keeps the abstract runtime dependency and console-script registration:
	
	```python
	setup(
		name="historic_calculator",
		version="4.0.0",
		install_requires=["numpy"],
		entry_points={
			"console_scripts": [
				"hist_calc = historic_calculator.main:main_cli",
			],
		},
	)
	```

=== "`requirements.txt`"

	The concrete deployment pin lives in `requirements.txt`:

	```text
	numpy==1.9.2
	```

## Build and install

### Runtime and build dependencies

Install the pinned runtime dependencies:

```bash
pip install -r requirements.txt
```

This installs the concrete dependency set for the Python 2.7 workflow before the project package is installed.

### Build the package

Build the source distribution:

```bash
python setup.py sdist
```

The era predates PEP 427 wheels, so the source distribution is the canonical artifact.

### Install the package

Install the project itself:

```bash
python setup.py install
```

### Run Project

After installation, run the installed console script:

```bash
hist_calc max 1,-2,4
```

Without installation, run the calculator from the source tree:

```bash
PYTHONPATH=src python -c "from historic_calculator.main import run_calculator; print run_calculator('max', '1,-2,4')"
```

Additional build and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-02/section-04/README.md).
