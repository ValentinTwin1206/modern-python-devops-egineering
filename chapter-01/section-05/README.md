# Pixelpack Dev Containers

This section demonstrates a VS Code Dev Container with CPython, PyPy, `uv`, and the Nuitka build toolchain, plus a Nuitka-based deployment image that ships a single self-contained binary. The sample project, `pixelpack`, is a small Pillow-based image-processing CLI. Pillow links against system image libraries and Nuitka invokes the native compiler, which is exactly the situation a Dev Container is designed for.

For background on Dev Containers, the image overview, and VS Code integration details, see the [MkDocs page](../../docs/chapter-01/section-05.md).

## Required Developer Tools

- Docker or Podman.
- VS Code with the Dev Containers extension, or Node.js with the Dev Containers CLI.
- `uv` for project commands inside the container.

### With Docker

Build the deployment image through the chapter helper:

```bash
../build.sh build --path section-05/Dockerfile --build-only
```

Run the Nuitka deployment image through the helper:

```bash
../build.sh build --path section-05/Dockerfile
```

The deployment image runs a Nuitka-compiled standalone executable that exposes the `pixelpack` CLI.

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

Run the CLI from inside the Dev Container:

```bash
uv run pixelpack --help
```

Resize an image:

```bash
uv run pixelpack resize input.png output.png --width 320 --height 240
```

Convert an image format (inferred from the destination suffix):

```bash
uv run pixelpack convert input.png output.jpg
```

Convert an image to grayscale:

```bash
uv run pixelpack grayscale input.png output.png
```

Run the Nuitka deployment image directly:

```bash
docker run --rm -v "$PWD":/data -w /data pixelpack-nuitka resize input.png output.png --width 320 --height 240
```

## Development Guide

Sync the development environment:

```bash
uv sync --group dev
```

Run the tests:

```bash
uv run karva test tests/
```

Run the linter:

```bash
uv run ruff check .
```

Build the project wheel:

```bash
uv build --wheel
```

Build the Nuitka deployment image:

```bash
docker build -t pixelpack-nuitka .
```
