# Journal Admin System Environment

This section demonstrates Python's system-level installation on Ubuntu and how packages reach the system, user, and admin install targets. It runs a small admin CLI, `journal-admin`, that reads recent `systemd` journal entries using the APT-only `python3-systemd` binding.

For background, full filesystem layout, install-target tradeoffs, and inspection commands, see the [MkDocs page](../../docs/chapter-01/section-01.md).

## Project Components

The table below lists the main files that support the system-environment example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image defines a safe environment for inspecting Python installation targets. It mirrors the package-installation layers discussed below without modifying the host machine, and installs `python3-systemd` so the `journal_admin` package can be imported. |
| [pyproject.toml](pyproject.toml) | This file holds the Python project metadata for the `journal-admin` CLI. It declares no PyPI runtime dependencies because the only runtime requirement, `systemd.journal`, comes from the APT package `python3-systemd`. |
| [debian/](debian/) | This directory contains the minimal Debian packaging files for building a local `.deb` package. The package installs the Python module into the system interpreter, exposes `/usr/bin/journal-admin`, and declares `python3-systemd` as an APT dependency. |

## Required Developer Tools

- Docker or Podman.
- A Linux host or Linux VM (for the on-host path). The host needs `systemd` if you want to read real journal entries.
- `uv` for the project workflow.
- `pip3` for user-level installs.
- Debian packaging tools: `build-essential`, `devscripts`, `debhelper`, `dh-python`, and `python3-all`.

### With Docker

Build the development image through the projects helper:

```bash
../build.sh build --path proj1_journal_admin/Dockerfile.devEnv --build-only
```

Open an interactive shell in the development image:

```bash
../build.sh build --path proj1_journal_admin/Dockerfile.devEnv
```

### On Host

Install Python, pip, and the systemd binding from APT:

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-systemd
```

Install the Debian package build tools:

```bash
sudo apt-get install -y build-essential devscripts debhelper dh-python python3-all
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

### Sync Environment

Sync the project environment with `uv`:

```bash
uv sync
```

### Run Tests

Run the test suite with Karva:

```bash
uv run karva test tests/
```

### Lint

Run Ruff against the source tree:

```bash
uv run ruff check .
```

### Build Guide

The Debian package configuration lives in [debian/](debian/). It uses `debhelper` and `dh-python` directly instead of building through `uv`, because this project is meant to install into the system Python environment and use the APT-managed `python3-systemd` binding.

Build a binary `.deb` package from the project root:

```bash
dpkg-buildpackage -us -uc -b
```

The `-b` flag builds the binary package only. That keeps this local project workflow simple and writes the package artifact to the parent directory:

```text
../journal-admin_1.0.0-1_all.deb
```

Install the package with APT so runtime dependencies, including `python3-systemd`, are resolved through the operating system package manager:

```bash
sudo apt install ../journal-admin_1.0.0-1_all.deb
```

Check the files installed by the package:

```bash
dpkg -L journal-admin
```

Run the installed CLI:

```bash
journal-admin --since-minutes 15
```

Remove the package again when you are done experimenting:

```bash
sudo apt remove journal-admin
```
