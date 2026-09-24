import pytest

import main
from pyguard import PyGuardMiddleware
from license_service.middleware import PROTECTED_PATHS


@pytest.fixture(autouse=True)
def reset_pyguard(monkeypatch):
    """Isolate PyGuard's brute-force state between tests.

    The guard is a module-level singleton keyed by request source. Without a
    reset, the shared "testclient" source accumulates attempts across tests and
    trips the rate limiter, causing unrelated tests to fail.
    """
    monkeypatch.setattr(
        main,
        "guard",
        PyGuardMiddleware(protected_paths=PROTECTED_PATHS),
    )
    monkeypatch.setattr(main.app.state, "guard", main.guard)
