# Python `Pipenv` environments

This page covers Pipenv, an application-oriented workflow tool that sits on top of `virtualenv` and `pip`. It is not just a classical environment tool, and it is not a pure package manager either: it combines environment creation, dependency resolution, package installation, and a lockfile into one workflow.

## FastAPI CRUD Project

### Project Setup

The [FastAPI CRUD Project](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/README.md) is a small [FastAPI](https://fastapi.tiangolo.com/) service that uses [Pydantic](https://docs.pydantic.dev/) and [uvicorn](https://www.uvicorn.org/) for the application stack, with [Karva](https://matthewmckee4.github.io/karva/) and [Ruff](https://docs.astral.sh/ruff/) as development tools. It is a natural fit for [Pipenv](https://pipenv.pypa.io/en/latest/) because a committed `Pipfile.lock` gives every developer and every container the same dependency graph.

| Component            | Description |
| -------------------- | ----------- |
| [`src/fastapi_crud/main.py`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/src/fastapi_crud/main.py) | This module defines the FastAPI app, the Pydantic `Item` model, and the four CRUD endpoints. It is intentionally small so the focus stays on the dependency-management workflow around it. |
| [`Pipfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/Pipfile) | This file declares the direct runtime (`fastapi`, `pydantic`, `uvicorn`) and development dependencies for the project. It is the human-edited source of truth that Pipenv resolves into a locked dependency graph. |
| [`Pipfile.lock`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/Pipfile.lock) | This file stores the fully resolved dependency graph with exact versions and hashes. It is what makes the FastAPI service reproducible across machines and containers. |
| [`Dockerfile.devEnv`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/Dockerfile.devEnv) | This development image is based on `python:3.12-slim`, installs Pipenv, and runs `pipenv install --deploy --dev` against the lockfile. It gives you a pre-configured container with the FastAPI runtime and dev tools ready to use. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/Dockerfile) | This deployment image builds the project wheel and runs it through the locked Pipenv environment, exposing port 8080 for uvicorn. It connects Pipenv's development workflow to a reproducible container build. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/pyproject.toml) | This file contains the Python package metadata used during wheel builds. It complements the Pipenv files, which focus on environment management rather than package metadata. |

### Run the project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/README.md).

## `Pipenv` environment model

Pipenv first appeared in 2017 to combine virtual environment management and lockfile-based dependency workflows behind one application-oriented command-line tool. 

It keeps direct dependencies in `Pipfile` and the resolved tree in `Pipfile.lock`, but the environment itself is still a virtual environment created through `virtualenv` and populated through `pip`. Setting `PIPENV_VENV_IN_PROJECT=1` places that managed environment at `.venv/` next to the project, which keeps the location obvious during inspection.

### When to use `Pipenv`?

Because it combines environment creation, dependency resolution, and a committed lockfile in one workflow, Pipenv is a good fit for web services, small APIs, scheduled jobs, and internal tools that need deterministic installs across laptops, CI, and containers.

### Tradeoffs

#### Pros

- ✅ Real lockfile with hashes for reproducible application installs, which is what you want for a deployable web service like this FastAPI app.
- ✅ Clear split between runtime (`fastapi`, `pydantic`, `uvicorn`) and development (`ruff`, `karva`) dependencies.
- ✅ Single workflow for creating, syncing, and running the project environment, including `pipenv install --deploy` for fail-fast container builds.

#### Cons

- ⚠️ Adds another tool on top of Python and `pip`.
- ⚠️ Dependency solving can be slower than plain `pip` workflows.
- ⚠️ Less common in newer projects than `uv`, Poetry, or PDM.

### Install `Pipenv`

Pipenv is not bundled with Python. Install it into an existing Python environment with `pip`, or install it as a standalone tool with `uv`.

=== "pip"

	Install Pipenv into the active Python interpreter:

	```bash
	pip install pipenv
	```

=== "uv"

	Install Pipenv as an isolated command-line tool:

	```bash
	uv tool install pipenv
	```

### Dependency files

The dependency declaration uses TOML and pins each direct dependency the FastAPI service needs at runtime:

```toml
[packages]
fastapi = "==0.115.5"
pydantic = "==2.9.2"
uvicorn = "==0.32.1"

[dev-packages]
karva = ">=0.0.1a5"
ruff = ">=0.15.12"
```

`Pipfile.lock` records the resolved graph (FastAPI plus its transitive dependencies such as Starlette and `anyio`) with hashes, and is the file used during reproducible installs.

| File             | Purpose                                                           |
| ---------------- | ----------------------------------------------------------------- |
| `Pipfile`        | Direct runtime and development dependency declarations            |
| `Pipfile.lock`   | Fully resolved dependency graph with hashes                       |
| `.venv/`         | The managed project-local virtual environment                     |

## Workflow

### Create and use the environment

Create the environment from the section folder:

```bash
pipenv install
```

Open a shell inside the environment:

```bash
pipenv shell
```

### Manage dependencies

Add a runtime dependency:

```bash
pipenv install <package>
```

Add a development-only dependency:

```bash
pipenv install --dev <package>
```

Reinstall the exact lockfile contents:

```bash
pipenv sync
```

## Inspection

Show the active Python prefix:

```bash
python -c "import sys; print(sys.prefix)"
```

