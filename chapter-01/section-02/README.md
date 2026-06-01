# Tiny Webserver `venv` Environment

This section shows how Python's standard-library `venv` module isolates dependencies inside a project-local directory. It runs the tiny Bottle web server through that environment.

For the folder layout, activation behavior, and tradeoffs, see the [MkDocs page](../../docs/chapter-01/section-02.md).

## Project Components

The table below lists the main files that support the `venv` example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image creates and activates a virtual environment at `/opt/venv`. It gives you a reproducible example of how the project and its tools are installed into an isolated interpreter. |
| [Dockerfile](Dockerfile) | This deployment image builds the project wheel and installs it into the same virtual-environment layout. It shows how the `venv` pattern carries from interactive development into container deployment. |
| [pyproject.toml](pyproject.toml) | This file defines the package metadata and dependencies for the example project. Those dependencies are what get installed into the virtual environment during the workflow shown below. |

## Required Developer Tools

- Docker or Podman.
- Python 3.12 with the standard-library `venv` module (for the on-host path).
- `pip` and `uv`.

## Setup Environment

### With Docker

Build the development image through the chapter helper:

```bash
../build.sh build --path section-02/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path section-02/Dockerfile.devEnv
```

Build and run the deployment image:

```bash
../build.sh build --path section-02/Dockerfile
```

### On Host

Install Python and the `venv` module on Ubuntu:

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
```

Create the virtual environment:

```bash
python3 -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Install the project into the active environment:

```bash
pip install .
```

Leave the environment:

```bash
deactivate
```

## Usage Guide

Run the Bottle application:

```bash
python -m tiny_webserver.app
```

Inspect the active prefix:

```bash
python -c "import sys; print(sys.prefix); print(sys.base_prefix)"
```

## Development Guide

Sync the project environment with `uv`:

```bash
uv sync
```

Run the tests:

```bash
uv run karva test tests/
```

Run the linter:

```bash
uv run ruff check .
```

Build a wheel:

```bash
uv build --wheel
```
