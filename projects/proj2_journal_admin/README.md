# Simply Journal Admin

*Simply Journal Admin* is a cross-platform administration CLI that reads recent
log entries from the host operating system and presents them through a unified
command-line interface. The project is distributed as native Debian (`.deb`) and
Windows (`.msi`) packages that install into isolated Python virtual
environments.

## Project Components

The table below lists the main files and directories that make up the project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | Linux development image containing `uv`, `python3-systemd`, Debian packaging tools, and the project's development dependencies. |
| [Dockerfile.windows](Dockerfile.windows) | Windows build image containing Python, `uv`, WiX Toolset, NSSM, Git, and Visual C++ build tools required for MSI generation. |
| [pyproject.toml](pyproject.toml) | Defines package metadata, dependencies, console entry points, and build configuration. |
| [src/simply_journal_admin/](src/simply_journal_admin/) | Cross-platform journal administration CLI implementation. |
| [tests/](tests/) | Automated test suite covering CLI behavior and platform abstractions. |
| [debian/](debian/) | Debian packaging metadata, maintainer scripts, and the optional systemd service definition. |
| [msi/](msi/) | WiX sources, PowerShell build scripts, MSI custom actions, and Windows service integration files. |

## End-User Guide

This section shows how an end user installs and operates *Simply Journal Admin*
through the supported operating-system packages.

### Requirements

#### Linux

- Debian-based Linux distribution.
- Python 3.12 or newer.
- `python3-systemd`.

#### Windows

- Windows 10 or newer.
- Python 3.12 or newer.
- Permission to read the Windows Event Log.

### Installation

#### Linux (Debian-based)

Install the generated package:

```bash
sudo apt install ./simply-journal-admin_<version>_all.deb
```

#### Windows

Install the generated MSI package:

```powershell
msiexec /i simply-journal-admin-<version>.msi
```

### Usage

Read entries from the last hour:

```bash
simply-journal-admin --since-minutes 60
```

Output JSON:

```bash
simply-journal-admin --format json
```

Filter by severity:

```bash
simply-journal-admin --priority 4
```

Linux-specific unit filtering:

```bash
simply-journal-admin --unit ssh.service
```

Windows-specific channel selection:

```bash
simply-journal-admin --log-name Application
```

Write output to a file:

```bash
simply-journal-admin \
    --since-minutes 120 \
    --format json \
    --output-file report.json
```

## Developer Guide

### Linux Development Environment

The Linux development environment is provided by
[Dockerfile.devEnv](Dockerfile.devEnv).

#### Setup Environment

Use the shared helper script from the parent `projects/` directory to build the
development image and open an interactive shell:

```bash
../build.sh build --path proj2_journal_admin/Dockerfile.devEnv
```

The helper automatically:

* Builds the container image.
* Opens an interactive Bash shell.
* Bind-mounts the project directory into the container.
* Bind-mounts the project's `.build/` directory to `/build` for build artifacts.

#### Sync Environment

Inside the container, synchronize all dependency groups:

```bash
uv sync --all-groups
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

#### Run Tests

Run the automated test suite:

```bash
uv run karva test tests/
```

#### Lint

Run Ruff against the source tree:

```bash
uv run ruff check .
```

#### Build Debian Package

The Debian package embeds the generated Python wheel inside a `.deb` package.

Build the wheel artifact:

```bash
uv build --wheel --out-dir /build
```

The generated wheel appears on the host inside:

```text
.build/simply_journal_admin-<version>-py3-none-any.whl
```

Build the Debian package:

```bash
dpkg-buildpackage -us -uc -b
```

### Windows MSI Build Environment

The Windows build environment is provided by
[Dockerfile.windows](Dockerfile.windows).

> Requires Docker Desktop [configured for Windows containers](https://docs.docker.com/desktop/setup/install/windows-install/#system-requirements).

#### Setup Environment

Build the Windows build image:

```powershell
docker build -f Dockerfile.windows -t sja-msi-builder .
```

> **Note:** The initial build may take a long time because several large Windows and development tool dependencies must be downloaded and installed.

Create the artifact directory if it does not already exist:

```powershell
New-Item -ItemType Directory -Path .build -Force
```

Open an interactive PowerShell session:

```powershell
docker run --rm -it -v "$($PWD.ProviderPath):C:\workspace" -v "$($PWD.ProviderPath)\.build:C:\build" sja-msi-builder
```

> **Note:** The following command must be run from the Windows filesystem (`C:\`); otherwise, the bind mounts will fail.

#### Build MSI Package

The Windows installer embeds the generated Python wheel inside an `.msi` package.

Build the wheel:

```powershell
uv build --wheel --out-dir C:\build\wheel
```

Build the MSI:

```powershell
powershell -ExecutionPolicy Bypass -File .\msi\scripts\build-msi.ps1 -WheelDir C:\build\wheel -OutDir C:\build
```

The generated installer appears on the host inside:

```text
.build\simply-journal-admin-<version>.msi
```
