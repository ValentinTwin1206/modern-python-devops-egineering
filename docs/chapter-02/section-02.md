# Debian Packages

Debian packages distribute applications as `.deb` archives that APT can discover, verify, install, upgrade, and remove. This section packages a compiled IrisLab CLI executable so users can install and run the command without managing Python themselves.

## Applied Project

The applied project is `IrisLab CLI`, an interactive command-line client for the IrisLab API that logs in through Keycloak in the browser. It is built on [Click](https://click.palletsprojects.com/) and [Requests](https://requests.readthedocs.io/), with [Nuitka](https://nuitka.net/) for native compilation and Debian packaging for APT installation. This makes it a good fit for Dev Containers because the project depends on a reproducible operating-system-level toolchain, not just isolated Python packages.

This design separates two concerns: Nuitka creates the runnable application artifact, while Debian packaging supplies installation metadata, filesystem placement, dependency tracking, upgrades, and removal through APT.

## Building Blocks

Debian packages are AR-based `.deb` artifacts used by Debian, Ubuntu, and related Linux distributions. A package combines an installable filesystem payload with metadata that describes its identity, architecture, dependencies, and lifecycle. They are commonly used for system utilities and command-line applications that should be installed and maintained by the operating system.

| Building Block | Role | IrisLab CLI Example |
|----------------|------|--------------------|
| Package Format | Stores the generated metadata and installable filesystem payload. | `.deb` |
| Maintainer Files | Define package identity, dependencies, build rules, installed paths, and release history. | `debian/control`, `debian/rules`, `debian/changelog` |
| Package Manager | Resolves dependencies, installs files, and records package state. | `apt`, `dpkg` |
| Remote Repository | Publishes `.deb` artifacts and signed indexes consumed by APT. | Debian repository, Cloudsmith |

### Project Layout

The project keeps executable-build scripts and Debian maintainer files next to the Python source:

```text
proj4_irislab_cli/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── debian/
│   ├── source/
│   │   └── format
│   ├── changelog
│   ├── control
│   ├── rules
│   └── irislab-cli.links
├── scripts/
│   ├── build-deb.sh
│   └── build-executable.sh
├── src/irislab_cli/
├── pyproject.toml
└── uv.lock
```

- `.devcontainer/`: Provides Python, `uv`, Nuitka, the native compiler, binary-inspection tools, and Debian packaging tools.
- `scripts/build-executable.sh`: Compiles the Linux `irislab-cli` executable with Nuitka.
- `scripts/build-deb.sh`: Copies the project and compiled executable to an isolated directory before invoking `dpkg-buildpackage`.
- `debian/control`: Defines source and binary package metadata and runtime dependencies.
- `debian/rules`: Installs the compiled executable into the package staging tree.
- `debian/irislab-cli.links`: Creates `/usr/bin/irislab-cli` as a link to the packaged executable.

### Package Manifest

The `debian/control` file defines the package identity, build requirements, runtime dependencies, and description:

```text
Source: irislab-cli
Section: utils
Priority: optional
Maintainer: Modern Python Engineering <maintainers@example.invalid>
Build-Depends: debhelper-compat (= 13)
Standards-Version: 4.7.0
Rules-Requires-Root: no
Homepage: https://github.com/ValentinTwin1206/modern-python-devops-egineering

Package: irislab-cli
Architecture: any
Depends:
 ${misc:Depends},
 ${shlibs:Depends}
Description: interactive command-line client for the IrisLab API
 irislab-cli is a Click-based interactive client for the IrisLab API. It logs
 in through Keycloak in the browser and uploads eye images for analysis.
 The Debian package contains a standalone Nuitka executable and does not need
 a Python interpreter or network access to install.
```

- `Architecture: any` means the build produces an architecture-specific package.
- `${shlibs:Depends}` contains dependencies Debhelper calculates from the compiled executable.
- `${misc:Depends}` contains dependencies required by other Debhelper features.
- `Python` is not a package dependency because Nuitka's one-file output contains the application and its Python runtime components.

### Package Layout

A `.deb` file is an AR archive containing a format marker, generated control information, and a filesystem payload:

```text
irislab-cli_0.0.1-1_amd64.deb
├── debian-binary
├── control.tar.*
│   ├── control
│   └── md5sums
└── data.tar.*
    └── usr/
        ├── bin/
        │   └── irislab-cli -> /usr/lib/irislab-cli/irislab-cli
        └── lib/
            └── irislab-cli/
                └── irislab-cli
```

The executable is built for the target operating system and architecture. It must therefore be compiled in an environment compatible with the Debian systems where the package will run.

### Python Binaries

Python binary tools turn an application and its dependencies into a platform-specific executable. They inspect imports, collect the Python runtime and required modules, and produce an artifact that users can launch without first creating a virtual environment or installing the project with `pip`. The output must be built separately for Linux, Windows, and each supported processor architecture.

=== "PyInstaller"

    PyInstaller bundles the Python interpreter, application bytecode, imported packages, and resources. It focuses on reliably collecting an application into a folder or one executable; it does not translate the complete program into native C code.

    An equivalent one-file build of IrisLab CLI would use:

    ```bash
    uv run pyinstaller \
        --onefile \
        --name irislab-cli \
        --paths src \
        src/irislab_cli/cli.py
    ```

=== "Nuitka"

    Nuitka translates Python modules to C and compiles them with a native compiler. Like PyInstaller, it follows imports and includes the runtime components needed by the application, but its compilation stage produces native machine code. IrisLab CLI uses Nuitka through its build script:

    ```bash
    ./scripts/build-executable.sh
    ```

    The script runs the following compilation command:

    ```bash
    nuitka \
        --onefile \
        --output-dir=.build \
        --output-filename=irislab-cli \
        --include-package=irislab_cli \
        src/irislab_cli/cli.py
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

### Create the Environment

Install the Dev Container CLI on the Linux host if it is not already available:

```bash
sudo apt-get update && sudo apt-get install -y nodejs npm
sudo npm install -g @devcontainers/cli
```

From the `projects/` directory, start the project Dev Container:

```bash
devcontainer up --workspace-folder proj4_irislab_cli
```

Open a shell in the container:

```bash
devcontainer exec --workspace-folder proj4_irislab_cli bash
```

The Dev Container image already provides the build tools, so no manual installation is needed:

- `debhelper`: Provides tools for building Debian packages.
- `dpkg-dev`: Provides low-level Debian package development tools.
- `devscripts`: Provides scripts for Debian package maintenance and release tasks.
- `nuitka`: Compiles the Python application into a standalone executable.

Inside the container, synchronize the project environment with `uv`:

```bash
uv sync --group dev
```

### Create the Package

Before building version `0.0.2`, update the version declarations in these files. Debian takes the package version from `debian/changelog`; `debian/control` contains package metadata but does not set the version.

| File | Version change |
|------|----------------|
| [`pyproject.toml`](../../projects/proj4_irislab_cli/pyproject.toml) | Set `[project].version` to `0.0.2`. |
| [`__init__.py`](../../projects/proj4_irislab_cli/src/irislab_cli/__init__.py) | Set `__version__` to `0.0.2`. |
| [`debian/changelog`](../../projects/proj4_irislab_cli/debian/changelog) | Set the Debian package version to `0.0.2-1`. |
| [`debian/control`](../../projects/proj4_irislab_cli/debian/control) | No version change; this file contains package metadata. |

Inside the Dev Container, compile the executable:

```bash
./scripts/build-executable.sh
```

Confirm that the compiled command starts:

```bash
./.build/irislab-cli --help
```

Build the Debian package from that executable:

```bash
./scripts/build-deb.sh
```

The resulting package is written to `.build/irislab-cli_0.0.2-1_amd64.deb` for an AMD64 build.

### Inspect the Package

List the three top-level members of the Debian archive:

```bash
ar t .build/irislab-cli_0.0.2-1_amd64.deb
```

Inspect package metadata and generated dependencies:

```bash
dpkg -I .build/irislab-cli_0.0.2-1_amd64.deb
```

List the filesystem payload:

```bash
dpkg -c .build/irislab-cli_0.0.2-1_amd64.deb
```

### Publish the Package (Optional)

!!! info "Upload To Cloudsmith"
    Uploading to Cloudsmith is optional and requires a valid Cloudsmith account. You can build and inspect the artifacts locally without a Cloudsmith account or API key. The project's Dev Container provides the tools needed for packaging and mounts the local project directory, so IDE changes are available inside the container immediately.

Before uploading, set the repository slug and enter your API key in the Dev Container shell. The key is hidden while you type:

```bash
export CLOUDSMITH_REPOSITORY="<owner>/<repository>"
read -rsp "Cloudsmith API key: " CLOUDSMITH_API_KEY
printf '\n'
export CLOUDSMITH_API_KEY
```

Install the Cloudsmith CLI inside the container before uploading:

```bash
uv tool install cloudsmith-cli
```

Cloudsmith stores the uploaded `.deb`, extracts its control metadata, and generates signed repository indexes for APT. Upload the package for Ubuntu 24.04:

```bash
cloudsmith push deb "${CLOUDSMITH_REPOSITORY}/ubuntu/noble" \
    .build/irislab-cli_0.0.2-1_amd64.deb
```

Verify that it was indexed:

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "irislab-cli"
```

## Consumer Workflow

### Install the Package

Import the repository signing key:

```bash
curl -fsSL "https://dl.cloudsmith.io/public/<cloudsmith-repo>/gpg.key" \
    | sudo gpg --dearmor -o /usr/share/keyrings/cloudsmith-repository.gpg
```

APT uses repositories to find software packages. Create a configuration file that tells APT where the Cloudsmith packages are, which Ubuntu release and package group to use, and which key to use to verify them:

```bash
printf 'Types: deb\nURIs: https://dl.cloudsmith.io/public/<cloudsmith-repo>/deb/ubuntu\nSuites: noble\nComponents: main\nSigned-By: /usr/share/keyrings/cloudsmith-repository.gpg\n' \
    | sudo tee /etc/apt/sources.list.d/cloudsmith.sources
```

Next, refresh APT's package lists so it can find packages from the new repository:

```bash
sudo apt update
```

Install IrisLab CLI:

```bash
sudo apt install irislab-cli
```

### Use the Package

Run IrisLab CLI:

```bash
irislab-cli --help
```

Running `irislab-cli` without arguments opens the Keycloak login in the browser and then starts the interactive `iris>` session. The required environment variables are listed in the project README.

To inspect which files belong to the installed package, use `dpkg`:

```bash
dpkg -L irislab-cli
```

## Useful Links

- [Debian Policy Manual](https://www.debian.org/doc/debian-policy/)
- [Nuitka User Manual](https://nuitka.net/user-documentation/user-manual.html)
- [Cloudsmith Debian Repository Documentation](https://help.cloudsmith.io/docs/debian-repository/)
