# `pipenv` Environment

This project shows how `pipenv` creates and manages an application
environment for the shared tiny `bottle` web server. It includes the
same `karva` and `ruff` development tooling as the other Chapter 2
examples.

The `Dockerfile` is the important demonstration. It builds a container
where `pipenv` owns the dependency workflow:

- It starts from `python:3.14-slim`.
- It installs Bash and a minimal build toolchain with APT.
- It installs `pipenv` into the system Python.
- It copies `Pipfile` and `Pipfile.lock` first.
- It creates a project-local `.venv` with `pipenv install --deploy`.
- It puts `/app/.venv/bin` first on `PATH`.
- It activates the environment automatically for interactive shells.

Start the container with a bind mount so local edits appear under `/app`
at runtime:

```sh
cd chapter-02/section-02/pipenv
docker build -t pyenv-pipenv .
docker run --rm -it -v "$PWD":/app pyenv-pipenv
```

## Pipenv Environment Footprint

### Overview

`pipenv` combines package installation, environment creation, and a
lockfile workflow. Direct dependencies live in [`Pipfile`](Pipfile),
while [`Pipfile.lock`](Pipfile.lock) records the resolved dependency
tree with hashes.

The Dockerfile sets `PIPENV_VENV_IN_PROJECT=1`, so the managed
environment is created at `/app/.venv` instead of under the user's home
directory. That makes the environment location obvious for inspection.

### Dependency Files

`Pipfile` is the human-edited dependency declaration:

```toml
[packages]
bottle = "==0.13.4"

[dev-packages]
karva = ">=0.0.1a5"
ruff = ">=0.15.12"
```

`Pipfile.lock` is the generated resolved dependency graph. It is the
file used by deterministic installs in the Docker build.

### PATH And Execution

The Dockerfile puts the Pipenv-managed environment first on `PATH`:

```sh
which python
which pip
which karva
which ruff
```

Commands resolve under `/app/.venv/bin` once the environment has been
created.

## Dependency Workflow

### Create The Environment

Install `pipenv` and create the environment from this folder:

```sh
pip install pipenv
pipenv install
```

Open a shell inside the environment:

```sh
pipenv shell
```

### Manage Packages

Add a runtime dependency:

```sh
pipenv install <package>
```

Add a development-only dependency:

```sh
pipenv install --dev <package>
```

Reinstall exactly what is recorded in the lockfile:

```sh
pipenv sync
```

### Run The Project

Run the tiny Bottle application without entering a shell:

```sh
pipenv run python -m tiny_webserver.app
```

Run tests and linting:

```sh
pipenv run karva test tests/
pipenv run ruff check .
```

### Leave The Environment

Leave an interactive `pipenv shell`:

```sh
exit
```

## Tradeoffs

### Pros

`pipenv` gives applications a real lockfile, separates runtime and
development dependencies, and offers one workflow for creating and using
the environment.

### Cons

`pipenv` adds another tool, can resolve more slowly than plain `pip`,
and is less common in newer Python projects than `uv`, Poetry, or PDM.

## Useful Inspection Commands

Use these command patterns inside the container to inspect the active
environment.

### Resolved Commands

```sh
which python
which pip
which karva
which ruff
```

Expected output starts with:

```text
/app/.venv/bin/python
/app/.venv/bin/pip
/app/.venv/bin/karva
/app/.venv/bin/ruff
```

### Python Prefixes

```sh
python -c "import sys; print('prefix =', sys.prefix); print('base_prefix =', sys.base_prefix)"
```

Expected output includes:

```text
prefix = /app/.venv
```

### Package Locations

```sh
python -c "import bottle, tiny_webserver; print('bottle =', bottle.__file__); print('tiny_webserver =', tiny_webserver.__file__)"
```

Expected output includes paths under:

```text
/app/.venv/lib/python3.14/site-packages/
/app/src/tiny_webserver/
```
