import base64
import hashlib

import pytest

from irislab_cli.auth import (
    OIDCError,
    _callback_port_from_environment,
    _is_secure_endpoint,
    _pkce_pair,
    _validate_callback,
)


def test_callback_requires_matching_state_and_code() -> None:
    params = {"state": ["expected"], "code": ["auth-code"]}
    assert _validate_callback(params, "expected") == "auth-code"

    with pytest.raises(OIDCError, match="state did not match"):
        _validate_callback({"state": ["other"], "code": ["auth-code"]}, "expected")
    with pytest.raises(OIDCError, match="did not contain"):
        _validate_callback({"state": ["expected"]}, "expected")


def test_pkce_pair_uses_s256() -> None:
    verifier, challenge = _pkce_pair()
    expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
    assert 43 <= len(verifier) <= 128
    assert challenge == expected.rstrip(b"=").decode()


def test_oidc_http_endpoints_are_limited_to_localhost() -> None:
    assert _is_secure_endpoint("http://keycloak.localhost:8081/realms/iris-analysis")
    assert _is_secure_endpoint("https://identity.example.test/issuer")
    assert not _is_secure_endpoint("http://identity.example.test/issuer")


def test_callback_port_uses_environment_and_validates_range(monkeypatch) -> None:
    monkeypatch.delenv("IRIS_CLI_CALLBACK_PORT", raising=False)
    assert _callback_port_from_environment() == 8765

    monkeypatch.setenv("IRIS_CLI_CALLBACK_PORT", "9123")
    assert _callback_port_from_environment() == 9123

    monkeypatch.setenv("IRIS_CLI_CALLBACK_PORT", "not-a-port")
    with pytest.raises(OIDCError, match="integer port"):
        _callback_port_from_environment()

    monkeypatch.setenv("IRIS_CLI_CALLBACK_PORT", "70000")
    with pytest.raises(OIDCError, match="between 1 and 65535"):
        _callback_port_from_environment()