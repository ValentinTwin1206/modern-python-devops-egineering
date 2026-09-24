import uvicorn
import asyncio
import logging
import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi  import Depends, FastAPI, HTTPException, Query, Request as FastAPIRequest
from pydantic import BaseModel

from license_service.cloudsmith import (
    CloudsmithClient,
    CloudsmithConfig,
    CloudsmithConfigurationError,
    verify_cloudsmith_on_startup,
)
from license_service.database import create_database
from license_service.helpers import is_admin, require_admin, require_admin_or_user
from license_service.middleware import configure_middleware, create_guard
from schedule import cloudsmith_refresh_loop, refresh_and_store_cloudsmith_token


# ========================================== 
# Logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("license-service")


# ==========================================
# Create the database instance and application instance
database = create_database(os.getenv("DATABASE_PATH", "licenses.db"))


# =========================================
# FastAPI application and request lifecycles
cloudsmith_config: CloudsmithConfig | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Keep the configuration scoped to the application lifecycle
    global cloudsmith_config

    # Keep network checks out of module import time.
    cloudsmith_config = CloudsmithConfig.from_environment()
    logger.info(
        "Cloudsmith configuration loaded: %s",
        "enabled" if cloudsmith_config is not None else "disabled",
    )
    stored_license = database.get_latest_active_license()
    logger.info(
        "License database state at startup: active_token=%s expires_at=%s user=%s",
        stored_license is not None,
        stored_license["expires_at"] if stored_license is not None else None,
        stored_license["user"] if stored_license is not None else None,
    )

    # return 503 if the Cloudsmith configuration is incomplete
    if cloudsmith_config is None:
        logger.warning(
            "Cloudsmith verification skipped; license creation will return "
            "503 until the Cloudsmith environment variables are configured"
        )

    # Keep a reference to the task so it can be cancelled during shutdown.
    # The task is started only after configuration and repository verification
    refresh_task = None
    if cloudsmith_config is not None:
        verify_cloudsmith_on_startup(cloudsmith_config)
        refresh_task = asyncio.create_task(
            cloudsmith_refresh_loop(cloudsmith_config, database)
        )
    try:
        # Yield control to FastAPI while the scheduler runs in the background.
        yield
    finally:
        if refresh_task is not None:
            refresh_task.cancel()
            await asyncio.gather(refresh_task, return_exceptions=True)


app = FastAPI(
    title="License Service",
    description="Small example service for generating and validating license keys.",
    lifespan=lifespan,
)


# ==========================================
# Middleware registration

guard = create_guard()
configure_middleware(app, guard)


# ==========================================
# Pydantic Models

class LicenseResponse(BaseModel):
    user: str
    cloudsmith_token: str
    cloudsmith_expires_at: str

class LicenseCheckResponse(BaseModel):
    valid: bool
    user: str | None = None


# ==========================================
# API Endpoints

@app.get("/health")
def root():
    """Return the service status."""
    return {
        "service": "license-service",
        "status": "ok",
    }


@app.post(
    "/licenses",
    response_model=LicenseResponse,
    dependencies=[Depends(require_admin)],
)
def create_license() -> LicenseResponse:
    """Refresh and store the Cloudsmith user token (administrator only)."""
    if cloudsmith_config is None:
        logger.error(
            "License creation rejected: Cloudsmith is disabled. "
            "Set CLOUDSMITH_API_KEY, CLOUDSMITH_OWNER, and "
            "CLOUDSMITH_REPOSITORY in the backend environment."
        )
        raise HTTPException(status_code=503, detail="Cloudsmith is not configured")

    try:
        result = refresh_and_store_cloudsmith_token(cloudsmith_config, database)
    except CloudsmithConfigurationError as exc:
        logger.warning("Cloudsmith user token refresh failed: %s", exc)
        raise HTTPException(status_code=502, detail="Cloudsmith request failed") from exc
    return LicenseResponse(**result)


@app.get(
    "/licenses",
    response_model=LicenseResponse,
    dependencies=[Depends(require_admin_or_user)],
)
def get_license() -> LicenseResponse:
    """Return the current Cloudsmith token without refreshing it."""
    license_row = database.get_latest_active_license()
    if license_row is None:
        raise HTTPException(status_code=404, detail="No active license token")
    
    logger.info(
        "Returning stored license: user=%s slug_perm=%s expires_at=%s",
        license_row["user"],
        license_row["cloudsmith_token_slug_perm"],
        license_row["expires_at"],
    )
    
    try:
        expired = datetime.fromisoformat(license_row["expires_at"]) <= datetime.now(
            timezone.utc
        )
    except (TypeError, ValueError):
        expired = True
    if expired:
        raise HTTPException(status_code=404, detail="No active license token")
    return LicenseResponse(
        user=license_row["user"],
        cloudsmith_token=license_row["cloudsmith_token"],
        cloudsmith_expires_at=license_row["expires_at"],
    )


@app.delete("/licenses/{cloudsmith_token}")
def revoke_license( cloudsmith_token: str, request: FastAPIRequest ):
    """Revoke a license for its owner, or any license as an admin."""

    # Read authentication results prepared by the JWT middleware.
    claims = getattr(request.state, "jwt_claims", None)
    admin = is_admin(request.headers.get("X-API-Key"))

    if claims is None and not admin:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Load the local record before contacting Cloudsmith.
    license_row = database.get_license(cloudsmith_token)
    if license_row is None:
        raise HTTPException(status_code=404, detail="License not found")
    if not license_row["active"]:
        raise HTTPException(status_code=409, detail="License is already revoked")

    # Owners may revoke their own license; admins may revoke any license.
    if not admin and license_row["keycloak_subject"] != claims.get("sub"):
        raise HTTPException(status_code=403, detail="License ownership required")

    # User-token refreshes do not create revocable entitlements. Revoke the
    # locally issued license so it can no longer be returned or checked.
    try:
        revoked = database.revoke_license(cloudsmith_token)
    except Exception as exc:
        logger.exception("Failed to persist license revocation")
        raise HTTPException(status_code=500, detail="License revocation failed") from exc

    # Confirm that the local record was updated successfully.
    if revoked is None:
        raise HTTPException(status_code=404, detail="License not found")
    return {"revoked": True}


@app.get("/licenses/{cloudsmith_token}", response_model=LicenseCheckResponse)
def check_license(cloudsmith_token: str):
    """Check whether a license exists and is currently active."""

    logger.info("Checking license")

    # Look up the entitlement without exposing its stored token in logs.
    license = database.get_license(cloudsmith_token)

    # Treat malformed or expired timestamps as invalid access.
    expired: bool = False
    if license is not None:
        try:
            expired = datetime.fromisoformat(license["expires_at"]) <= datetime.now(
                timezone.utc
            )
        except (TypeError, ValueError):
            expired = True

    # Reject missing, disabled, and expired entitlements.
    if license is None or not license["active"] or expired:
        logger.warning("Inactive or unknown license checked")
        return LicenseCheckResponse(valid=False)

    logger.info( "Valid license checked for user=%s", license["user"], )

    return LicenseCheckResponse(
        valid=True,
        user=license["user"],
    )


def main():
    """Initialize the database and start the FastAPI service."""
    logger.info("Initializing database...")
    database.init()

    logger.info("Starting license service...")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )


if __name__ == "__main__":
    main()
