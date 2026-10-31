"""FastAPI application entry point."""

from fastapi import FastAPI

from .api.routes import analysis, health


def create_app() -> FastAPI:
    app = FastAPI(title="IrisLab API", version="1.0.0")
    app.include_router(health.router, tags=["health"])
    app.include_router(analysis.router, prefix="/api/v1", tags=["iris analysis"])
    return app


app = create_app()
