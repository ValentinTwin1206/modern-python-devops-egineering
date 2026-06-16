"""Tests for the simply-journal-admin CLI.

The suite never touches a real systemd journal or a real Windows Event Log.
Both backends are exercised through dependency injection (``reader=`` for
Linux, ``backend=`` for Windows) and through monkeypatched module imports.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

from simply_journal_admin import cli, constants


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


class FakeReader:
    """Minimal stand-in for ``systemd.journal.Reader``."""

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


def parse_args(argv):
    return cli.build_parser().parse_args(argv)


# --------------------------------------------------------------------------- #
# Platform detection
# --------------------------------------------------------------------------- #


def test_is_windows_and_is_linux_are_mutually_exclusive():
    assert cli.is_windows() != cli.is_linux()


def test_is_windows_true(monkeypatch):
    monkeypatch.setattr(cli.sys, "platform", "win32")
    assert cli.is_windows() is True
    assert cli.is_linux() is False


def test_is_linux_true(monkeypatch):
    monkeypatch.setattr(cli.sys, "platform", "linux")
    assert cli.is_linux() is True
    assert cli.is_windows() is False


# --------------------------------------------------------------------------- #
# Linux backend
# --------------------------------------------------------------------------- #


def test_read_linux_entries_applies_filters_and_returns_plain_dicts():
    reader = FakeReader([sample_entry()])

    entries = cli.read_linux_entries(
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


def test_read_entries_backward_compatible_signature():
    # The historic public entry point still accepts ``reader=`` and applies
    # filters the same way it did before the Windows refactor.
    reader = FakeReader([sample_entry()])
    entries = cli.read_entries(
        unit="ssh.service", priority=6, since_minutes=15, reader=reader
    )
    assert entries[0]["unit"] == "ssh.service"


def test_read_linux_entries_honours_limit():
    entries = [sample_entry() for _ in range(5)]
    result = cli.read_linux_entries(reader=FakeReader(entries), limit=2)
    assert len(result) == 2


def test_read_linux_entries_opens_reader_when_none(monkeypatch):
    fake = FakeReader([sample_entry()])
    monkeypatch.setattr(cli, "_open_reader", lambda: fake)
    result = cli.read_linux_entries()
    assert result[0]["unit"] == "ssh.service"


def test_open_reader_missing_systemd_raises(monkeypatch):
    # Simulate ``from systemd import journal`` failing.
    monkeypatch.setitem(sys.modules, "systemd", None)
    with pytest.raises(cli.MissingDependencyError):
        cli._open_reader()


def test_format_text_uses_priority_names():
    entries = cli.read_linux_entries(reader=FakeReader([sample_entry()]))
    text = cli.format_text(entries)

    assert "[info]" in text
    assert "ssh.service" in text
    assert "Accepted publickey for admin" in text


def test_format_text_unknown_priority_falls_back_to_number():
    text = cli.format_text(
        [{"timestamp": "t", "unit": "u", "priority": 99, "message": "m"}]
    )
    assert "[99]" in text


# --------------------------------------------------------------------------- #
# Windows backend - mappings
# --------------------------------------------------------------------------- #


def test_windows_eventtype_priority_mapping():
    assert cli.WINDOWS_EVENTTYPE_PRIORITY[1] == 3  # error -> err
    assert cli.WINDOWS_EVENTTYPE_PRIORITY[2] == 4  # warning -> warning
    assert cli.WINDOWS_EVENTTYPE_PRIORITY[4] == 6  # information -> info
    assert cli.WINDOWS_EVENTTYPE_PRIORITY[8] == 5  # audit success -> notice


def test_windows_level_priority_mapping():
    assert cli.WINDOWS_LEVEL_PRIORITY[1] == 2  # critical -> crit
    assert cli.WINDOWS_LEVEL_PRIORITY[2] == 3  # error -> err
    assert cli.WINDOWS_LEVEL_PRIORITY[3] == 4  # warning -> warning
    assert cli.WINDOWS_LEVEL_PRIORITY[5] == 7  # verbose -> debug


# --------------------------------------------------------------------------- #
# Windows backend - read_windows_entries with injected backend
# --------------------------------------------------------------------------- #


def windows_event(priority=3, source="Application Error", message="boom"):
    return {
        "timestamp": "2026-05-24T10:00:00+00:00",
        "unit": source,
        "priority": priority,
        "message": message,
    }


def test_read_windows_entries_returns_entries_from_backend():
    def backend(log_name, cutoff, limit):
        assert log_name == "Application"
        return [windows_event()]

    entries = cli.read_windows_entries(backend=backend)
    assert entries == [windows_event()]


def test_read_windows_entries_filters_by_priority():
    def backend(log_name, cutoff, limit):
        return [
            windows_event(priority=3, message="error"),
            windows_event(priority=6, message="info"),
        ]

    entries = cli.read_windows_entries(priority=4, backend=backend)
    messages = [e["message"] for e in entries]
    assert messages == ["error"]  # info (6) filtered out by max priority 4


def test_read_windows_entries_honours_limit():
    def backend(log_name, cutoff, limit):
        return [windows_event(message=str(i)) for i in range(10)]

    entries = cli.read_windows_entries(limit=3, backend=backend)
    assert len(entries) == 3


def test_read_windows_entries_invalid_log_name_raises():
    with pytest.raises(cli.InvalidLogError):
        cli.read_windows_entries(log_name="DoesNotExist")


def test_read_windows_entries_passes_log_name_to_backend():
    captured = {}

    def backend(log_name, cutoff, limit):
        captured["log_name"] = log_name
        return []

    cli.read_windows_entries(log_name="System", backend=backend)
    assert captured["log_name"] == "System"


# --------------------------------------------------------------------------- #
# Windows backend - backend selection / pywin32 fallback
# --------------------------------------------------------------------------- #


def test_select_windows_backend_falls_back_without_pywin32(monkeypatch):
    monkeypatch.setitem(sys.modules, "win32evtlog", None)
    assert cli._select_windows_backend() is cli._read_windows_wevtutil


def test_select_windows_backend_prefers_pywin32(monkeypatch):
    fake_module = type(sys)("win32evtlog")
    monkeypatch.setitem(sys.modules, "win32evtlog", fake_module)
    assert cli._select_windows_backend() is cli._read_windows_win32


# --------------------------------------------------------------------------- #
# Windows backend - win32evtlog reader
# --------------------------------------------------------------------------- #


class FakeRecord:
    def __init__(self, time_generated, source, event_type, inserts):
        self.TimeGenerated = time_generated
        self.SourceName = source
        self.EventType = event_type
        self.StringInserts = inserts


def make_fake_win32evtlog(records, fail_open=None):
    module = type(sys)("win32evtlog")
    module.EVENTLOG_BACKWARDS_READ = 0x0008
    module.EVENTLOG_SEQUENTIAL_READ = 0x0001

    def open_event_log(server, log_name):
        if fail_open:
            raise fail_open
        return {"log": log_name}

    state = {"served": False}

    def read_event_log(handle, flags, offset):
        if state["served"]:
            return []
        state["served"] = True
        return list(records)

    module.OpenEventLog = open_event_log
    module.ReadEventLog = read_event_log
    module.CloseEventLog = lambda handle: None
    return module


def test_read_windows_win32_normalizes_records(monkeypatch):
    now = int(datetime.now(timezone.utc).timestamp())
    record = FakeRecord(
        time_generated=now,
        source="Application Error",
        event_type=1,  # EVENTLOG_ERROR_TYPE -> priority 3
        inserts=["Faulting application name", "myapp.exe"],
    )
    module = make_fake_win32evtlog([record])
    monkeypatch.setitem(sys.modules, "win32evtlog", module)

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
    entries = cli._read_windows_win32("Application", cutoff, limit=100)

    assert len(entries) == 1
    assert entries[0]["unit"] == "Application Error"
    assert entries[0]["priority"] == 3
    assert "myapp.exe" in entries[0]["message"]


def test_read_windows_win32_stops_at_cutoff(monkeypatch):
    old = int((datetime.now(timezone.utc) - timedelta(hours=5)).timestamp())
    record = FakeRecord(old, "Old Source", 4, ["too old"])
    module = make_fake_win32evtlog([record])
    monkeypatch.setitem(sys.modules, "win32evtlog", module)

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
    entries = cli._read_windows_win32("Application", cutoff, limit=100)
    assert entries == []


def test_read_windows_win32_access_denied(monkeypatch):
    module = make_fake_win32evtlog([], fail_open=OSError("Access is denied."))
    monkeypatch.setitem(sys.modules, "win32evtlog", module)

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
    with pytest.raises(cli.PermissionDeniedError):
        cli._read_windows_win32("Security", cutoff, limit=100)


def test_read_windows_win32_invalid_log(monkeypatch):
    module = make_fake_win32evtlog([], fail_open=OSError("The log does not exist"))
    monkeypatch.setitem(sys.modules, "win32evtlog", module)

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
    with pytest.raises(cli.InvalidLogError):
        cli._read_windows_win32("Application", cutoff, limit=100)


# --------------------------------------------------------------------------- #
# Windows backend - wevtutil parser and subprocess wrapper
# --------------------------------------------------------------------------- #


WEVTUTIL_XML = (
    "<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>"
    "<System>"
    "<Provider Name='Application Error'/>"
    "<Level>2</Level>"
    "<TimeCreated SystemTime='2026-05-24T10:00:00.000000Z'/>"
    "</System>"
    "<EventData><Data>Faulting application myapp.exe</Data></EventData>"
    "</Event>"
)


def test_parse_wevtutil_xml_maps_fields():
    cutoff = datetime(2000, 1, 1, tzinfo=timezone.utc)
    entries = cli._parse_wevtutil_xml(WEVTUTIL_XML, cutoff, limit=100)

    assert len(entries) == 1
    assert entries[0]["unit"] == "Application Error"
    assert entries[0]["priority"] == 3  # Level 2 (Error) -> err
    assert "myapp.exe" in entries[0]["message"]


def test_parse_wevtutil_xml_filters_by_cutoff():
    cutoff = datetime(2030, 1, 1, tzinfo=timezone.utc)
    entries = cli._parse_wevtutil_xml(WEVTUTIL_XML, cutoff, limit=100)
    assert entries == []


def test_parse_wevtutil_xml_malformed_raises():
    with pytest.raises(cli.InvalidLogError):
        cli._parse_wevtutil_xml("<Event><not-closed>", cutoff=None, limit=10)


def test_read_windows_wevtutil_success(monkeypatch):
    def fake_run(cmd, capture_output, text, check):
        assert cmd[0] == "wevtutil"
        return subprocess.CompletedProcess(cmd, 0, stdout=WEVTUTIL_XML, stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    cutoff = datetime(2000, 1, 1, tzinfo=timezone.utc)
    entries = cli._read_windows_wevtutil("Application", cutoff, limit=10)
    assert entries[0]["unit"] == "Application Error"


def test_read_windows_wevtutil_missing_tool(monkeypatch):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("wevtutil")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(cli.MissingDependencyError):
        cli._read_windows_wevtutil("Application", None, limit=10)


def test_read_windows_wevtutil_access_denied(monkeypatch):
    def fake_run(cmd, capture_output, text, check):
        raise subprocess.CalledProcessError(5, cmd, stderr="Access is denied.")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(cli.PermissionDeniedError):
        cli._read_windows_wevtutil("Security", None, limit=10)


def test_read_windows_wevtutil_other_error(monkeypatch):
    def fake_run(cmd, capture_output, text, check):
        raise subprocess.CalledProcessError(1, cmd, stderr="bad channel")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(cli.InvalidLogError):
        cli._read_windows_wevtutil("Application", None, limit=10)


# --------------------------------------------------------------------------- #
# Cross-platform dispatch
# --------------------------------------------------------------------------- #


def test_read_entries_dispatches_to_windows(monkeypatch):
    monkeypatch.setattr(cli, "is_windows", lambda: True)
    monkeypatch.setattr(
        cli,
        "read_windows_entries",
        lambda **kwargs: [windows_event()],
    )
    result = cli.read_entries(log_name="Application")
    assert result[0]["unit"] == "Application Error"


def test_read_entries_dispatches_to_linux(monkeypatch):
    monkeypatch.setattr(cli, "is_windows", lambda: False)
    result = cli.read_entries(reader=FakeReader([sample_entry()]))
    assert result[0]["unit"] == "ssh.service"


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def test_render_json_compact_by_default():
    text = cli.render([windows_event()], "json", pretty=False)
    assert "\n" not in text


def test_render_json_pretty():
    text = cli.render([windows_event()], "json", pretty=True)
    assert "\n" in text


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #


def test_parser_defaults():
    args = parse_args([])
    assert args.since_minutes == constants.DEFAULT_SINCE_MINUTES
    assert args.limit == constants.DEFAULT_LIMIT
    assert args.log_name == constants.DEFAULT_WINDOWS_LOG_NAME
    assert args.format == "text"
    assert args.follow is False
    assert args.pretty is False
    assert args.output_file is None


def test_parser_accepts_log_name_choices():
    args = parse_args(["--log-name", "System"])
    assert args.log_name == "System"


def test_parser_rejects_invalid_log_name():
    with pytest.raises(SystemExit):
        parse_args(["--log-name", "Nope"])


def test_parser_rejects_invalid_priority():
    with pytest.raises(SystemExit):
        parse_args(["--priority", "9"])


def test_validate_args_rejects_zero_limit():
    parser = cli.build_parser()
    args = parser.parse_args(["--limit", "0"])
    with pytest.raises(SystemExit):
        cli._validate_args(parser, args)


def test_validate_args_rejects_zero_since_minutes():
    parser = cli.build_parser()
    args = parser.parse_args(["--since-minutes", "0"])
    with pytest.raises(SystemExit):
        cli._validate_args(parser, args)


# --------------------------------------------------------------------------- #
# main()
# --------------------------------------------------------------------------- #


def test_main_text_output(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_open_reader", lambda: FakeReader([sample_entry()]))
    exit_code = cli.main(["--since-minutes", "10"])
    captured = capsys.readouterr()
    assert exit_code == constants.EXIT_OK
    assert "ssh.service" in captured.out


def test_main_json_output(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_open_reader", lambda: FakeReader([sample_entry()]))
    exit_code = cli.main(["--format", "json", "--since-minutes", "10"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload[0]["unit"] == "ssh.service"
    assert payload[0]["priority"] == 6


def test_main_pretty_json(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_open_reader", lambda: FakeReader([sample_entry()]))
    cli.main(["--format", "json", "--pretty"])
    captured = capsys.readouterr()
    assert "\n  " in captured.out  # indentation present


def test_main_output_file(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "_open_reader", lambda: FakeReader([sample_entry()]))
    out = tmp_path / "out.json"
    exit_code = cli.main(["--format", "json", "--output-file", str(out)])
    assert exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["unit"] == "ssh.service"


def test_main_limit_passed_through(monkeypatch, capsys):
    captured = {}

    def fake_read(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(cli, "read_entries", fake_read)
    cli.main(["--limit", "5"])
    assert captured["limit"] == 5


def test_main_follow_dispatch(monkeypatch):
    called = {}
    monkeypatch.setattr(cli, "_run_follow", lambda args: called.setdefault("ran", True))
    cli.main(["--follow"])
    assert called["ran"] is True


def test_main_handles_missing_dependency(monkeypatch, capsys):
    def boom(**kwargs):
        raise cli.MissingDependencyError("python3-systemd missing")

    monkeypatch.setattr(cli, "read_entries", boom)
    exit_code = cli.main([])
    captured = capsys.readouterr()
    assert exit_code == constants.EXIT_MISSING_DEPENDENCY
    assert "error:" in captured.err


def test_main_handles_permission_denied(monkeypatch):
    def boom(**kwargs):
        raise cli.PermissionDeniedError("denied")

    monkeypatch.setattr(cli, "read_entries", boom)
    assert cli.main([]) == constants.EXIT_PERMISSION_DENIED


def test_main_handles_invalid_log(monkeypatch):
    def boom(**kwargs):
        raise cli.InvalidLogError("bad log")

    monkeypatch.setattr(cli, "read_entries", boom)
    assert cli.main([]) == constants.EXIT_INVALID_LOG


def test_main_handles_keyboard_interrupt(monkeypatch):
    def boom(**kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "read_entries", boom)
    assert cli.main([]) == constants.EXIT_INTERRUPTED


def test_main_handles_os_error(monkeypatch):
    def boom(**kwargs):
        raise OSError("disk gone")

    monkeypatch.setattr(cli, "read_entries", boom)
    assert cli.main([]) == constants.EXIT_RUNTIME_ERROR


# --------------------------------------------------------------------------- #
# Follow mode loops
# --------------------------------------------------------------------------- #


class FollowArgs:
    unit = None
    priority = None
    since_minutes = 60
    limit = 100
    log_name = "Application"
    format = "text"
    pretty = False
    output_file = None


class TailReader:
    def __init__(self, batches):
        self._batches = list(batches)
        self.sought_tail = False
        self.previous = False

    def add_match(self, **kwargs):
        pass

    def log_level(self, level):
        pass

    def seek_tail(self):
        self.sought_tail = True

    def get_previous(self):
        self.previous = True

    def __iter__(self):
        if self._batches:
            return iter(self._batches.pop(0))
        return iter([])

    def wait(self, timeout):
        pass


def test_follow_linux_emits_entries():
    import io

    stream = io.StringIO()
    reader = TailReader([[sample_entry()]])
    cli._follow_linux(FollowArgs(), stream, reader=reader, _max_cycles=1)
    assert "ssh.service" in stream.getvalue()
    assert reader.sought_tail is True


def test_follow_windows_emits_new_entries_once():
    import io

    stream = io.StringIO()

    def backend(log_name, cutoff, limit):
        return [windows_event(message="repeated")]

    sleeps = []
    cli._follow_windows(
        FollowArgs(),
        stream,
        backend=backend,
        _sleep=sleeps.append,
        _max_cycles=2,
    )
    # The same event must only be emitted once across the two cycles.
    assert stream.getvalue().count("repeated") == 1
    assert len(sleeps) == 2


def test_run_follow_writes_to_output_file(monkeypatch, tmp_path):
    out = tmp_path / "tail.log"

    def fake_follow_linux(args, stream):
        stream.write("tailed line\n")

    monkeypatch.setattr(cli, "is_windows", lambda: False)
    monkeypatch.setattr(cli, "_follow_linux", fake_follow_linux)

    args = cli.build_parser().parse_args(["--follow", "--output-file", str(out)])
    exit_code = cli._run_follow(args)

    assert exit_code == constants.EXIT_OK
    assert "tailed line" in out.read_text(encoding="utf-8")


def test_run_follow_dispatches_to_windows(monkeypatch):
    called = {}
    monkeypatch.setattr(cli, "is_windows", lambda: True)
    monkeypatch.setattr(
        cli, "_follow_windows", lambda args, stream: called.setdefault("win", True)
    )
    args = cli.build_parser().parse_args(["--follow"])
    cli._run_follow(args)
    assert called["win"] is True


def test_win_message_uses_string_inserts():
    record = FakeRecord(0, "src", 4, ["hello", "world"])
    assert cli._win_message(record) == "hello world"


def test_win_message_empty_when_no_inserts():
    record = FakeRecord(0, "src", 4, None)
    assert cli._win_message(record) == ""


def test_emit_entry_json_format():
    import io

    stream = io.StringIO()
    cli._emit_entry(windows_event(), stream, "json", pretty=False)
    payload = json.loads(stream.getvalue())
    assert payload["unit"] == "Application Error"
