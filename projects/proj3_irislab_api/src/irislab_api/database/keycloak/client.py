"""Keycloak Admin REST API client: the data-access layer for IrisLab user accounts."""

import json
import logging
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger("irislab_api")


class KeycloakError(RuntimeError):
    """Keycloak request failed; status_code mirrors the HTTP status for the API response."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _error_detail(raw: bytes) -> str:
    """Extract Keycloak's error message without echoing large bodies."""
    try:
        body = json.loads(raw)
    except ValueError:
        return "no details"
    if not isinstance(body, dict):
        return "no details"
    return str(
        body.get("errorMessage") or body.get("error_description") or body.get("error") or "no details"
    )


class KeycloakClient:
    """Thin wrapper around the realm Admin REST API calls IrisLab needs."""

    TOKEN_REFRESH_MARGIN_SECONDS = 30
    PAGE_SIZE = 100

    def __init__(
        self,
        server_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        timeout: float = 10.0,
    ):
        """Store connection settings; no request is sent until the first call."""
        self.server_url = server_url.rstrip("/")
        self.realm = realm
        self.client_id = client_id
        self._client_secret = client_secret
        self.timeout = timeout
        self._admin_url = f"{self.server_url}/admin/realms/{quote(realm, safe='')}"
        self._token: str | None = None
        self._token_expires_at = 0.0
        self._lock = threading.Lock()

    # -----------------------------------------------------------------------
    # HTTP helpers
    # -----------------------------------------------------------------------
    def _send(self, method: str, url: str, body: bytes | None = None, headers: dict | None = None):
        """Send one HTTP request and return (headers, parsed JSON body or None)."""
        request = Request(url, data=body, method=method, headers=headers or {})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                return response.headers, json.loads(raw) if raw else None
        except HTTPError as error:
            raise KeycloakError(
                f"Keycloak returned HTTP {error.code}: {_error_detail(error.read())}",
                error.code,
            ) from None
        except (URLError, OSError) as error:
            raise KeycloakError(f"Keycloak is unreachable: {error}") from None
        except ValueError:
            raise KeycloakError("Keycloak returned invalid JSON") from None

    def authenticate(self) -> str:
        """Return a cached service-account token, requesting a new one shortly before expiry."""
        with self._lock:
            if self._token and time.monotonic() < self._token_expires_at:
                return self._token

            form = urlencode(
                {
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self._client_secret,
                }
            ).encode()
            _, payload = self._send(
                "POST",
                f"{self.server_url}/realms/{quote(self.realm, safe='')}/protocol/openid-connect/token",
                body=form,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            try:
                token = payload["access_token"]
                expires_in = float(payload.get("expires_in", 60))
            except (TypeError, KeyError, ValueError):
                raise KeycloakError("Keycloak returned an invalid token response") from None

            self._token = token
            self._token_expires_at = time.monotonic() + max(expires_in - self.TOKEN_REFRESH_MARGIN_SECONDS, 0)
            logger.info("Obtained Keycloak admin token for client %s", self.client_id)
            return token

    def _admin(self, method: str, path: str, payload=None):
        """Call the realm Admin API; on HTTP 401 refresh the token and retry once."""
        body = json.dumps(payload).encode() if payload is not None else None
        for attempt in range(2):
            headers = {"Authorization": f"Bearer {self.authenticate()}"}
            if body is not None:
                headers["Content-Type"] = "application/json"
            try:
                return self._send(method, self._admin_url + path, body=body, headers=headers)
            except KeycloakError as error:
                if error.status_code != 401 or attempt:
                    raise
                with self._lock:
                    self._token = None

    # -----------------------------------------------------------------------
    # Users
    # -----------------------------------------------------------------------
    def find_user(self, username: str) -> dict | None:
        """Return the Keycloak user with this exact username, or None."""
        query = urlencode({"username": username, "exact": "true"})
        _, users = self._admin("GET", f"/users?{query}")
        return next(iter(users or []), None)

    def list_users(self) -> list[dict]:
        """Return all Keycloak users of the realm, fetched page by page."""
        users, first = [], 0
        while True:
            query = urlencode({"first": first, "max": self.PAGE_SIZE})
            _, page = self._admin("GET", f"/users?{query}")
            users.extend(page or [])
            if len(page or []) < self.PAGE_SIZE:
                return users
            first += self.PAGE_SIZE

    def get_realm_roles(self, user_id: str) -> set[str]:
        """Return the user's effective realm roles, including composite and group roles."""
        _, roles = self._admin("GET", f"/users/{quote(user_id, safe='')}/role-mappings/realm/composite")
        return {role["name"] for role in roles or []}

    def create_user(self, username: str) -> str:
        """Create an enabled user without credentials and return its id."""
        headers, _ = self._admin("POST", "/users", {"username": username, "enabled": True})
        location = (headers.get("Location") or "").rstrip("/")
        return location.rsplit("/", 1)[-1] if location else self.find_user(username)["id"]

    def set_password(self, user_id: str, password: str) -> None:
        """Set a permanent password through Keycloak's credentials API."""
        self._admin(
            "PUT",
            f"/users/{quote(user_id, safe='')}/reset-password",
            {"type": "password", "value": password, "temporary": False},
        )

    def assign_realm_role(self, user_id: str, role_name: str) -> None:
        """Map an existing realm role to the user."""
        path = f"/users/{quote(user_id, safe='')}/role-mappings/realm"
        _, available = self._admin("GET", f"{path}/available")
        role = next((r for r in available or [] if r.get("name") == role_name), None)
        if role is None:
            raise KeycloakError(f"Realm role '{role_name}' cannot be assigned")
        self._admin("POST", path, [{"id": role["id"], "name": role["name"]}])

    def disable_user(self, user_id: str) -> None:
        """Disable the user so it can no longer sign in."""
        self._admin("PUT", f"/users/{quote(user_id, safe='')}", {"enabled": False})

    def delete_user(self, user_id: str) -> None:
        """Delete the user permanently."""
        self._admin("DELETE", f"/users/{quote(user_id, safe='')}")
