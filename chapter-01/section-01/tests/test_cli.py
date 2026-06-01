"""Tests for the journal-admin CLI using a fake journal reader."""

import json
from datetime import datetime, timezone

from journal_admin import cli


class FakeReader:
    def __init__(self, entries):
        self._entries = entries
        self.matches = []
        self.log_level_called_with = None
        self.seek_called_with = None

    def add_match(self, **kwargs):
        self.matches.append(kwargs)

    def log_level(self, level):
        self.log_level_called_with = level

    def seek_realtime(self, ts):
        self.seek_called_with = ts

    def __iter__(self):
        return iter(self._entries)


def sample_entry():
    return {
        "__REALTIME_TIMESTAMP": datetime(2026, 5, 24, 10, 0, tzinfo=timezone.utc),
        "_SYSTEMD_UNIT": "ssh.service",
        "PRIORITY": 6,
        "MESSAGE": "Accepted publickey for admin",
    }


def test_read_entries_applies_filters_and_returns_plain_dicts():
    reader = FakeReader([sample_entry()])

    entries = cli.read_entries(
        unit="ssh.service", priority=6, since_minutes=15, reader=reader
    )

    assert reader.matches == [{"_SYSTEMD_UNIT": "ssh.service"}]
    assert reader.log_level_called_with == 6
    assert reader.seek_called_with is not None
    assert entries == [
        {
            "timestamp": "2026-05-24T10:00:00+00:00",
            "unit": "ssh.service",
            "priority": 6,
            "message": "Accepted publickey for admin",
        }
    ]


def test_format_text_uses_priority_names():
    entries = cli.read_entries(reader=FakeReader([sample_entry()]))
    text = cli.format_text(entries)

    assert "[info]" in text
    assert "ssh.service" in text
    assert "Accepted publickey for admin" in text


def test_main_json_output(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_open_reader", lambda: FakeReader([sample_entry()]))

    exit_code = cli.main(["--format", "json", "--since-minutes", "10"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload[0]["unit"] == "ssh.service"
    assert payload[0]["priority"] == 6
