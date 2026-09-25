# Server CLI

Server CLI is a small Click-based command-line client for a future server API.
It demonstrates a modern Python development workflow that combines `uv`, a VS
Code Dev Container, Nuitka, and Debian packaging.

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
    DEB --> APT[APT installation]
    APT --> COMMAND[/usr/bin/server-cli]
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
| `scripts/build-executable.sh` | Nuitka standalone executable build |
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
Python and uv
      |
      +-- Click application dependencies
      +-- Karva and Ruff
      +-- Nuitka and native compiler toolchain
      +-- Debian packaging tools
```

Nuitka is deliberately installed by the Dockerfile as a container-level build
tool. It is not declared in `pyproject.toml` because it is not a runtime or
test dependency of the application.

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

The container synchronizes the environment with `uv sync --group dev` after it
is created. Run the same command manually after changing dependencies:

```bash
uv sync --group dev
```

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

## Future Authentication Flow

The planned authentication flow is:

1. `login` accepts supplied credentials or prompts for missing values.
2. The credentials are sent to the configured server authentication endpoint.
3. `get-token` requests a short-lived API token from the server.
4. Token storage and expiration handling are added to the client configuration.

These server interactions will be implemented in a later refinement.
