"""KeycloakClient and UserService tests against a fake Admin REST API (no running Keycloak)."""

import json
import logging
from io import BytesIO
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

import pytest

from irislab_api.database import keycloak
from irislab_api.database.keycloak import KeycloakClient, KeycloakError, bootstrap_keycloak, client as keycloak_client
from irislab_api.services.users import UserService

TOKEN = "/realms/iris-analysis/protocol/openid-connect/token"
ADMIN = "/admin/realms/iris-analysis"
PASSWORD = "correct-horse-battery"
APP_USER = {"id": "role-user", "name": "app-user"}
APP_ADMIN = {"id": "role-admin", "name": "app-admin"}


class FakeResponse:
    def __init__(self, payload, headers):
        self.headers = headers
        self.body = b"" if payload is None else json.dumps(payload).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeKeycloak:
    """Route (method, path?query) to queued (status, payload, headers) replies."""

    def __init__(self):
        self.routes = {}
        self.calls = []
        self.on("POST", TOKEN, (200, {"access_token": "tok-1", "expires_in": 300}))

    def on(self, method, path, *replies):
        self.routes[(method, path)] = list(replies)

    def count(self, method, path):
        return sum(1 for call in self.calls if call[:2] == (method, path))

    def __call__(self, request, timeout):
        url = urlsplit(request.full_url)
        path = url.path + (f"?{url.query}" if url.query else "")
        key = (request.get_method(), path)
        self.calls.append((*key, request))
        replies = self.routes[key]
        status, payload, *headers = replies.pop(0) if len(replies) > 1 else replies[0]
        if status >= 400:
            raise HTTPError(request.full_url, status, "error", {}, BytesIO(json.dumps(payload or {}).encode()))
        return FakeResponse(payload, headers[0] if headers else {})


@pytest.fixture
def server(monkeypatch):
    fake = FakeKeycloak()
    monkeypatch.setattr(keycloak_client, "urlopen", fake)
    return fake


@pytest.fixture
def kc():
    return KeycloakClient("http://keycloak:8080/", "iris-analysis", "iris-admin-service", "s3cret", timeout=2)


@pytest.fixture
def service(kc):
    return UserService(kc)


def user(user_id, username, enabled=True):
    return {"id": user_id, "username": username, "enabled": enabled}


def given_users(server, *users_and_roles):
    server.on("GET", f"{ADMIN}/users?first=0&max=100", (200, [u for u, _ in users_and_roles]))
    for u, roles in users_and_roles:
        server.on("GET", f"{ADMIN}/users?username={u['username']}&exact=true", (200, [u]))
        server.on("GET", f"{ADMIN}/users/{u['id']}/role-mappings/realm/composite", (200, roles))


def given_create_flow(server):
    server.on("GET", f"{ADMIN}/users?username=alice&exact=true", (200, []))
    server.on("POST", f"{ADMIN}/users", (201, None, {"Location": f"http://keycloak:8080{ADMIN}/users/u-1"}))
    server.on("PUT", f"{ADMIN}/users/u-1/reset-password", (204, None))
    server.on("GET", f"{ADMIN}/users/u-1/role-mappings/realm/available", (200, [APP_ADMIN, APP_USER]))
    server.on("POST", f"{ADMIN}/users/u-1/role-mappings/realm", (204, None))
    server.on("DELETE", f"{ADMIN}/users/u-1", (204, None))


# ---------------------------------------------------------------------------
# KeycloakClient: configuration and authentication
# ---------------------------------------------------------------------------
def test_bootstrap_keycloak(monkeypatch):
    for name in keycloak.CONFIG_VARIABLES:
        monkeypatch.setenv(name, "value")
    app = SimpleNamespace(state=SimpleNamespace())
    bootstrap_keycloak(app)
    assert isinstance(app.state.keycloak_client, KeycloakClient)

    monkeypatch.delenv("KEYCLOAK_ADMIN_CLIENT_SECRET")
    bootstrap_keycloak(app)
    assert app.state.keycloak_client is None


def test_authenticate_uses_client_credentials_and_caches_token(server, kc):
    given_users(server)
    assert kc.authenticate() == "tok-1"
    kc.list_users()
    kc.list_users()

    assert server.count("POST", TOKEN) == 1
    form = server.calls[0][2].data.decode()
    assert "grant_type=client_credentials" in form and "client_id=iris-admin-service" in form
    assert server.calls[-1][2].get_header("Authorization") == "Bearer tok-1"


def test_token_is_refreshed_shortly_before_expiry(server, kc):
    # expires_in below the refresh margin makes the cached token immediately stale.
    server.on("POST", TOKEN, (200, {"access_token": "tok-1", "expires_in": 10}),
              (200, {"access_token": "tok-2", "expires_in": 10}))
    given_users(server)
    kc.list_users()
    kc.list_users()

    assert server.count("POST", TOKEN) == 2
    assert server.calls[-1][2].get_header("Authorization") == "Bearer tok-2"


def test_rejected_token_is_refreshed_once(server, kc):
    server.on("POST", TOKEN, (200, {"access_token": "tok-1", "expires_in": 300}),
              (200, {"access_token": "tok-2", "expires_in": 300}))
    server.on("GET", f"{ADMIN}/users?first=0&max=100", (401, {"error": "expired"}), (200, []))
    assert kc.list_users() == []
    assert server.count("POST", TOKEN) == 2


def test_failed_authentication_raises(server, kc):
    server.on("POST", TOKEN, (401, {"error": "invalid_client", "error_description": "Invalid client credentials"}))
    with pytest.raises(KeycloakError) as error:
        kc.authenticate()
    assert error.value.status_code == 401
    assert "Invalid client credentials" in str(error.value)
    assert "s3cret" not in str(error.value)


def test_keycloak_server_error(server, kc):
    server.on("GET", f"{ADMIN}/users?first=0&max=100", (500, {"error": "unknown_error"}))
    with pytest.raises(KeycloakError) as error:
        kc.list_users()
    assert error.value.status_code == 500


def test_keycloak_unreachable(monkeypatch, kc):
    def unreachable(request, timeout):
        assert timeout == 2
        raise URLError("connection refused")

    monkeypatch.setattr(keycloak_client, "urlopen", unreachable)
    with pytest.raises(KeycloakError, match="unreachable"):
        kc.authenticate()


# ---------------------------------------------------------------------------
# UserService: listing and validation
# ---------------------------------------------------------------------------
def test_list_users_returns_application_roles_only(server, service):
    given_users(
        server,
        (user("u-1", "iris-admin"), [APP_ADMIN, APP_USER, {"id": "x", "name": "offline_access"}]),
        (user("u-2", "bob", enabled=False), [APP_USER]),
    )
    assert service.list_users() == [
        {"id": "u-1", "username": "iris-admin", "enabled": True, "roles": ["app-admin", "app-user"]},
        {"id": "u-2", "username": "bob", "enabled": False, "roles": ["app-user"]},
    ]


def test_username_and_password_validation(server, service):
    for invalid in ["", "ab", "-alice", "alice smith", "alice@example.com", "a" * 65]:
        with pytest.raises(KeycloakError, match="Username") as error:
            service.create_user(invalid, PASSWORD)
        assert error.value.status_code == 400
    with pytest.raises(KeycloakError, match="at least 12") as error:
        service.create_user("alice", "x" * 11)
    assert error.value.status_code == 400
    assert server.calls == []


# ---------------------------------------------------------------------------
# UserService: creation
# ---------------------------------------------------------------------------
def test_create_user_sets_password_and_assigns_app_user(server, service, caplog):
    given_create_flow(server)
    with caplog.at_level(logging.DEBUG):
        assert service.create_user("Alice", PASSWORD) == {"id": "u-1", "username": "alice"}

    created = json.loads(next(c[2].data for c in server.calls if c[:2] == ("POST", f"{ADMIN}/users")))
    assert created == {"username": "alice", "enabled": True}
    password = json.loads(next(c[2].data for c in server.calls if c[1].endswith("reset-password")))
    assert password == {"type": "password", "value": PASSWORD, "temporary": False}
    mapped = json.loads(next(c[2].data for c in server.calls if c[:2] == ("POST", f"{ADMIN}/users/u-1/role-mappings/realm")))
    assert mapped == [APP_USER]
    assert server.count("DELETE", f"{ADMIN}/users/u-1") == 0
    assert PASSWORD not in caplog.text and "s3cret" not in caplog.text and "tok-1" not in caplog.text


def test_create_user_rejects_existing_username(server, service):
    server.on("GET", f"{ADMIN}/users?username=alice&exact=true", (200, [user("u-1", "alice")]))
    with pytest.raises(KeycloakError, match="already exists") as error:
        service.create_user("alice", PASSWORD)
    assert error.value.status_code == 409
    assert server.count("POST", f"{ADMIN}/users") == 0


def test_create_user_maps_keycloak_conflict(server, service):
    given_create_flow(server)
    server.on("POST", f"{ADMIN}/users", (409, {"errorMessage": "User exists with same username"}))
    with pytest.raises(KeycloakError, match="already exists") as error:
        service.create_user("alice", PASSWORD)
    assert error.value.status_code == 409


def test_password_failure_removes_partial_user(server, service):
    given_create_flow(server)
    server.on("PUT", f"{ADMIN}/users/u-1/reset-password", (400, {"errorMessage": "invalidPasswordMinLengthMessage"}))
    with pytest.raises(KeycloakError) as error:
        service.create_user("alice", PASSWORD)
    assert error.value.status_code == 400
    assert server.count("DELETE", f"{ADMIN}/users/u-1") == 1


def test_role_failure_removes_or_disables_partial_user(server, service):
    given_create_flow(server)
    server.on("GET", f"{ADMIN}/users/u-1/role-mappings/realm/available", (200, [APP_ADMIN]))
    server.on("DELETE", f"{ADMIN}/users/u-1", (500, {}))
    server.on("PUT", f"{ADMIN}/users/u-1", (204, None))
    with pytest.raises(KeycloakError, match="app-user"):
        service.create_user("alice", PASSWORD)
    disabled = json.loads(next(c[2].data for c in server.calls if c[:2] == ("PUT", f"{ADMIN}/users/u-1")))
    assert disabled == {"enabled": False}


# ---------------------------------------------------------------------------
# UserService: deletion
# ---------------------------------------------------------------------------
def test_delete_user(server, service):
    given_users(server, (user("u-1", "admin"), [APP_ADMIN, APP_USER]), (user("u-2", "bob"), [APP_USER]))
    server.on("DELETE", f"{ADMIN}/users/u-2", (204, None))
    assert service.delete_user("Bob", acting_user_id="u-1") == {"id": "u-2", "username": "bob"}


def test_delete_unknown_user(server, service):
    server.on("GET", f"{ADMIN}/users?username=ghost&exact=true", (200, []))
    with pytest.raises(KeycloakError, match="not found") as error:
        service.delete_user("ghost")
    assert error.value.status_code == 404


def test_delete_prevents_self_deletion(server, service):
    given_users(server, (user("u-1", "admin"), [APP_ADMIN]), (user("u-2", "admin2"), [APP_ADMIN]))
    with pytest.raises(KeycloakError, match="own account"):
        service.delete_user("admin", acting_user_id="u-1")
    assert server.count("DELETE", f"{ADMIN}/users/u-1") == 0


def test_delete_prevents_removing_last_enabled_admin(server, service):
    given_users(
        server,
        (user("u-1", "admin"), [APP_ADMIN]),
        (user("u-2", "disabled-admin", enabled=False), [APP_ADMIN]),
    )
    with pytest.raises(KeycloakError, match="last administrator"):
        service.delete_user("admin", acting_user_id="u-9")


def test_delete_admin_when_another_admin_exists(server, service):
    given_users(server, (user("u-1", "admin"), [APP_ADMIN]), (user("u-2", "admin2"), [APP_ADMIN]))
    server.on("DELETE", f"{ADMIN}/users/u-2", (204, None))
    assert service.delete_user("admin2", acting_user_id="u-1")["id"] == "u-2"
