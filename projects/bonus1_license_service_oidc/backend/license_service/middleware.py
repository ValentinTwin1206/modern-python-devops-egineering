"""HTTP middleware used by the license service."""

import os
import logging

from fastapi import Request as FastAPIRequest, responses
from pyguard import PyGuardMiddleware, Request, RequestBlocked

from .helpers import TokenError, validate_bearer_token

logger = logging.getLogger("license-service")
PROTECTED_PATHS = {("POST", "/licenses"), ("GET", "/licenses")}


def is_jwt_protected(request: FastAPIRequest) -> bool:
    # Protect license creation and dynamic license revocation routes.
    return (request.method, request.url.path) in PROTECTED_PATHS or (
        request.method == "DELETE" and request.url.path.startswith("/licenses/")
    )


def create_guard() -> PyGuardMiddleware:
    """Creates the PyGuardMiddleware instance with the specified configuration."""
    return PyGuardMiddleware(
        protected_paths=PROTECTED_PATHS, 
        brute_force_config={
            "max_attempts": int(os.getenv("PYGUARD_MAX_ATTEMPTS", 5)),
            "window_seconds": int(os.getenv("PYGUARD_WINDOW_SECONDS", 60)),
            "block_seconds": int(os.getenv("PYGUARD_BLOCK_SECONDS", 300)),
        },
    )


def configure_middleware(app, guard: PyGuardMiddleware) -> None:
    app.state.guard = guard

    @app.middleware("http")
    async def security_middleware(request: FastAPIRequest, call_next):
        # Run PyGuard before the request reaches the API endpoint.
        guard = request.app.state.guard
        guard_request = Request(
            method=request.method,
            path=request.url.path,
            query=request.url.query,
            source=request.client.host,
        )
        logger.info(
            "Request: %s %s from %s",
            request.method,
            request.url.path,
            request.client.host,
        )
        try:
            guard.before_request(guard_request)
        except RequestBlocked as exc:
            logger.warning("Request blocked: %s | reason=%s", request.url.path, str(exc))
            return responses.JSONResponse(status_code=429, content={"detail": str(exc)})
        response = await call_next(request)
        logger.info("Response: %s %s -> %s", request.method, request.url.path, response.status_code)
        return response


    @app.middleware("http")
    async def jwt_auth_middleware(request: FastAPIRequest, call_next):
        # Validate a bearer token only on protected license operations.
        if is_jwt_protected(request):
            authorization = request.headers.get("Authorization")
            if authorization:
                try:
                    claims = validate_bearer_token(authorization)
                except TokenError as exc:
                    logger.warning("Token rejected: %s", exc.detail)
                    return responses.JSONResponse(
                        status_code=exc.status_code,
                        content={"detail": exc.detail},
                    )
                # Make validated claims available to endpoint authorization.
                request.state.jwt_claims = claims
                logger.info("Token accepted for sub=%s", claims.get("sub"))
        return await call_next(request)
