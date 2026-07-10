# Python Binaries

Python binaries package a Python application into an executable form for users who may not manage Python environments directly. They are useful for command-line tools that need simple installation and predictable startup behavior.

## Applied Project

### Project Setup

The applied project is a small image-processing CLI called `Pixelpack Project`. It is built on [Pillow](https://pillow.readthedocs.io/) and [Click](https://click.palletsprojects.com/), with [Nuitka](https://nuitka.net/) for native compilation. This makes it a good fit for Dev Containers because the project depends on a reproducible operating-system-level toolchain, not just isolated Python packages.

### Run the Project

Application, test, lint, container startup, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj5_pixelpack/README.md).

## Distribution Fundamentals

### Overview

Python binary distributions are created using specialized packaging tools that transform Python applications into standalone executables. Unlike wheel distributions, which require a Python interpreter on the target system, binaries package the application together with its runtime dependencies.

* ✅ command-line applications
* ✅ desktop applications
* ✅ internal business tools
* ✅ software distributed to non-Python users

### Binary Packaging Ecosystem

Python binary packaging differs from Python package distribution because the generated artifacts are operating-system-specific.

The most common packaging tools are:

| Tool        | Description |
|-------------|-------------|
| PyInstaller | Bundles Python applications and dependencies into a standalone executable. It focuses on portability and ease of use |
| Nuitka | Compiles Python code to C/C++ and produces native executables. It focuses on native compilation and potential runtime performance improvements |

> In many production environments, the generated executable is further packaged into an [operating-system-level installer](./section-02.md).

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

### Package Layout

The result of a Python binary build is usually a single platform-specific standalone executable file that users can run directly without installing a separate Python environment. Unlike installer packages such as `.msi`, `.deb`, or `.rpm`, this binary distribution typically does not include additional installation files.

Examples:

```text
pixelpack.exe
pixelpack
```

## Packaging Workflow

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
devcontainer exec --workspace-folder proj5_pixelpack bash
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

### Validate the Binary

After building the executable, verify that:

* the application starts successfully
* command-line arguments work as expected
* all required resources are included
* the executable runs on a clean target system

For example:

```bash
./pixelpack --help
```

### Publish the Binary

Once a binary build passes validation, upload it to the proprietary raw repository hosted on Cloudsmith.

!!! info
    This workflow assumes that a Cloudsmith Raw repository already exists and that you already have a Cloudsmith API key available for the container session.

For a managed download endpoint, upload the compiled binary to a Cloudsmith Raw repository.

Inside the container, define the API key before uploading the binary.

```bash
export CLOUDSMITH_API_KEY="<your-api-key>"
```

Upload the Linux or Windows binary to the target raw repository and assign a release version.

```bash
cloudsmith push raw "${CLOUDSMITH_NAMESPACE}/${CLOUDSMITH_REPOSITORY}" ./dist/pixelpack --name pixelpack --version 1.0.0
```

```powershell
cloudsmith push raw pravi-brothers/modern-python-engineering .\dist\pixelpack.exe --name pixelpack.exe --version 1.0.0
```

After the upload finishes, Cloudsmith serves the binary through a stable download URL that you can share in release notes, internal portals, or installation scripts.

```text
https://dl.cloudsmith.io/public/pravi-brothers/modern-python-engineering/raw/versions/1.0.0/pixelpack
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
