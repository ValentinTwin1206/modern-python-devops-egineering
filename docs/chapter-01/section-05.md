# Python Dev Containers

This page explains how a Dev Container turns a Python project environment into a complete editor-backed development environment. The example uses the tiny Bottle web server together with the Karva test runner and the Ruff linter from the rest of Chapter 1. Step-by-step development workflow instructions live in the section README at [`README.md`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/README.md).

| Component            | Description                                      | Role in this section                                  |
| -------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| [Bottle](https://bottlepy.org/docs/dev/) | Lightweight Python web framework.              | Example application dependency and web server         |
| [Karva](https://matthewmckee4.github.io/karva/) | Python test runner written in Rust.            | Test runner used for the section test workflow        |
| [Ruff](https://docs.astral.sh/ruff/) | Fast Python linter and formatter.              | Linter used for the section code-quality checks       |
| [Dev Containers](https://containers.dev/) | Containerized development environment standard. | Editor-backed development boundary for this section   |

!!! info "`.devcontainer/` and `Dockerfile`"
	The `.devcontainer/` folder declares a Ubuntu base image with CPython, PyPy, `uv`, Nuitka, the build toolchain, the `vscode` user, forwarded ports, and a `postCreateCommand` that runs `uv sync --group dev`. The companion top-level `Dockerfile` is a Nuitka-based deployment image that ships a single self-contained executable.

## Dev Container boundary

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

## Image overview

The section ships two images. Each one has a different purpose.

| Path                          | Role                | When to use                                                                                  |
| ----------------------------- | ------------------- | -------------------------------------------------------------------------------------------- |
| `.devcontainer/Dockerfile`    | Development image   | Editor-backed development through VS Code Dev Containers or the Dev Containers CLI.          |
| `Dockerfile`                  | Deployment image    | Build a Nuitka-compiled standalone binary and run it in a slim runtime container.            |

## Container entrypoints

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

## Runtimes and tooling

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

## See also

- Virtual environment basics in [Section 02](section-02.md).
- Conda environments and non-Python dependencies in [Section 03](section-03.md).
- Pipenv lockfile workflow in [Section 04](section-04.md).
