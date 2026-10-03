"""HTTP middleware used by the license service."""

import os
import logging

from fastapi import Request as FastAPIRequest, responses
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from pyguard import PyGuardMiddleware, Request, RequestBlocked

from .helpers import TokenError, validate_bearer_token

logger = logging.getLogger("license-service")
PROTECTED_PATHS = {("POST", "/licenses"), ("GET", "/licenses")}


def is_jwt_protected(request: FastAPIRequest) -> bool:
    # Protect license creation and dynamic license revocation routes.
    return (request.method, request.url.path) in PROTECTED_PATHS or (
        request.method == "DELETE" and request.url.path.startswith("/licenses/")
    )


# ========================================
# Create PyGuardMiddleware and InfluxDB metrics writer for the FastAPI application.

def _create_guard() -> PyGuardMiddleware:
    """Creates the PyGuardMiddleware instance with the specified configuration."""
    return PyGuardMiddleware(
        protected_paths=PROTECTED_PATHS, 
        brute_force_config={
            "max_attempts": int(os.getenv("PYGUARD_MAX_ATTEMPTS", 5)),
            "window_seconds": int(os.getenv("PYGUARD_WINDOW_SECONDS", 60)),
            "block_seconds": int(os.getenv("PYGUARD_BLOCK_SECONDS", 300)),
        },
    )


def _create_metrics_writer() -> tuple[InfluxDBClient, any] | None:
    """Create the InfluxDB writer when monitoring is configured."""

    token = os.getenv("INFLUXDB_TOKEN") or os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
    if not token:
        logger.warning("InfluxDB monitoring disabled: no token configured")
        return None

    client = InfluxDBClient(
        url=os.getenv("INFLUXDB_URL", "http://influxdb:8086"),
        token=token,
        org=os.getenv("INFLUXDB_ORG", "oidc_license_service"),
    )
    return client, client.write_api(write_options=SYNCHRONOUS)


# =========================================
# Configure FastAPI middleware for security and metrics.

def configure_middleware(app) -> None:
    """
    Configure the FastAPI application with security and metrics middleware.
    
    :param app: The FastAPI application instance to configure middleware for.
    """
    
    # instantiate the PyGuardMiddleware and InfluxDB metrics writer
    guard = _create_guard()
    metrics = _create_metrics_writer()
    app.state.guard = guard
    app.state.metrics = metrics

    @app.middleware("http")
    async def security_middleware(request: FastAPIRequest, call_next):
        """
        Security middleware that runs PyGuard before the request reaches the API endpoint.
        
        :param request: The incoming HTTP request.
        :type request: FastAPIRequest
        :param call_next: The next request handler in the middleware chain.
        :type call_next: Callable[[FastAPIRequest], Response]
        """

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
        logger.info(
            "Response: %s %s -> %s",
            request.method,
            request.url.path,
            response.status_code,
        )
        return response

    @app.middleware("http")
    async def jwt_auth_middleware(request: FastAPIRequest, call_next):
        """
        Middleware that validates JWT bearer tokens for protected license operations.
        
        :param request: The incoming HTTP request.
        :type request: FastAPIRequest
        :param call_next: The next request handler in the middleware chain.
        :type call_next: Callable[[FastAPIRequest], Response]
        """

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
                request.state.jwt_claims = claims
                logger.info("Token accepted for sub=%s", claims.get("sub"))
        return await call_next(request)

    @app.middleware("http")
    async def metrics_middleware(request: FastAPIRequest, call_next):
        """Record each API path and its HTTP status in InfluxDB."""
        try:
            response = await call_next(request)
        except Exception:
            # Exceptions do not produce a Response object, so record them as
            # failed requests before allowing the exception to propagate.
            await _write_metric(request, 500)
            raise

        # Write after the endpoint completes to capture its actual status code.
        await _write_metric(request, response.status_code)
        return response

    async def _write_metric(request: FastAPIRequest, status_code: int) -> None:
        """Write one API request metric to InfluxDB."""
        if app.state.metrics is None:
            return

        _, write_api = app.state.metrics
        # Tags support filtering by request dimensions; the status code is a
        # field so InfluxDB can aggregate response counts.
        # Starlette exposes the peer address through request.client. The
        # fallback keeps metric writing safe for synthetic test requests.

        # The service is accessed directly, so the peer address is the
        # requester address available to FastAPI.
        client_ip = request.client.host if request.client is not None else "unknown"

        point = (
            Point("api_requests")
            .tag("method", request.method)
            .tag("endpoint", request.url.path)
            .tag("client_ip", client_ip)
            .field("status_code", status_code)
        )
        try:
            logger.info(
                "Writing API metric: method=%s endpoint=%s client_ip=%s status_code=%s",
                request.method,
                request.url.path,
                client_ip,
                status_code,
            )
            write_api.write(
                bucket=os.getenv("INFLUXDB_BUCKET", "api_metrics"),
                org=os.getenv("INFLUXDB_ORG", "oidc_license_service"),
                record=point,
            )
            logger.info("API metric written successfully")
        except Exception:
            # Monitoring must never make an otherwise healthy API request fail.
            logger.exception("Failed to write API metric to InfluxDB")
