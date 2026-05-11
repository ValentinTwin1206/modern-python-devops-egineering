# Python `Dev Containers`

This page explains how a Dev Container turns a Python project environment into a complete editor-backed development environment.

## Pixelpack Project

### Project Setup

The [Pixelpack Project](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/README.md) is a small image-processing CLI built on [Pillow](https://pillow.readthedocs.io/) and [Click](https://click.palletsprojects.com/), with [Karva](https://matthewmckee4.github.io/karva/) and [Ruff](https://docs.astral.sh/ruff/) as project tools, [Nuitka](https://nuitka.net/) for native compilation, and [Dev Containers](https://containers.dev/) hosting the build toolchain. Pillow links against system image libraries and Nuitka invokes the native compiler, which makes a Dev Container a much better fit than a plain virtual environment.

| Component            | Description |
| -------------------- | ----------- |
| [`.devcontainer/devcontainer.json`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/.devcontainer/devcontainer.json) | This file is the entry point for the Dev Container setup. It defines workspace behavior, lifecycle hooks, extensions, and the remote user. |
| [`.devcontainer/Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/.devcontainer/Dockerfile) | This development image builds the environment that VS Code opens. It installs runtimes, the C toolchain, Pillow's system image libraries, and tools such as `uv` and Nuitka before the editor attaches. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/Dockerfile) | This separate deployment image builds and runs the Nuitka-compiled binary. It helps distinguish the interactive development container from the production-oriented runtime image. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-05/pyproject.toml) | This file defines the project metadata and dependencies that `uv sync --group dev` installs inside the container. It ties the editor setup back to the Python packaging configuration of the project. |

## `Dev Container` environment model

Dev Containers emerged in VS Code workflows in 2019 to make full development machines reproducible, not just Python package sets. A virtual environment isolates Python packages, while a Dev Container declares the operating system image, system packages, language runtimes, editor extensions, lifecycle hooks, workspace mount, user account, and project setup commands. The boundary moves from one `site-packages` directory to the entire development machine.

### When to use `Dev Container`?

Because they reproduce the operating system, tools, editor integrations, and project setup in one definition, Dev Containers are a strong fit for projects that need more than Python package isolation. Examples include projects with native extensions that need a C toolchain and matching system libraries, compilation steps such as Nuitka or Cython, database clients, browser tooling, or multiple language runtimes. For small projects with only pure-Python dependencies, a plain `venv`, Pipenv, or Conda environment is usually faster to create and easier to maintain.

### Tradeoffs

#### Pros

- ✅ Captures the operating system, tools, editor integration, and project setup in one reproducible boundary.
- ✅ Keeps host machine dependencies to a minimum while still giving a full development environment.
- ✅ Makes native build toolchains and multi-runtime setups such as CPython plus PyPy straightforward.

#### Cons

- ⚠️ Heavier than plain `venv`, Conda, or Pipenv workflows because the boundary is an entire containerized machine.
- ⚠️ Depends on container tooling and editor integration, which adds setup overhead.
- ⚠️ Build, startup, and image maintenance costs are higher than interpreter-only workflows.

### Install `Dev Container`

Dev Containers are not bundled with Python. They require container tooling and either VS Code's Dev Containers extension or the Dev Containers CLI.

=== "VS Code"

	Install the Dev Containers extension in VS Code.

	After that, open the section folder and reopen it in the container from the editor.

=== "Dev Containers CLI"

	Install the Dev Containers CLI with npm:

	```bash
	npm install -g @devcontainers/cli
	```

### Environment scope

| Aspect                  | Virtual environment                | Dev Container                                         |
| ----------------------- | ---------------------------------- | ----------------------------------------------------- |
| Boundary                | Interpreter and packages           | Container plus editor integration                     |
| System packages         | Inherited from host                | Declared in image or Dev Container features           |
| Native build toolchain  | Inherited from host                | Declared in the image (`build-essential`, headers)    |
| Python implementations  | Usually one                        | CPython, PyPy, and others side by side                |
| Editor setup            | Configured per host                | Declared in `devcontainer.json`                       |
| Lifecycle commands      | Manual shell commands              | `postCreateCommand` and related hooks                 |
| Reproducibility scope   | Python dependencies                | OS, tools, runtimes, editor extensions, and project   |

### Image overview

The section ships two images. Each one has a different purpose.

| Path                          | Role                | When to use                                                                                  |
| ----------------------------- | ------------------- | -------------------------------------------------------------------------------------------- |
| `.devcontainer/Dockerfile`    | Development image   | Editor-backed development through VS Code Dev Containers or the Dev Containers CLI.          |
| `Dockerfile`                  | Deployment image    | Build a Nuitka-compiled standalone binary and run it in a slim runtime container.            |

### Container entrypoints

The `.devcontainer/devcontainer.json` file is the contract between VS Code and the container. It declares the base image, the workspace mount, the remote user, the lifecycle commands, and the extensions to install. Opening the section folder and running `Dev Containers: Reopen in Container` launches the container, mounts the workspace under `/workspaces/`, runs `postCreateCommand`, and attaches VS Code to the container.

The remote user is `vscode`, which matches the user created inside the image. Mounted source files are owned by that user, so terminal commands and editor saves operate on the same files.

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

The development image installs both CPython and PyPy from APT. PyPy is a separate Python implementation with a JIT compiler. Installing it next to CPython makes interpreter comparisons easy without changing the host machine.

The development image also installs `build-essential`, `python3-dev`, `patchelf`, and the system libraries Pillow links against (`libjpeg-dev`, `libpng-dev`, `zlib1g-dev`). Pillow needs those headers to build its native extension, and Nuitka needs the compiler and `patchelf` to produce the standalone binary.

The Pixelpack project uses `uv` for the project workflow. The `postCreateCommand` setting runs `uv sync --group dev` after VS Code mounts the workspace, so the project environment is created against the real source tree rather than against an image-time copy.

| Tool or runtime   | Role in this section                                              |
| ----------------- | ----------------------------------------------------------------- |
| CPython           | Default interpreter for the project workflow                      |
| PyPy              | Alternate interpreter for side-by-side inspection and comparison  |
| `uv`              | Project dependency sync, command execution, and build workflow    |
| C build toolchain | Builds Pillow's native extension and the Nuitka-compiled binary   |
| Nuitka            | Produces the standalone deployment binary                         |

## Workflow

### Development workflow

Run the CLI:

```bash
uv run pixelpack --help
```

Resize an image:

```bash
uv run pixelpack resize input.png output.png --width 320 --height 240
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
docker build -t pixelpack-nuitka .
```

Run the deployment image against a mounted directory:

```bash
docker run --rm -v "$PWD":/data -w /data pixelpack-nuitka resize input.png output.png --width 320 --height 240
```

The deployment runtime starts a standalone Nuitka-compiled executable. It does not install the project wheel and does not ship a Python interpreter for the application code.

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

Show the Pillow build that the project resolved:

```bash
uv run python -c "import PIL; print(PIL.__version__)"
```
