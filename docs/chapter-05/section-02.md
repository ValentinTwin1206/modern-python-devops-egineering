# Development Environment

## Overview

It is common practice to use virtual environment tools such as `venv`, Conda, or `virtualenv` when running Python projects locally. They isolate project packages from the system Python and from other projects, keeping dependency versions consistent and preventing conflicts. For many projects that level of isolation is sufficient.

The *Depsight* project goes further by integrating [***Dev Containers***](https://containers.dev/), which define the full development environment as code rather than only isolating Python packages. Unlike a traditional virtual environment, a DevContainer also standardizes the OS layer, system tools, runtimes, editor setup, and the local toolchain used in CI. Because Depsight's CI pipeline also builds a production Docker image, the DevContainer uses Docker outside of Docker (DooD) so developers can build and test the container image locally without leaving the DevContainer.

| Capability | venv | DevContainer |
|-------------|:---:|:---:|
| Keep project packages separate from the system Python and other projects | ✅ | ✅ |
| Guarantee every developer uses the exact same Python interpreter version | ❌ | ✅ |
| Install OS-level libraries via `apt` (e.g. `gcc` for C extensions, `libpq` for Postgres) | ❌ | ✅ |
| Ship tools like `uv`, `ruff`, or Nuitka compiler dependencies inside the environment | ❌ | ✅ |
| Automatically install editor extensions and apply workspace settings for every developer | ❌ | ✅ |
| Run the exact same OS, Python, and toolchain locally as the CI pipeline | ❌ | ✅ |

---

## DevContainer Components

### DevContainer Configuration

The `devcontainer.json` is the central configuration file. It instructs the IDE how to build the container image, which extensions to install, which ports to forward, and which environment variables and lifecycle commands to apply.

```json
{
    "name": "Depsight DevContainer",
    "build": {
        "context": "..",
        "dockerfile": "Dockerfile",
        "args": {
            "PYTHON_VERSION": "${localEnv:PYTHON_VERSION:3.12}",
            "UV_VERSION": "${localEnv:UV_VERSION:0.11.1}"
        }
    },
    "features": {
        "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {
            "moby": false
        }
    },
    "customizations": {
        "vscode": {
            "settings": {
                "python.defaultInterpreterPath": "${containerWorkspaceFolder}/.venv/bin/python"
            }
        }
    },
    "containerEnv": {
        "APP_NAME": "DEPSIGHT",
        "DEPSIGHT_ENV": "development"
    },
    "forwardPorts": [8000],
    "mounts": [
        "source=depsight-uv-cache,target=/home/vscode/.cache/uv,type=volume"
    ],
    "portsAttributes": {
        "8000": {
            "label": "MkDocs Dev Server",
            "onAutoForward": "notify"
        }
    },
    "postCreateCommand": "uv sync --all-groups",
    "workspaceFolder": "/workspaces/${localWorkspaceFolderBasename}"
}
```

- `build`: Points to the `Dockerfile` and passes build arguments. `${localEnv:PYTHON_VERSION:3.12}` reads `PYTHON_VERSION` from the host environment, and the value after the colon is used as the fallback default.
- `features`: Adds pre-packaged capabilities from the [DevContainer Features registry](https://containers.dev/features). Here, `docker-outside-of-docker` installs the Docker CLI and mounts the host Docker socket so the project image can be built from inside the DevContainer.
- `containerEnv`: Injects environment variables into the running container so they are available to every process.
- `forwardPorts`: Exposes container ports to the host so local tools and browsers can access them.
- `workspaceFolder`: Sets the path inside the container where the project is mounted. If omitted, the Dev Containers extension defaults to `/workspaces/<repo-name>`.
- `postCreateCommand`: Runs after the workspace has been mounted and uses `workspaceFolder` as its working directory.

!!! info "Running a Python `venv` inside the DevContainer by default"

    `uv sync --all-groups` runs as the `postCreateCommand` and creates a `.venv/` directory named after the project (`prompt = depsight` in `.venv/pyvenv.cfg`). The `ms-python.python` extension then auto-detects the `.venv/` directory and activates it in every new integrated terminal — no manual step needed.


---

### Container Image

The `Dockerfile` defines the content of the container image — the pre-installed system tools, users, and their permissions — while `devcontainer.json` controls how the IDE integrates with that image and which lifecycle commands to run.

When `devcontainer.json` includes a `build` block, the IDE builds the image from the Dockerfile before starting the container. Without one, DevContainers use a pre-built image directly.

Depsight's Dockerfile is intentionally minimal — it extends the [Microsoft DevContainer base image](https://mcr.microsoft.com/en-us/catalog?search=devcontainers) and only adds what it doesn't already include:

```dockerfile
ARG PYTHON_VERSION="3.12"
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

ARG UV_VERSION="0.11.1"
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh \
    | UV_INSTALL_DIR=/usr/local/bin sh

ENV PYTHONUNBUFFERED=1
ENV APP_NAME=DEPSIGHT
ENV DEPSIGHT_ENV=development

EXPOSE 8000
```