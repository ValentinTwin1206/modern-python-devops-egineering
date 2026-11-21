"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from influxdb_client import InfluxDBClient
from pymongo import MongoClient

from .api.middleware.metrics_middleware import configure_metrics
from .api.middleware.middleware import configure_middleware
from .api.routes import analysis, health, users
from .database.keycloak import bootstrap_keycloak
from .database.mongo import bootstrap_db


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    :return (FastAPI) Configured FastAPI application
    """

    # Initialize application resources during startup and release them at shutdown.
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        client = MongoClient(os.environ["MONGODB_URI"])
        try:
            influxdb_client = InfluxDBClient(
                url=os.getenv("INFLUXDB_URL", None),
                token=os.getenv("INFLUXDB_TOKEN", None),
                org=os.getenv("INFLUXDB_ORG", None),
                timeout=5000,
            )
            configure_metrics(app, influxdb_client, os.getenv("INFLUXDB_ORG", None), os.getenv("INFLUXDB_BUCKET", None))
            bootstrap_db(app, client, os.environ["MONGODB_DATABASE"])
            bootstrap_keycloak(app)
            yield
        finally:
            influxdb_client = getattr(app.state, "influxdb_client", None)
            if influxdb_client is not None:
                influxdb_client.close()
            client.close()

    # Create FastAPI app and configure middleware
    app = FastAPI( title="IrisLab API", version="1.0.0", lifespan=lifespan )
    configure_middleware(app)

    # Add routers
    app.include_router( health.router, tags=["health"] )
    app.include_router( analysis.router, prefix="/api/v1", tags=["iris analysis"] )
    app.include_router( users.router, prefix="/api/v1", tags=["user management"] )

    return app


app = create_app()
