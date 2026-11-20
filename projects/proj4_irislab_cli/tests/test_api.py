from pathlib import Path

import pytest
import requests

from irislab_cli.api import IrisAPIClient, IrisAPIError


class Response:
    def __init__(self, value: object, status_code: int = 200) -> None:
        self.value = value
        self.status_code = status_code
        self.content = b"json"
        self.text = str(value)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            error = requests.HTTPError(response=self)
            raise error

    def json(self) -> object:
        return self.value


def test_api_calls_use_bearer_and_upload_image(monkeypatch, tmp_path: Path) -> None:
    client = IrisAPIClient("test-access-token")
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return Response({"ok": True})

    monkeypatch.setattr(
        client.session,
        "request",
        fake_request,
    )
    image_path = tmp_path / "eye.png"
    image_path.write_bytes(b"image-data")

    assert client.analyze_image(image_path) == {"ok": True}
    assert client.get_analysis_history() == {"ok": True}
    assert client.get_reference_colors() == {"ok": True}
    assert client.session.headers["Authorization"] == "Bearer test-access-token"
    assert calls[0][0:2] == ("POST", "http://localhost:8080/api/v1/analyses")
    upload = calls[0][2]["files"]["image"]
    assert upload[0] == "eye.png"
    assert upload[2] == "image/png"
    assert calls[1][1].endswith("/api/v1/analyses")
    assert calls[2][1].endswith("/api/v1/reference-colors")
    client.close()


def test_api_error_contains_status_and_detail(monkeypatch) -> None:
    client = IrisAPIClient("not-for-output")
    monkeypatch.setattr(
        client.session,
        "request",
        lambda *args, **kwargs: Response({"detail": "Unauthorized"}, 401),
    )
    with pytest.raises(IrisAPIError, match="HTTP 401: Unauthorized"):
        client.get_analysis_history()
    client.close()


def test_closing_client_clears_the_access_token() -> None:
    client = IrisAPIClient("short-lived-token")
    client.close()
    assert "Authorization" not in client.session.headers