from license_service.middleware import _safe_request_path


def test_safe_request_path_redacts_license_tokens():
    assert _safe_request_path("/licenses/secret-token") == "/licenses/{token}"
    assert _safe_request_path("/licenses") == "/licenses"
    assert _safe_request_path("/licenses/") == "/licenses/"
    assert _safe_request_path("/health") == "/health"
