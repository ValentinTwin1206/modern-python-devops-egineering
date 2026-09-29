# Debian Packages

Debian packages distribute applications as `.deb` archives that APT can discover, verify, install, upgrade, and remove. This section packages a compiled Server CLI executable so users can install and run the command without managing Python themselves.

## Applied Project

### Project Setup

The applied project is a small Click-based administration tool called `Server CLI`, exposed as the `server-cli` command. The project uses [Nuitka](https://nuitka.net/) to compile its Python modules and dependencies into a platform-specific executable. Its Debian package installs that executable under `/usr/lib/server-cli` and creates the public `/usr/bin/server-cli` link.

This design separates two concerns: Nuitka creates the runnable application artifact, while Debian packaging supplies installation metadata, filesystem placement, dependency tracking, upgrades, and removal through APT.

### Run the Project

Application, test, lint, executable-build, and Debian-package commands are documented in the [project README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_servercli/README.md).

## Building Blocks

Debian packages are AR-based `.deb` artifacts used by Debian, Ubuntu, and related Linux distributions. A package combines an installable filesystem payload with metadata that describes its identity, architecture, dependencies, and lifecycle. They are commonly used for system utilities and command-line applications that should be installed and maintained by the operating system.

| Building Block | Role | Server CLI Example |
|----------------|------|--------------------|
| Package Format | Stores the generated metadata and installable filesystem payload. | `.deb` |
| Maintainer Files | Define package identity, dependencies, build rules, installed paths, and release history. | `debian/control`, `debian/rules`, `debian/changelog` |
| Package Manager | Resolves dependencies, installs files, and records package state. | `apt`, `dpkg` |
| Remote Repository | Publishes `.deb` artifacts and signed indexes consumed by APT. | Debian repository, Cloudsmith |

### Project Layout

The project keeps executable-build scripts and Debian maintainer files next to the Python source:

```text
proj4_servercli/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── debian/
│   ├── source/
│   │   └── format
│   ├── changelog
│   ├── control
│   ├── rules
│   └── server-cli.links
├── scripts/
│   ├── build-deb.sh
│   └── build-executable.sh
├── src/server_cli/
├── pyproject.toml
└── uv.lock
```

- `.devcontainer/`: Provides Python, `uv`, Nuitka, the native compiler, binary-inspection tools, and Debian packaging tools.
- `scripts/build-executable.sh`: Compiles the Linux `server-cli` executable with Nuitka.
- `scripts/build-deb.sh`: Copies the project and compiled executable to an isolated directory before invoking `dpkg-buildpackage`.
- `debian/control`: Defines source and binary package metadata and runtime dependencies.
- `debian/rules`: Installs the compiled executable into the package staging tree.
- `debian/server-cli.links`: Creates `/usr/bin/server-cli` as a link to the packaged executable.

### Package Manifest

The `debian/control` file defines the package identity, build requirements, runtime dependencies, and description:

```text
Source: server-cli
Section: admin
Priority: optional
Maintainer: Modern Python Engineering <maintainers@example.invalid>
Build-Depends: debhelper-compat (= 13)
Standards-Version: 4.7.0
Rules-Requires-Root: no

Package: server-cli
Architecture: any
Depends:
 ${misc:Depends},
 ${shlibs:Depends}
Description: command-line client for a server API
 server-cli is a Click-based command-line client for server administration.
 The Debian package contains a standalone Nuitka executable and does not need
 a Python interpreter or network access to install.
```

`Architecture: any` means the build produces an architecture-specific package. Debhelper calculates `${shlibs:Depends}` from the compiled executable, while `${misc:Depends}` contains dependencies required by other Debhelper features. Python is not a package dependency because Nuitka's one-file output contains the application and its Python runtime components.

### Package Layout

A `.deb` file is an AR archive containing a format marker, generated control information, and a filesystem payload:

```text
server-cli_1.0.0-1_amd64.deb
├── debian-binary
├── control.tar.*
│   ├── control
│   └── md5sums
└── data.tar.*
    └── usr/
        ├── bin/
        │   └── server-cli -> /usr/lib/server-cli/server-cli
        └── lib/
            └── server-cli/
                └── server-cli
```

The executable is built for the target operating system and architecture. It must therefore be compiled in an environment compatible with the Debian systems where the package will run.

### Python Binaries

Python binary tools turn an application and its dependencies into a platform-specific executable. They inspect imports, collect the Python runtime and required modules, and produce an artifact that users can launch without first creating a virtual environment or installing the project with `pip`. The output must be built separately for Linux, Windows, and each supported processor architecture.

=== "PyInstaller"

    PyInstaller bundles the Python interpreter, application bytecode, imported packages, and resources. It focuses on reliably collecting an application into a folder or one executable; it does not translate the complete program into native C code.

    An equivalent one-file build of Server CLI would use:

    ```bash
    uv run pyinstaller \
        --onefile \
        --name server-cli \
        --paths src \
        src/server_cli/cli.py
    ```

=== "Nuitka"

    Nuitka translates Python modules to C and compiles them with a native compiler. Like PyInstaller, it follows imports and includes the runtime components needed by the application, but its compilation stage produces native machine code. Server CLI uses Nuitka through its build script:

    ```bash
    ./scripts/build-executable.sh
    ```

    The script runs the following compilation command:

    ```bash
    nuitka \
        --onefile \
        --output-dir=.build \
        --output-filename=server-cli \
        --include-package=server_cli \
        src/server_cli/cli.py
    ```

## Tradeoffs

### Pros

- ✅ Integrates with the OS lifecycle
- ✅ Manages system dependencies through APT
- ✅ Installs into standard system paths
- ✅ Supports signed package repositories

### Cons

- ⚠️ Stable releases may provide stale versions
- ⚠️ Limited to Debian-based systems
- ⚠️ Requires architecture-specific builds
- ⚠️ Packaging policies increase maintenance

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

### Create the Environment

Install the Dev Container CLI on the Linux host if it is not already available:

```bash
sudo apt-get update && sudo apt-get install -y nodejs npm
sudo npm install -g @devcontainers/cli
```

From the `projects/` directory, start the project Dev Container:

```bash
devcontainer up --workspace-folder proj4_servercli
```

Open a shell and pass the Cloudsmith configuration into the container:

```bash
devcontainer exec --workspace-folder proj4_servercli \
    --remote-env CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" \
    --remote-env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY" \
    bash
```

Inside the container, install the Debian packaging tools with APT:

```bash
sudo apt-get update
sudo apt-get install -y debhelper dpkg-dev devscripts
```

- `debhelper`: Provides tools for building Debian packages.
- `dpkg-dev`: Provides low-level Debian package development tools.
- `devscripts`: Provides scripts for Debian package maintenance and release tasks.

Then, synchronize the project environment and install the Python packaging tools with `uv`:

```bash
uv sync --group dev
uv tool install nuitka
uv tool install cloudsmith-cli
```

- `nuitka`: Compiles the Python application into a standalone executable.
- `cloudsmith-cli`: Uploads and manages packages in Cloudsmith repositories.

### Create the Package

Inside the Dev Container, compile the executable:

```bash
./scripts/build-executable.sh
```

Confirm that the compiled command starts:

```bash
./.build/server-cli --help
```

Build the Debian package from that executable:

```bash
./scripts/build-deb.sh
```

The resulting package is written to `.build/server-cli_1.0.0-1_amd64.deb` for an AMD64 build.

### Inspect the Package

List the three top-level members of the Debian archive:

```bash
ar t .build/server-cli_1.0.0-1_amd64.deb
```

Inspect package metadata and generated dependencies:

```bash
dpkg -I .build/server-cli_1.0.0-1_amd64.deb
```

List the filesystem payload:

```bash
dpkg -c .build/server-cli_1.0.0-1_amd64.deb
```

### Publish the Package

Cloudsmith stores the uploaded `.deb`, extracts its control metadata, and generates signed repository indexes for APT. Upload the package for Ubuntu 24.04:

```bash
cloudsmith push deb "${CLOUDSMITH_REPOSITORY}/ubuntu/noble" \
    .build/server-cli_1.0.0-1_amd64.deb
```

Verify that it was indexed:

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "server-cli"
```

## Consumer Workflow

### Configure the Package Manager

Import the repository signing key:

```bash
curl -fsSL "https://dl.cloudsmith.io/public/<cloudsmith-repo>/gpg.key" \
    | sudo gpg --dearmor -o /usr/share/keyrings/cloudsmith-repository.gpg
```

Add a deb822 repository source and refresh APT metadata:

```bash
printf 'Types: deb\nURIs: https://dl.cloudsmith.io/public/<cloudsmith-repo>/deb/ubuntu\nSuites: noble\nComponents: main\nSigned-By: /usr/share/keyrings/cloudsmith-repository.gpg\n' \
    | sudo tee /etc/apt/sources.list.d/cloudsmith.sources
sudo apt update
```

### Install the OS Package

Install and run Server CLI:

```bash
sudo apt install server-cli
server-cli --help
```

Ask `dpkg` which files belong to the package:

```bash
dpkg -L server-cli
```

## Useful Links

- [Debian Policy Manual](https://www.debian.org/doc/debian-policy/)
- [Nuitka User Manual](https://nuitka.net/user-documentation/user-manual.html)
- [Cloudsmith Debian Repository Documentation](https://help.cloudsmith.io/docs/debian-repository/)
