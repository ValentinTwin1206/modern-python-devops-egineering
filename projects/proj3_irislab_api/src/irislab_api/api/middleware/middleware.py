"""Central registration for the IrisLab HTTP middleware."""

from .jwt_middleware import jwt_auth_middleware
from .metrics_middleware import metrics_middleware
from .security_middleware import create_security_guard, security_middleware

# =========================================
# Configure FastAPI middleware for security and metrics.

def configure_middleware(app) -> None:
    """
    Configure the FastAPI application with security and metrics middleware.
    
    :param app: The FastAPI application instance to configure middleware for.
    """
    
    # Create and assign the security guard to the FastAPI application state.
    app.state.guard = create_security_guard()

    # Register the middleware functions with the FastAPI application.
    app.middleware("http")(jwt_auth_middleware)
    app.middleware("http")(security_middleware)
    app.middleware("http")(metrics_middleware)
