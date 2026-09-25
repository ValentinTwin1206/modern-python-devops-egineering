import time

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from license_service import helpers
import main
from license_service.database import create_database
from license_service.helpers import ADMIN_API_KEY, TokenError, validate_bearer_token


@pytest.fixture
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(autouse=True)
def stub_jwks(monkeypatch, rsa_key):
    """Serve the locally generated public key instead of Keycloak's JWKS."""

    class _SigningKey:
        def __init__(self, key):
            self.key = key

    monkeypatch.setattr(
        helpers._jwks_client,
        "get_signing_key_from_jwt",
        lambda token: _SigningKey(rsa_key.public_key()),
    )


def _make_token(rsa_key, **overrides):
    claims = {
        "iss": helpers.OIDC_ISSUER_URL,
        "sub": "user-123",
        "exp": int(time.time()) + 300,
        "realm_access": {"roles": ["license-admin"]},
    }
    claims.update(overrides)
    return "Bearer " + pyjwt.encode(claims, rsa_key, algorithm="RS256")


def test_missing_bearer_scheme_is_rejected():
    with pytest.raises(TokenError) as exc:
        validate_bearer_token("Basic abc")
    assert exc.value.status_code == 401


def test_valid_token_returns_claims(rsa_key):
    claims = validate_bearer_token(_make_token(rsa_key))
    assert claims["sub"] == "user-123"


def test_expired_token_is_rejected(rsa_key):
    token = _make_token(rsa_key, exp=int(time.time()) - 10)
    with pytest.raises(TokenError) as exc:
        validate_bearer_token(token)
    assert exc.value.status_code == 401


def test_wrong_issuer_is_rejected(rsa_key):
    token = _make_token(rsa_key, iss="http://evil/realms/other")
    with pytest.raises(TokenError) as exc:
        validate_bearer_token(token)
    assert exc.value.status_code == 401


def test_audience_enforced_when_configured(monkeypatch, rsa_key):
    monkeypatch.setattr(helpers, "OIDC_AUDIENCE", "streamlit-frontend")
    token = _make_token(rsa_key, aud="someone-else")
    with pytest.raises(TokenError) as exc:
        validate_bearer_token(token)
    assert exc.value.status_code == 401


def test_missing_required_role_is_forbidden(monkeypatch, rsa_key):
    monkeypatch.setattr(helpers, "OIDC_REQUIRED_ROLE", "license-admin")
    token = _make_token(rsa_key, realm_access={"roles": ["user"]})
    with pytest.raises(TokenError) as exc:
        validate_bearer_token(token)
    assert exc.value.status_code == 403


def test_authenticated_user_can_get_license(tmp_path, monkeypatch, rsa_key):
    """A normal authenticated user can retrieve the stored token."""
    database = create_database(str(tmp_path / "test.db"))
    database.init()
    monkeypatch.setattr(main, "database", database)
    database.save_license(
        "cloudsmith-token",
        "2099-01-01T00:00:00+00:00",
        "cloudsmith-user-token",
        "",
    )

    client = TestClient(main.app)

    response = client.get(
        "/licenses",
        headers={"Authorization": _make_token(rsa_key)},
    )

    assert response.status_code == 200
    assert response.json()["cloudsmith_token"] == "cloudsmith-token"


def test_admin_license_creation_refreshes_cloudsmith_token(monkeypatch):
    monkeypatch.setattr(
        main,
        "cloudsmith_config",
        main.CloudsmithConfig(
        api_key="secret",
        owner="acme",
            user="service-user",
        repository="packages",
        token_slug_perm="user-token",
        ),
    )
    monkeypatch.setattr(
        main,
        "refresh_and_store_cloudsmith_token",
        lambda config, database: {
            "user": "cloudsmith-user-token",
            "cloudsmith_token": "refreshed-token",
            "cloudsmith_expires_at": "2099-01-01T00:00:00+00:00",
        },
    )

    response = TestClient(main.app).post(
        "/licenses", headers={"X-API-Key": ADMIN_API_KEY}
    )

    assert response.status_code == 200
    assert response.json()["cloudsmith_token"] == "refreshed-token"


