import uvicorn
import logging

from fastapi  import Depends, FastAPI, HTTPException, responses, Request as FastAPIRequest
from pydantic import BaseModel

from database import create_database
from helpers  import generate_license_key, require_admin

# ========================================== 
# Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("license-service")

# ==========================================
# Create the database instance and application instance
database = create_database()

app = FastAPI(
    title="License Service",
    description="Small example service for generating and validating license keys.",
)

# ==========================================
# PyGuard Middleware

from pyguard import PyGuardMiddleware, Request, RequestBlocked

PROTECTED_PATHS = {
    ("POST", "/licenses")
}

guard = PyGuardMiddleware(
    protected_paths=PROTECTED_PATHS,
)

@app.middleware("http")
async def security_middleware(
    request: FastAPIRequest,
    call_next,
):
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
        logger.warning( 
            "Request blocked: %s %s from %s | reason=%s", 
            request.method, 
            request.url.path, 
            request.client.host, 
            str(exc), 
        )

        return responses.JSONResponse(
            status_code=429,
            content={"detail": str(exc)},
        )

    response = await call_next(request)

    logger.info( 
        "Response: %s %s -> %s", 
        request.method, 
        request.url.path, 
        response.status_code, 
    )

    return response


# ==========================================
# Pydantic Models
class LicenseResponse(BaseModel):
    license_key: str
    user: str


class LicenseCheckResponse(BaseModel):
    valid: bool
    user: str | None = None


@app.get("/")
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
def create_license(user: str):
    """Create and store a new license for an authorized user."""

    logger.info("Creating license for user=%s", user)

    license_key = generate_license_key()

    db = database.get_connection()

    try:
        db.execute(
            """
            INSERT INTO licenses (license_key, user)
            VALUES (?, ?)
            """,
            (license_key, user),
        )

        db.commit()

        logger.info( "License created successfully for user=%s", user, )
    
    except Exception as e:
        logger.exception( "Failed to create license for user=%s", user, )

    finally:
        db.close()

    return LicenseResponse(
        license_key=license_key,
        user=user,
    )


@app.get("/licenses/{license_key}", response_model=LicenseCheckResponse)
def check_license(license_key: str):
    """Check whether a license exists and is currently active."""
    logger.info("Checking license")

    db = database.get_connection()

    try:
        license = db.execute(
            """
            SELECT user, active
            FROM licenses
            WHERE license_key = ?
            """,
            (license_key,),
        ).fetchone()
    finally:
        db.close()

    if license is None or not license["active"]:
        logger.warning( "Inactive license checked for user=%s", license["user"], )
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
