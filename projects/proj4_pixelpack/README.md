# Pixelpack Dev Containers

This section demonstrates a VS Code Dev Container with CPython, PyPy, `uv`, and the Nuitka build toolchain. The sample project, `pixelpack`, is a small Pillow-based image-processing CLI. Pillow links against system image libraries and Nuitka invokes the native compiler to produce a self-contained binary, which is exactly the situation a Dev Container is designed for.

For background on Dev Containers, the image overview, and VS Code integration details, see the [MkDocs page](../../docs/chapter-01/section-04.md).

## Project Components

The table below lists the main files that support the Dev Container example project.

| Component | Description |
| --------- | ----------- |
| [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) | This file is the entry point for the Dev Container setup. It defines workspace behavior, lifecycle hooks, extensions, and the remote user. |
| [.devcontainer/Dockerfile](.devcontainer/Dockerfile) | This development image builds the environment that VS Code opens. It installs runtimes, the C toolchain, Pillow's system image libraries, and tools such as `uv` and Nuitka before the editor attaches. |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This standalone development image installs the system libraries Pillow needs, the C toolchain Nuitka requires, and all Python dependencies through `uv sync --group dev`. It opens an interactive shell so you can explore the project and run tools manually without modifying the host machine. |
| [pyproject.toml](pyproject.toml) | This file defines the project metadata and dependencies that `uv sync --group dev` installs inside the container. It ties the editor setup back to the Python packaging configuration of the project. |

## Required Developer Tools

- Docker or Podman.
- VS Code with the Dev Containers extension, or Node.js with the Dev Containers CLI.
- `uv` for project commands inside the container.
- `nuitka` for compiling the project into a standalone binary.

### With Docker

Build the development image through the projects helper:

```bash
../build.sh build --path proj4_pixelpack/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path proj4_pixelpack/Dockerfile.devEnv
```

### On Host

Open the section in VS Code:

```bash
code .
```

Then run `Dev Containers: Reopen in Container` from the Command Palette.

Drive the same setup from a shell with `npx`:

```bash
npx @devcontainers/cli up --workspace-folder .
```

Install the Dev Containers CLI globally instead:

```bash
npm install -g @devcontainers/cli
```

## Usage Guide

Run the CLI from inside the Dev Container or the synced project environment:

```bash
PYTHONPATH=src uv run python -m pixelpack.cli --help
```

Resize an image:

```bash
PYTHONPATH=src uv run python -m pixelpack.cli resize input.png output.png --width 320 --height 240
```

Convert an image format (inferred from the destination suffix):

```bash
PYTHONPATH=src uv run python -m pixelpack.cli convert input.png output.jpg
```

Convert an image to grayscale:

```bash
PYTHONPATH=src uv run python -m pixelpack.cli grayscale input.png output.png
```

## Development Guide

### Sync Environment

Sync the project environment, including the `dev` group that provides Karva, Ruff, and Nuitka:

```bash
uv sync --group dev
```

### Run Tests

Run the test suite with Karva:

```bash
PYTHONPATH=src uv run karva test tests/
```

### Lint

Run Ruff against the source tree:

```bash
uv run ruff check .
```

### Build Guide

Pixelpack is compiled into a self-contained standalone binary using [Nuitka](https://nuitka.net). The resulting executable bundles the Python runtime and all dependencies, so the binary runs on any compatible Linux host without a Python installation.

Compile the `pixelpack` CLI into a single-file executable:

```bash
uv run python -m nuitka \
    --onefile \
    --output-dir=dist \
    --output-filename=pixelpack \
    --include-package=PIL \
    --include-package=click \
    src/pixelpack/cli.py
```

The binary is written to `dist/pixelpack`. Run it directly without activating any environment:

```bash
./dist/pixelpack --help
```
