# PyGuard

PyGuard is a Python library that blocks suspicious requests, including path traversal attempts and repeated requests to protected endpoints.

## Installation

### Configure Cloudsmith Repository

Replace `<CLOUDSMITH_REPOSITORY>` with your Cloudsmith repository slug. Add the package index to your consumer project's `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "cloudsmith"
url = "https://dl.cloudsmith.io/public/<CLOUDSMITH_REPOSITORY>/python/simple/"
```

### Install PyGuard

Add PyGuard to your project's dependencies:

```toml
[project]
dependencies = ["pyguard"]
```

Install it with `uv`:

```bash
uv sync
```

## Usage

### Block a Suspicious Request

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
except RequestBlocked as error:
    print(error)
```

### Protect an Endpoint from Repeated Requests

```python
from pyguard import PyGuardMiddleware

guard = PyGuardMiddleware(
    protected_paths={("POST", "/login")},
)
```

By default, the brute-force rule blocks a source after five requests to a protected endpoint within the configured time window.

### Integrate with FastAPI

Call `guard.before_request()` from a FastAPI HTTP middleware and return an HTTP 429 response when it raises `RequestBlocked`. Set `protected_paths` to the method and path pairs that should be rate-limited.
