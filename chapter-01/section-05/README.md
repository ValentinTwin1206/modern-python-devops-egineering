# Tiny Webserver Dev Containers

This section demonstrates a VS Code Dev Container with CPython, PyPy, `uv`, and the Nuitka build toolchain, plus a Nuitka-based deployment image that ships a single self-contained binary.

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

The deployment image runs a Nuitka-compiled standalone executable on port `8080`.

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

Run the Bottle application from inside the Dev Container:

```bash
uv run tiny-webserver
```

Verify the forwarded endpoint from the host:

```bash
curl http://localhost:8080/
```

Run the Nuitka deployment image directly:

```bash
docker run --rm -p 8080:8080 tiny-webserver-nuitka
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
docker build -t tiny-webserver-nuitka .
```
