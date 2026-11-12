# PyGuard

PyGuard checks incoming requests with configurable security rules.

## Installation

### Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)

### Configure Cloudsmith Repository

Replace `<CLOUDSMITH_REPOSITORY>` with your Cloudsmith repository slug, then
add the Cloudsmith index and tell uv to install PyGuard from it in your
project's `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "cloudsmith"
url = "https://python.cloudsmith.io/<CLOUDSMITH_OWNER>/<CLOUDSMITH_REPOSITORY>/simple/"

[tool.uv.sources]
pyguard = { index = "cloudsmith" }
```

### Install PyGuard

```bash
uv add pyguard==0.1.0
```

## Usage

### Import PyGuard

```python
from pyguard import PyGuard, RequestBlocked
from pyguard.rules import BruteForce, PathTraversal
```

### Protect an Endpoint

Following example demonstrates the PyGuard integration with an `FastAPI` application middleware.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
guard = PyGuard(rules=[
    PathTraversal(),
    BruteForce(
        paths=["/login"], 
        max_attempts=5, 
        window=60, 
        block_duration=300
    ),
])

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    guarded_request = PyGuard.Request(
        method=request.method,
        path=request.url.path,
        source=request.client.host if request.client else "unknown",
    )
    try:
        return await guard.check(guarded_request, lambda: call_next(request))
    except RequestBlocked as error:
        return JSONResponse(status_code=429, content={"detail": str(error)})
```

`BruteForce` counts only `401` and `403` responses on the configured paths. After
five such responses within 60 seconds, the next request from that source is
blocked for 300 seconds. Tracking is in memory and is not shared across workers.