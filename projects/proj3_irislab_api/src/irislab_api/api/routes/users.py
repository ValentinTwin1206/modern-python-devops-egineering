"""Administrator-only user management endpoints backed by Keycloak."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from ...database.keycloak import KeycloakError
from ...schemas.users import UserCreate, UserReference, UserSummary
from ...services.users import UserService, get_user_service

logger = logging.getLogger("irislab_api")
router = APIRouter()
CLIENT_ERROR_CODES = {400, 404, 409}


def require_app_admin(request: Request) -> dict:
    """Allow only tokens that carry the app-admin realm role."""
    claims = getattr(request.state, "jwt_claims", None)
    if claims is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    if UserService.APP_ADMIN_ROLE not in claims.get("realm_access", {}).get("roles", []):
        raise HTTPException(status_code=403, detail="Insufficient role")
    return claims


def _to_http_error(error: KeycloakError) -> HTTPException:
    # Invalid input, unknown user and conflicts are passed on; anything else is an outage.
    if error.status_code in CLIENT_ERROR_CODES:
        return HTTPException(status_code=error.status_code, detail=str(error))
    logger.error("User management request failed: %s", error)
    return HTTPException(status_code=503, detail="User management is unavailable")


Admin = Annotated[dict, Depends(require_app_admin)]
Service = Annotated[UserService, Depends(get_user_service)]

# ===============================================================
# Endpoints
# ===============================================================
@router.get("/users", response_model=list[UserSummary])
def list_users(_claims: Admin, service: Service) -> list[dict]:
    try:
        return service.list_users()
    except KeycloakError as error:
        raise _to_http_error(error) from error


@router.post("/users", response_model=UserReference, status_code=201)
def create_user(user: UserCreate, _claims: Admin, service: Service) -> dict:
    try:
        return service.create_user(user.username, user.password.get_secret_value())
    except KeycloakError as error:
        raise _to_http_error(error) from error


@router.delete("/users/{username}", response_model=UserReference)
def delete_user(username: str, claims: Admin, service: Service) -> dict:
    try:
        return service.delete_user(username, acting_user_id=claims["sub"])
    except KeycloakError as error:
        raise _to_http_error(error) from error
