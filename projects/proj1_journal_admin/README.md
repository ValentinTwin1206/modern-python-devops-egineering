# Journal Admin System Environment

This section demonstrates Python's system-level installation on Ubuntu and how packages reach the system, user, and admin install targets. It runs a small admin CLI, `journal-admin`, that reads recent `systemd` journal entries using the APT-only `python3-systemd` binding.

For background, full filesystem layout, install-target tradeoffs, and inspection commands, see the [MkDocs page](../../docs/chapter-01/section-01.md).

## Project Components

The table below lists the main files that support the system-environment example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image defines a safe environment for inspecting Python installation targets. It mirrors the package-installation layers discussed below without modifying the host machine, and includes `python3-systemd`, `uv`, and the Debian packaging tools needed to build the local `.deb` package. |
| [pyproject.toml](pyproject.toml) | This file holds the Python project metadata for the `journal-admin` CLI. It declares no PyPI runtime dependencies because the only runtime requirement, `systemd.journal`, comes from the APT package `python3-systemd`. |
| [debian/](debian/) | This directory contains the minimal Debian packaging files for building a local `.deb` package. The package ships the prebuilt project wheel under `/opt/journal_admin`, installs it into the system Python interpreter from a `postinst` script, and registers a `journal-admin.service` systemd unit. |

## Required Developer Tools

- Docker or Podman.
- A Linux host or Linux VM (for the on-host path). The host needs `systemd` if you want to read real journal entries.
- `uv` for the project workflow and for building the wheel.
- Debian packaging tools: `build-essential`, `devscripts`, and `debhelper`.

### With Docker

The development image already includes Python, `uv`, `python3-systemd`, `build-essential`, `devscripts`, `debhelper`, Karva, and Ruff.

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
sudo apt-get install -y build-essential devscripts debhelper
```

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Usage Guide

Install the local Debian package with APT. Run this command from the directory that contains `journal-admin_1.0.0-1_all.deb`:

```bash
sudo apt install ./journal-admin_1.0.0-1_all.deb
```

After the package is installed, use the `journal-admin` command to show recent journal entries:

```bash
journal-admin --since-minutes 15
```

Filter entries for a specific systemd unit:

```bash
journal-admin --unit ssh.service --priority 6
```

Emit JSON when another tool needs structured output:

```bash
journal-admin --since-minutes 30 --format json
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

The project is shipped as a Debian package that bundles the prebuilt project wheel under `/opt/journal_admin/`. A `postinst` script installs that wheel into the system Python interpreter through `pip`, and `dh_installsystemd` registers the bundled [journal-admin.service](debian/journal-admin.service) unit so the CLI can be run on demand under journald.

Build the project wheel into the local `dist/` directory:

```bash
uv build --wheel
```

The wheel is written to:

```text
dist/journal_admin-1.0.0-py3-none-any.whl
```

Build a binary `.deb` package from the project root. `debian/journal-admin.install` picks up the wheel from `dist/` and places it under `/opt/journal_admin/` inside the package:

```bash
dpkg-buildpackage -us -uc -b
```

The `-b` flag builds the binary package only and writes the artifact to the parent directory:

```text
../journal-admin_1.0.0-1_all.deb
```

Install the package with APT so runtime dependencies, including `python3-systemd` and `python3-pip`, are resolved through the operating system package manager:

```bash
sudo apt install ../journal-admin_1.0.0-1_all.deb
```

During `configure`, the `postinst` script runs `python3 -m pip install --break-system-packages /opt/journal_admin/journal_admin-*.whl`. The console script lands at `/usr/local/bin/journal-admin` and the package is importable as `journal_admin` from the system interpreter.

Check the files installed by the package and by `pip`:

```bash
dpkg -L journal-admin
```

```bash
python3 -m pip show --files journal-admin
```

Run the installed CLI directly:

```bash
journal-admin --since-minutes 15
```

Trigger the bundled systemd service to record the last hour of entries through journald under the `journal-admin.service` unit:

```bash
sudo systemctl start journal-admin.service
```

Check the unit's recent runs:

```bash
journalctl -u journal-admin.service --since "1 hour ago"
```

Remove the package again when you are done experimenting. The `prerm` script first uninstalls the wheel from the system interpreter, then `dpkg` cleans up `/opt/journal_admin/`:

```bash
sudo apt remove journal-admin
```
