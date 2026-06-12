# Simply Journal Admin

This section introduces *Simply Journal Admin* project as a simple Python CLI that demonstrates how to use Python's (Linux) system environment for development, and how the project can be packaged as a distributable Debian package.

## Project Components

The table below lists the main files that support the system-environment example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image defines a safe environment for inspecting Python installation targets. It mirrors the package-installation layers discussed below without modifying the host machine, and includes `python3-systemd`, `uv`, the Debian packaging tools, one system-level dev tool, and one user-level dev tool. |
| [pyproject.toml](pyproject.toml) | This file holds the Python project metadata for the `simply-journal-admin` CLI. It declares no PyPI runtime dependencies because the only runtime requirement, `systemd.journal`, comes from the APT package `python3-systemd`. |
| [debian/](debian/) | This directory contains the minimal Debian packaging files for building a local `.deb` package. The package ships the prebuilt project wheel under `/opt/simply_journal_admin`, installs it into the system Python interpreter from a `postinst` script, and registers a `simply-journal-admin.service` systemd unit. |

## End-User Guide

This section shows how an end user installs and runs `simply-journal-admin` as a Debian package on a systemd-based Linux system.

### Requirements

- A Debian-based Linux host or Linux VM with `systemd` and access to the journal entries you want to inspect.
- APT, so the local `.deb` package can resolve and install `python3`, `python3-pip`, and `python3-systemd`.
- Administrator privileges for installing the package and starting the optional `simply-journal-admin.service` unit.

### Installation

Install the local Debian package with APT. Run this command from the project directory after building the package:

```bash
sudo apt install ./.build/simply-journal-admin_1.0.0-1_all.deb
```

Then start the bundled *SystemD* service:

```bash
sudo systemctl start simply-journal-admin.service
```

### Uninstallation

Remove the package again when you are done experimenting:

```bash
sudo apt remove simply-journal-admin
```

### Usage

After the package is installed, use the `simply-journal-admin` command to show recent journal entries:

```bash
simply-journal-admin --since-minutes 30 --format json
```

Optionally, you can also use `journalctl` to inspect the service output:

```bash
journalctl -u simply-journal-admin.service --since "1 hour ago"
```

## Developer Guide

### Setup Environment

The [Dockerfile.devEnv](Dockerfile.devEnv) contains all required development tools. It combines multiple Python installation targets in one image while using `uv` as a fast, pip-compatible layer for traditional `pip install` workflows. Build artifacts are stored on the host in `.build/`. Open an interactive shell in the development image through the projects helper:

```bash
../build.sh build --path proj2_journal_admin/Dockerfile.devEnv
```

### Sync Environment

The development image installs the Python tools into the system interpreter, so they are already available on `PATH` when the shell starts. No additional environment activation or profile sourcing is required.

### Run Tests

Within the running container, you can run the test suite with Karva:

```bash
karva test tests/
```

### Lint

Within the running container, you can run Ruff against the source tree:

```bash
ruff check .
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

