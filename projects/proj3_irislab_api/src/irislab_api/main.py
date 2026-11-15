"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import MongoClient

from .api.routes import analysis, health
from .api.middleware.middleware import configure_middleware

from .database.mongo import bootstrap_db


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    :return (FastAPI) Configured FastAPI application
    """

    # Initialize FastAPI application with lifespan context manager for database connection
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        client = MongoClient(os.environ["MONGODB_URI"])
        try:
            bootstrap_db(app, client, os.environ["MONGODB_DATABASE"])
            yield
        finally:
            client.close()

    # Create FastAPI app and configure middleware
    app = FastAPI( title="IrisLab API", version="1.0.0", lifespan=lifespan )
    configure_middleware(app)

    # Add routers
    app.include_router( health.router, tags=["health"] )
    app.include_router( analysis.router, prefix="/api/v1", tags=["iris analysis"] )

    return app


app = create_app()
