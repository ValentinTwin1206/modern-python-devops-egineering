"""HTTP client for the IrisLab API."""

import os
from typing import Any

import requests


class IrisAPIError(RuntimeError):
    """Raised when the IrisLab API returns an error or cannot be reached."""


class IrisAPIClient:
    def __init__(self, access_token: str | None = None):
        self.base_url = os.getenv("IRIS_API_URL", "http://localhost:8000").rstrip("/")
        self.timeout = float(os.getenv("IRIS_API_TIMEOUT", "60"))
        self.session = requests.Session()
        if access_token:
            # Sent consistently so the frontend is ready for the future
            # IrisLab authentication middleware. The current routes may ignore it.
            self.session.headers.update(
                {"Authorization": f"Bearer {access_token}"}
            )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            try:
                detail = exc.response.json().get("detail", exc.response.text)
            except (ValueError, AttributeError):
                detail = str(exc)
            raise IrisAPIError(f"HTTP {status}: {detail}") from exc
        except requests.RequestException as exc:
            raise IrisAPIError(f"Could not reach IrisLab API at {url}: {exc}") from exc

        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise IrisAPIError("The API returned a response that is not valid JSON.") from exc

    def get_reference_colors(self) -> list:
        return self._request("GET", "/api/v1/reference-colors")

    def analyze_image(
        self,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> dict:
        return self._request(
            "POST",
            "/api/v1/analyses",
            files={
                "image": (
                    filename,
                    content,
                    content_type,
                )
            },
        )
