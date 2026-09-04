import os
import secrets
import string

from fastapi import Header, HTTPException


ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-secret")


def generate_license_key() -> str:
    """Generate a random license key consisting of four groups of four characters."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

    groups = [
        "".join(secrets.choice(alphabet) for _ in range(4))
        for _ in range(4)
    ]

    return "-".join(groups)


def require_admin(x_api_key: str = Header(...)):
    """Verify that the request contains a valid administrator API key."""
    if not secrets.compare_digest(x_api_key, ADMIN_API_KEY):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )
