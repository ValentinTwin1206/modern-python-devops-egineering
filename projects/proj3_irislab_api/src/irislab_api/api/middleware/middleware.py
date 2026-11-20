"""Central registration for the IrisLab HTTP middleware."""

from .jwt_middleware import jwt_auth_middleware
from .metrics_middleware import metrics_middleware
from .security_middleware import create_moderation_guard, security_middleware

# =========================================
# Configure FastAPI middleware for authentication, moderation, and metrics.

def configure_middleware(app) -> None:
    """
    Configure the FastAPI application with security and metrics middleware.
    
    :param app: The FastAPI application instance to configure middleware for.
    """
    
    # Create and assign the image moderation guard to the application state.
    app.state.moderation_guard = create_moderation_guard()

    # Authentication runs before moderation so unauthenticated uploads are not inspected.
    app.middleware("http")(security_middleware)
    app.middleware("http")(jwt_auth_middleware)
    app.middleware("http")(metrics_middleware)
