# Pixelpack

This section introduces *Pixelpack* as a small Pillow-based image-processing CLI that demonstrates how a Python Dev Container alongside `uv` and the `nuitka` build toolchain, and how the project can be packaged as a distributable Debian package.

## Project Components

The table below lists the main files that support the Dev Container example project.

| Component | Description |
| --------- | ----------- |
| [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) | This file is the entry point for the Dev Container setup. It defines workspace behavior, lifecycle hooks, extensions, and the remote user. |
| [.devcontainer/Dockerfile](.devcontainer/Dockerfile) | This development image builds the environment that VS Code opens. It installs the Pillow system libraries, the Nuitka compiler toolchain, and the Debian packaging tools needed to build the local `.deb` package before the editor attaches. |
| [pyproject.toml](pyproject.toml) | This file defines the project metadata and dependencies that `uv sync --group dev` installs inside the Dev Container. It ties the editor setup back to the Python packaging configuration of the project. |
| [debian/](debian/) | This directory contains the minimal Debian packaging files for building a local `.deb` package. The package ships the prebuilt Nuitka binary at `/usr/bin/pixelpack`. |

## End-User Guide

This section shows how an end user installs and runs `pixelpack` as a standalone Linux binary.

### Requirements

- A compatible Linux host for the compiled `pixelpack` binary.
- Input image files the `pixelpack` CLI can read.

### Installation

Install the Debian package with APT. Run this command from the project directory after building the package:

```bash
sudo apt install ./.build/pixelpack_1.0.0-1_amd64.deb
```

### Usage

Show the available commands:

```bash
pixelpack --help
```

Resize an image:

```bash
pixelpack resize input.png output.png --width 320 --height 240
```

Convert an image format (inferred from the destination suffix):

```bash
pixelpack convert input.png output.jpg
```

Convert an image to grayscale:

```bash
pixelpack grayscale input.png output.png
```

## Developer Guide

The project workflow runs inside the Dev Container image because Pillow needs system image libraries, Nuitka needs a native compiler toolchain, and the Debian package build requires the standard Debian packaging tools.

### Setup Environment

Install the Dev Container CLI on the host if you want to build and enter the same environment outside VS Code:

```bash
sudo apt-get update && sudo apt-get install -y nodejs npm
```

Next, install the DevContainer CLI via `npm`:

```bash
sudo npm install -g @devcontainers/cli
```

From the project directory, start the Dev Container workspace:

```bash
devcontainer up --workspace-folder .
```

Open an interactive shell in that container:

```bash
devcontainer exec --workspace-folder . bash
```

### Sync Environment

The Dev Container runs `uv sync --group dev` automatically through `postCreateCommand`. If you change dependencies later, resync them manually inside the container:

```bash
uv sync --group dev
```

### Run Tests

Within the running container, you can run the test suite with Karva:

```bash
PYTHONPATH=src uv run karva test tests/
```

### Lint

Within the running container, you can run Ruff against the source tree:

```bash
uv run ruff check .
```

### Build Guide

Run the build commands below from a shell opened with `devcontainer exec --workspace-folder . bash`. Files written inside the project directory remain available on the host because the workspace is bind-mounted into the Dev Container.

#### Build the Binary

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

The binary is written to `dist/pixelpack`. Run it directly to confirm that the compiled CLI starts correctly:

```bash
./dist/pixelpack --help
```

#### Build the Debian Package

Build the Debian package from the project root:

```bash
dpkg-buildpackage -us -uc -b
```

Move the resulting package into a project-local artifact directory so it is easy to install from the host:

```bash
mkdir -p .build && mv ../pixelpack_1.0.0-1_amd64.deb .build/
```

The end-user package artifact is now available on the host at:

```text
.build/pixelpack_1.0.0-1_amd64.deb
```
