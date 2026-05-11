# FastAPI CRUD `pipenv` Environment

This section shows how Pipenv combines installation, virtual-environment management, and a real lockfile into a single workflow. It builds a tiny FastAPI CRUD API (an `Item` resource with create, read, list, and delete) that benefits from deterministic, hash-pinned installs through `Pipfile.lock`.

For background on `Pipfile` and `Pipfile.lock`, see the [MkDocs page](../../docs/chapter-01/section-04.md).

## Required Developer Tools

- Docker or Podman.
- Python 3.12 (for the on-host path).
- `pipenv`.
- `uv` for the project development workflow.

## Setup Environment

### With Docker

Build the development image through the chapter helper:

```bash
../build.sh build --path section-04/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path section-04/Dockerfile.devEnv
```

Build and run the deployment image (FastAPI listens on `8080`):

```bash
../build.sh build --path section-04/Dockerfile
```

### On Host

Install Python on Ubuntu:

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-pip
```

Install Pipenv:

```bash
pip install pipenv
```

Keep the managed environment next to the project:

```bash
export PIPENV_VENV_IN_PROJECT=1
```

Generate the lockfile (first time only):

```bash
pipenv lock
```

Install runtime and development dependencies from the lockfile:

```bash
pipenv install --deploy --dev
```

## Usage Guide

Run the FastAPI app through Pipenv:

```bash
pipenv run python -m fastapi_crud.main
```

Open the interactive API docs at <http://localhost:8080/docs>.

Create an item with `curl`:

```bash
curl -X POST http://localhost:8080/items -H 'content-type: application/json' -d '{"name":"Book","price":9.5}'
```

Reinstall exactly what is recorded in the lockfile:

```bash
pipenv sync
```

## Development Guide

Sync the project environment with `uv`:

```bash
uv sync
```

Run the tests through Pipenv:

```bash
pipenv run karva test tests/
```

Run the linter through Pipenv:

```bash
pipenv run ruff check .
```

Build a wheel:

```bash
uv build --wheel
```
