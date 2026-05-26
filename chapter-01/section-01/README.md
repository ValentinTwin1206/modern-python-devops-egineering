# Journal Admin System Environment

This section demonstrates Python's system-level installation on Ubuntu and how packages reach the system, user, and admin install targets. It runs a small admin CLI, `journal-admin`, that reads recent `systemd` journal entries using the APT-only `python3-systemd` binding.

For background, full filesystem layout, install-target tradeoffs, and inspection commands, see the [MkDocs page](../../docs/chapter-01/section-01.md).

## Project Components

The table below lists the main files that support the system-environment example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image defines a safe environment for inspecting Python installation targets. It mirrors the package-installation layers discussed below without modifying the host machine, and installs `python3-systemd` so the `journal_admin` package can be imported. |
| [Dockerfile](Dockerfile) | This deployment image shows the same system-level installation model in a runtime container. It uses Ubuntu so that `python3-systemd` stays available from APT, then installs the project wheel straight into the system interpreter. |
| [pyproject.toml](pyproject.toml) | This file holds the Python project metadata for the `journal-admin` CLI. It declares no PyPI runtime dependencies because the only runtime requirement, `systemd.journal`, comes from the APT package `python3-systemd`. |

## Required Developer Tools

- Docker or Podman.
- A Linux host or Linux VM (for the on-host path). The host needs `systemd` if you want to read real journal entries.
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

The deployment image needs the host journal to read real entries. Systemd does not need to be PID 1 inside the container, because `systemd.journal.Reader` opens the journal files directly through `libsystemd`. Mount the host journal directories and `machine-id` read-only when starting the container:

```bash
docker run --rm \
    -v /etc/machine-id:/etc/machine-id:ro \
    -v /var/log/journal:/var/log/journal:ro \
    -v /run/log/journal:/run/log/journal:ro \
    journal-admin --since-minutes 30
```

### On Host

Install Python, pip, and the systemd binding from APT:

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-systemd
```

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install user-level developer tools:

```bash
pip3 install --user karva ruff
```

## Usage Guide

Run the admin CLI directly with the system Python:

```bash
python3 -m journal_admin.cli --since-minutes 15
```

Filter by a specific systemd unit:

```bash
python3 -m journal_admin.cli --unit ssh.service --priority 6
```

Inspect the active import path:

```bash
python3 -c "import sys; [print(p) for p in sys.path]"
```

Inspect where the APT-managed binding lives:

```bash
python3 -c "import systemd.journal; print(systemd.journal.__file__)"
```

## Development Guide

The project workflow uses a `uv`-managed virtual environment for testing and linting, but the runtime story always points back to the system interpreter.

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
