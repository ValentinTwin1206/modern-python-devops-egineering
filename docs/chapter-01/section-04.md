# Python `pipenv` environments

This page covers Pipenv, an application-oriented dependency manager that combines package installation, environment creation, and a lockfile. The example uses the tiny Bottle web server together with the Karva test runner and the Ruff linter from the rest of Chapter 1. Step-by-step development workflow instructions live in the section README at [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-04/README.md).

| Component            | Description                                      | Role in this section                                  |
| -------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Lightweight Python web framework.              | Example application dependency and web server         |
| [Karva](https://matthewmckee4.github.io/karva/) | Python test runner written in Rust.            | Test runner used for the section test workflow        |
| [Ruff](https://docs.astral.sh/ruff/) | Fast Python linter and formatter.              | Linter used for the section code-quality checks       |
| [Pipenv](https://pipenv.pypa.io/en/latest/) | Python environment and lockfile manager.       | Environment boundary and dependency workflow for this section |

!!! info "`Dockerfile.devEnv` and `Dockerfile`"
	The development image installs Pipenv, copies `Pipfile` and `Pipfile.lock`, creates a project-local `.venv` with `pipenv install --ignore-pipfile`, and activates that environment for interactive shells. The deployment image builds a wheel, creates the same `.venv`, installs the wheel, and starts the `tiny-webserver` entry point.

## Pipenv environment model

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

### Install Pipenv

=== "pip"

	Install Pipenv into the active Python interpreter with `pip`:

	```bash
	pip install pipenv
	```

=== "uv"

	Install Pipenv as a standalone tool with `uv`:

	```bash
	uv tool install pipenv
	```

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

Run the Bottle application without entering a shell:

```bash
pipenv run python -m tiny_webserver.app
```

Run the tests:

```bash
pipenv run karva test tests/
```

Run the linter:

```bash
pipenv run ruff check .
```

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

For lockfile-free isolation, see [Section 02](section-02.md). For interpreter and non-Python dependencies, see [Section 03](section-03.md). For an editor-backed development boundary that includes the host environment, see [Section 05](section-05.md).
