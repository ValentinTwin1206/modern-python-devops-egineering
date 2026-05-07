import json
from wsgiref.util import setup_testing_defaults

from tiny_webserver.app import app


def request(path="/"):
    environ = {}
    setup_testing_defaults(environ)
    environ["PATH_INFO"] = path
    environ["REQUEST_METHOD"] = "GET"

    captured = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(app(environ, start_response)).decode("utf-8")
    return captured["status"], captured["headers"], body


def test_index_returns_json_message():
    status, headers, body = request("/")

    assert status.startswith("200")
    assert headers["Content-Type"].startswith("application/json")
    assert json.loads(body) == {"message": "Hello from tiny webserver"}
