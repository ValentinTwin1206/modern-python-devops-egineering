import pytest
from fastapi.testclient import TestClient

import main
from database import create_database
from helpers import ADMIN_API_KEY


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client using an isolated temporary database."""
    database = create_database(str(tmp_path / "test.db"))
    database.init()

    monkeypatch.setattr(main, "database", database)

    return TestClient(main.app)


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "license-service",
        "status": "ok",
    }


def test_create_license_requires_api_key(client):
    response = client.post(
        "/licenses",
        params={"user": "alice"},
    )

    assert response.status_code == 422


def test_create_license_rejects_invalid_api_key(client):
    response = client.post(
        "/licenses",
        params={"user": "alice"},
        headers={"X-API-Key": "invalid-key"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid API key",
    }


def test_create_license(client):
    response = client.post(
        "/licenses",
        params={"user": "alice"},
        headers={"X-API-Key": ADMIN_API_KEY},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user"] == "alice"
    assert data["license_key"]

    # Verify the expected license-key format.
    groups = data["license_key"].split("-")

    assert len(groups) == 4
    assert all(len(group) == 4 for group in groups)


def test_create_and_check_license(client):
    response = client.post(
        "/licenses",
        params={"user": "alice"},
        headers={"X-API-Key": ADMIN_API_KEY},
    )

    assert response.status_code == 200

    license_key = response.json()["license_key"]

    response = client.get(f"/licenses/{license_key}")

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "user": "alice",
    }


def test_check_unknown_license(client):
    response = client.get("/licenses/does-not-exist")

    assert response.status_code == 200
    assert response.json() == {
        "valid": False,
        "user": None,
    }


def test_check_inactive_license(client):
    # Create a license.
    response = client.post(
        "/licenses",
        params={"user": "alice"},
        headers={"X-API-Key": ADMIN_API_KEY},
    )

    license_key = response.json()["license_key"]

    # Manually deactivate it in the test database.
    db = main.database.get_connection()

    try:
        db.execute(
            "UPDATE licenses SET active = 0 WHERE license_key = ?",
            (license_key,),
        )
        db.commit()
    finally:
        db.close()

    # The inactive license should be rejected.
    response = client.get(f"/licenses/{license_key}")

    assert response.status_code == 200
    assert response.json() == {
        "valid": False,
        "user": None,
    }
