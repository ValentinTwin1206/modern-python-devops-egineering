"""Record request metrics in InfluxDB without affecting API responses."""

import logging
import time

from fastapi import Request
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger("iris-lab")
METRIC_NAME = "api_requests"


def configure_metrics(app, client=None, org=None, bucket=None) -> None:
    """Attach the optional InfluxDB client and writer to app state."""
    app.state.influxdb_client    = client
    app.state.influxdb_write_api = None
    app.state.influxdb_org       = None
    app.state.influxdb_bucket    = None

    if client is None:
        logger.warning("InfluxDB metrics disabled: configure all INFLUXDB_* settings")
        return
    app.state.influxdb_write_api = client.write_api(write_options=SYNCHRONOUS)
    app.state.influxdb_org = org
    app.state.influxdb_bucket = bucket


async def metrics_middleware(request: Request, call_next):
    """Record method, path, client, status, and request duration."""
    started_at = time.perf_counter()
    # Keep a useful status if downstream handling raises an exception.
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        # Record failed requests as well as normal responses.
        write_api = request.app.state.influxdb_write_api
        if write_api is not None:
            duration_ms = (time.perf_counter() - started_at) * 1000
            client_ip   = request.client.host if request.client else "unknown"
            point = (
                Point(METRIC_NAME)
                .tag("method", request.method)
                .tag("endpoint", request.url.path)
                .tag("client_ip", client_ip)
                .field("duration_ms", duration_ms)
                .field("status_code", status_code)
            )
            try:
                write_api.write(
                    bucket=request.app.state.influxdb_bucket,
                    org=request.app.state.influxdb_org,
                    record=point,
                )
            except Exception:
                # Telemetry failures must not change the API response.
                logger.exception("Failed to write request metrics to InfluxDB")
