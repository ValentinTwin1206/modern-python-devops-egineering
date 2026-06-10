# simply_journal_admin System Environment

This section demonstrates Python's system-level installation on Ubuntu and how packages reach the system, user, and admin install targets. It runs a small admin CLI, `simply-journal-admin`, that reads recent `systemd` journal entries using the APT-only `python3-systemd` binding.

## Project Components

The tree below shows the main project layout. The `.build/` directory is created during the build workflow and stores generated artifacts.

```text
proj1_journal_admin/
|-- .build/
|   |-- simply_journal_admin-1.0.0-py3-none-any.whl
|   `-- simply-journal-admin_1.0.0-1_all.deb
|-- debian/
|-- src/
|-- tests/
|-- Dockerfile.devEnv
|-- pyproject.toml
|-- README.md
`-- uv.lock
```

The table below lists the main files that support the system-environment example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image defines a safe environment for inspecting Python installation targets. It mirrors the package-installation layers discussed below without modifying the host machine, and includes `python3-systemd`, `uv`, and the Debian packaging tools needed to build the local `.deb` package. |
| [pyproject.toml](pyproject.toml) | This file holds the Python project metadata for the `simply-journal-admin` CLI. It declares no PyPI runtime dependencies because the only runtime requirement, `systemd.journal`, comes from the APT package `python3-systemd`. |
| [debian/](debian/) | This directory contains the minimal Debian packaging files for building a local `.deb` package. The package ships the prebuilt project wheel under `/opt/simply_journal_admin`, installs it into the system Python interpreter from a `postinst` script, and registers a `simply-journal-admin.service` systemd unit. |

## System Requirements

- A Debian-based Linux host or Linux VM with `systemd` and access to the journal entries you want to inspect.
- APT, so the local `.deb` package can resolve and install `python3`, `python3-pip`, and `python3-systemd`.
- Administrator privileges for installing the package and starting the optional `simply-journal-admin.service` unit.

## Installation

Install the local Debian package with APT. Run this command from the project directory after building the package:

```bash
sudo apt install ./.build/simply-journal-admin_1.0.0-1_all.deb
```

## Uninstallation

Remove the package again when you are done experimenting:

```bash
sudo apt remove simply-journal-admin
```

## Usage Guide

After the package is installed, use the `simply-journal-admin` command to show recent journal entries:

```bash
simply-journal-admin --since-minutes 15
```

Filter entries for a specific systemd unit:

```bash
simply-journal-admin --unit ssh.service --priority 6
```

Emit JSON when another tool needs structured output:

```bash
simply-journal-admin --since-minutes 30 --format json
```

Run the bundled systemd service when you want the tool to execute under journald:

```bash
sudo systemctl start simply-journal-admin.service
```

Inspect the service output:

```bash
journalctl -u simply-journal-admin.service --since "1 hour ago"
```

## Development Guide

The project workflow uses a `uv`-managed virtual environment for testing and linting, but the runtime story always points back to the system interpreter.

### With Docker

The [Dockerfile.devEnv](Dockerfile.devEnv) contains all required development tools. Build artifacts are stored on the host in `.build/`. Open an interactive shell in the development image through the projects helper:

```bash
../build.sh build --path proj1_journal_admin/Dockerfile.devEnv
```

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

The project is shipped as a Debian package that bundles the prebuilt project wheel under `/opt/simply_journal_admin/`. A `postinst` script installs that wheel into the system Python interpreter through `pip`, and `dh_installsystemd` registers the bundled [simply-journal-admin.service](debian/simply-journal-admin.service) unit so the CLI can be run on demand under journald.

#### Build Environment

Run the build commands from the shell opened by the [development image](Dockerfile.devEnv). The projects helper bind-mounts the local `.build/` directory at `/build`, so artifacts written to `/build` inside the container are available on the host under `.build/`.

#### Build Wheel

Build the project wheel into the mounted artifact directory:

```bash
uv build --wheel --out-dir /build
```

The wheel is written inside the container to `/build` and appears on the host at:

```text
.build/simply_journal_admin-1.0.0-py3-none-any.whl
```

#### Build Debian Package

Build a binary `.deb` package from the project root. `debian/simply-journal-admin.install` picks up the wheel from `.build/` and places it under `/opt/simply_journal_admin/` inside the package:

```bash
dpkg-buildpackage -us -uc -b
```

The `-b` flag builds the binary package only. Move the resulting package into the mounted artifact directory so it appears beside the wheel on the host:

```bash
mv ../simply-journal-admin_1.0.0-1_all.deb /build/
```

#### Package Artifact

The end-user package artifact is now available on the host at:

```text
.build/simply-journal-admin_1.0.0-1_all.deb
```

