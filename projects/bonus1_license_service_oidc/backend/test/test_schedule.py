from datetime import datetime, timezone

import schedule
from license_service.cloudsmith import CloudsmithConfig


class FakeDatabase:
    def __init__(self):
        self.saved = None

    def save_license(self, *args):
        self.saved = args


def test_refresh_and_store_cloudsmith_token(monkeypatch):
    class FakeClient:
        def __init__(self, config):
            assert config.token_slug_perm == "user-token"

        def refresh_user_token(self):
            return {"token": "refreshed-token"}

    monkeypatch.setattr(schedule, "CloudsmithClient", FakeClient)
    database = FakeDatabase()
    config = CloudsmithConfig(
        api_key="secret",
        owner="acme",
        user="service-user",
        repository="packages",
        token_slug_perm="user-token",
    )

    result = schedule.refresh_and_store_cloudsmith_token(config, database)

    assert result["user"] == "cloudsmith-user-token"
    assert result["cloudsmith_token"] == "refreshed-token"
    assert database.saved[0] == "refreshed-token"
    assert database.saved[2:] == (
        "cloudsmith-user-token",
        "",
        None,
        "user-token",
    )
    expires_at = datetime.fromisoformat(database.saved[1])
    remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()
    assert 3590 < remaining <= 3600
