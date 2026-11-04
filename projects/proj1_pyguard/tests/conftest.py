from pathlib import Path
import sys

import pytest

# Support the src/ package layout when pytest is run from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if SRC_DIR.is_dir():
    sys.path.insert(0, str(SRC_DIR))

from pyguard import PyGuard


@pytest.fixture
def request_factory():
    """Factory for creating PyGuard request objects."""

    def _make_request(
        *,
        method="GET",
        path="/",
        query="",
        body="",
        source="192.0.2.10",
    ):
        return PyGuard.Request(
            method=method,
            path=path,
            query=query,
            body=body,
            source=source,
        )

    return _make_request