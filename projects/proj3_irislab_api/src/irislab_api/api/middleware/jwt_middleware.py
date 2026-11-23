"""JWT authentication middleware for protected API operations."""

import logging
import os
from functools import lru_cache

from fastapi import Request as FastAPIRequest, responses
import jwt
from jwt import PyJWKClient

logger = logging.getLogger("iris-lab")
PROTECTED_PATHS = {
    ("GET", "/api/v1/reference-colors"),
    ("GET", "/api/v1/analyses"),
    ("POST", "/api/v1/analyses"),
}

# =========================================
# Environment Variables
# =========================================
class TokenError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@lru_cache(maxsize=1)
def _jwks_client(url: str) -> PyJWKClient:
    """
    Create a cached PyJWKClient instance.

    :param url (str): The URL of the JWKS endpoint
    :return (PyJWKClient): Cached PyJWKClient instances
    """
    return PyJWKClient(url)


def _is_jwt_protected(request: FastAPIRequest) -> bool:
    # Protect analyses, user management and license operations, including dynamic revocation.
    path = request.url.path
    return (
        (request.method, path) in PROTECTED_PATHS
        or path == "/api/v1/users"
        or path.startswith("/api/v1/users/")
        or (request.method == "DELETE" and path.startswith("/licenses/"))
    )


def _validate_bearer_token(authorization: str) -> dict:
    """
    Validate a bearer token and return its claims.

    :param authorization (str): The authorization header containing the bearer token
    :return (dict): The decoded JWT claims
    """

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise TokenError(401, "Invalid authorization header")
    
    # Validate the token using the JWKS endpoint and check for required claims
    issuer         = os.getenv("OIDC_ISSUER_URL")
    jwks_url       = os.getenv("OIDC_JWKS_URL")
    audience       = os.getenv("OIDC_AUDIENCE")
    required_role  = os.getenv("OIDC_REQUIRED_ROLE")

    if not issuer or not jwks_url:
        raise TokenError(503, "OIDC authentication is not configured")
    
    # Validate the token using the JWKS endpoint
    try:
        signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            audience=audience,
            options={"verify_aud": audience is not None},
        )
    except jwt.PyJWTError as exc:
        raise TokenError(401, f"Invalid token: {exc}") from exc
    
    # Check for required role and subject claim
    if required_role:
        roles = claims.get("realm_access", {}).get("roles", [])
        if required_role not in roles:
            raise TokenError(403, "Insufficient role")
        
    if not claims.get("sub"):
        raise TokenError(401, "Token is missing subject")
    
    return claims


async def jwt_auth_middleware(request: FastAPIRequest, call_next):
    """Validate bearer tokens on protected operations."""

    # Check if the request is for a protected path
    if _is_jwt_protected(request):
        authorization = request.headers.get("Authorization")
        if not authorization:
            return responses.JSONResponse(
                status_code=401,
                content={"detail": "Authorization header is required"},
            )
        
        # Validate the bearer token and set the claims in the request state
        try:
            claims = _validate_bearer_token(authorization)
        except TokenError as exc:
            logger.warning("Token rejected: %s", exc.detail)
            return responses.JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        
        # Set the validated claims in the request state for downstream access
        request.state.jwt_claims = claims
        logger.info("Token accepted for sub=%s", claims.get("sub"))

    return await call_next(request)
