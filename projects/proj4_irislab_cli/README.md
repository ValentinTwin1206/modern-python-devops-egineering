# IrisLab CLI

IrisLab CLI is a Click-based interactive client for the authenticated IrisLab API. It logs in through Keycloak in the browser, then keeps the access token in memory while the shell is running. Exiting or interrupting the process ends the session; the next run requires a fresh login.

## Installation

### Configure Cloudsmith Repository

Replace `<CLOUDSMITH_REPOSITORY>` with your Cloudsmith repository slug. Add its signing key and APT source:

```bash
curl -fsSL "https://dl.cloudsmith.io/public/<CLOUDSMITH_REPOSITORY>/gpg.key" \
  | sudo gpg --dearmor -o /usr/share/keyrings/cloudsmith-repository.gpg

printf 'Types: deb\nURIs: https://dl.cloudsmith.io/public/<CLOUDSMITH_REPOSITORY>/deb/ubuntu\nSuites: noble\nComponents: main\nSigned-By: /usr/share/keyrings/cloudsmith-repository.gpg\n' \
  | sudo tee /etc/apt/sources.list.d/cloudsmith.sources
```

Afterwards, update the APT soruces by running the following command:

```bash
sudo apt update
```

### Install IrisLab CLI

To install the `irislab-cli` package, run following command:

```bash
sudo apt install irislab-cli
```

The package contains a standalone executable; Python is not required. On Windows, install `irislab-cli-1.0.0.msi` instead.

## Configuration

IrisLab CLI needs a Keycloak realm with a public client configured for authorization code with PKCE S256 (no client secret). The client's allowed redirect URI must match the CLI callback, normally `http://127.0.0.1:8765/callback`.

Set these environment variables before starting the CLI:

| Variable | Value | Notes |
| --- | --- | --- |
| `IRIS_OIDC_ISSUER` | `http://keycloak.localhost:8081/realms/iris-analysis` | Required; `OIDC_ISSUER_URL` is also accepted. |
| `IRIS_CLI_CLIENT_ID` | `iris-analysis-cli` | Required; must match the Keycloak client. |
| `IRIS_API_URL` | `http://localhost:8080` | API base URL. |
| `IRIS_CLI_CALLBACK_PORT` | `8765` | Callback port; must match Keycloak's redirect URI. |
| `IRIS_API_TIMEOUT` | `60` | Request timeout in seconds. |

## Usage

### Show Help and Version

```bash
irislab-cli --help
irislab-cli --version
```

### Start a Session

```bash
irislab-cli
```

The browser opens for Keycloak login. Once it returns to the loopback callback, the `iris>` prompt accepts the commands below. Each command prints JSON; `--output` writes it to a file instead.

### Analyze an Image

```text
iris> analyze --image ./portrait.jpg --output ./analysis.json
```

Uploads a PNG or JPEG image and returns the analysis result.

### Show the Analysis History

```text
iris> history --output ./history.json
```

Returns the analyses of the logged-in user.

### Show the Reference Colors

```text
iris> reference-colors
```

### End the Session

```text
iris> help
iris> exit
```

`help` lists the commands. `exit`, `quit`, or Ctrl+D ends the session and discards the access token.

## Development

Open the project in its dev container (`.devcontainer/`), which provides uv, Nuitka, and the Debian packaging tools. Then:

```bash
uv sync
uv run irislab-cli
uv run pytest
uv run ruff check .
```

### Build the Debian Package

```bash
scripts/build-executable.sh
scripts/build-deb.sh
```

The first script compiles `.build/irislab-cli` with Nuitka. The second wraps it into `.build/irislab-cli_1.0.0-1_<arch>.deb`.

### Build the Windows Installer

Build the image with the Windows container engine on a Windows host and start it with the project mounted at `C:\workspace`:

```powershell
docker build -f Dockerfile.windows -t irislab-cli-msi-builder .
docker run --rm -it -v "${PWD}:C:\workspace" irislab-cli-msi-builder
```

Inside the container:

```powershell
uv sync
.\scripts\build-executable.ps1
.\msi\scripts\build-msi.ps1
```

The result is `.build\irislab-cli-1.0.0.msi`.

## License

Apache-2.0, see [LICENSE](LICENSE).
