# Python Binaries

Python binaries package a Python application into an executable form for users who may not manage Python environments directly. They are useful for command-line tools that need simple installation and predictable startup behavior.

## Applied Project

### Project Setup

The applied project is a small server administration CLI called `Server CLI`. It is built on [Click](https://click.palletsprojects.com/), with [Nuitka](https://nuitka.net/) for native compilation and Debian packaging for APT installation. This makes it a good fit for Dev Containers because the project depends on a reproducible operating-system-level toolchain, not just isolated Python packages.

### Run the Project

Application, test, lint, container startup, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_servercli/README.md).

## Building Blocks

### Overview

Python binary distributions transform an application into a platform-specific executable that can run without a separately managed Python environment. Packaging tools bundle or compile the application together with the interpreter and required dependencies, producing an ELF binary on Linux, a PE executable on Windows, or a Mach-O binary on macOS. Standalone binaries are typically used for command-line applications, desktop software, internal business tools, and utilities distributed to users who do not manage Python installations.

Binary distribution connects four building blocks: the executable carries the runnable payload, packaging configuration controls how the artifact is assembled and identifies its release, a delivery mechanism places it on the target system, and a remote repository hosts versioned downloads. A standalone executable does not require a dedicated package manager, although projects often wrap it in an [operating-system package](./section-02/index.md) when managed installation and upgrades are required.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Stores native machine code or a bundled Python runtime and application payload for one target platform. | ELF executable, Windows PE `.exe`, macOS Mach-O executable |
| Maintainer / Metadata File | Configures included modules, resources, entry points, version information, and build behavior. | PyInstaller `.spec`, Nuitka settings in `pyproject.toml` |
| Package Manager | Delivers or installs the executable; no dedicated manager is required for direct downloads. | Direct download, `curl`, optional OS package manager |
| Remote Repository | Hosts versioned binaries and checksums for users or automation to download. | GitHub Releases, Cloudsmith Raw, object storage |

### Project Layout

A typical Python binary project is structured to separate application code, packaging configuration, and operating-system-specific packaging metadata:

```text
{project_root}/
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
├── tests/
└── uv.lock
```

* `src/`: Contains the application source code.
* `tests/`: Contains automated tests.
* `pyproject.toml`: The central configuration file for modern Python packaging, defining metadata, dependencies, and build configuration.
* `uv.lock`: Dependency lock file used to reproduce builds.
* `README.md`: Project documentation and usage instructions.
* `LICENSE`: Defines the legal terms under which the project can be used and distributed.

### Build Configuration

`Server CLI` does not use a separate binary manifest file. The project metadata lives in `pyproject.toml`, while the packaging workflow passes Nuitka build flags on the command line. Nuitka is installed by the Dev Container Dockerfile as a platform-specific build tool and is intentionally not listed in the project dependency metadata.

```toml
[project]
name = "server-cli"
version = "1.0.0"
description = "Click server administration CLI distributed as a Nuitka-compiled Debian executable"
authors = [
    { name = "Julius Pravtchev" },
    { name = "Valentin Pravtchev" }
]
license = "Apache-2.0"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1.7",
]

[project.scripts]
server-cli = "server_cli.cli:main"

[dependency-groups]
dev = [
    "karva>=0.0.1a5",
    "ruff>=0.15.12",
]

[tool.uv]
package = true

```

- `[project]`: Defines the application identity, Python version support, and runtime dependencies that the build command installs into the build environment.
- `[dependency-groups]`: Records development-only testing and linting tools.
- `[tool.uv]`: Marks that `uv` should install the project into the development environment.
- Binary build options are kept in `scripts/build-executable.sh` so Nuitka remains a container-level build tool rather than a project dependency.

!!! note
    This project intentionally keeps Nuitka out of `pyproject.toml`; the Dev Container installs it with `uv tool install nuitka`.

### Package Layout

A standalone executable is a native binary rather than a general-purpose archive. Linux commonly uses the ELF format, while Windows uses PE/COFF. Both formats divide the file into headers and sections that the operating-system loader uses to map code and data into memory. Thus, unlike `.whl`, `.deb`, or `.conda` packages, an executable does not have one portable internal directory layout.

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container shell.

Install the Dev Container CLI on the host first.

```bash
sudo apt-get update && sudo apt-get install -y nodejs npm
sudo npm install -g @devcontainers/cli
```

From the `projects/` directory, start the dedicated development container.

```bash
devcontainer up --workspace-folder proj5_servercli
```

Open a shell in the running development container.

```bash
devcontainer exec --workspace-folder proj5_servercli \
    --remote-env CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" \
    --remote-env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY" \
    bash
```

The Dev Container image already includes Nuitka, the native compiler toolchain,
and Debian packaging tools. Nuitka is available as the `nuitka` command but is
not installed through the project's Python dependency metadata.

### Create the Binary

Build the executable.

=== "Nuitka"

    ```bash
    nuitka \
        --onefile \
        --output-dir=.build \
        --output-filename=server-cli \
        --include-package=server_cli \
        src/server_cli/cli.py
    ```

The resulting executable is written to the build output directory.

### Inspect The Package

A Linux standalone executable is an ELF binary, while a Windows executable (`.exe`) uses the PE/COFF format. These files are not archives like wheels, Debian packages, or Conda packages; inspection focuses on the executable header, linked shared libraries, embedded runtime behavior, and file identity.

Identify the executable file format and target architecture.

```bash
file .build/server-cli
```

Inspect the ELF header, including the binary class, machine architecture, entry point, and program-header layout.

```bash
readelf -h .build/server-cli
```

List the shared libraries the executable expects from the target system.

```bash
ldd .build/server-cli
```

Generate a checksum that can be published with the binary so consumers can verify the downloaded artifact.

```bash
sha256sum .build/server-cli
```

### Publish the Binary

Once you have inspected the binary build, upload it to the proprietary raw repository hosted on Cloudsmith.

For a managed download endpoint, upload the compiled binary to a Cloudsmith Raw repository.

Upload the Linux or Windows binary to the target raw repository and assign a release version.

```bash
cloudsmith push raw "${CLOUDSMITH_REPOSITORY}" ./.build/server-cli --name server-cli --version 1.0.0
```

```powershell
cloudsmith push raw "$env:CLOUDSMITH_REPOSITORY" .\.build\server-cli.exe --name server-cli.exe --version 1.0.0
```

After the upload finishes, Cloudsmith serves the binary through a stable download URL that you can share in release notes, internal portals, or installation scripts.

```text
https://dl.cloudsmith.io/public/<cloudsmith-repo>/raw/versions/1.0.0/server-cli
```

## Consumer Workflow

### Install the Binary

Users typically install the binary by downloading the appropriate release artifact and execute it:

=== "Linux executable"

    ```bash
    chmod +x server-cli && ./server-cli --help
    ```

=== "Windows executable"

    ```powershell
    .\server-cli.exe --help
    ```
