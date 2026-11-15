"""Shared HTTP client and JSON output helpers."""

from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
from typing import Any

import click
import requests


# ================================================================
# IrisLab API client and error handling
# ================================================================
class IrisAPIError(RuntimeError):
    """Raised when the IrisLab API returns an error or cannot be reached."""


class IrisAPIClient:
    """Small authenticated client for the public IrisLab API routes."""

    def __init__(self, access_token: str) -> None:
        self.base_url: str             = os.getenv("IRIS_API_URL", "http://localhost:8080").rstrip("/")
        self.timeout: float            = float(os.getenv("IRIS_API_TIMEOUT", "60"))
        self.session: requests.Session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})


    def close(self) -> None:
        self.session.headers.pop("Authorization", None)
        self.session.close()


    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """
        Make an HTTP request to the IrisLab API.

        :param self: The API client instance.
        :param method (str) Description
        :param path (str) Description
        :param kwargs (Any): Description
        :return (Any) Description
        """

        # Build the full URL and make the request, handling errors.
        url: str = f"{self.base_url}{path}"
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
        except requests.HTTPError as error:
            response = error.response
            status = response.status_code if response is not None else "unknown"
            try:
                body = response.json() if response is not None else {}
                detail = body.get("detail", body) if isinstance(body, dict) else body
            except (ValueError, AttributeError):
                detail = response.text if response is not None else str(error)
            raise IrisAPIError(f"HTTP {status}: {detail}") from error
        except requests.RequestException as error:
            message = f"Could not reach IrisLab API at {url}: {error}"
            raise IrisAPIError(message) from error

        # Return the JSON-decoded response body, 
        # or raise an error if it is not valid JSON.
        try:
            return response.json()
        except ValueError as error:
            message = "The API returned a response that is not valid JSON."
            raise IrisAPIError(message) from error


    def get_analysis_history(self) -> list[dict[str, Any]]:
        # Return the authenticated user's analysis history as a list of dictionaries.
        return self._request("GET", "/api/v1/analyses")


    def get_reference_colors(self) -> list[dict[str, Any]]:
        # Return the IrisLab reference colors as a list of dictionaries.
        return self._request("GET", "/api/v1/reference-colors")


    def analyze_image(self, image_path: Path) -> dict[str, Any]:
        # Upload an image file to the IrisLab API for analysis 
        # and return the result as a dictionary.
        content_type = (
            mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
        )
        try:
            with image_path.open("rb") as image:
                return self._request(
                    "POST",
                    "/api/v1/analyses",
                    files={"image": (image_path.name, image, content_type)},
                )
        except OSError as error:
            raise IrisAPIError(f"Could not read image {image_path}: {error}") from error


# ===============================================================
# IrisSession and JSON output helpers
# ================================================================

class IrisSession:
    """Own the authenticated API client for one interactive process."""

    def __init__(self, access_token: str) -> None:
        self.api = IrisAPIClient(access_token)

    def close(self) -> None:
        self.api.close()


def write_json(data: Any, output: Path | None) -> None:
    """Write an API result to stdout or a UTF-8 JSON file."""
    rendered = json.dumps(data, indent=2, ensure_ascii=False)
    if output is None:
        click.echo(rendered)
        return

    try:
        output.write_text(rendered + "\n", encoding="utf-8")
    except OSError as error:
        raise click.ClickException(f"Could not write {output}: {error}") from error

    click.echo(f"Saved JSON to {output}", err=True)