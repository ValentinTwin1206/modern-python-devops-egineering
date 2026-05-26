"""Command-line entry point for the journal-admin tool.

The tool reads recent systemd journal entries with optional filters and
prints them as text or JSON. It depends on ``systemd.journal`` from the
APT package ``python3-systemd``, which links against ``libsystemd`` and
is therefore installed through the system package manager rather than
PyPI.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone


PRIORITY_NAMES = {
    0: "emerg",
    1: "alert",
    2: "crit",
    3: "err",
    4: "warning",
    5: "notice",
    6: "info",
    7: "debug",
}


def _open_reader():
    """Open a journal reader.

    Imported lazily so the module can be inspected on systems where
    ``systemd.journal`` is not installed and so tests can replace this
    function with a fake reader.
    """
    from systemd import journal

    return journal.Reader()


def read_entries(unit=None, priority=None, since_minutes=60, reader=None):
    """Return recent journal entries as a list of plain dictionaries."""
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
        timestamp = entry.get("__REALTIME_TIMESTAMP")
        entries.append(
            {
                "timestamp": timestamp.isoformat() if timestamp else None,
                "unit": entry.get("_SYSTEMD_UNIT"),
                "priority": entry.get("PRIORITY"),
                "message": entry.get("MESSAGE"),
            }
        )
    return entries


def format_text(entries):
    lines = []
    for entry in entries:
        priority = entry.get("priority")
        name = PRIORITY_NAMES.get(priority, str(priority))
        lines.append(
            f"{entry['timestamp']} [{name}] {entry['unit']}: {entry['message']}"
        )
    return "\n".join(lines)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="journal-admin",
        description="Read recent systemd journal entries.",
    )
    parser.add_argument(
        "--unit",
        help="Filter by systemd unit, for example ssh.service.",
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
        default=60,
        help="How far back to read (default: 60 minutes).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    entries = read_entries(
        unit=args.unit,
        priority=args.priority,
        since_minutes=args.since_minutes,
    )
    if args.format == "json":
        print(json.dumps(entries, indent=2, default=str))
    else:
        print(format_text(entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
