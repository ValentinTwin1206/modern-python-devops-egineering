import os
import secrets

from fastapi import Header, HTTPException, Request

ADMIN_API_KEY:str    = os.getenv("ADMIN_API_KEY")


def require_admin(x_api_key: str = Header(...)):
    if not secrets.compare_digest(x_api_key, ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


def is_admin(x_api_key: str | None) -> bool:
    return x_api_key is not None and secrets.compare_digest(x_api_key, ADMIN_API_KEY)


def require_admin_or_user(
    request: Request,
    x_api_key: str | None = Header(default=None),
):
    if is_admin(x_api_key) or getattr(request.state, "jwt_claims", None) is not None:
        return
    raise HTTPException(status_code=401, detail="Authentication required")
