"""Cloudsmith repository verification and entitlement client."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

import requests

logger = logging.getLogger("license-service.cloudsmith")


class CloudsmithConfigurationError(RuntimeError):
    """Raised when Cloudsmith configuration or a request is invalid."""


class CloudsmithConfig:
    def __init__(
        self,
        api_key: str,
        owner: str,
        user: str,
        repository: str,
        api_base_url: str = "https://api.cloudsmith.io",
        timeout_seconds: float = 5.0,
        max_token_duration_seconds: int = 3600,
        token_slug_perm: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.owner = owner
        self.user = user
        self.repository = repository
        self.token_slug_perm = token_slug_perm
        self.api_base_url = api_base_url
        self.timeout_seconds = timeout_seconds
        self.max_token_duration_seconds = max_token_duration_seconds

    @classmethod
    def from_environment(cls) -> CloudsmithConfig | None:
        """Create a CloudsmithConfig from environment variables."""

        # Read configuration values from environment variables,
        # allowing for optional configuration.
        values = {
            name: os.getenv(f"CLOUDSMITH_{name.upper()}") or None
            for name in ("api_key", "owner", "user", "repository")
        }

        configured = [value is not None for value in values.values()]
        
        if not any(configured):
            logger.warning(
                "Cloudsmith is disabled: CLOUDSMITH_API_KEY, "
                "CLOUDSMITH_OWNER, and CLOUDSMITH_REPOSITORY are not set"
            )
            return None
        
        if not all(configured):
            missing = ", ".join(
                f"CLOUDSMITH_{name.upper()}"
                for name, value in values.items()
                if value is None
            )
            logger.error("Cloudsmith configuration is incomplete; missing %s", missing)
            raise CloudsmithConfigurationError(
                f"Incomplete Cloudsmith configuration; missing {missing}"
            )

        try:
            timeout_seconds = float(os.getenv("CLOUDSMITH_TIMEOUT_SECONDS", "5"))
            max_token_duration = int(
                os.getenv("CLOUDSMITH_MAX_TOKEN_DURATION_SECONDS", "3600")
            )
        except ValueError as exc:
            logger.error(
                "Cloudsmith timeout or token duration is not numeric: "
                "CLOUDSMITH_TIMEOUT_SECONDS=%r, "
                "CLOUDSMITH_MAX_TOKEN_DURATION_SECONDS=%r",
                os.getenv("CLOUDSMITH_TIMEOUT_SECONDS"),
                os.getenv("CLOUDSMITH_MAX_TOKEN_DURATION_SECONDS"),
            )
            raise CloudsmithConfigurationError(
                "Cloudsmith timeout and token duration must be numeric"
            ) from exc
        if timeout_seconds <= 0 or max_token_duration <= 0:
            raise CloudsmithConfigurationError(
                "Cloudsmith timeout and token duration must be positive"
            )

        return cls(
            api_key=values["api_key"],
            owner=values["owner"],
            user=values["user"],
            repository=values["repository"],
            token_slug_perm=os.getenv("CLOUDSMITH_TOKEN_SLUG_PERM") or None,
            api_base_url=os.getenv(
                "CLOUDSMITH_API_BASE_URL", "https://api.cloudsmith.io"
            ).rstrip("/"),
            timeout_seconds=timeout_seconds,
            max_token_duration_seconds=max_token_duration,
        )


class CloudsmithClient:
    """ Client for interacting with the Cloudsmith API for repository verification and entitlement management."""
    
    def __init__(self, config: CloudsmithConfig) -> None:
        self.config = config


    def _headers(self) -> dict[str, str]:
        return {"Accept": "application/json", "X-Api-Key": self.config.api_key}


    def verify_repository(self) -> None:
        url = f"{self.config.api_base_url}/v1/repos/{self.config.owner}/{self.config.repository}/"
        payload = self._request("GET", url)
        if not isinstance(payload, dict):
            raise CloudsmithConfigurationError(
                "Cloudsmith repository verification returned an invalid response"
            )
        logger.info(
            "Cloudsmith repository verified: owner=%s repository=%s",
            self.config.owner,
            self.config.repository,
        )


    def refresh_user_token(self) -> dict:
        """Refresh the configured Cloudsmith user token."""
        if not self.config.token_slug_perm:
            raise CloudsmithConfigurationError(
                "CLOUDSMITH_TOKEN_SLUG_PERM is not configured"
            )
        response = self._request(
            "PUT",
            f"{self.config.api_base_url}/v1/user/tokens/"
            f"{self.config.token_slug_perm}/refresh/",
        )
        if not isinstance(response, dict):
            raise CloudsmithConfigurationError(
                "Cloudsmith returned an invalid user token response"
            )

        # Cloudsmith rotates the user token during refresh. Keep the client
        # configuration synchronized so every later request authenticates with
        # the newly issued API key instead of the expired key.
        refreshed_api_key = (
            response.get("token")
            or response.get("key")
            or response.get("api_key")
        )
        if not isinstance(refreshed_api_key, str) or not refreshed_api_key:
            raise CloudsmithConfigurationError(
                "Cloudsmith returned a response without a refreshed API key"
            )
        self.config.api_key = refreshed_api_key

        refreshed_slug_perm = response.get("slug_perm")
        if refreshed_slug_perm is not None:
            if not isinstance(refreshed_slug_perm, str) or not refreshed_slug_perm:
                raise CloudsmithConfigurationError(
                    "Cloudsmith returned an invalid refreshed token slug"
                )
            self.config.token_slug_perm = refreshed_slug_perm
            logger.info(
                "Cloudsmith token slug synchronized: slug_present=%s",
                True,
            )
        return response


    def create_entitlement(
        self,
        subject: str,
        duration_seconds: int,
        *,
        package_query: str | None = None,
        path_query: str | None = None,
        limit_downloads: int | None = None,
        limit_clients: int | None = None,
    ) -> dict:
        """Create a Cloudsmith entitlement token for the given subject."""

        if not subject or duration_seconds <= 0:
            raise CloudsmithConfigurationError("Invalid entitlement request")
        
        if duration_seconds > self.config.max_token_duration_seconds:
            raise CloudsmithConfigurationError("Entitlement duration exceeds the limit")

        # prepare the payload for the entitlement request
        issued_at = datetime.now(timezone.utc)
        payload = {
            "name": f"license-service:{subject}",
            "limit_date_range_from": issued_at.isoformat(),
            "limit_date_range_to": (
                issued_at + timedelta(seconds=duration_seconds)
            ).isoformat(),
        }
        payload.update(
            {
                key: value
                for key, value in {
                    "limit_package_query": package_query,
                    "limit_path_query": path_query,
                    "limit_num_downloads": limit_downloads,
                    "limit_num_clients": limit_clients,
                }.items()
                if value is not None
            }
        )

        # start the request
        response = self._request(
            "POST", 
            f"{self.config.api_base_url}/v1/entitlements/{self.config.owner}/{self.config.repository}/", 
            json=payload
        )

        if not isinstance(response, dict):
            logger.warning("Cloudsmith entitlement request returned an invalid response: %s", response)
            raise CloudsmithConfigurationError(
                "Cloudsmith returned an invalid entitlement response"
            )
        return response


    def revoke_entitlement(self, entitlement_id: str) -> None:
        """Revoke a repository entitlement in Cloudsmith."""
        if not entitlement_id:
            raise CloudsmithConfigurationError("Invalid entitlement identifier")

        self._request(
            "DELETE",
            f"{self.config.api_base_url}/v1/entitlements/"
            f"{self.config.owner}/{self.config.repository}/{entitlement_id}/",
        )


    def _request(self, method: str, url: str, **kwargs) -> dict:
        """Make a request to the Cloudsmith API and return the JSON response."""
        logger.info("Cloudsmith request started: method=%s url=%s", method, url)
        try:
            response = requests.request(
                method,
                url,
                headers=self._headers(),
                timeout=self.config.timeout_seconds,
                **kwargs,
            )
            response.raise_for_status()
            if getattr(response, "status_code", 200) == 204 or not getattr(
                response, "content", True
            ):
                logger.info(
                    "Cloudsmith request succeeded: method=%s status=%s empty_response=%s",
                    method,
                    getattr(response, "status_code", 200),
                    True,
                )
                return {}
            payload = response.json()
            logger.info(
                "Cloudsmith request succeeded: method=%s status=%s response_type=%s",
                method,
                getattr(response, "status_code", 200),
                type(payload).__name__,
            )
            return payload
        except (requests.RequestException, ValueError) as exc:
            status = getattr(locals().get("response"), "status_code", None)
            logger.error(
                "Cloudsmith %s request failed: url=%s status=%s error=%s",
                method,
                url,
                status or "n/a",
                exc,
            )
            raise CloudsmithConfigurationError("Cloudsmith request failed") from exc


def verify_cloudsmith_repository(config: CloudsmithConfig) -> None:
    CloudsmithClient(config).verify_repository()


def verify_cloudsmith_on_startup(config: CloudsmithConfig | None = None) -> None:
    """Verify the already-loaded configuration during application startup."""
    if config is None:
        config = CloudsmithConfig.from_environment()
    if config is None:
        logger.warning("Cloudsmith startup verification skipped because it is disabled")
        return
    logger.info(
        "Verifying Cloudsmith repository owner=%s repository=%s base_url=%s",
        config.owner,
        config.repository,
        config.api_base_url,
    )
    verify_cloudsmith_repository(config)
