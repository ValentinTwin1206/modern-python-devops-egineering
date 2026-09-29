# Python Dev Containers

This page explains how a Dev Container turns a Python project environment into a complete editor-backed development environment.

## Applied Project

### Project Setup

The applied project is a small server administration CLI called `Server CLI`. It is built on [Click](https://click.palletsprojects.com/), with [Nuitka](https://nuitka.net/) for native compilation and Debian packaging for APT installation. This makes it a good fit for Dev Containers because the project depends on a reproducible operating-system-level toolchain, not just isolated Python packages.

### Run the Project

Application, test, lint, container startup, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_servercli/README.md).

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

- ✅ Reproduces the operating system, tools, and project setup.
- ✅ Minimizes host machine dependencies.
- ✅ Simplifies native toolchains and multi-runtime setups.

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

The Dev Container environment is defined by a `.devcontainer/devcontainer.json` file and, when needed, a `Dockerfile`, Features, or Templates. The configuration describes how to build the image, mount the workspace, declare editor support, and prepare the development environment. The `devcontainer.json` file is the central configuration file that tells a compatible IDE or CLI how to build and start the development container. The CLI handles the container, Features, and lifecycle commands, while an IDE integration handles IDE-specific customizations such as extensions and plugins.

```json
{
	"name": "Python Dev Container",
	"build": {
		"dockerfile": "Dockerfile",
		"context": ".."
	},
	"workspaceFolder": "/workspaces/project",
	"runArgs": [
		"--name",
		"mpe-proj5_server_cli"
	],
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
	"postCreateCommand": "uv venv --clear && uv sync --group dev",
	"remoteUser": "bob"
}
```

- `name`: Gives the development environment a display name in compatible tools.
- `build`: Defines how to create the container image.
	- `dockerfile`: Selects the `Dockerfile`. Microsoft publishes [Dev Container base images](https://mcr.microsoft.com/en-us/catalog?search=devcontainers) for environments such as Python, JavaScript, and Rust. They provide a ready non-root user, common development tools, and editor integration.
	- `context`: Sets the files available during the image build, usually the project root.
- `workspaceFolder`: Sets the path where the project is opened inside the container.
- `customizations`: Declares IDE-specific configuration for integrations that support it. The `devcontainer` CLI does not install these extensions or plugins itself.
	- `vscode`:
		- `extensions`: Requests VS Code extensions such as Python, Pylance, and Ruff from the VS Code Dev Container integration.
		- `settings`: Applies VS Code settings, including the container's Python interpreter.
	- `jetbrains`:
		- `plugins`: Requests JetBrains plugins such as Python from the JetBrains Dev Container integration.
- `runArgs`: Passes Docker run arguments to the container. The `--name` argument gives the container the stable name `mpe-proj5_server_cli`.
- `postCreateCommand`: Clears any stale mounted environment, creates a project-local `.venv` with the Ubuntu system Python, and installs the project and development dependencies with the project interpreter after the workspace is mounted.
- `remoteUser`: Selects the user for terminals, tools, and lifecycle commands. This example uses `bob`, which is renamed from the base image's host-mapped `vscode` account. Renaming the existing account preserves its UID/GID, so lifecycle commands can modify files in the bind-mounted workspace.

##### Container image

The `Dockerfile` defines the content of the container image, such as preinstalled system tools, users, shells, and permissions, while `devcontainer.json` controls how the IDE integrates with that image and which lifecycle commands to run.

```dockerfile
# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - installs CPython build headers, uv, Nuitka, and Debian packaging tooling
#   - uses the base image's host-mapped UID/GID under the bob account
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive APT prompts during image build.
ENV DEBIAN_FRONTEND=noninteractive

# Put user-level tools installed by uv on PATH.
ENV PATH="/home/bob/.local/bin:${PATH}"

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
		sudo \
	&& rm -rf /var/lib/apt/lists/*

# Keep the base image's host-mapped UID/GID while using the project's bob name.
USER root
RUN usermod --login bob --home /home/bob --move-home vscode \
	&& groupmod --new-name bob vscode

# Install user-level tools as the same account the container uses.
USER bob

# Install Nuitka as a user-level uv tool. It is intentionally not a
# pyproject.toml dependency because it is a container build tool.
RUN uv tool install nuitka

# Keep the final image user aligned with devcontainer.json.
USER bob
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

- `postCreateCommand`: runs once after the container is created and the project has been mounted into `workspaceFolder`. It is typically used to create the project environment and install dependencies with commands such as `uv venv --clear && uv sync --group dev` or `npm install`.
- `postStartCommand`: runs each time the container starts, including later restarts. It is useful for repeatable startup tasks such as launching a local service or refreshing a development process.
- `postAttachCommand`: runs each time the IDE attaches to the running container, including later reconnects. It is useful for editor-session setup tasks that should happen after the development environment is ready for interaction.

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

### Create the Environment

Build the image with the stable tag `mpe/proj5_server_cli`:

```bash
devcontainer build \
    --workspace-folder projects/proj4_servercli \
	--image-name mpe/proj5_server_cli
```

Create the container from the Dev Container configuration:

```bash
devcontainer up	--workspace-folder projects/proj4_servercli
```

> `runArgs` inside `devcontainer.json` gives it the stable name `mpe-proj5_server_cli`

Open a `bash` shell inside the running container:

```bash
devcontainer exec --workspace-folder projects/proj4_servercli bash
```

Activate the automatically created `.venv` project environment:

```bash
source .venv/bin/activate
```

> See [*Create the Environment*](section-02.md#create-the-environment) in *Section 01* for creation of `.venv` by `uv`

### Add Additional Dependencies

Use the appropriate tab for Python dependencies or system tools.

=== "Python dependencies"

	Add a package to the project and synchronize the project environment that uses the Ubuntu system Python:

	```bash
	uv add package-name
	uv sync --group dev
	```

	Run `uv sync --group dev` after editing
	`pyproject.toml` or updating the lockfile.

=== "System tools"

	Install operating-system packages inside the container:

	```bash
	sudo apt-get update
	sudo apt-get install -y package-name
	```

	Use `apt` for compilers, libraries, and command-line tools rather than
	Python packages.

### Run the Project

With the container shell and `.venv` active, run the applied project:

```bash
server-cli --help
```

### Inspect the Environment

Run these commands inside the container to inspect its workspace, `bob` user,
system interpreter, project environment, and Dev Container definition.

Print the current workspace directory to confirm where the project is mounted:

```bash
pwd
```

Show the current user inside the container and confirm that the session runs as
`bob`:

```bash
whoami
```

Show the numeric user and group IDs used for bind-mounted workspace files:

```bash
id
```

Locate the system Python interpreter available in the container:

```bash
which python3
```

Confirm the system interpreter version:

```bash
python3 --version
```

Confirm that the project environment uses the system interpreter:

```bash
source .venv/bin/activate
python --version
python -c 'import sys; print(sys.executable); print(sys.implementation.name)'
uv run python -c 'import sys; print(sys.executable)'
```

Display the active Dev Container configuration from the mounted workspace:

```bash
cat .devcontainer/devcontainer.json
```
