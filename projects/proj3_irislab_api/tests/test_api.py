"""Exercise the HTTP contract without invoking model inference."""

import base64
from io import BytesIO

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient
from irislab import ColorAnalysisResult, EyeColorDetectionError
from irislab.eye_color import EyeColor
from PIL import Image

from irislab_api.main import create_app
from irislab_api.api.middleware import jwt_middleware
from irislab_api import main
from irislab_api.database import mongo
from irislab_api.services import analysis

AUTH_HEADERS = {"Authorization": "Bearer test-token"}


class FakeCollection:
    def __init__(self):
        self.documents = []

    def create_index(self, *args, **kwargs):
        return None

    def insert_one(self, document):
        document = dict(document)
        document.setdefault("_id", ObjectId())
        self.documents.append(document)
        return type("InsertResult", (), {"inserted_id": document["_id"]})()

    def find_one(self, query):
        return next((doc for doc in self.documents if all(doc.get(k) == v for k, v in query.items())), None)

    def find(self, query):
        return [doc for doc in self.documents if all(doc.get(k) == v for k, v in query.items())]

    def update_one(self, query, update, upsert=False):
        document = self.find_one(query)
        if document is None and upsert:
            document = {"_id": ObjectId(), **update.get("$setOnInsert", {})}
            self.documents.append(document)
        elif document is not None:
            for key, value in update.get("$addToSet", {}).items():
                document.setdefault(key, [])
                if value not in document[key]:
                    document[key].append(value)
        return type("UpdateResult", (), {"matched_count": int(document is not None)})()

    def delete_one(self, query):
        document = self.find_one(query)
        if document is not None:
            self.documents.remove(document)


class FakeDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        return self.collections.setdefault(name, FakeCollection())


class FakeMongoClient:
    def __init__(self, uri):
        self.database = FakeDatabase()
        self.closed = False

    def __getitem__(self, name):
        return self.database

    def close(self):
        self.closed = True


class FakeGridFS:
    def __init__(self, database):
        self.files = {}

    def upload_from_stream(self, filename, source, metadata=None):
        file_id = ObjectId()
        self.files[file_id] = {"filename": filename, "data": source.read(), "metadata": metadata}
        return file_id

    def delete(self, file_id):
        self.files.pop(file_id)

    def open_download_stream(self, file_id):
        file = self.files[file_id]
        stream = BytesIO(file["data"])
        stream.filename = file["filename"]
        stream.metadata = file["metadata"]
        return stream


@pytest.fixture
def client(tmp_path, monkeypatch):
    model = tmp_path / "model.task"
    model.write_bytes(b"model")
    monkeypatch.setenv("IRISLAB_MODEL_PATH", str(model))
    monkeypatch.setenv("MONGODB_URI", "mongodb://fake")
    monkeypatch.setenv("MONGODB_DATABASE", "irislab_test")
    mongo_clients = []
    monkeypatch.setattr(main, "MongoClient", lambda uri: mongo_clients.append(FakeMongoClient(uri)) or mongo_clients[-1])
    monkeypatch.setattr(mongo, "GridFSBucket", FakeGridFS)
    monkeypatch.setattr(jwt_middleware, "_validate_bearer_token", lambda authorization: {"sub": "user-123"})
    with TestClient(create_app()) as test_client:
        yield test_client
    assert mongo_clients[0].closed


def image_bytes(image_format="PNG"):
    stream = BytesIO()
    Image.new("RGB", (20, 20), (20, 100, 150)).save(stream, format=image_format)
    return stream.getvalue()


def test_health_and_reference_colors(client, monkeypatch, tmp_path):
    assert client.get("/health/live").json() == {"status": "alive"}
    assert client.get("/health/ready").status_code == 200
    colors = client.get("/api/v1/reference-colors", headers=AUTH_HEADERS).json()
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
    original_image = image_bytes()
    assert client.post("/api/v1/analyses", files={"image": ("portrait.png", original_image, "image/png")}).status_code == 401
    response = client.post(
        "/api/v1/analyses",
        files={"image": ("portrait.png", original_image, "image/png")},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["eye_color"] == "Blue"
    assert response.json()["eye_rgb"] == [1, 2, 3]
    assert response.json()["eyes_detected"] == 2
    assert not paths[0].exists()
    stored_analysis = client.app.state.analysis_db.collection.documents[0]
    stored_user = client.app.state.users_db.collection.documents[0]
    stored_image = client.app.state.gridfs.files[stored_analysis["image_id"]]
    assert stored_image["data"] == original_image
    assert stored_analysis["result"]["eye_color"] == "Blue"
    assert stored_user["analyses"] == [stored_analysis["_id"]]


def test_analysis_history_returns_user_image_and_result(client, monkeypatch):
    def fake_analyze(path, device):
        return ColorAnalysisResult(EyeColor.BLUE, (1, 2, 3), (4.0, 5.0, 6.0),
                                   (7.0, 8.0, 9.0), 10.0, 11.0, "Blue-01",
                                   (92, 126, 145), 12.0, "iris-segmentation", 0.95, 2)

    monkeypatch.setattr(analysis, "analyze", fake_analyze)
    original_image = image_bytes()
    created = client.post(
        "/api/v1/analyses",
        files={"image": ("portrait.png", original_image, "image/png")},
        headers=AUTH_HEADERS,
    )
    assert created.status_code == 200

    response = client.get("/api/v1/analyses", headers=AUTH_HEADERS)

    assert response.status_code == 200
    [item] = response.json()
    assert item["result"]["eye_color"] == "Blue"
    assert item["image_base64"] == base64.b64encode(original_image).decode("ascii")
    assert item["filename"] == "portrait.png"
    assert item["content_type"] == "image/png"
    assert item["id"]


def test_analysis_history_requires_authentication(client):
    assert client.get("/api/v1/analyses").status_code == 401


def test_reference_colors_requires_authentication(client):
    assert client.get("/api/v1/reference-colors").status_code == 401


def test_invalid_token_returns_401(client, monkeypatch):
    def reject_token(_authorization):
        raise jwt_middleware.TokenError(401, "Invalid token")

    monkeypatch.setattr(jwt_middleware, "_validate_bearer_token", reject_token)
    response = client.get("/api/v1/reference-colors", headers=AUTH_HEADERS)

    assert response.status_code == 401


def test_missing_required_role_returns_403(client, monkeypatch):
    def reject_role(_authorization):
        raise jwt_middleware.TokenError(403, "Insufficient role")

    monkeypatch.setattr(jwt_middleware, "_validate_bearer_token", reject_role)
    response = client.get("/api/v1/analyses", headers=AUTH_HEADERS)

    assert response.status_code == 403


def test_repeated_auth_failures_temporarily_block_client_ip(client, monkeypatch):
    def reject_token(_authorization):
        raise jwt_middleware.TokenError(401, "Invalid token")

    monkeypatch.setattr(jwt_middleware, "_validate_bearer_token", reject_token)
    client.app.state.guard.rules[1].max_attempts = 5

    for _ in range(5):
        assert client.get("/api/v1/analyses", headers=AUTH_HEADERS).status_code == 401

    brute_force = client.app.state.guard.rules[1]
    assert len(brute_force.attempts["testclient"]) == 5
    assert brute_force.is_blocked("testclient") is True
    response = client.get("/api/v1/analyses", headers=AUTH_HEADERS)
    assert response.status_code == 429


def test_analysis_storage_failure_cleans_up_gridfs_and_document(client, monkeypatch):
    def fake_analyze(path, device):
        return ColorAnalysisResult(EyeColor.BLUE, (1, 2, 3), (4.0, 5.0, 6.0),
                                   (7.0, 8.0, 9.0), 10.0, 11.0, "Blue-01",
                                   (92, 126, 145), 12.0, "iris-segmentation", 0.95, 2)

    monkeypatch.setattr(analysis, "analyze", fake_analyze)
    monkeypatch.setattr(client.app.state.users_db, "add_analysis_id", lambda *args: (_ for _ in ()).throw(RuntimeError("write failed")))
    response = client.post(
        "/api/v1/analyses",
        files={"image": ("portrait.png", image_bytes(), "image/png")},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 503
    assert client.app.state.analysis_db.collection.documents == []
    assert client.app.state.gridfs.files == {}


def test_invalid_and_oversized_uploads(client, monkeypatch):
    assert client.post("/api/v1/analyses", files={"image": ("x.png", b"invalid", "image/png")}, headers=AUTH_HEADERS).status_code == 415
    assert client.post("/api/v1/analyses", files={"image": ("x.gif", image_bytes("GIF"), "image/gif")}, headers=AUTH_HEADERS).status_code == 415
    monkeypatch.setattr(analysis, "MAX_UPLOAD_BYTES", 4)
    assert client.post("/api/v1/analyses", files={"image": ("x.png", b"12345", "image/png")}, headers=AUTH_HEADERS).status_code == 413


def test_detection_failure_and_missing_model(client, monkeypatch, tmp_path):
    def no_iris(*args, **kwargs):
        raise EyeColorDetectionError("No iris detected")

    monkeypatch.setattr(analysis, "analyze", no_iris)
    files = {"image": ("x.png", image_bytes(), "image/png")}
    assert client.post("/api/v1/analyses", files=files, headers=AUTH_HEADERS).status_code == 422
    monkeypatch.setenv("IRISLAB_MODEL_PATH", str(tmp_path / "missing"))
    assert client.post("/api/v1/analyses", files=files, headers=AUTH_HEADERS).status_code == 503
