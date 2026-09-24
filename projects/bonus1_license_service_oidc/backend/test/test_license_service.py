import pytest
from fastapi.testclient import TestClient

import main
from license_service.database import create_database
from license_service.helpers import ADMIN_API_KEY


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client using an isolated temporary database."""
    database = create_database(str(tmp_path / "test.db"))
    database.init()
    monkeypatch.setattr(main, "database", database)
    return TestClient(main.app)


def configure_cloudsmith(monkeypatch):
    config = main.CloudsmithConfig(
        api_key="secret",
        owner="acme",
        user="service-user",
        repository="packages",
        token_slug_perm="user-token",
    )
    monkeypatch.setattr(main, "cloudsmith_config", config)
    return config


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "license-service",
        "status": "ok",
    }


def test_create_license_requires_admin(client):
    response = client.post("/licenses")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["header", "x-api-key"]


def test_create_license_rejects_invalid_api_key(client):
    response = client.post("/licenses", headers={"X-API-Key": "invalid-key"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}


def test_create_license_refreshes_and_stores_token(client, monkeypatch):
    configure_cloudsmith(monkeypatch)

    def fake_refresh(config, database):
        assert config.owner == "acme"
        database.save_license(
            "cloudsmith-token",
            "2099-01-01T00:00:00+00:00",
            "cloudsmith-user-token",
            "",
        )
        return {
            "user": "cloudsmith-user-token",
            "cloudsmith_token": "cloudsmith-token",
            "cloudsmith_expires_at": "2099-01-01T00:00:00+00:00",
        }

    monkeypatch.setattr(main, "refresh_and_store_cloudsmith_token", fake_refresh)
    response = client.post("/licenses", headers={"X-API-Key": ADMIN_API_KEY})

    assert response.status_code == 200
    assert response.json() == {
        "user": "cloudsmith-user-token",
        "cloudsmith_token": "cloudsmith-token",
        "cloudsmith_expires_at": "2099-01-01T00:00:00+00:00",
    }


def test_get_license_requires_authentication(client):
    response = client.get("/licenses")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_check_license_token(client):
    main.database.save_license(
        "cloudsmith-token",
        "2099-01-01T00:00:00+00:00",
        "cloudsmith-user-token",
        "",
    )

    response = client.get("/licenses/cloudsmith-token")

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "user": "cloudsmith-user-token",
    }


def test_check_unknown_license(client):
    response = client.get("/licenses/does-not-exist")

    assert response.status_code == 200
    assert response.json() == {"valid": False, "user": None}


def test_check_inactive_license(client):
    main.database.save_license(
        "inactive-token",
        "2099-01-01T00:00:00+00:00",
        "cloudsmith-user-token",
        "",
    )
    db = main.database.get_connection()
    try:
        db.execute(
            "UPDATE licenses SET active = 0 WHERE cloudsmith_token = ?",
            ("inactive-token",),
        )
        db.commit()
    finally:
        db.close()

    response = client.get("/licenses/inactive-token")

    assert response.status_code == 200
    assert response.json() == {"valid": False, "user": None}
