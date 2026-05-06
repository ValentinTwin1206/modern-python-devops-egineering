# Python Virtual Environments

This section compares project-local Python environments. It uses the
same tiny `bottle` web server, `karva` test runner, and `ruff` linting
tooling as the rest of Chapter 2 so the environment mechanics stay the
main subject.

The examples focus on three distinct environment styles:

- `venv` uses Python's standard-library environment tool.
- `conda` uses an external package and environment manager.
- `pipenv` combines package installation, environment creation, and a
  lockfile-driven application workflow.
- `virtualenv` is intentionally not a separate subchapter here because its
  core layout and development workflow are very close to `venv` for the
  purposes of this chapter.

Start with one of the concrete examples:

```sh
cd chapter-02/section-02/venv
docker build -t pyenv-venv .
docker run --rm -it -v "$PWD":/app pyenv-venv
```

## Environment Isolation

### Overview

A virtual environment gives a project its own Python executable,
package directory, and command-line scripts. Activating the environment
changes `PATH` so commands such as `python`, `pip`, `karva`, and `ruff`
resolve inside the environment instead of the operating system Python.

The key idea is that dependency changes stay local to one project. That
keeps unrelated projects and operating system tools from importing the
wrong package versions.

### Folder Index

| Folder | Tool | Focus | Details |
| ------ | ---- | ----- | ------- |
| [`venv/`](./venv/) | `venv` | standard-library virtual environments | [README](./venv/README.md) |
| [`conda/`](./conda/) | `conda` | interpreter and non-Python dependency management | [README](./conda/README.md) |
| [`pipenv/`](./pipenv/) | `pipenv` | lockfile-based application environments | [README](./pipenv/README.md) |

### Comparison

| Aspect | `venv` | `conda` | `pipenv` |
| ------ | ------ | ------- | -------- |
| Ships with Python | yes | no | no |
| Manages Python itself | no | yes | no |
| Dependency source | PyPI through `pip` | conda channels, with optional `pip` | PyPI through `pip` |
| Locking model | none by default | `environment.yml` can pin the environment | `Pipfile.lock` |
| Non-Python packages | no | yes | no |
| Best fit | simple Python projects | scientific and native dependency stacks | applications needing deterministic installs |

## Choosing A Tool

### `venv`

Use `venv` when you want the smallest standard workflow and already have
the Python version you need installed. It is the default choice for many
pure-Python projects.

### `conda`

Use `conda` when Python is only part of the environment and the project
also needs native libraries, compiler-adjacent packages, GPU stacks, or
a managed Python interpreter version.

### `pipenv`

Use `pipenv` when you want an application-oriented workflow with one
tool that creates the environment, installs dependencies, and records a
resolved lockfile.

## Common Workflow

Each subfolder is self-contained and can be entered directly:

```sh
cd chapter-02/section-02/venv
```

Run the web server from inside the selected environment:

```sh
python -m tiny_webserver.app
```

Run tests and linting with the environment-local tools:

```sh
karva test tests/
ruff check .
```

## Useful Inspection Commands

Use these command patterns inside any of the example containers to see
which environment is active.

### Resolved Commands

Show which executables the shell resolves from `PATH`.

```sh
which python
which pip
which karva
which ruff
```

### Python Prefixes

Show whether Python considers itself inside an environment.

```sh
python -c "import sys; print('prefix =', sys.prefix); print('base_prefix =', sys.base_prefix)"
```

### Import Path

Print every entry on Python's import path.

```sh
python -c "import sys; [print(path) for path in sys.path]"
```

### Package Locations

Show where the example packages physically live.

```sh
python -c "import bottle; print('bottle =', bottle.__file__)"
which karva
which ruff
```
