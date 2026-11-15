"""Request security and logging middleware backed by PyGuard."""

import logging
import os

from fastapi import Request as FastAPIRequest, responses
from pyguard import PyGuard, RequestBlocked
from pyguard.rules import BruteForce, PathTraversal

logger = logging.getLogger("iris-lab")


def _safe_request_path(path: str) -> str:
    prefix = "/licenses/"
    token = path[len(prefix):] if path.startswith(prefix) else ""
    return f"{prefix}{{token}}" if token and "/" not in token else path


async def security_middleware(request: FastAPIRequest, call_next):
    """Run PyGuard and log requests and responses with a sanitized path."""
    guard = request.app.state.guard

    client_ip = request.client.host if request.client else "unknown"
    safe_path = _safe_request_path(request.url.path)

    guard_request = PyGuard.Request(
        method=request.method,
        path=request.url.path,
        query=request.url.query,
        source=client_ip,
    )

    logger.info(
        "Request: %s %s from %s",
        request.method,
        safe_path,
        client_ip,
    )

    try:
        response = await guard.check(guard_request, lambda: call_next(request))
    except RequestBlocked as exc:
        logger.warning(
            "Request blocked: %s | reason=%s",
            safe_path,
            str(exc),
        )
        return responses.JSONResponse(
            status_code=429,
            content={"detail": str(exc)},
        )

    logger.info(
        "Response: %s %s -> %s",
        request.method,
        safe_path,
        response.status_code,
    )
    return response


def create_security_guard() -> PyGuard:
    """Create the PyGuard instance used by the security middleware."""
    return PyGuard(
        rules=[
            PathTraversal(),
            BruteForce(
                paths=["/api/v1/analyses", "/api/v1/reference-colors"],
                max_attempts=int(os.getenv("PYGUARD_MAX_ATTEMPTS", "5")),
                window=int(os.getenv("PYGUARD_WINDOWS_SECONDS", "60")),
                block_duration=int(
                    os.getenv("PYGUARD_BLOCK_SECONDS", "300").removesuffix("s")
                ),
            ),
        ]
    )
