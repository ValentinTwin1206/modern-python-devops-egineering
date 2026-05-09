# Python `Pipenv` environments

This page covers Pipenv, an application-oriented dependency manager that combines package installation, environment creation, and a lockfile.

## Tiny Webserver Project

The example uses the tiny Bottle web server project. Step-by-step development workflow instructions live in the section README at [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/README.md).

### Used DevTools

These tools cover the example application's runtime package, development utilities, and the Pipenv workflow explained in this section.

| Component            | Description |
| -------------------- | ----------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Bottle is the main runtime dependency for the example application. It gives the Pipenv workflow a concrete package to lock and reinstall reproducibly. |
| [Karva](https://matthewmckee4.github.io/karva/) | Karva is the test runner used by the example project. It appears here as a development dependency that Pipenv can keep separate from runtime requirements. |
| [Ruff](https://docs.astral.sh/ruff/) | Ruff is the linter and formatter used for code-quality checks. It is part of the development toolchain that benefits from Pipenv's lockfile-based workflow. |
| [Pipenv](https://pipenv.pypa.io/en/latest/) | Pipenv is the environment manager and lockfile tool explained in this section. It creates the environment, tracks direct dependencies, and reproduces exact versions through the lockfile. |

### Project Files

These project files show how the Pipenv-based workflow is declared, locked, and reproduced for both development and container builds.

| Component            | Description |
| -------------------- | ----------- |
| [`Pipfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/Pipfile) | This file declares the direct runtime and development dependencies for the project. It is the human-edited source of truth that Pipenv resolves into a locked dependency graph. |
| [`Pipfile.lock`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/Pipfile.lock) | This file stores the fully resolved dependency graph with exact versions and hashes. It is what makes the Pipenv environment reproducible across machines and containers. |
| [`Dockerfile.devEnv`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/Dockerfile.devEnv) | This development image installs Pipenv and creates a project-local `.venv`. It gives you a containerized example of the same locked environment workflow described in the text. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/Dockerfile) | This deployment image builds the project wheel and runs it through the locked environment pattern. It connects Pipenv's development workflow to a reproducible container build. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/pyproject.toml) | This file contains the Python package metadata used during wheel builds. It complements the Pipenv files, which focus on environment management rather than package metadata. |

## Install `Pipenv`

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

## `Pipenv` environment model

Pipenv keeps direct dependencies in `Pipfile` and the resolved tree in `Pipfile.lock`. Setting `PIPENV_VENV_IN_PROJECT=1` places the managed environment at `.venv/` next to the project, which keeps the location obvious during inspection.

### Dependency files

The dependency declaration uses TOML:

```toml
[packages]
bottle = "==0.13.4"

[dev-packages]
karva = ">=0.0.1a5"
ruff = ">=0.15.12"
```

`Pipfile.lock` records the resolved graph with hashes and is the file used during reproducible installs.

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

### Run the project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/README.md).

## Inspection

Show the active Python prefix:

```bash
python -c "import sys; print(sys.prefix)"
```

## Tradeoffs

### Pros

- ✅ Real lockfile for reproducible application installs.
- ✅ Clear split between runtime and development dependencies.
- ✅ Single workflow for creating, syncing, and running the project environment.

### Cons

- ⚠️ Adds another tool on top of Python and `pip`.
- ⚠️ Dependency solving can be slower than plain `pip` workflows.
- ⚠️ Less common in newer projects than `uv`, Poetry, or PDM.
