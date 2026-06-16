"""Command-line entry point for the ``simply-journal-admin`` tool.

The tool reads recent log entries from the host's native logging system and
prints them as text or JSON. It supports two platforms with a deliberately
identical user experience:

* **Linux** reads the systemd journal through ``systemd.journal`` from the
  APT package ``python3-systemd``.
* **Windows** reads the Windows Event Log, preferring the ``pywin32``
  (``win32evtlog``) bindings and falling back to the ``wevtutil`` command-line
  tool when ``pywin32`` is not installed.

Both backends normalize their records into the same output schema::

    {
        "timestamp": "2026-05-24T10:00:00+00:00",
        "unit": "ssh.service",   # Linux unit / Windows provider name
        "priority": 6,            # syslog-style priority (0=emerg .. 7=debug)
        "message": "..."
    }

Windows event levels are mapped onto syslog-style priorities so that the
``--priority`` filter behaves consistently across platforms. See
``WINDOWS_EVENTTYPE_PRIORITY`` and ``WINDOWS_LEVEL_PRIORITY`` for the mapping.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone

from .constants import (
    DEFAULT_LIMIT,
    DEFAULT_SINCE_MINUTES,
    DEFAULT_WINDOWS_LOG_NAME,
    EXIT_INTERRUPTED,
    EXIT_INVALID_LOG,
    EXIT_MISSING_DEPENDENCY,
    EXIT_OK,
    EXIT_PERMISSION_DENIED,
    EXIT_RUNTIME_ERROR,
    PRIORITY_NAMES,
    WINDOWS_FOLLOW_POLL_SECONDS,
    WINDOWS_LOG_NAMES,
)

# Re-exported for backward compatibility with earlier versions and tests.
__all__ = [
    "PRIORITY_NAMES",
    "is_windows",
    "is_linux",
    "read_entries",
    "read_linux_entries",
    "read_windows_entries",
    "format_text",
    "build_parser",
    "main",
]


# --------------------------------------------------------------------------- #
# Errors and exit codes
# --------------------------------------------------------------------------- #


class JournalAdminError(Exception):
    """Base class for predictable, user-facing failures.

    Each subclass carries the process ``exit_code`` that :func:`main` returns
    when the error propagates out of the command implementation.
    """

    exit_code = EXIT_RUNTIME_ERROR


class MissingDependencyError(JournalAdminError):
    """A required backend (``systemd`` or ``pywin32``/``wevtutil``) is absent."""

    exit_code = EXIT_MISSING_DEPENDENCY


class PermissionDeniedError(JournalAdminError):
    """The current user is not allowed to read the requested log."""

    exit_code = EXIT_PERMISSION_DENIED


class InvalidLogError(JournalAdminError):
    """The requested log name/channel is invalid or inaccessible."""

    exit_code = EXIT_INVALID_LOG


# --------------------------------------------------------------------------- #
# Platform detection
# --------------------------------------------------------------------------- #


def is_windows() -> bool:
    """Return ``True`` when running on a Windows platform."""
    return sys.platform.startswith("win")


def is_linux() -> bool:
    """Return ``True`` when running on a Linux platform."""
    return sys.platform.startswith("linux")


# --------------------------------------------------------------------------- #
# Windows event-level to syslog-priority mappings
# --------------------------------------------------------------------------- #

#: Classic Event Log API (``win32evtlog`` ``EventType``) -> syslog priority.
#:
#: ====================  =====  =================  ========
#: EventType constant    value  syslog priority    name
#: ====================  =====  =================  ========
#: EVENTLOG_SUCCESS          0  6                  info
#: EVENTLOG_ERROR_TYPE       1  3                  err
#: EVENTLOG_WARNING_TYPE     2  4                  warning
#: EVENTLOG_INFORMATION      4  6                  info
#: EVENTLOG_AUDIT_SUCCESS    8  5                  notice
#: EVENTLOG_AUDIT_FAILURE   16  4                  warning
#: ====================  =====  =================  ========
WINDOWS_EVENTTYPE_PRIORITY = {
    0: 6,
    1: 3,
    2: 4,
    4: 6,
    8: 5,
    16: 4,
}

#: Modern EVTX ``Level`` field (used by ``wevtutil`` XML) -> syslog priority.
#:
#: =====  ============  =================  ========
#: Level  meaning       syslog priority    name
#: =====  ============  =================  ========
#: 0      LogAlways     6                  info
#: 1      Critical      2                  crit
#: 2      Error         3                  err
#: 3      Warning       4                  warning
#: 4      Information   6                  info
#: 5      Verbose       7                  debug
#: =====  ============  =================  ========
WINDOWS_LEVEL_PRIORITY = {
    0: 6,
    1: 2,
    2: 3,
    3: 4,
    4: 6,
    5: 7,
}

#: XML namespace used by ``wevtutil qe ... /f:xml`` output.
_WIN_EVENT_NS = {"e": "http://schemas.microsoft.com/win/2004/08/events/event"}


# --------------------------------------------------------------------------- #
# Linux backend
# --------------------------------------------------------------------------- #


def _open_reader():
    """Open a systemd journal reader.

    Imported lazily so the module can be inspected on systems where
    ``systemd.journal`` is not installed, and so tests can replace this
    function with a fake reader.
    """
    try:
        from systemd import journal
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatch
        raise MissingDependencyError(
            "python3-systemd is not installed; install the APT package "
            "'python3-systemd' to read the journal."
        ) from exc

    return journal.Reader()


def _normalize_linux(entry) -> dict:
    """Convert a raw journal entry into the shared output schema."""
    timestamp = entry.get("__REALTIME_TIMESTAMP")
    return {
        "timestamp": timestamp.isoformat() if timestamp else None,
        "unit": entry.get("_SYSTEMD_UNIT"),
        "priority": entry.get("PRIORITY"),
        "message": entry.get("MESSAGE"),
    }


def read_linux_entries(
    unit=None,
    priority=None,
    since_minutes=DEFAULT_SINCE_MINUTES,
    limit=DEFAULT_LIMIT,
    reader=None,
):
    """Return recent systemd journal entries as a list of plain dictionaries."""
    if reader is None:
        reader = _open_reader()

    if unit:
        reader.add_match(_SYSTEMD_UNIT=unit)
    if priority is not None:
        reader.log_level(priority)

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
    reader.seek_realtime(cutoff)

    entries = []
    for entry in reader:
        entries.append(_normalize_linux(entry))
        if limit and len(entries) >= limit:
            break
    return entries


# --------------------------------------------------------------------------- #
# Windows backend
# --------------------------------------------------------------------------- #


def _win_timestamp(raw) -> datetime:
    """Convert a pywin32 ``TimeGenerated`` value to an aware UTC datetime."""
    return datetime.fromtimestamp(int(raw), tz=timezone.utc)


def _win_message(record) -> str:
    """Best-effort extraction of a human-readable message from a record."""
    try:
        import win32evtlogutil

        formatted = win32evtlogutil.SafeFormatMessage(record, None)
        if formatted:
            return formatted.strip()
    except Exception:  # pragma: no cover - depends on Windows message tables
        pass

    inserts = getattr(record, "StringInserts", None)
    if inserts:
        return " ".join(str(part) for part in inserts).strip()
    return ""


def _read_windows_win32(log_name, cutoff, limit):
    """Read events using the ``pywin32`` ``win32evtlog`` bindings."""
    import win32evtlog

    flags = (
        win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    )

    try:
        handle = win32evtlog.OpenEventLog(None, log_name)
    except Exception as exc:  # pywintypes.error
        message = str(exc).lower()
        if "access" in message and "denied" in message:
            raise PermissionDeniedError(
                f"access denied while opening the '{log_name}' event log; "
                "the Security log usually requires Administrator privileges."
            ) from exc
        raise InvalidLogError(
            f"could not open the '{log_name}' event log: {exc}"
        ) from exc

    entries = []
    try:
        while True:
            records = win32evtlog.ReadEventLog(handle, flags, 0)
            if not records:
                break
            for record in records:
                timestamp = _win_timestamp(record.TimeGenerated)
                if timestamp < cutoff:
                    return entries
                entries.append(
                    {
                        "timestamp": timestamp.isoformat(),
                        "unit": record.SourceName,
                        "priority": WINDOWS_EVENTTYPE_PRIORITY.get(
                            record.EventType, 6
                        ),
                        "message": _win_message(record),
                    }
                )
                if limit and len(entries) >= limit:
                    return entries
    finally:
        win32evtlog.CloseEventLog(handle)
    return entries


def _join_event_data(event) -> str:
    """Collect ``<EventData>`` / ``<UserData>`` text into a single message."""
    parts = []
    for data in event.iter():
        tag = data.tag.split("}")[-1]
        if tag in ("Data", "Message") and data.text:
            parts.append(data.text.strip())
    return " ".join(parts).strip()


def _parse_iso_z(value):
    """Parse an ISO-8601 timestamp that may end in ``Z`` into aware UTC."""
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_wevtutil_xml(xml_text, cutoff, limit):
    """Parse ``wevtutil qe ... /f:xml`` output into the shared schema."""
    import xml.etree.ElementTree as ET

    # wevtutil emits a sequence of <Event> elements without a shared root.
    wrapped = f"<Events>{xml_text}</Events>"
    try:
        root = ET.fromstring(wrapped)
    except ET.ParseError as exc:
        raise InvalidLogError(f"could not parse event log output: {exc}") from exc

    entries = []
    for event in root.findall("e:Event", _WIN_EVENT_NS):
        system = event.find("e:System", _WIN_EVENT_NS)
        if system is None:
            continue

        provider = system.find("e:Provider", _WIN_EVENT_NS)
        unit = provider.get("Name") if provider is not None else None

        level_el = system.find("e:Level", _WIN_EVENT_NS)
        level = int(level_el.text) if level_el is not None and level_el.text else 4
        priority = WINDOWS_LEVEL_PRIORITY.get(level, 6)

        time_el = system.find("e:TimeCreated", _WIN_EVENT_NS)
        raw_time = time_el.get("SystemTime") if time_el is not None else None
        timestamp = _parse_iso_z(raw_time)
        if timestamp is not None and timestamp < cutoff:
            continue

        entries.append(
            {
                "timestamp": timestamp.isoformat() if timestamp else raw_time,
                "unit": unit,
                "priority": priority,
                "message": _join_event_data(event),
            }
        )
        if limit and len(entries) >= limit:
            break
    return entries


def _read_windows_wevtutil(log_name, cutoff, limit):
    """Read events by shelling out to the ``wevtutil`` command-line tool."""
    import subprocess

    command = [
        "wevtutil",
        "qe",
        log_name,
        "/f:xml",
        "/rd:true",  # reverse direction: newest first
        f"/c:{limit}",
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise MissingDependencyError(
            "neither pywin32 nor wevtutil is available to read the event log."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").lower()
        if "access" in stderr and "denied" in stderr:
            raise PermissionDeniedError(
                f"access denied while reading the '{log_name}' event log."
            ) from exc
        raise InvalidLogError(
            f"wevtutil could not read the '{log_name}' event log: "
            f"{(exc.stderr or '').strip()}"
        ) from exc

    return _parse_wevtutil_xml(completed.stdout, cutoff, limit)


def _select_windows_backend():
    """Return the best available Windows backend callable."""
    try:
        import win32evtlog  # noqa: F401
    except ImportError:
        return _read_windows_wevtutil
    return _read_windows_win32


def read_windows_entries(
    priority=None,
    since_minutes=DEFAULT_SINCE_MINUTES,
    limit=DEFAULT_LIMIT,
    log_name=DEFAULT_WINDOWS_LOG_NAME,
    backend=None,
):
    """Return recent Windows Event Log entries as a list of plain dictionaries.

    ``backend`` is injectable for testing; when omitted the best available
    backend (``win32evtlog`` preferred, ``wevtutil`` fallback) is selected.
    """
    if log_name not in WINDOWS_LOG_NAMES:
        raise InvalidLogError(
            f"invalid log name '{log_name}'; choose one of "
            f"{', '.join(WINDOWS_LOG_NAMES)}."
        )

    if backend is None:
        backend = _select_windows_backend()

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
    raw_entries = backend(log_name, cutoff, limit)

    entries = []
    for entry in raw_entries:
        if priority is not None and entry["priority"] > priority:
            continue
        entries.append(entry)
        if limit and len(entries) >= limit:
            break
    return entries


# --------------------------------------------------------------------------- #
# Cross-platform dispatch
# --------------------------------------------------------------------------- #


def read_entries(
    unit=None,
    priority=None,
    since_minutes=DEFAULT_SINCE_MINUTES,
    limit=DEFAULT_LIMIT,
    reader=None,
    log_name=DEFAULT_WINDOWS_LOG_NAME,
):
    """Read recent entries from the host's native logging system.

    When an explicit ``reader`` is supplied, or when running on Linux, the
    systemd journal backend is used. On Windows the Event Log backend is used.
    The returned schema is identical on both platforms.
    """
    if reader is not None or not is_windows():
        return read_linux_entries(
            unit=unit,
            priority=priority,
            since_minutes=since_minutes,
            limit=limit,
            reader=reader,
        )
    return read_windows_entries(
        priority=priority,
        since_minutes=since_minutes,
        limit=limit,
        log_name=log_name,
    )


# --------------------------------------------------------------------------- #
# Rendering and output
# --------------------------------------------------------------------------- #


def format_text(entries):
    """Render entries as one human-readable line each."""
    lines = []
    for entry in entries:
        priority = entry.get("priority")
        name = PRIORITY_NAMES.get(priority, str(priority))
        lines.append(
            f"{entry['timestamp']} [{name}] {entry['unit']}: {entry['message']}"
        )
    return "\n".join(lines)


def render(entries, output_format="text", pretty=False):
    """Render entries to a string using the requested output format."""
    if output_format == "json":
        indent = 2 if pretty else None
        return json.dumps(entries, indent=indent, default=str)
    return format_text(entries)


def _write_output(text, output_file=None):
    """Write rendered text to ``output_file`` or standard output."""
    if output_file:
        with open(output_file, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)


# --------------------------------------------------------------------------- #
# Follow (tail) mode
# --------------------------------------------------------------------------- #


def _emit_entry(entry, stream, output_format="text", pretty=False):
    """Write a single entry to a live stream during follow mode."""
    if output_format == "json":
        line = json.dumps(entry, default=str)
    else:
        line = format_text([entry])
    stream.write(line + "\n")
    stream.flush()


def _follow_linux(args, stream, reader=None, _max_cycles=None):
    """Tail the systemd journal, emitting new entries as they arrive."""
    if reader is None:
        reader = _open_reader()
    if args.unit:
        reader.add_match(_SYSTEMD_UNIT=args.unit)
    if args.priority is not None:
        reader.log_level(args.priority)

    reader.seek_tail()
    reader.get_previous()

    cycles = 0
    while _max_cycles is None or cycles < _max_cycles:
        for entry in reader:
            _emit_entry(
                _normalize_linux(entry), stream, args.format, args.pretty
            )
        reader.wait(WINDOWS_FOLLOW_POLL_SECONDS)
        cycles += 1


def _follow_windows(args, stream, backend=None, _sleep=time.sleep, _max_cycles=None):
    """Poll the Windows Event Log, emitting newly seen entries."""
    seen = set()
    cycles = 0
    while _max_cycles is None or cycles < _max_cycles:
        entries = read_windows_entries(
            priority=args.priority,
            since_minutes=max(args.since_minutes, 1),
            limit=args.limit,
            log_name=args.log_name,
            backend=backend,
        )
        for entry in reversed(entries):
            key = (entry["timestamp"], entry["message"])
            if key in seen:
                continue
            seen.add(key)
            _emit_entry(entry, stream, args.format, args.pretty)
        _sleep(WINDOWS_FOLLOW_POLL_SECONDS)
        cycles += 1


def _run_follow(args):
    """Open the output stream and dispatch to the platform follow loop."""
    stream = (
        open(args.output_file, "a", encoding="utf-8")
        if args.output_file
        else sys.stdout
    )
    try:
        if is_windows():
            _follow_windows(args, stream)
        else:
            _follow_linux(args, stream)
    finally:
        if args.output_file:
            stream.close()
    return EXIT_OK


# --------------------------------------------------------------------------- #
# Argument parsing and entry point
# --------------------------------------------------------------------------- #


def build_parser():
    """Build the argument parser shared by both platforms."""
    parser = argparse.ArgumentParser(
        prog="simply-journal-admin",
        description=(
            "Read recent entries from the systemd journal (Linux) or the "
            "Windows Event Log (Windows)."
        ),
    )
    parser.add_argument(
        "--unit",
        help="Linux only: filter by systemd unit, for example ssh.service.",
    )
    parser.add_argument(
        "--log-name",
        choices=WINDOWS_LOG_NAMES,
        default=DEFAULT_WINDOWS_LOG_NAME,
        help="Windows only: event log channel to read (default: Application).",
    )
    parser.add_argument(
        "--priority",
        type=int,
        choices=range(0, 8),
        help="Maximum syslog priority (0=emerg .. 7=debug).",
    )
    parser.add_argument(
        "--since-minutes",
        type=int,
        default=DEFAULT_SINCE_MINUTES,
        help=f"How far back to read (default: {DEFAULT_SINCE_MINUTES} minutes).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Maximum number of entries returned (default: {DEFAULT_LIMIT}).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (ignored for text format).",
    )
    parser.add_argument(
        "--output-file",
        help="Write output to a file instead of standard output.",
    )
    parser.add_argument(
        "--follow",
        action="store_true",
        help="Tail mode: keep printing new entries as they arrive.",
    )
    return parser


def _validate_args(parser, args):
    """Validate interdependent argument values."""
    if args.since_minutes <= 0:
        parser.error("--since-minutes must be a positive integer")
    if args.limit <= 0:
        parser.error("--limit must be a positive integer")


def _run_once(args):
    """Read entries once, render them, and write the result."""
    entries = read_entries(
        unit=args.unit,
        priority=args.priority,
        since_minutes=args.since_minutes,
        limit=args.limit,
        log_name=args.log_name,
    )
    rendered = render(entries, args.format, args.pretty)
    _write_output(rendered, args.output_file)
    return EXIT_OK


def main(argv=None):
    """Program entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    _validate_args(parser, args)

    try:
        if args.follow:
            return _run_follow(args)
        return _run_once(args)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return EXIT_INTERRUPTED
    except JournalAdminError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    sys.exit(main())
