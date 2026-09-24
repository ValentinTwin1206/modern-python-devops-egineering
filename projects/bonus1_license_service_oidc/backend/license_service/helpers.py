import os
import secrets

import jwt
from fastapi import Header, HTTPException, Request
from jwt import PyJWKClient

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-secret")
OIDC_ISSUER_URL = os.getenv(
    "OIDC_ISSUER_URL", "http://localhost:8081/realms/license-service"
)
OIDC_JWKS_URL = os.getenv(
    "OIDC_JWKS_URL",
    "http://keycloak:8080/realms/license-service/protocol/openid-connect/certs",
)
OIDC_AUDIENCE = os.getenv("OIDC_AUDIENCE")
OIDC_REQUIRED_ROLE = os.getenv("OIDC_REQUIRED_ROLE")
_jwks_client = PyJWKClient(OIDC_JWKS_URL)


class TokenError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


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


def validate_bearer_token(authorization: str) -> dict:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise TokenError(401, "Invalid authorization header")
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=OIDC_ISSUER_URL,
            audience=OIDC_AUDIENCE,
            options={"verify_aud": OIDC_AUDIENCE is not None},
        )
    except jwt.PyJWTError as exc:
        raise TokenError(401, f"Invalid token: {exc}") from exc
    if OIDC_REQUIRED_ROLE:
        roles = claims.get("realm_access", {}).get("roles", [])
        if OIDC_REQUIRED_ROLE not in roles:
            raise TokenError(403, "Insufficient role")
    return claims
