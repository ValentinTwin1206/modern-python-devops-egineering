"""User management workflow on top of the Keycloak client."""

import logging
import re

from fastapi import HTTPException, Request

from ..database.keycloak import KeycloakClient, KeycloakError

logger = logging.getLogger("irislab_api")


class UserService:
    """Apply IrisLab's user rules (validation, roles, admin protection) using Keycloak."""

    APP_USER_ROLE = "app-user"
    APP_ADMIN_ROLE = "app-admin"
    APP_ROLES = (APP_ADMIN_ROLE, APP_USER_ROLE)
    MIN_PASSWORD_LENGTH = 12
    USERNAME_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{2,63}")

    def __init__(self, keycloak: KeycloakClient):
        """Use the given Keycloak client for all account operations."""
        self.keycloak = keycloak

    def _summary(self, user: dict) -> dict:
        """Reduce a Keycloak user to id, username, enabled flag and IrisLab roles."""
        roles = self.keycloak.get_realm_roles(user["id"])
        return {
            "id": user["id"],
            "username": user["username"],
            "enabled": bool(user.get("enabled", False)),
            "roles": [role for role in self.APP_ROLES if role in roles],
        }

    def list_users(self) -> list[dict]:
        """Return a summary of every user in the realm."""
        # GET /roles/{role}/users if the realm grows to thousands of users.
        return [self._summary(user) for user in self.keycloak.list_users()]

    def get_user(self, username: str) -> dict:
        """Return the summary of one user; raise KeycloakError 404 if unknown."""
        user = self.keycloak.find_user(username.strip().lower())
        if user is None:
            raise KeycloakError(f"User '{username}' was not found", 404)
        return self._summary(user)

    def _remove_partial_user(self, user_id: str, username: str) -> None:
        """Delete a half-created user, or at least disable it if deletion fails."""
        try:
            self.keycloak.delete_user(user_id)
            return
        except KeycloakError as error:
            logger.error("Could not remove partially created user %s: %s", username, error)
        try:
            self.keycloak.disable_user(user_id)
        except KeycloakError as error:
            logger.critical("Partially created user %s is still enabled: %s", username, error)


    def create_user(self, username: str, password: str) -> dict:
        """Create an enabled user with a password and the app-user role; roll back on failure."""
        username = username.strip().lower()
        if not self.USERNAME_PATTERN.fullmatch(username):
            raise KeycloakError(
                "Username must be 3-64 characters long, start with a letter or digit, "
                "and contain only letters, digits, '.', '_' or '-'",
                400,
            )
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise KeycloakError(f"Password must contain at least {self.MIN_PASSWORD_LENGTH} characters", 400)

        # The lookup gives a clear error; Keycloak's 409 still covers races.
        if self.keycloak.find_user(username) is not None:
            raise KeycloakError(f"User '{username}' already exists", 409)
        try:
            user_id = self.keycloak.create_user(username)
        except KeycloakError as error:
            if error.status_code == 409:
                raise KeycloakError(f"User '{username}' already exists", 409) from None
            raise

        # set the password and assign the app-user role; roll back if either fails
        try:
            self.keycloak.set_password(user_id, password)
            self.keycloak.assign_realm_role(user_id, self.APP_USER_ROLE)
        except KeycloakError:
            self._remove_partial_user(user_id, username)
            raise

        logger.info("Created user %s", username)
        return {"id": user_id, "username": username}

    def delete_user(self, username: str, acting_user_id: str | None = None) -> dict:
        """Delete a user unless it is the caller or the last enabled administrator."""
        user = self.get_user(username)
        if acting_user_id and user["id"] == acting_user_id:
            raise KeycloakError("You cannot delete your own account", 409)
        if self.APP_ADMIN_ROLE in user["roles"]:
            
            other_admins = [
                u for u in self.list_users()
                if u["id"] != user["id"] and u["enabled"] and self.APP_ADMIN_ROLE in u["roles"]
            ]
            if not other_admins:
                raise KeycloakError("The last administrator cannot be deleted", 409)

        try:
            self.keycloak.delete_user(user["id"])
        except KeycloakError as error:
            if error.status_code == 404:
                raise KeycloakError(f"User '{username}' was not found", 404) from None
            raise

        logger.info("Deleted user %s", user["username"])
        return {"id": user["id"], "username": user["username"]}


def get_user_service(request: Request) -> UserService:
    """Build the request's user service from the lifespan-managed Keycloak client."""
    keycloak = getattr(request.app.state, "keycloak_client", None)
    if keycloak is None:
        raise HTTPException(status_code=503, detail="User management is not configured")
    return UserService(keycloak)
