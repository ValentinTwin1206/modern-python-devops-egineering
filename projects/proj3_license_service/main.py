import uvicorn

from fastapi  import Depends, FastAPI, HTTPException, responses, Request as FastAPIRequest
from pydantic import BaseModel

from database import create_database
from helpers  import generate_license_key, require_admin


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

    try:
        guard.before_request(guard_request)
    except RequestBlocked as exc:
        return responses.JSONResponse(
            status_code=429,
            content={"detail": str(exc)},
        )

    return await call_next(request)


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
    finally:
        db.close()

    return LicenseResponse(
        license_key=license_key,
        user=user,
    )


@app.get("/licenses/{license_key}", response_model=LicenseCheckResponse)
def check_license(license_key: str):
    """Check whether a license exists and is currently active."""
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
        return LicenseCheckResponse(valid=False)

    return LicenseCheckResponse(
        valid=True,
        user=license["user"],
    )


def main():
    """Initialize the database and start the FastAPI service."""
    print("Initializing database...")
    database.init()

    print("Starting license service...")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8800,
    )


if __name__ == "__main__":
    main()
