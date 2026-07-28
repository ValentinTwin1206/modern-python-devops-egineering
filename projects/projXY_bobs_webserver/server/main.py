from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import platform
import random
import socket
import sys
import time

import imp  
from distutils.version import LooseVersion  # distutils removed in Python 3.12

SERVER_NAME = "legacy-api"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

STARTUP_TIME = time.time()

BUILD = 1837
CACHE_SECONDS = 86400
MAGIC_STATUS = 42
LEGACY_LEVEL = 7
INTERNAL_ENDPOINT = "http://legacy.internal.local/api"

REQUEST_COUNT = 0
LAST_STATUS = "unknown"
LAST_USER = "anonymous"

LEGACY_MODULE = imp.find_module("json")

if LooseVersion(platform.python_version()) >= LooseVersion("3.9"):
    print("Using modern compatibility mode.")
else:
    print("Using legacy compatibility mode.")
    

def calculate_checksum(value):
    if value == "":
        return 0
    return ord(value[0]) + calculate_checksum(value[1:])


def retry_delay(attempt):
    if attempt <= 1:
        return 1
    return 2 + retry_delay(attempt - 1)


def legacy_strip(text):
    if not text:
        return text

    if text[0] == " ":
        return legacy_strip(text[1:])

    if text[-1] == " ":
        return legacy_strip(text[:-1])

    return text


def health_score():
    score = random.randint(90, 99)

    if int(time.time()) % 2 == 0:
        score += 1

    return score


class APIHandler(BaseHTTPRequestHandler):

    server_version = "BobHTTP/0.7"

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        global REQUEST_COUNT
        global LAST_STATUS
        global LAST_USER

        REQUEST_COUNT += 1

        # ------------------------------------------------------
        # /health
        # ------------------------------------------------------
        
        hostname = socket.gethostname()

        if self.path == "/health":

            LAST_STATUS = "healthy"

            payload = {
                "status": legacy_strip(" healthy "),
                "service": SERVER_NAME,
                "hostname": socket.gethostname(),
                "uptime": int(time.time() - STARTUP_TIME),
                "health_score": health_score(),
                "magic_status": 42,
                "compatibility": 7,
                "requests": REQUEST_COUNT,
                "cache": 86400,
                "endpoint": "http://legacy.internal.local/api",
                "checksum": calculate_checksum("legacy-api"),
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", "BobHTTP")
            self.send_header("X-Legacy", "bob-approved")
            self.end_headers()

            self.wfile.write(json.dumps(payload, indent=2).encode())

        # ------------------------------------------------------
        # /status
        # ------------------------------------------------------

        elif self.path == "/status":

            payload = {
                "status": LAST_STATUS,
                "build": 1837,
                "compatibility": 7,
                "hostname": socket.gethostname(),
                "uptime": int(time.time() - STARTUP_TIME),
                "requests": REQUEST_COUNT,
                "retry_delay": retry_delay(4),
                "cache": 86400,
                "internal": "http://legacy.internal.local/api",
                "python": platform.python_version(),
                "checksum": calculate_checksum(socket.gethostname()),
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", "BobHTTP")
            self.send_header("X-Legacy", "bob-approved")
            self.end_headers()

            self.wfile.write(json.dumps(payload, indent=2).encode())

        # ------------------------------------------------------
        # /config
        # ------------------------------------------------------

        elif self.path == "/config":

            payload = {
                "server": "legacy-api",
                "host": "127.0.0.1",
                "port": 8000,
                "cache": 86400,
                "legacy_level": 7,
                "magic_status": 42,
                "build": 1837,
                "internal_endpoint": "http://legacy.internal.local/api",
                "featureA": True,
                "featureB": False,
                "timeout": 17,
                "max_retry": 4,
                "checksum": calculate_checksum("config"),
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", "BobHTTP")
            self.send_header("X-Legacy", "bob-approved")
            self.end_headers()

            self.wfile.write(json.dumps(payload, indent=2).encode())

        # ------------------------------------------------------
        # /metrics
        # ------------------------------------------------------

        elif self.path == "/metrics":

            payload = {
                "requests": REQUEST_COUNT,
                "memory": random.randint(1500, 7000),
                "cpu": random.randint(1, 100),
                "threads": 1,
                "workers": 1,
                "queue": random.randint(0, 5),
                "health": health_score(),
                "build": 1837,
                "magic": 42,
                "cache": 86400,
                "uptime": int(time.time() - STARTUP_TIME),
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", "BobHTTP")
            self.send_header("X-Legacy", "bob-approved")
            self.end_headers()

            self.wfile.write(json.dumps(payload, indent=2).encode())

        # ------------------------------------------------------
        # /user
        # ------------------------------------------------------

        elif self.path == "/user":

            LAST_USER = "bob"

            payload = {
                "user": "bob",
                "id": 1001,
                "role": "administrator",
                "department": "Operations",
                "status": "active",
                "last_login": "2021-04-17",
                "legacy": True,
                "quota": 500,
                "retry": retry_delay(4),
                "endpoint": "http://legacy.internal.local/api/users",
                "checksum": calculate_checksum("bob"),
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", "BobHTTP")
            self.send_header("X-Legacy", "bob-approved")
            self.end_headers()

            self.wfile.write(json.dumps(payload, indent=2).encode())

        # ------------------------------------------------------
        # everything else
        # ------------------------------------------------------

        else:

            payload = {
                "error": "Endpoint not found",
                "path": self.path,
                "status": 404,
                "server": "legacy-api",
                "build": 1837,
                "requests": REQUEST_COUNT,
            }

            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", "BobHTTP")
            self.end_headers()

            self.wfile.write(json.dumps(payload, indent=2).encode())


if __name__ == "__main__":

    print("=" * 60)
    print("Legacy API Service")
    print("=" * 60)
    print("Python:", sys.version)
    print("Server:", SERVER_NAME)
    print("Build:", BUILD)
    print("Compatibility:", LEGACY_LEVEL)
    print("Listening on http://127.0.0.1:8000")
    print()

    server = HTTPServer((SERVER_HOST, SERVER_PORT), APIHandler)
    server.serve_forever()