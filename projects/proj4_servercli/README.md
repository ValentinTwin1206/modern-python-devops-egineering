# Server CLI

Server CLI is a small Click-based command-line client for a future server API.
It demonstrates a modern Python development workflow that combines `uv`, a VS
Code Dev Container, Nuitka, Debian packaging, and Windows MSI packaging.

The current release provides the command structure for login and token
retrieval. Authentication and the server API request are intentionally not
implemented yet.

## Architecture

```mermaid
graph LR

    CLI[Click CLI] --> LOGIN[login]
    CLI --> TOKEN[get-token]

    LOGIN --> CREDENTIALS[Username and password]
    CREDENTIALS --> PROMPT[Interactive prompts for missing values]

    TOKEN --> API[Future server API request]
    API --> SHORT[Short-lived token]

    CLI --> NUITKA[Nuitka standalone executable]
    NUITKA --> DEB[Debian package]
    NUITKA --> MSI[Windows MSI package]
    DEB --> APT[APT installation]
    APT --> COMMAND[/usr/bin/server-cli]
    MSI --> WINGET[WinGet installation]
    WINGET --> EXE[server-cli.exe]
```

`login` accepts `--username` and `--password`. When either option is missing,
the command asks for that value interactively. Password input is hidden. The
collected credentials are not sent anywhere in this release.

`get-token` is the placeholder for a future request to the server API. That
request will eventually return a short-lived token.

## Project Structure

| Path | Purpose |
| --- | --- |
| `src/server_cli/` | Python package containing the Click CLI and package metadata |
| `tests/` | Minimal Karva tests for CLI behavior |
| `.devcontainer/` | VS Code Dev Container definition and build environment |
| `debian/` | Debian package metadata and installation layout |
| `msi/` | WiX product definition and PowerShell MSI build script |
| `Dockerfile.windows` | Windows Nuitka and MSI build environment |
| `scripts/build-executable.sh` | Linux Nuitka standalone executable build |
| `scripts/build-executable.ps1` | Windows Nuitka standalone executable build |
| `scripts/build-deb.sh` | Debian package build wrapper |
| `pyproject.toml` | Runtime and development dependency metadata |
| `uv.lock` | Locked Python dependencies |
| `.build/` | Host-visible executable and Debian build artifacts |

## Development Setup

The development container starts from Ubuntu 24.04 and installs the tools used
by the project workflow:

```text
Ubuntu 24.04
      |
      v
Ubuntu system Python and uv
      |
      +-- Click application dependencies
      +-- Karva and Ruff
      +-- Native compiler prerequisites
```

Nuitka, Debian packaging tools, and Cloudsmith CLI are installed during the
packaging workflow rather than in the image. They are not declared in
`pyproject.toml` because they are build or publication tools, not runtime or
test dependencies of the application.

Install the Dev Container CLI on the host if it is not already available:

```bash
sudo apt-get update && sudo apt-get install -y nodejs npm
sudo npm install -g @devcontainers/cli
```

Start the workspace from this project directory:

```bash
devcontainer up --workspace-folder .
```

Open a shell inside the running container:

```bash
devcontainer exec --workspace-folder . bash
```

The container creates its project environment with the system Python supplied
by Ubuntu 24.04 and then synchronizes the project dependencies into that
environment. The project environment is created with:

```bash
uv venv --clear
uv sync --group dev
```

Run the same command manually after changing dependencies.

## Run Server CLI

Show the available commands:

```bash
uv run server-cli --help
```

Provide both login values explicitly:

```bash
uv run server-cli login --username alice --password secret
```

Omit either value to provide it interactively:

```bash
uv run server-cli login
```

Request a token through the future API integration:

```bash
uv run server-cli get-token
```

The commands currently report that their authentication behavior is not
implemented. No credentials are persisted and no network requests are made.

## Run Tests

Run the minimal test suite with Karva:

```bash
uv run karva test tests/
```

The tests cover the root help output, explicit credentials, interactive
prompts, and the token command placeholder.

## Lint

Run Ruff against the project:

```bash
uv run ruff check .
```

## Build the Executable

Build the standalone Linux executable inside the Dev Container:

```bash
./scripts/build-executable.sh
```

The executable is written to `.build/server-cli`. Verify that the compiled
application starts and exposes its commands:

```bash
./.build/server-cli --help
./.build/server-cli login --help
./.build/server-cli get-token --help
```

The executable is platform- and architecture-specific. Build it in an
environment compatible with the Debian systems where it will be installed.

## Debian Package

The Debian package contains the compiled Nuitka executable directly. It does
not install a Python wheel, create a virtual environment, or require Python or
network access on the target host.

Build the Debian package after compiling the executable:

```bash
./scripts/build-deb.sh
```

The finished package is written to `.build/` with a name similar to:

```text
server-cli_1.0.0-1_amd64.deb
```

The package installs the executable and its public command link as follows:

```text
/usr/lib/server-cli/server-cli
/usr/bin/server-cli -> /usr/lib/server-cli/server-cli
```

## Install the Packaged Application

Install the locally built package with APT:

```bash
sudo apt install ./.build/server-cli_1.0.0-1_amd64.deb
```

Verify the installed command:

```bash
command -v server-cli
server-cli --help
```

The public command uses the conventional Debian and Unix hyphenated form
`server-cli`. No `server_cli` compatibility alias is installed.

## Windows Executable and MSI

Windows output must be built on a Windows container host. The build image
contains Python 3.12, `uv`, Nuitka, Visual C++ Build Tools, WiX Toolset v3, and
Cloudsmith CLI. Switch Docker Desktop to Windows containers before continuing:

```powershell
& "$Env:ProgramFiles\Docker\Docker\DockerCli.exe" -SwitchWindowsEngine
docker info --format "{{.OSType}}"
```

Build the image from the project directory and create the artifact directory:

```powershell
docker build -f Dockerfile.windows -t server-cli-msi-builder .
New-Item -ItemType Directory -Path .build -Force
```

Open a PowerShell session with the source and output directory mounted:

```powershell
docker run --rm -it `
    -v "$($PWD.ProviderPath):C:\workspace" `
    -v "$($PWD.ProviderPath)\.build:C:\workspace\.build" `
    server-cli-msi-builder
```

Synchronize the project and compile the Windows executable inside the
container:

```powershell
uv sync --group dev
powershell -ExecutionPolicy Bypass `
    -File .\scripts\build-executable.ps1
.\.build\server-cli.exe --help
```

Package the compiled executable with WiX:

```powershell
powershell -ExecutionPolicy Bypass `
    -File .\msi\scripts\build-msi.ps1 `
    -Version 1.0.0
```

The resulting `.build\server-cli-1.0.0.msi` installs the executable under
`C:\Program Files\ServerCLI` and adds that directory to the machine `PATH`.
The MSI does not install Python, create a virtual environment, or access the
network during installation.

Inspect the generated package with WiX `dark.exe`:

```powershell
dark.exe `
    -x .build\msi-inspect `
    -out .build\msi-inspect\Product.wxs `
    .build\server-cli-1.0.0.msi
```

Publish the installer to a Cloudsmith Raw repository:

```powershell
cloudsmith push raw `
    "$env:CLOUDSMITH_REPOSITORY" `
    .\.build\server-cli-1.0.0.msi `
    --name server-cli `
    --version 1.0.0
```

Generate and validate WinGet manifests from the published URL:

```powershell
wingetcreate new `
    "https://dl.cloudsmith.io/public/<cloudsmith-repo>/raw/versions/1.0.0/server-cli-1.0.0.msi"
winget validate --manifest `
    .\manifests\m\ModernPythonEngineering\ServerCLI\1.0.0
```

## Future Authentication Flow

The planned authentication flow is:

1. `login` accepts supplied credentials or prompts for missing values.
2. The credentials are sent to the configured server authentication endpoint.
3. `get-token` requests a short-lived API token from the server.
4. Token storage and expiration handling are added to the client configuration.

These server interactions will be implemented in a later refinement.
