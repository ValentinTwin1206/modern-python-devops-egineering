import asyncio
from types import SimpleNamespace

from irislab_api.api.middleware import metrics_middleware as metrics


class FakePoint:
    def __init__(self, measurement):
        self.measurement = measurement
        self.tags = {}
        self.fields = {}

    def tag(self, key, value):
        self.tags[key] = value
        return self

    def field(self, key, value):
        self.fields[key] = value
        return self


class FakeWriteAPI:
    def write(self, **kwargs):
        self.record = kwargs


class FakeInfluxClient:
    def __init__(self, write_api):
        self._write_api = write_api

    def write_api(self, write_options):
        return self._write_api


def test_metrics_middleware_writes_response_metadata(monkeypatch):
    write_api = FakeWriteAPI()
    monkeypatch.setattr(metrics, "Point", FakePoint)
    app = SimpleNamespace(state=SimpleNamespace())
    influxdb_client = FakeInfluxClient(write_api)
    metrics.configure_metrics(app, influxdb_client, "irislab", "api_metrics")
    request = SimpleNamespace(
        app=app,
        method="GET",
        url=SimpleNamespace(path="/api/v1/analyses"),
        client=SimpleNamespace(host="192.0.2.10"),
    )

    async def call_next(_request):
        return SimpleNamespace(status_code=401)

    response = asyncio.run(metrics.metrics_middleware(request, call_next))

    assert response.status_code == 401
    assert write_api.record["bucket"] == "api_metrics"
    assert write_api.record["org"] == "irislab"
    point = write_api.record["record"]
    assert point.measurement == "api_requests"
    assert point.tags == {
        "method": "GET",
        "endpoint": "/api/v1/analyses",
        "client_ip": "192.0.2.10",
    }
    assert point.fields["status_code"] == 401
    assert point.fields["duration_ms"] >= 0


def test_metrics_are_disabled_without_client():
    app = SimpleNamespace(state=SimpleNamespace())
    metrics.configure_metrics(app)

    assert app.state.influxdb_client is None
    assert app.state.influxdb_write_api is None
    assert app.state.influxdb_org is None
    assert app.state.influxdb_bucket is None