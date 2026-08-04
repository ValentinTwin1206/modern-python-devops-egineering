# PyGuard

This section introduces *PyGuard* as a small Python library that blocks suspicious web requests before they reach application handlers, while demonstrating how a pure-Python package can be developed with `venv` and `uv`, distributed as a wheel, and published to PyPI.

## Project Components

The table below lists the main files that support the `venv` example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image installs `uv`, syncs the `dev` dependency group, and opens an interactive shell with the project virtual environment on `PATH`. It provides a reproducible containerized setup for the library workflow. |
| [pyproject.toml](pyproject.toml) | This file defines the package metadata, the `uv_build` build backend, and the development dependency group for Karva and Ruff. It is the main configuration file for the library-style project layout. |
| [src/pyguard/](src/pyguard/) | This source package holds the reusable request-scanning middleware that end users import from their own web applications. The `src` layout keeps imports honest by ensuring development behavior matches the installed package shape. |

## End-User Guide

This section shows how an end user installs and uses `pyguard` as a published Python library from PyPI.

### Requirements

- Python 3.9 or newer.
- `uv` if you install from `pyproject.toml`.
- `pip`, or another installer that reads `requirements.txt` files.

### Installation

Add `pyguard` to your project metadata when you manage dependencies with `uv`:

```toml
[project]
dependencies = [
    "pyguard==0.1.0",
]
```

Sync the environment with `uv`:

```bash
uv sync
```

If your project uses a `requirements.txt` file instead, add the published package there:

```text
pyguard==0.1.0
```

Install the requirements with `pip`:

```bash
python -m pip install -r requirements.txt
```

### Usage

Create a request model and scan it before your application handles the request:

```python
from pyguard import PyGuardMiddleware, Request

guard = PyGuardMiddleware()
request = Request(method="GET", path="/download", query="file=report.pdf")

guard.before_request(request)
```

Block a path traversal attempt:

```python
from pyguard import PyGuardMiddleware, Request, RequestBlocked

guard = PyGuardMiddleware()
request = Request(method="GET", path="/download", query="file=../../etc/passwd")

try:
    guard.before_request(request)
except RequestBlocked as exc:
    print(exc)
```

Integrate the middleware with a FastAPI application:

```python
from fastapi import FastAPI, HTTPException, Request as FastAPIRequest

from pyguard import PyGuardMiddleware, Request, RequestBlocked

app = FastAPI()
guard = PyGuardMiddleware()


@app.middleware("http")
async def security_middleware(request: FastAPIRequest, call_next):
    guard_request = Request(
        method=request.method,
        path=request.url.path,
        query=request.url.query,
    )

    try:
        guard.before_request(guard_request)
    except RequestBlocked as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return await call_next(request)
```

## Developer Guide

### Setup Environment

Use the development image in [Dockerfile.devEnv](Dockerfile.devEnv) to open an interactive shell with `uv` and the project environment already prepared. Run the following command from the `projects/` directory through the shared helper:

```bash
./build.sh build --path proj1_pyguard/Dockerfile.devEnv
```

### Sync Environment

Within the running container, you can sync the project environment with `uv`:

```bash
uv sync --all-groups
```

Then source the virtual environment so the installed tools are on `PATH`:

```bash
source .venv/bin/activate
```

### Lint

Within the active virtual environment, you can run Ruff against the source tree:

```bash
ruff check .
```

### Build Guide

The project is shipped as a pure-Python wheel so that end users can install it directly from PyPI through `pyproject.toml` or `requirements.txt` without building from source.

#### Build the Wheel

Build the wheel artifact from the project root:

```bash
uv build --wheel --out-dir /build
```

The wheel is written inside the container to `/build` and appears on the host at:

```text
.build/pyguard-0.1.0-py3-none-any.whl
```

#### Upload to PyPI

Upload the built distribution to PyPI with `uv`:

```bash
uv publish
```

`uv publish` reads the PyPI authentication settings from your environment or your configured credential store, so no extra publishing dependency is needed inside the project itself.