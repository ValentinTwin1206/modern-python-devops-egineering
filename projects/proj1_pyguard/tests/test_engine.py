import pytest

from pyguard import PyGuard, RequestBlocked
from pyguard.rules import BruteForce, PathTraversal, SecurityRule


class AlwaysBlockRule(SecurityRule):
    def check(self, request) -> bool:
        return True


class NeverBlockRule(SecurityRule):
    def check(self, request) -> bool:
        return False


def test_empty_engine_allows_request(request_factory):
    request = request_factory()
    guard = PyGuard()

    result = guard.scan(request)

    assert result.blocked is False
    assert result.reason == ""
    assert guard.check(request) is request


def test_engine_allows_request_when_no_rule_blocks(request_factory):
    request = request_factory(path="/licenses")
    guard = PyGuard(rules=[NeverBlockRule()])

    result = guard.scan(request)

    assert result.blocked is False
    assert result.reason == ""
    assert guard.check(request) is request


def test_engine_returns_name_of_blocking_rule(request_factory):
    request = request_factory(path="/suspicious")
    guard = PyGuard(rules=[AlwaysBlockRule()])

    result = guard.scan(request)

    assert result.blocked is True
    assert result.reason == "AlwaysBlockRule"


def test_check_raises_request_blocked(request_factory):
    request = request_factory(path="/suspicious")
    guard = PyGuard(rules=[AlwaysBlockRule()])

    with pytest.raises(RequestBlocked, match="AlwaysBlockRule"):
        guard.check(request)


def test_engine_stops_after_first_blocking_rule(request_factory):
    class MustNotRunRule(SecurityRule):
        def check(self, request) -> bool:
            pytest.fail("A rule after the first blocking rule must not run")

    guard = PyGuard(rules=[AlwaysBlockRule(), MustNotRunRule()])

    result = guard.scan(request_factory())

    assert result.blocked is True
    assert result.reason == "AlwaysBlockRule"


@pytest.mark.parametrize(
    "value",
    [
        "../etc/passwd",
        "..%2Fetc/passwd",
        "%2e%2e%2fetc/passwd",
        "%252e%252e%252fetc/passwd",
        r"..\windows\system.ini",
    ],
)
def test_path_traversal_detects_path_variants(request_factory, value):
    request = request_factory(path=f"/download/{value}")

    assert PathTraversal().check(request) is True


def test_path_traversal_detects_query(request_factory):
    request = request_factory(
        path="/download",
        query="file=%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    )

    assert PathTraversal().check(request) is True


def test_path_traversal_detects_body(request_factory):
    request = request_factory(
        method="POST",
        path="/upload",
        body='{"filename": "../../etc/passwd"}',
    )

    assert PathTraversal().check(request) is True


@pytest.mark.parametrize(
    ("path", "query", "body"),
    [
        ("/licenses", "", ""),
        ("/users/123", "page=2", ""),
        ("/search", "q=python", '{"active": true}'),
    ],
)
def test_path_traversal_allows_normal_requests(
    request_factory, path, query, body
):
    request = request_factory(path=path, query=query, body=body)

    assert PathTraversal().check(request) is False


def test_brute_force_ignores_unprotected_paths(request_factory):
    rule = BruteForce(paths=["/login"], max_attempts=2)
    request = request_factory(path="/licenses")

    assert rule.check(request) is False
    assert "192.0.2.10" not in rule.attempts


def test_brute_force_blocks_at_max_attempts(request_factory):
    rule = BruteForce(
        paths=["/login"],
        max_attempts=3,
        window=60,
        block_duration=300,
    )
    request = request_factory(path="/login")

    assert rule.check(request) is False
    assert rule.check(request) is False
    assert rule.check(request) is True
    assert rule.is_blocked("192.0.2.10") is True


def test_brute_force_tracks_sources_independently(request_factory):
    rule = BruteForce(paths=["/login"], max_attempts=2)

    first = request_factory(path="/login", source="192.0.2.10")
    second = request_factory(path="/login", source="192.0.2.11")

    assert rule.check(first) is False
    assert rule.check(second) is False
    assert rule.check(first) is True
    assert rule.is_blocked("192.0.2.10") is True
    assert rule.is_blocked("192.0.2.11") is False


def test_brute_force_expires_attempts_outside_window(
    request_factory, monkeypatch
):
    import pyguard.rules as rules_module

    current_time = [100.0]
    monkeypatch.setattr(
        rules_module.time,
        "monotonic",
        lambda: current_time[0],
    )

    rule = BruteForce(
        paths=["/login"],
        max_attempts=2,
        window=10,
        block_duration=30,
    )
    request = request_factory(path="/login")

    assert rule.check(request) is False

    current_time[0] = 111.0
    assert rule.check(request) is False
    assert rule.is_blocked("192.0.2.10") is False
    assert len(rule.attempts["192.0.2.10"]) == 1


def test_cleanup_removes_expired_attempts_and_blocks(
    request_factory, monkeypatch
):
    import pyguard.rules as rules_module

    current_time = [100.0]
    monkeypatch.setattr(
        rules_module.time,
        "monotonic",
        lambda: current_time[0],
    )

    rule = BruteForce(
        paths=["/login"],
        max_attempts=2,
        window=10,
        block_duration=20,
    )
    request = request_factory(path="/login")

    assert rule.check(request) is False
    rule.blocked_until["192.0.2.11"] = 105.0

    current_time[0] = 111.0
    rule._cleanup(current_time[0])

    assert "192.0.2.10" not in rule.attempts
    assert "192.0.2.11" not in rule.blocked_until
