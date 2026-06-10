# Python Dev Containers

This page explains how a Dev Container turns a Python project environment into a complete editor-backed development environment.

## Applied Project

### Project Setup

The applied project is a small image-processing CLI called `Pixelpack Project`. It is built on [Pillow](https://pillow.readthedocs.io/) and [Click](https://click.palletsprojects.com/), with [Nuitka](https://nuitka.net/) for native compilation. This makes it a good fit for Dev Containers because the project depends on a reproducible operating-system-level toolchain, not just isolated Python packages.

### Run the Project

Application, test, lint, container startup, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_pixelpack/README.md).

## Dev Containers environment model

Dev Containers emerged in VS Code workflows in 2019 to make full development machines reproducible, not just Python package sets. A `venv` isolates a project-local Python interpreter and its Python packages, and Conda can extend that boundary to non-Python runtime packages as well. By contrast, a Dev Container declares the operating system image, system packages, language runtimes, editor extensions, lifecycle hooks, workspace mount, user account, and project setup commands. The boundary moves from one project environment to the entire development machine.

### When to use Dev Containers?

As described in the [Dev Containers environment model](#dev-containers-environment-model), Dev Containers are a strong fit for projects that need more than Python package isolation. Examples include projects with native extensions that need a C toolchain and matching system libraries, compilation steps such as Nuitka or Cython, database clients, browser tooling, or multiple language runtimes.

| Capability | `venv` | Conda | Dev Containers |
| ---------- | ------ | ----- | -------------- |
| Keep project packages separate from the system Python and other projects | ✅ | ✅ | ✅ |
| Guarantee every developer uses the exact same Python interpreter version | ❌ | ✅ | ✅ |
| Install non-Python runtime packages inside the environment boundary | ❌ | ✅ | ✅ |
| Install OS-level libraries via `apt` or similar inside the environment boundary | ❌ | ❌ | ✅ |
| Ship tools such as `uv`, `ruff`, or compiler dependencies inside the environment boundary | ❌ | Limited | ✅ |
| Automatically install editor extensions and apply workspace settings for every developer | ❌ | ❌ | ✅ |
| Run the same OS, Python, and toolchain locally as the CI pipeline | ❌ | ❌ | ✅ |

### Tradeoffs

#### Pros

- ✅ Captures the operating system, tools, editor integration, and project setup in one reproducible boundary.
- ✅ Keeps host machine dependencies to a minimum while still giving a full development environment.
- ✅ Makes native build toolchains and multi-runtime setups such as CPython plus PyPy straightforward.

#### Cons

- ⚠️ Heavier than plain `venv` or Conda workflows because the boundary is an entire containerized machine.
- ⚠️ Depends on container tooling and editor integration, which adds setup overhead.
- ⚠️ Build, startup, and image maintenance costs are higher than interpreter-only workflows.
- ⚠️ Centered on Linux containers, so Windows environments are not supported.

### Install Dev Containers

#### System requirements

The Dev Containers CLI runs on Linux, macOS, and Windows. In typical Python workflows, it works with Linux containers provided by a supported container runtime such as Docker or Podman. The following examples use the Dev Containers CLI because its installation and usage are easier to reproduce in documentation than a full IDE setup with the Dev Containers extension, and some editor-driven steps cannot be performed entirely from a shell or other CLI-only environment.

#### Install the Dev Containers CLI

=== "Linux (Debian-based)"

	Use the official install script. It downloads the Dev Containers CLI together with a bundled Node.js runtime, so no separate `node` or `npm` installation is required:

	```bash
	curl -fsSL https://raw.githubusercontent.com/devcontainers/cli/main/scripts/install.sh | sh
	export PATH="$HOME/.devcontainers/bin:$PATH"
	```

	Check that the CLI is available:

	```bash
	devcontainer --version
	```

=== "Windows"

	Install Node.js LTS with Windows Package Manager, then install the Dev Containers CLI with npm:

	```powershell
	winget install OpenJS.NodeJS.LTS
	npm install -g @devcontainers/cli
	```

	Check that the CLI is available:

	```powershell
	devcontainer --version
	```

=== "macOS"

	Use the official install script. It supports both Intel and Apple Silicon Macs and installs the Dev Containers CLI together with a bundled Node.js runtime:

	```bash
	curl -fsSL https://raw.githubusercontent.com/devcontainers/cli/main/scripts/install.sh | sh
	export PATH="$HOME/.devcontainers/bin:$PATH"
	```

	Check that the CLI is available:

	```bash
	devcontainer --version
	```

### Environment layout

#### Project structure

A Dev Container is configured through a `.devcontainer/` folder at the repository root. The required file is `devcontainer.json`, while `Dockerfile` and helper scripts such as `postCreateCommand.sh` are optional and useful when the project needs system-level setup or more complex lifecycle commands.

```text
project-root/
├── .devcontainer/
│   ├── devcontainer.json
│   ├── Dockerfile            # optional
│   └── postCreateCommand.sh  # optional
├── src/
├── tests/
└── pyproject.toml
```

#### DevContainer configuration

The `devcontainer.json` file is the central configuration file. It tells the IDE or CLI how to build and start the development container for the applied project.

```json
{
	"name": "Python Dev Containers",
	"build": {
		"dockerfile": "Dockerfile",
		"context": ".."
	},
	"workspaceFolder": "/workspaces/section-04",
	"customizations": {
		"vscode": {
			"extensions": [
				"ms-python.python",
				"ms-python.vscode-pylance",
				"charliermarsh.ruff"
			],
			"settings": {
				"python.defaultInterpreterPath": "${containerWorkspaceFolder}/.venv/bin/python",
				"python.terminal.activateEnvironment": true,
				"ruff.nativeServer": "on"
			}
		}
	},
	"postCreateCommand": "uv sync --group dev",
	"remoteUser": "vscode"
}
```

- `name`: labels the development container as `Python Dev Containers`.
- `build`: tells Dev Containers to build the environment from the local `Dockerfile` instead of pulling a prebuilt image directly.
- `build.dockerfile`: points to `Dockerfile`; see [Container image](#container-image).
- `build.context`: sets the build context to the project root relative to `.devcontainer/`.
- `workspaceFolder`: mounts the project into `/workspaces/section-04` inside the container.
- `customizations.vscode.extensions`: installs the Python, Pylance, and Ruff extensions in VS Code.
- `customizations.vscode.settings`: sets the default interpreter, enables terminal activation for the project environment, and turns on Ruff's native server.
- `postCreateCommand`: runs `uv sync --group dev` after the workspace has been mounted; see [Lifecycle commands](#lifecycle-commands).
- `remoteUser`: runs the development session as the built-in `vscode` user.

#### Container image

The `Dockerfile` defines the content of the container image, such as preinstalled system tools, users, shells, and permissions, while `devcontainer.json` controls how the IDE integrates with that image and which lifecycle commands to run.

```dockerfile
# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - installs CPython, PyPy, uv, and Nuitka tooling
#   - runs editor terminals and lifecycle commands as vscode
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive APT prompts during image build.
ENV DEBIAN_FRONTEND=noninteractive

# Put user-level tools installed by uv on PATH.
ENV PATH="/home/vscode/.local/bin:${PATH}"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Python runtimes, the native tools Nuitka needs, and the system
# libraries Pillow links against for JPEG, PNG, and zlib support.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		ca-certificates \
		curl \
		git \
		libjpeg-dev \
		libpng-dev \
		patchelf \
		pypy3 \
		pypy3-venv \
		python3 \
		python3-dev \
		python3-pip \
		python3-venv \
		zlib1g-dev \
	&& rm -rf /var/lib/apt/lists/*

# Install user-level tools as the same account VS Code uses.
USER vscode

# Install Nuitka as a user-level uv tool.
RUN uv tool install nuitka

# Keep the final image user aligned with devcontainer.json.
USER vscode
```

#### Microsoft's DevContainer base images

Microsoft publishes purpose-built base images at [mcr.microsoft.com/devcontainers](https://mcr.microsoft.com/en-us/catalog?search=devcontainers) for common languages and stacks such as Python, JavaScript, and Rust. Unlike general-purpose container images, these Dev Container images are prepared for development workflows.

| Feature / Aspect | `python:3.12` | `mcr.microsoft.com/devcontainers/python:3.12` |
| ---------------- | ------------- | ---------------------------------------------- |
| Default user | `root` | `vscode` with `sudo` access |
| Non-root workflow | Manual setup required | Ready out of the box |
| Preinstalled tools | Minimal | Extensive |
| Python tooling | `pip` only | `pip`, `pipx`, and common development tools |
| Shell | `sh`, `bash` | `sh`, `bash`, `zsh` |
| VS Code Server support | Manual setup required | Works out of the box |

#### Lifecycle commands

Dev Containers support several lifecycle hooks that run at different points in the environment startup flow:

```mermaid
flowchart LR
	A[Create container] --> B[Mount workspace]
	B --> C[postCreateCommand]
	C --> D[Start container]
	D --> E[postStartCommand]
	E --> F[Attach IDE]
	F --> G[postAttachCommand]
	classDef lifecycle fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#0f172a;
	class A,B,C,D,E,F,G lifecycle;
```

- `postCreateCommand`: runs once after the container is created and the project has been mounted into `workspaceFolder`. It is typically used to install project dependencies with commands such as `uv sync --group dev` or `npm install`. ⚠️ **Do not install project dependencies in the `Dockerfile`**: the image is built before the repository is mounted, so the workspace mount would hide those files.
- `postStartCommand`: runs each time the container starts, including later restarts.
- `postAttachCommand`: runs each time the IDE attaches to the running container, including later reconnects, which makes it useful for editor-session setup tasks.

## Workflow

### Create and start

Start the environment from a shell with the globally installed CLI:

```bash
devcontainer up --workspace-folder projects/proj4_pixelpack
```

After the container has started, activate the virtual environment created by `uv`:
inside it:

```bash
vscode@container:/workspaces/section-04$ source .venv/bin/activate
```

Then you can run the applied project:

```bash
(.venv) vscode@container:/workspaces/section-04$ pixelpack --help
```

## Inspection

Show the workspace location inside the running container:

```bash
pwd
```

Show the current user inside the container:

```bash
whoami
```

Show the default Python interpreter inside the container:

```bash
which python3
```

Show the active container configuration file:

```bash
cat .devcontainer/devcontainer.json
```
