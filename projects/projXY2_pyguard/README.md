# PyGuard

A lightweight security middleware for Python web applications.

## Features

- Detects path traversal attacks
- Framework-independent core
- Compatible with Python 3.9+

---

## Installation

```bash
pip install pyguard
```

---

## FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, Request

from pyguard import PyGuardMiddleware
from pyguard.models import Request as GuardRequest
from pyguard.exceptions import RequestBlocked

app = FastAPI()
guard = PyGuardMiddleware()


@app.middleware("http")
async def security_middleware(request: Request, call_next):

    guard_request = GuardRequest(
        method=request.method,
        path=request.url.path,
        query=request.url.query,
    )

    try:
        guard.before_request(guard_request)
    except RequestBlocked as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    return await call_next(request)


@app.get("/")
async def root():
    return {"message": "Hello World"}
```
curl http://127.0.0.1:8000/download?file=api-example.json
---

## Roadmap

- [x] Path traversal detection
- [ ] SQL injection detection
- [ ] XSS detection
- [ ] Command injection detection
- [ ] Configurable rule engine
- [ ] Logging
- [ ] Risk scoring