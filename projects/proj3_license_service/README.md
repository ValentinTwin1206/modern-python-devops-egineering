# License Service

**License Service** is a small FastAPI application that generates and validates license keys for a fictional product. It stores licenses in a local SQLite database and uses [PyGuard](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_pyguard/README.md) middleware to rate-limit the license-creation endpoint.

## Project Components

| Component       | Description                                                                 |
| --------------- | ----------------------------------------------------------------------------- |
| `pyproject.toml` | Package metadata, dependencies, and the Cloudsmith package index used to resolve `pyguard`. |
| `main.py`       | FastAPI application, routes, PyGuard middleware wiring, and the `uvicorn` entrypoint. |
| `database.py`   | SQLite connection helper and schema initialization for the `licenses` table.  |
| `helpers.py`    | License key generation and admin API key verification.                       |
| `Dockerfile`    | Builds a runtime image with `uv` and starts the service with `python main.py`. |
| `test/`         | `pytest` unit tests and an end-to-end brute-force test.                       |

## Requirements

* Python 3.9+
* `uv`

## Installation

Sync the project environment, which installs `fastapi`, `uvicorn`, and `pyguard` from the configured package indexes:

```bash
uv sync
```

## Run

Start the service:

```bash
uv run python main.py
```

The service listens on `http://0.0.0.0:8080`.

## Test

Run the unit and end-to-end tests with `pytest`:

```bash
uv run pytest
```

## API

| Endpoint | Method | Auth | Description |
| -------- | ------ | ---- | ------------ |
| `/` | GET | none | Returns the service status. |
| `/licenses` | POST | `X-API-Key` header | Creates a license for a user. Rate-limited by PyGuard. |
| `/licenses/{license_key}` | GET | none | Checks whether a license exists and is active. |

Set `ADMIN_API_KEY` to override the default development API key (`dev-secret`) used by `/licenses`.
