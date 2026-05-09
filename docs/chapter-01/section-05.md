# Python `Dev Containers`

This page explains how a Dev Container turns a Python project environment into a complete editor-backed development environment.

## Tiny Webserver Project

The example uses the tiny Bottle web server project. Step-by-step development workflow instructions live in the section README at [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/README.md).

### Used DevTools

These tools cover the example application's runtime package, development utilities, and the Dev Container tooling used in this section.

| Component            | Description |
| -------------------- | ----------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Bottle is the example application dependency used inside the containerized development setup. It provides a simple web service that makes the Dev Container workflow easy to inspect. |
| [Karva](https://matthewmckee4.github.io/karva/) | Karva is the test runner used in the project workflow. It demonstrates how development tools can be provisioned automatically inside the Dev Container. |
| [Ruff](https://docs.astral.sh/ruff/) | Ruff is the linter and formatter used for code-quality checks. It is part of the development toolchain that the container prepares for the editor-backed environment. |
| [Dev Containers](https://containers.dev/) | Dev Containers are the main topic of this section. They expand the isolation boundary from Python packages to an entire editor-integrated development machine. |

### Project Files

These project files show how the editor-integrated container is configured and how it differs from the separate deployment image.

| Component            | Description |
| -------------------- | ----------- |
| [`.devcontainer/devcontainer.json`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/.devcontainer/devcontainer.json) | This file is the entry point for the Dev Container setup. It defines workspace behavior, lifecycle hooks, extensions, forwarded ports, and the remote user. |
| [`.devcontainer/Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/.devcontainer/Dockerfile) | This development image builds the environment that VS Code opens. It installs runtimes, system packages, and tools such as `uv` and Nuitka before the editor attaches. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/Dockerfile) | This separate deployment image builds and runs the Nuitka-based executable. It helps distinguish the interactive development container from the production-oriented runtime image. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/pyproject.toml) | This file defines the project metadata and dependencies that `uv sync --group dev` installs inside the container. It ties the editor setup back to the Python packaging configuration of the project. |

## Install `Dev Container`

Dev Containers are not bundled with Python. They require container tooling and either VS Code's Dev Containers extension or the Dev Containers CLI.

=== "VS Code"

	Install the Dev Containers extension in VS Code.

	After that, open the section folder and reopen it in the container from the editor.

=== "Dev Containers CLI"

	Install the Dev Containers CLI with npm:

	```bash
	npm install -g @devcontainers/cli
	```

## `Dev Container` environment model

A virtual environment isolates Python packages. A Dev Container declares the operating system image, system packages, language runtimes, editor extensions, forwarded ports, lifecycle hooks, workspace mount, user account, and project setup commands. The boundary moves from one `site-packages` directory to the entire development machine.

### Environment scope

| Aspect                  | Virtual environment                | Dev Container                                         |
| ----------------------- | ---------------------------------- | ----------------------------------------------------- |
| Boundary                | Interpreter and packages           | Container plus editor integration                     |
| System packages         | Inherited from host                | Declared in image or Dev Container features           |
| Python implementations  | Usually one                        | CPython, PyPy, and others side by side                |
| Editor setup            | Configured per host                | Declared in `devcontainer.json`                       |
| Ports and services      | Manual host setup                  | Forwarded in container config                         |
| Lifecycle commands      | Manual shell commands              | `postCreateCommand` and related hooks                 |
| Reproducibility scope   | Python dependencies                | OS, tools, runtimes, editor extensions, and project   |

### Image overview

The section ships two images. Each one has a different purpose.

| Path                          | Role                | When to use                                                                                  |
| ----------------------------- | ------------------- | -------------------------------------------------------------------------------------------- |
| `.devcontainer/Dockerfile`    | Development image   | Editor-backed development through VS Code Dev Containers or the Dev Containers CLI.          |
| `Dockerfile`                  | Deployment image    | Build a Nuitka-compiled standalone binary and run it in a slim runtime container.            |

### Container entrypoints

The `.devcontainer/devcontainer.json` file is the contract between VS Code and the container. It declares the base image, the workspace mount, the remote user, the lifecycle commands, the extensions to install, and the ports to forward. Opening the section folder and running `Dev Containers: Reopen in Container` launches the container, mounts the workspace under `/workspaces/`, runs `postCreateCommand`, and attaches VS Code to the container.

The remote user is `vscode`, which matches the user created inside the image. Mounted source files are owned by that user, so terminal commands and editor saves operate on the same files. Port `8080` is forwarded automatically, which makes the Bottle endpoint reachable from the host browser.

=== "VS Code"

	Open the section in VS Code:

	```bash
	code chapter-01/section-05
	```

=== "Dev Containers CLI"

	Drive the same setup from a shell with the Dev Containers CLI:

	```bash
	npx @devcontainers/cli up --workspace-folder chapter-01/section-05
	```

Install the Dev Containers CLI globally instead:

```bash
npm install -g @devcontainers/cli
```

### Runtimes and tooling

The Dev Container installs both CPython and PyPy from APT. PyPy is a separate Python implementation with a JIT compiler. Installing it next to CPython makes interpreter comparisons easy without changing the host machine.

The Bottle project uses `uv` for the project workflow. The `postCreateCommand` setting runs `uv sync --group dev` after VS Code mounts the workspace, so the project environment is created against the real source tree rather than against an image-time copy.

| Tool or runtime | Role in this section                                                   |
| --------------- | ---------------------------------------------------------------------- |
| CPython         | Default interpreter for the project workflow                           |
| PyPy            | Alternate interpreter for side-by-side inspection and comparison       |
| `uv`            | Project dependency sync, command execution, and build workflow         |
| Nuitka          | Produces the standalone deployment binary                              |

## Workflow

### Development workflow

Run the Bottle application:

```bash
uv run tiny-webserver
```

Run the tests:

```bash
uv run karva test tests/
```

Run the linter:

```bash
uv run ruff check .
```

### Build and deployment workflow

Build the project wheel:

```bash
uv build --wheel
```

Build the Nuitka deployment image:

```bash
docker build -t tiny-webserver-nuitka .
```

Run the deployment image:

```bash
docker run --rm -p 8080:8080 tiny-webserver-nuitka
```

The deployment runtime starts a standalone Nuitka-compiled executable. It does not install the project wheel.

### Runtime inspection

Check PyPy alongside CPython:

```bash
pypy3 -c "import sys; print(sys.implementation.name); print(sys.executable)"
```

## Inspection

Show the workspace location inside the container:

```bash
pwd
```

Show the default CPython interpreter:

```bash
which python3
```

Show the Python that `uv` selected for the project environment:

```bash
uv run python -c "import sys; print(sys.executable); print(sys.version)"
```

Verify the forwarded endpoint from the host:

```bash
curl http://localhost:8080/
```

Expected response:

```json
{"message": "Hello from tiny webserver"}
```

## Tradeoffs

### Pros

- ✅ Captures the operating system, tools, editor integration, and project setup in one reproducible boundary.
- ✅ Keeps host machine dependencies to a minimum while still giving a full development environment.
- ✅ Makes multi-runtime setups such as CPython plus PyPy straightforward.

### Cons

- ⚠️ Heavier than plain `venv`, Conda, or Pipenv workflows because the boundary is an entire containerized machine.
- ⚠️ Depends on container tooling and editor integration, which adds setup overhead.
- ⚠️ Build, startup, and image maintenance costs are higher than interpreter-only workflows.
