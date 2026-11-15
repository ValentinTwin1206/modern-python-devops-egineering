# IrisLab CLI

An interactive UV-managed client for the authenticated IrisLab API. It logs in
through Keycloak in the browser, then keeps the access token in memory while
the shell is running. Exiting or interrupting the process ends the session; the
next run requires a fresh login.

## Installation

### Prerequisites

- Python 3.12 or later 
- [uv](https://docs.astral.sh/uv/)
- Keycloak realm with a public client configured for authorization code with PKCE S256 (no client secret). 

>NOTE: Its allowed redirect URI must match the CLI callback, normally `http://127.0.0.1:8765/callback`. 

Set these environment variables before starting the CLI:

| Variable | Value | Notes |
| --- | --- | --- |
| `IRIS_OIDC_ISSUER` | `http://keycloak.localhost:8081/realms/iris-analysis` | Required; `OIDC_ISSUER_URL` is also accepted. |
| `IRIS_CLI_CLIENT_ID` | `iris-analysis-cli` | Required; must match the Keycloak client. |
| `IRIS_API_URL` | `http://localhost:8080` | API base URL. |
| `IRIS_CLI_CALLBACK_PORT` | `8765` | Callback port; must match Keycloak's redirect URI. |
| `IRIS_API_TIMEOUT` | `60` | Request timeout in seconds. |

### Install IrisLab CLI

From this directory, install the project and its development dependencies:

```sh
uv sync
```

## Usage

Run the interactive shell:

```sh
uv run iris-cli
```

The browser opens for Keycloak login. Once it returns to the loopback callback, enter commands at the `iris>` prompt:

```text
analyze --image ./portrait.jpg --output ./analysis.json
history --output ./history.json
reference-colors
help
exit
```

> NOTE: the authenticated API client, request errors, and JSON output remain shared.

## Development

```sh
uv run pytest
uv run ruff check .
```