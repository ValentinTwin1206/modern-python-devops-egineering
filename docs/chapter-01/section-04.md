# Python Dev Containers

This page explains how a Dev Container turns a Python project environment into a complete editor-backed development environment.

## Applied Project

### Project Setup

The applied project is a small server administration CLI called `Server CLI`. It is built on [Click](https://click.palletsprojects.com/), with [Nuitka](https://nuitka.net/) for native compilation and Debian packaging for APT installation. This makes it a good fit for Dev Containers because the project depends on a reproducible operating-system-level toolchain, not just isolated Python packages.

### Run the Project

Application, test, lint, container startup, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_servercli/README.md).

## Dev Containers Environment Model

Dev Containers emerged in VS Code workflows in 2019 to make full development machines reproducible, not just Python package sets. The open [Development Containers Specification](https://containers.dev/implementors/spec/) generalizes this model beyond VS Code, with popular examples including JetBrains IDEs and GitHub Codespaces. Its most important building blocks are a `devcontainer.json` configuration file, a container image, optional Features and Templates, and lifecycle commands that prepare the workspace. 

A `venv` establishes the smallest environment boundary by isolating a project-local Python interpreter and its Python packages. Conda extends that boundary to non-Python runtime packages as well. A Dev Container carries the progression further by declaring the operating system image, system packages, language runtimes, editor extensions, lifecycle hooks, workspace mount, user account, and project setup commands. The boundary expands from one project environment to the entire development machine.

| Capability | `venv` | Conda | Dev Containers |
| ---------- | ------ | ----- | -------------- |
| Project package isolation | ✅ | ✅ | ✅ |
| Pinned Python version | ❌ | ✅ | ✅ |
| Non-Python runtime packages | ❌ | ✅ | ✅ |
| OS-level libraries | ❌ | ❌ | ✅ |
| Tools and compiler dependencies | ❌ | Limited | ✅ |
| Editor extensions and workspace settings | ❌ | ❌ | ✅ |
| CI environment parity | ❌ | ❌ | ✅ |

### When to Use Dev Containers?

Dev Containers are a strong fit for machine-learning, data-science, and scientific-computing projects, native-extension and systems projects, and applications using databases, browser automation, or multiple runtimes. These projects often need system libraries, compilers, command-line tools, and fixed runtime versions in addition to Python packages. Defining them in the container image and Dev Container configuration makes onboarding reproducible and keeps local development aligned with CI.

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

The following examples use the `devcontainer` CLI to demonstrate a tool-independent workflow. Each IDE provides its own Dev Container integration, including [Visual Studio Code](https://code.visualstudio.com/docs/devcontainers/containers) and [JetBrains IDEs](https://www.jetbrains.com/help/idea/connect-to-devcontainer.html).

The system requirements are a supported host operating system, a container runtime such as Docker or Podman, and network access to download images and dependencies. The `devcontainer` CLI runs on Linux, macOS, and Windows.

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

### Environment Layout

#### Environment Definition

The Dev Container environment is defined by a `.devcontainer/devcontainer.json` file and, when needed, a `Dockerfile`, Features, or Templates. The configuration describes how to build the image, mount the workspace, install editor support, and prepare the development environment. The `devcontainer.json` file is the central configuration file that tells a compatible IDE or CLI how to build and start the development container.

```json
{
	"name": "Python Dev Container",
	"build": {
		"dockerfile": "Dockerfile",
		"context": ".."
	},
	"workspaceFolder": "/workspaces/project",
	"customizations": {
		"vscode": {
			"extensions": [
				"ms-python.python",
				"ms-python.vscode-pylance",
				"charliermarsh.ruff"
			],
			"settings": {
				"python.defaultInterpreterPath": "${containerWorkspaceFolder}/.venv/bin/python",
				"python.terminal.activateEnvironment": true
			}
		},
		"jetbrains": {
			"plugins": [
				"Python"
			]
		}
	},
	"postCreateCommand": "uv sync",
	"remoteUser": "vscode"
}
```

- `name`: Gives the development environment a display name in compatible tools.
- `build`: Defines how to create the container image.
	- `dockerfile`: Selects the `Dockerfile`. Microsoft publishes [Dev Container base images](https://mcr.microsoft.com/en-us/catalog?search=devcontainers) for environments such as Python, JavaScript, and Rust. They provide a ready non-root user, common development tools, and editor integration.
	- `context`: Sets the files available during the image build, usually the project root.
- `workspaceFolder`: Sets the path where the project is opened inside the container.
- `customizations`:
	- `vscode`: 
		- `extensions`: Installs VS Code extensions such as Python, Pylance, and Ruff.
		- `settings`: Applies VS Code settings, including the container's Python interpreter.
	- `jetbrains`:
		- `plugins`: Installs JetBrains plugins such as Python.
- `postCreateCommand`: Runs project setup commands after the workspace is mounted.
- `remoteUser`: Selects the user for terminals, tools, and lifecycle commands.

##### Container image

The `Dockerfile` defines the content of the container image, such as preinstalled system tools, users, shells, and permissions, while `devcontainer.json` controls how the IDE integrates with that image and which lifecycle commands to run.

```dockerfile
# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - installs CPython, uv, Nuitka, and Debian packaging tooling
#   - runs editor terminals and lifecycle commands as vscode
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive APT prompts during image build.
ENV DEBIAN_FRONTEND=noninteractive

# Put user-level tools installed by uv on PATH.
ENV PATH="/home/vscode/.local/bin:${PATH}"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Python, the native tools Nuitka needs, and Debian packaging tools.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		binutils \
		ca-certificates \
		curl \
		debhelper \
		devscripts \
		dpkg-dev \
		git \
		patchelf \
		python3 \
		python3-dev \
		python3-venv \
	&& rm -rf /var/lib/apt/lists/*

# Install user-level tools as the same account VS Code uses.
USER vscode

# Install Nuitka as a user-level uv tool. It is intentionally not a
# pyproject.toml dependency because it is a container build tool.
RUN uv tool install nuitka

# Keep the final image user aligned with devcontainer.json.
USER vscode
```

!!! warning "Keep project setup commands out of the `Dockerfile`"
	The image is built before the repository is mounted, so project files are not available during the image build and the workspace mount would hide them later. Put commands that install or update project dependencies in `postCreateCommand` inside `devcontainer.json`, as described in [Lifecycle commands](#lifecycle-commands).

##### Lifecycle commands

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

- `postCreateCommand`: runs once after the container is created and the project has been mounted into `workspaceFolder`. It is typically used to install project dependencies with commands such as `uv sync --group dev` or `npm install`. 
- `postStartCommand`: runs each time the container starts, including later restarts.
- `postAttachCommand`: runs each time the IDE attaches to the running container, including later reconnects, which makes it useful for editor-session setup tasks.

#### Key Directories and Files

A Dev Container is configured through a `.devcontainer/` folder at the project
root. The required file is `devcontainer.json`, while `Dockerfile` and helper
scripts such as `postCreateCommand.sh` are optional and useful when the project
needs system-level setup or more complex lifecycle commands.

```text
project-root/
├── .devcontainer/
│   ├── devcontainer.json
│   ├── Dockerfile            # optional
│   └── postCreateCommand.sh  # optional
├── src/
├── tests/
├── pyproject.toml
└── uv.lock
```

## Development Workflow

### Activate the Environment

Start the environment from a shell with the globally installed CLI. This
project intentionally uses `devcontainer up` rather than `projects/build.sh`:
`build.sh` accepts project Dockerfiles and `Dockerfile.devEnv` files, but
explicitly rejects `.devcontainer/Dockerfile` images.

```bash
devcontainer up --workspace-folder projects/proj5_servercli
```

Open a shell inside the running container and activate the virtual environment
created by `uv`:

```bash
devcontainer exec --workspace-folder projects/proj5_servercli bash
```

```bash
source .venv/bin/activate
```

### Installing Dependencies

The first container creation runs the following command automatically through
`postCreateCommand`:

```bash
uv sync --group dev
```

Run the same command inside the container after changing `pyproject.toml` or
when the lockfile and environment need to be synchronized.

### Run the Project

With the container shell and `.venv` active, run the applied project:

```bash
server-cli --help
```

### Inspect the Environment

Run these commands inside the container to inspect its workspace, user,
interpreter, and Dev Container definition.

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
