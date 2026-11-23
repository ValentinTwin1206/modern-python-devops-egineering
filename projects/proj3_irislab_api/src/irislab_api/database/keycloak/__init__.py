"""Keycloak user store and application bootstrap."""

import logging
import os

from fastapi import FastAPI

from .client import KeycloakClient, KeycloakError

logger = logging.getLogger("irislab_api")

CONFIG_VARIABLES = (
    "KEYCLOAK_INTERNAL_URL",
    "KEYCLOAK_REALM",
    "KEYCLOAK_ADMIN_CLIENT_ID",
    "KEYCLOAK_ADMIN_CLIENT_SECRET",
)


def bootstrap_keycloak(app: FastAPI) -> None:
    """Create the Keycloak client from the environment; disable user management if unconfigured."""
    missing = [name for name in CONFIG_VARIABLES if not os.getenv(name)]
    if missing:
        # The analysis API keeps working; /api/v1/users answers 503.
        logger.warning("User management disabled, missing: %s", ", ".join(missing))
        app.state.keycloak_client = None
        return
    app.state.keycloak_client = KeycloakClient(
        *(os.environ[name] for name in CONFIG_VARIABLES),
        timeout=float(os.getenv("KEYCLOAK_TIMEOUT_SECONDS", "10")),
    )


__all__ = ["KeycloakClient", "KeycloakError", "bootstrap_keycloak"]
