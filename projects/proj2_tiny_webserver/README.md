# Tiny Webserver `venv` Environment

This section shows how Python's standard-library `venv` module isolates dependencies inside a project-local directory. It runs the tiny Bottle web server through that environment.

## Project Components

The table below lists the main files that support the `venv` example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image creates and activates a virtual environment at `/opt/venv`. It gives you a reproducible example of how the project and its tools are installed into an isolated interpreter. |
| [Dockerfile](Dockerfile) | This deployment image builds the project wheel and installs it into the same virtual-environment layout. It shows how the `venv` pattern carries from interactive development into container deployment. |
| [pyproject.toml](pyproject.toml) | This file defines the package metadata and dependencies for the example project. Those dependencies are what get installed into the virtual environment during the workflow shown below. |

## System Requirements

- Docker or Podman for the container workflow.
- Python 3.12 with the standard-library `venv` module for the on-host path.
- `pip` for installing the project package and `uv` for the development workflow.

## Installation

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

Install the project dependencies into the active environment:

```bash
pip install .
```

Leave the environment:

```bash
deactivate
```

## Usage Guide

The deployment image in [Dockerfile](Dockerfile) ships the Bottle server as the container entry point. Build the image once with the [Build Guide](#build-guide), then start the server with the `docker` CLI directly.

Start the server in the foreground and publish its port on the host:

```bash
docker run --rm -p 8080:8080 tiny-webserver
```

Send a request from another terminal:

```bash
curl http://localhost:8080
```

The Bottle app responds with `{"message": "Hello from tiny webserver"}`. Stop the server with `Ctrl+C`.

Run the container detached and give it a name so you can manage it explicitly:

```bash
docker run --rm --detach --name tiny-webserver --publish 8080:8080 tiny-webserver
```

Stop the detached container when you are done:

```bash
docker stop tiny-webserver
```

## Development Guide

The project workflow uses `uv` for development commands. You can run it inside the containerized environment or inside the on-host `venv` created above.

### With Docker

Build the development image through the projects helper:

```bash
../build.sh build --path proj2_tiny_webserver/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path proj2_tiny_webserver/Dockerfile.devEnv
```

### Sync Environment

Sync the project environment with `uv`:

```bash
uv sync
```

### Run Tests

Run the test suite with Karva:

```bash
uv run karva test tests/
```

### Lint

Run Ruff against the source tree:

```bash
uv run ruff check .
```

### Build Guide

The deployment image in [Dockerfile](Dockerfile) is a two-stage build. The first stage uses `uv build --wheel` to produce the project wheel, the second stage installs that wheel into a virtual environment at `/opt/venv`, and the runtime stage starts the `tiny-webserver` console script on port 8080.

Build the deployment image from the project directory using the `docker` CLI directly:

```bash
docker build --file Dockerfile --tag tiny-webserver .
```

Inspect the resulting image:

```bash
docker image inspect tiny-webserver
```

See the [Usage Guide](#usage-guide) for the `docker run` invocations that exercise the built image.
