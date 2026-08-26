# PyGuard

**PyGuard** is a small Python security library that blocks suspicious web requests before they reach application handlers. It currently provides **path traversal** and **brute-force protection for configurable protected endpoints**.

## Project Components

| Component              | Description                                                                            |
| ---------------------- | -------------------------------------------------------------------------------------- |
| `pyproject.toml`       | Package metadata and build configuration.                                              |
| `src/pyguard/`         | Reusable middleware, scanner, models, and security rules.                              |
| `src/pyguard/rules.py` | Contains the `SecurityRule` base class, `PathTraversalRule`, and `AuthBruteForceRule`. |

## End-User Guide

### Requirements

* Python 3.9+
* `uv` or `pip`

### Installation

With `uv`:

```toml
[project]

dependencies = [
    "pyguard==0.1.0",
]
```

```bash
uv sync
```

Or with `pip`:

```bash
python -m pip install pyguard==0.1.0
```

## Usage

### Path Traversal Protection

```python
from pyguard import PyGuardMiddleware, Request, RequestBlocked

guard = PyGuardMiddleware()

request = Request(
    method="GET",
    path="/download",
    query="file=../../etc/passwd",
)

try:
    guard.before_request(request)
except RequestBlocked as exc:
    print(exc)
```

### Brute-Force Protection

Protected endpoints are configured by the application:

```python
from pyguard import PyGuardMiddleware

guard = PyGuardMiddleware(
    protected_paths={
        ("POST", "/licenses"),
    },
)
```

By default, the brute-force rule:

* Allows 4 requests within the configured window.
* Blocks on the 5th request.
* Blocks the source for 5 minutes.
* Tracks requests per source.

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, responses, Request as FastAPIRequest
from pyguard import PyGuardMiddleware, Request, RequestBlocked

app = FastAPI()

guard = PyGuardMiddleware(
    protected_paths={
        ("POST", "/licenses"),
    },
)


@app.middleware("http")
async def security_middleware(
    request: FastAPIRequest,
    call_next,
):
    guard_request = Request(
        method=request.method,
        path=request.url.path,
        query=request.url.query,
        source=request.client.host,
    )

    try:
        guard.before_request(guard_request)
    except RequestBlocked as exc:
        return responses.JSONResponse(
            status_code=429,
            content={"detail": str(exc)},
        )

    return await call_next(request)
```

## Developer Guide

### Setup

```bash
./build.sh build --path proj1_pyguard/Dockerfile.devEnv
```

```bash
uv sync --all-groups
source .venv/bin/activate
```

### Lint

```bash
ruff check .
```

### Build

```bash
uv build --wheel --out-dir /build
```

### Publish

```bash
uv publish
```

PyGuard is distributed as a pure-Python wheel and can be installed directly from PyPI.
