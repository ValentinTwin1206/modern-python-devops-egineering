import pytest

from license_service import cloudsmith


def test_cloudsmith_configuration_is_optional(monkeypatch):
    for name in (
        "CLOUDSMITH_API_KEY",
        "CLOUDSMITH_OWNER",
        "CLOUDSMITH_USER",
        "CLOUDSMITH_REPOSITORY",
    ):
        monkeypatch.delenv(name, raising=False)

    assert cloudsmith.CloudsmithConfig.from_environment() is None


def test_partial_cloudsmith_configuration_is_rejected(monkeypatch):
    monkeypatch.setenv("CLOUDSMITH_API_KEY", "secret")
    monkeypatch.delenv("CLOUDSMITH_OWNER", raising=False)
    monkeypatch.setenv("CLOUDSMITH_REPOSITORY", "packages")

    with pytest.raises(cloudsmith.CloudsmithConfigurationError, match="CLOUDSMITH_OWNER"):
        cloudsmith.CloudsmithConfig.from_environment()


def test_cloudsmith_configuration_reads_limits(monkeypatch):
    monkeypatch.setenv("CLOUDSMITH_API_KEY", "secret")
    monkeypatch.setenv("CLOUDSMITH_OWNER", "acme")
    monkeypatch.setenv("CLOUDSMITH_USER", "service-user")
    monkeypatch.setenv("CLOUDSMITH_REPOSITORY", "packages")
    monkeypatch.setenv("CLOUDSMITH_API_BASE_URL", "https://cloudsmith.test/")
    monkeypatch.setenv("CLOUDSMITH_TIMEOUT_SECONDS", "3")
    monkeypatch.setenv("CLOUDSMITH_MAX_TOKEN_DURATION_SECONDS", "900")

    config = cloudsmith.CloudsmithConfig.from_environment()

    assert config.api_base_url == "https://cloudsmith.test"
    assert config.timeout_seconds == 3
    assert config.max_token_duration_seconds == 900


def test_repository_verification_uses_scoped_api_request(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"slug": "packages"}

    captured = {}

    def fake_request(method, url, headers, timeout):
        assert method == "GET"
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(cloudsmith.requests, "request", fake_request)

    config = cloudsmith.CloudsmithConfig(
        api_key="secret",
        owner="acme",
        user="service-user",
        repository="packages",
        timeout_seconds=3,
    )
    cloudsmith.verify_cloudsmith_repository(config)

    assert captured["url"] == (
        "https://api.cloudsmith.io/v1/repos/acme/packages/"
    )
    assert captured["headers"]["X-Api-Key"] == "secret"
    assert captured["timeout"] == 3


def test_client_refreshes_user_token(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"token": "refreshed-token", "slug_perm": "refreshed-slug"}

    captured = {}

    def fake_request(method, url, headers, timeout):
        captured.update(method=method, url=url, headers=headers, timeout=timeout)
        return Response()

    monkeypatch.setattr(cloudsmith.requests, "request", fake_request)
    config = cloudsmith.CloudsmithConfig(
        api_key="secret",
        owner="acme",
        user="service-user",
        repository="packages",
        token_slug_perm="user-token",
    )

    result = cloudsmith.CloudsmithClient(config).refresh_user_token()

    assert result == {"token": "refreshed-token", "slug_perm": "refreshed-slug"}
    assert config.api_key == "refreshed-token"
    assert config.token_slug_perm == "refreshed-slug"
    assert captured["method"] == "PUT"
    assert captured["url"] == (
        "https://api.cloudsmith.io/v1/user/tokens/user-token/refresh/"
    )
    assert captured["headers"]["X-Api-Key"] == "secret"
    assert captured["timeout"] == 5.0


def test_client_creates_limited_entitlement(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"token": "entitlement-token", "slug": "entitlement-1"}

    captured = {}

    def fake_request(method, url, headers, timeout, json):
        captured.update(method=method, url=url, headers=headers, timeout=timeout, json=json)
        return Response()

    monkeypatch.setattr(cloudsmith.requests, "request", fake_request)
    config = cloudsmith.CloudsmithConfig(
        api_key="secret",
        owner="acme",
        user="service-user",
        repository="packages",
        max_token_duration_seconds=900,
    )

    result = cloudsmith.CloudsmithClient(config).create_entitlement(
        "user-123",
        300,
        package_query="name:demo",
    )

    assert result["token"] == "entitlement-token"
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/v1/entitlements/acme/packages/")
    assert captured["json"]["name"] == "license-service:user-123"
    assert captured["json"]["limit_package_query"] == "name:demo"
    assert captured["timeout"] == 5.0


def test_client_rejects_duration_above_configured_limit():
    config = cloudsmith.CloudsmithConfig(
        api_key="secret",
        owner="acme",
        user="service-user",
        repository="packages",
        max_token_duration_seconds=60,
    )

    with pytest.raises(cloudsmith.CloudsmithConfigurationError):
        cloudsmith.CloudsmithClient(config).create_entitlement("user-123", 61)
