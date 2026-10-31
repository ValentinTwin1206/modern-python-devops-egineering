"""Exercise the HTTP contract without invoking model inference."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from irislab import ColorAnalysisResult, EyeColorDetectionError
from irislab.eye_color import EyeColor
from PIL import Image

from irislab_api.main import create_app
from irislab_api.services import analysis


@pytest.fixture
def client(tmp_path, monkeypatch):
    model = tmp_path / "model.task"
    model.write_bytes(b"model")
    monkeypatch.setenv("IRISLAB_MODEL_PATH", str(model))
    with TestClient(create_app()) as test_client:
        yield test_client


def image_bytes(image_format="PNG"):
    stream = BytesIO()
    Image.new("RGB", (20, 20), (20, 100, 150)).save(stream, format=image_format)
    return stream.getvalue()


def test_health_and_reference_colors(client, monkeypatch, tmp_path):
    assert client.get("/health/live").json() == {"status": "alive"}
    assert client.get("/health/ready").status_code == 200
    colors = client.get("/api/v1/reference-colors").json()
    assert len(colors) == 6
    assert colors[0] == {"name": "Blue-01", "eye_color": "Blue", "rgb": [92, 126, 145]}
    monkeypatch.setenv("IRISLAB_MODEL_PATH", str(tmp_path / "missing"))
    assert client.get("/health/ready").status_code == 503


def test_analysis_serializes_result_and_cleans_up_upload(client, monkeypatch):
    paths = []

    def fake_analyze(path, device):
        assert path.is_file()
        assert device == "cpu"
        paths.append(path)
        return ColorAnalysisResult(EyeColor.BLUE, (1, 2, 3), (4.0, 5.0, 6.0),
                                   (7.0, 8.0, 9.0), 10.0, 11.0, "Blue-01",
                                   (92, 126, 145), 12.0, "iris-segmentation", 0.95, 2)

    monkeypatch.setattr(analysis, "analyze", fake_analyze)
    response = client.post("/api/v1/analyses", files={"image": ("portrait.png", image_bytes(), "image/png")})
    assert response.status_code == 200
    assert response.json()["eye_color"] == "Blue"
    assert response.json()["eye_rgb"] == [1, 2, 3]
    assert response.json()["eyes_detected"] == 2
    assert not paths[0].exists()


def test_invalid_and_oversized_uploads(client, monkeypatch):
    assert client.post("/api/v1/analyses", files={"image": ("x.png", b"invalid", "image/png")}).status_code == 415
    assert client.post("/api/v1/analyses", files={"image": ("x.gif", image_bytes("GIF"), "image/gif")}).status_code == 415
    monkeypatch.setattr(analysis, "MAX_UPLOAD_BYTES", 4)
    assert client.post("/api/v1/analyses", files={"image": ("x.png", b"12345", "image/png")}).status_code == 413


def test_detection_failure_and_missing_model(client, monkeypatch, tmp_path):
    def no_iris(*args, **kwargs):
        raise EyeColorDetectionError("No iris detected")

    monkeypatch.setattr(analysis, "analyze", no_iris)
    files = {"image": ("x.png", image_bytes(), "image/png")}
    assert client.post("/api/v1/analyses", files=files).status_code == 422
    monkeypatch.setenv("IRISLAB_MODEL_PATH", str(tmp_path / "missing"))
    assert client.post("/api/v1/analyses", files=files).status_code == 503
