# Python Binaries

Python binaries package a Python application into an executable form for users who may not manage Python environments directly. They are useful for command-line tools that need simple installation and predictable startup behavior.

## Applied Project

### Project Setup

The applied project is a small image-processing CLI called `Pixelpack Project`. It is built on [Pillow](https://pillow.readthedocs.io/) and [Click](https://click.palletsprojects.com/), with [Nuitka](https://nuitka.net/) for native compilation. This makes it a good fit for Dev Containers because the project depends on a reproducible operating-system-level toolchain, not just isolated Python packages.

### Run the Project

Application, test, lint, container startup, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_pixelpack/README.md).

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

`Pixelpack` does not use a separate binary manifest file. The project metadata lives in `pyproject.toml`, while the packaging workflow passes Nuitka build flags on the command line. The configuration below shows the real project manifest and commented placeholders for binary-specific options that teams may choose to move into project-local configuration.

```toml
[project]
name = "pixelpack"
version = "1.0.0"
description = "Pillow + Click image-processing CLI distributed as a Nuitka-compiled standalone binary"
authors = [
    { name = "Julius Pravtchev" },
    { name = "Valentin Pravtchev" }
]
license = "Apache-2.0"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1.7",
    "pillow>=10.4.0",
]

[dependency-groups]
dev = [
    "karva>=0.0.1a5",
    "nuitka>=2.4",
    "ruff>=0.15.12",
]

[tool.uv]
package = false

# Optional project-local binary-build settings could be tracked separately.
# [tool.nuitka]
# onefile = true
# output-dir = "dist"
# output-filename = "pixelpack"
# include-package = ["PIL", "click"]
```

- `[project]`: Defines the application identity, Python version support, and runtime dependencies that the build command installs into the build environment.
- `[dependency-groups]`: Records development-only tooling such as Nuitka and Ruff.
- `[tool.uv]`: Marks that `uv` should manage the environment but not treat the project itself as a wheel-built package.
- `[tool.nuitka]`: Illustrates where a team could centralize additional binary-build settings if it wanted to move them out of the CLI invocation.

!!! note
    Nuitka can store project options in `pyproject.toml`. Chapter 04 covers [`pyproject.toml` project configuration](../chapter-04/section-01.md) in more detail.

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
devcontainer up --workspace-folder proj5_pixelpack
```

Open a shell in the running development container.

```bash
devcontainer exec --workspace-folder proj5_pixelpack \
    --remote-env CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" \
    --remote-env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY" \
    bash
```

The Dev Container image already includes the binary build tooling, including PyInstaller, Nuitka, and the Cloudsmith CLI.

### Create the Binary

Build the executable.

=== "PyInstaller"

    ```bash
    pyinstaller --onefile src/pixelpack/cli.py
    ```

=== "Nuitka"

    ```bash
    python -m nuitka \
        --onefile \
        --standalone \
        src/pixelpack/cli.py
    ```

The resulting executable is written to the build output directory.

### Inspect The Package

A Linux standalone executable is an ELF binary, while a Windows executable (`.exe`) uses the PE/COFF format. These files are not archives like wheels, Debian packages, or Conda packages; inspection focuses on the executable header, linked shared libraries, embedded runtime behavior, and file identity.

Identify the executable file format and target architecture.

```bash
file dist/pixelpack
```

Inspect the ELF header, including the binary class, machine architecture, entry point, and program-header layout.

```bash
readelf -h dist/pixelpack
```

List the shared libraries the executable expects from the target system.

```bash
ldd dist/pixelpack
```

Generate a checksum that can be published with the binary so consumers can verify the downloaded artifact.

```bash
sha256sum dist/pixelpack
```

### Publish the Binary

Once you have inspected the binary build, upload it to the proprietary raw repository hosted on Cloudsmith.

For a managed download endpoint, upload the compiled binary to a Cloudsmith Raw repository.

Upload the Linux or Windows binary to the target raw repository and assign a release version.

```bash
cloudsmith push raw "${CLOUDSMITH_REPOSITORY}" ./dist/pixelpack --name pixelpack --version 1.0.0
```

```powershell
cloudsmith push raw "$env:CLOUDSMITH_REPOSITORY" .\dist\pixelpack.exe --name pixelpack.exe --version 1.0.0
```

After the upload finishes, Cloudsmith serves the binary through a stable download URL that you can share in release notes, internal portals, or installation scripts.

```text
https://dl.cloudsmith.io/public/<cloudsmith-repo>/raw/versions/1.0.0/pixelpack
```

## Consumer Workflow

### Install the Binary

Users typically install the binary by downloading the appropriate release artifact and execute it:

=== "Linux executable"

    ```bash
    chmod +x pixelpack && ./pixelpack --help
    ```

=== "Windows executable"

    ```powershell
    .\pixelpack.exe --help
    ```
