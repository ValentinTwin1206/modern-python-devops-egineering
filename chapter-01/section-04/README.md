# Tiny Webserver `pipenv` Environment

This section shows how Pipenv combines installation, virtual-environment management, and a real lockfile into a single workflow. It runs the tiny Bottle web server through that environment.

For background on `Pipfile` and `Pipfile.lock`, see the [MkDocs page](../../docs/chapter-01/section-04.md).

## Required Developer Tools

- Docker or Podman.
- Python 3.12 (for the on-host path).
- `pipenv`.
- `uv` for the project development workflow.

### With Docker

Build the development image through the chapter helper:

```bash
../build.sh build --path section-04/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path section-04/Dockerfile.devEnv
```

Build and run the deployment image:

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

Create the environment from the lockfile:

```bash
pipenv install
```

Install development dependencies as well:

```bash
pipenv install --dev
```

## Usage Guide

Run the Bottle application through Pipenv:

```bash
pipenv run python -m tiny_webserver.app
```

Open an interactive shell in the environment:

```bash
pipenv shell
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
