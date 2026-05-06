# Python Dev Containers

This section explains how a Dev Container turns a Python project
environment into a complete editor-backed development environment. It
uses the shared tiny `bottle` web server, `karva` test runner, and
`ruff` linting setup from the rest of Chapter 2.

The `.devcontainer` setup is the important demonstration. It builds a
VS Code development container from a standard Ubuntu Dev Containers base
image:

- It starts from `mcr.microsoft.com/devcontainers/base:ubuntu-24.04`.
- It installs CPython, `pip`, `venv`, and PyPy with APT.
- It installs `uv` for the project workflow.
- It configures VS Code Python tooling and forwards port `8080`.
- It runs `uv sync --group dev` after the workspace is mounted.
- It keeps the source tree bind-mounted so editor changes and container
  commands operate on the same files.

Open this folder in a Dev Container from VS Code:

```sh
code chapter-02/section-03
```

Then run **Dev Containers: Reopen in Container** from the Command
Palette.

## Dev Container Footprint

### Overview

A Python virtual environment isolates Python packages. A Dev Container
does much more: it defines the operating system image, system packages,
language runtimes, editor extensions, forwarded ports, lifecycle hooks,
workspace mount, user account, shell environment, and project setup
commands.

That makes Dev Containers a higher-level development boundary. The
environment is not only "which `site-packages` directory does this
project use?" but also "which Linux distribution, system packages,
interpreter implementations, editor tools, and startup commands does the
whole workspace use?"

### Container Layout

The project keeps its container contract under `.devcontainer/`:

| Path | Purpose |
| ---- | ------- |
| [`.devcontainer/devcontainer.json`](./.devcontainer/devcontainer.json) | VS Code Dev Containers configuration, extensions, lifecycle commands, and forwarded ports |
| [`.devcontainer/Dockerfile`](./.devcontainer/Dockerfile) | Ubuntu-based development image with CPython, PyPy, and `uv` |
| [`pyproject.toml`](./pyproject.toml) | Local project metadata, Bottle runtime dependency, Karva/Ruff dev dependencies, and `uv_build` backend |
| [`src/tiny_webserver/app.py`](./src/tiny_webserver/app.py) | Minimal Bottle application with one JSON endpoint |
| [`tests/test_app.py`](./tests/test_app.py) | Karva-compatible test for the Bottle endpoint |

### Dev Container Vs Virtual Environment

| Aspect | Python virtual environment | Dev Container |
| ------ | -------------------------- | ------------- |
| Boundary | Python interpreter and packages | full development container plus editor integration |
| System packages | inherited from host | declared in image or features |
| Python implementations | usually one active interpreter | can include CPython, PyPy, and other runtimes side by side |
| Editor setup | configured separately on each host | declared in `devcontainer.json` |
| Ports and services | manual host setup | forwarded and named by the container config |
| Lifecycle commands | manual shell commands | `postCreateCommand`, `postStartCommand`, and related hooks |
| Reproducibility scope | Python dependencies | OS, tools, interpreters, editor extensions, and project setup |

Virtual environments are still useful inside Dev Containers. The point
is that the Dev Container owns the larger development machine, while the
virtual environment remains one Python-specific layer inside it.

## Runtime Installation

### CPython

The Dockerfile installs Ubuntu's CPython packages:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv
```

This gives the container the standard `/usr/bin/python3` interpreter,
`pip3`, and the standard-library `venv` module.

### PyPy

The same image also installs PyPy:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        pypy3 \
        pypy3-venv
```

PyPy is a separate Python implementation with a JIT compiler. Installing
it next to CPython makes the container useful for comparing interpreter
behavior without changing the host machine.

### Project Environment

The Dev Container uses `uv` to create and sync the project environment
after VS Code mounts the workspace:

```json
"postCreateCommand": "uv sync --group dev"
```

This timing matters. During image build, the source tree is not copied
into the image. During Dev Container startup, VS Code mounts the working
copy into `/workspaces/section-03`, then runs the lifecycle command
against the real project files.

## Common Workflow

Run the tiny web server inside the Dev Container:

```sh
uv run tiny-webserver
```

Run tests and linting:

```sh
uv run karva test tests/
uv run ruff check .
```

Build the project wheel:

```sh
uv build --wheel
```

Run a quick PyPy check:

```sh
pypy3 --version
pypy3 -c "import sys; print(sys.implementation.name); print(sys.executable)"
```

## Useful Inspection Commands

Use these command patterns inside the Dev Container to inspect the full
development environment.

### Workspace Location

Show where VS Code mounted the project.

```sh
pwd
ls -la
```

Expected path shape:

```text
/workspaces/section-03
```

### CPython Interpreter

Show the default CPython executable.

```sh
which python3
python3 --version
```

Expected output starts with:

```text
/usr/bin/python3
Python 3.12
```

### PyPy Interpreter

Show the PyPy executable installed by APT.

```sh
which pypy3
pypy3 --version
```

Expected output includes:

```text
/usr/bin/pypy3
PyPy
```

### uv Project Environment

Show which Python `uv` selected for the project environment.

```sh
uv run python -c "import sys; print(sys.executable); print(sys.version)"
```

### Forwarded Web Port

Run the server:

```sh
uv run tiny-webserver
```

VS Code forwards port `8080`, so the endpoint is available from the host:

```sh
curl http://localhost:8080/
```

Expected response:

```json
{"message": "Hello from tiny webserver"}
```
