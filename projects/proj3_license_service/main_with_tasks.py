import uvicorn
from fastapi import Depends, FastAPI
from pydantic import BaseModel

# TODO: import the database and helpers modules


# TODO: create the database instance
database = None


app = FastAPI(
    title="License Service",
    description="Small example service for generating and validating license keys.",
)


# TODO: Create a pydantic LicenseResponse Model that contains
# the license_key and user fields.
# - license_key: str
# - user: str
class LicenseResponse(BaseModel):
    ...


# TODO: Create a pydantic LicenseCheckResponse Model that contains
# the valid and user fields. The user field should be optional.
class LicenseCheckResponse(BaseModel):
    ...


@app.get("/")
def root():
    """Return the service status."""
    return {
        "service": "license-service",
        "status": "ok",
    }


# TODO: Add the LicenseResponse model as the response_model for this endpoint and
# require the require_admin dependency.
@app.post(
    "/licenses",
    response_model=None,
    dependencies=[None],
)
def create_license(user: str):
    """ Create and store a new license for an authorized user.
       Args:
           user (str): The username for which to create a license.
       Returns:
           LicenseResponse: The response containing the license key and user.
    """
    
    # TODO: generate a license Key (check the helpers.py)
    license_key = None

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

    # TODO: return a LicenseResponse object with the license_key and user
    return None


# TODO: 
#   - define the fastapi signatures for the GET /licenses/{license_key} endpoint
#   - add the LicenseCheckResponse model as the response_model for this endpoint.
def check_license(license_key: str):
    """ Check whether a license exists and is currently active.
        Args:
            license_key (str): The license key to check.
        Returns:
            LicenseCheckResponse: The response indicating whether the license is valid and the associated user.
    """
    
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

    # TODO: return a LicenseCheckResponse object with 
    # valid set to True and the user field set to the associated user.
    return None


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
