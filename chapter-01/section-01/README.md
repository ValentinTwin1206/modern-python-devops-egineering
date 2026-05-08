# Tiny Webserver System Environment

This section demonstrates Python's system-level installation on Ubuntu and how packages reach the system, user, and admin install targets. It runs a tiny Bottle web server installed straight into the system Python.

For background, full filesystem layout, install-target tradeoffs, and inspection commands, see the [MkDocs page](../../docs/chapter-01/section-01.md).

## Required Developer Tools

- Docker or Podman.
- A Linux host or Linux VM (for the on-host path).
- `uv` for the project workflow.
- `pip3` for user-level installs.

### With Docker

Build the development image through the chapter helper:

```bash
../build.sh build --path section-01/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path section-01/Dockerfile.devEnv
```

Build and run the deployment image:

```bash
../build.sh build --path section-01/Dockerfile
```

### On Host

Install Python and pip from APT:

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-pip
```

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install Bottle into the system Python:

```bash
uv pip install --system --break-system-packages bottle
```

Install user-level developer tools:

```bash
pip3 install --user karva ruff
```

## Usage Guide

Run the Bottle application directly with the system Python:

```bash
python3 -m tiny_webserver.app
```

Inspect the active import path:

```bash
python3 -c "import sys; [print(p) for p in sys.path]"
```

Inspect where a system package lives:

```bash
python3 -c "import bottle; print(bottle.__file__)"
```

## Development Guide

Sync the project environment with `uv`:

```bash
uv sync
```

Run the tests:

```bash
uv run karva test tests/
```

Run the linter:

```bash
uv run ruff check .
```

Build a wheel:

```bash
uv build --wheel
```
