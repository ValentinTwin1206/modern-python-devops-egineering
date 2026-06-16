# Simply Journal Admin

*Simply Journal Admin* is a cross-platform administration CLI that reads recent
log entries from the host's native logging system and prints them as text or
JSON. A single code base supports two platforms with an identical command-line
experience:

- **Linux** reads the systemd journal through the APT package `python3-systemd`.
- **Windows** reads the Windows Event Log through `pywin32`, falling back to the
  built-in `wevtutil` tool when `pywin32` is not installed.

The same command works on both platforms:

```bash
simply-journal-admin --since-minutes 60
```

## Features

- One CLI, two backends, one normalized output schema.
- Text and JSON output (`--format`, `--pretty`).
- Filtering by time (`--since-minutes`), severity (`--priority`), and count
  (`--limit`).
- Linux unit filtering (`--unit`) and Windows channel selection (`--log-name`).
- Tail/follow mode (`--follow`) on both platforms.
- Write to a file (`--output-file`).
- Reproducible packaging: a Debian `.deb` and a Windows `.msi`, both installing
  into a dedicated virtual environment.
- Meaningful, consistent exit codes for automation.

### Output schema

Both backends emit the same record shape:

```json
{
  "timestamp": "2026-05-24T10:00:00+00:00",
  "unit": "ssh.service",
  "priority": 6,
  "message": "Accepted publickey for admin"
}
```

On Windows, `unit` carries the **event provider / source name** (for example
`Application Error`).

### Priority mapping (Windows → syslog)

Windows event levels are mapped onto syslog-style priorities so that
`--priority` behaves the same everywhere. Two mappings are used depending on the
backend.

Classic Event Log API (`win32evtlog` `EventType`):

| EventType | Meaning | syslog priority |
| --------- | ------- | --------------- |
| 0 | Success | 6 (info) |
| 1 | Error | 3 (err) |
| 2 | Warning | 4 (warning) |
| 4 | Information | 6 (info) |
| 8 | Audit success | 5 (notice) |
| 16 | Audit failure | 4 (warning) |

Modern EVTX `Level` field (`wevtutil` XML):

| Level | Meaning | syslog priority |
| ----- | ------- | --------------- |
| 0 | LogAlways | 6 (info) |
| 1 | Critical | 2 (crit) |
| 2 | Error | 3 (err) |
| 3 | Warning | 4 (warning) |
| 4 | Information | 6 (info) |
| 5 | Verbose | 7 (debug) |

## Installation

### Linux

**Wheel (any Python 3.11+ environment):**

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install simply_journal_admin-2.0.0-py3-none-any.whl
```

Reading the systemd journal also requires the APT binding:

```bash
sudo apt install python3-systemd
```

**Debian package (recommended):**

```bash
sudo apt install ./.build/simply-journal-admin_2.0.0-1_all.deb
```

The `.deb` creates a dedicated virtual environment at
`/opt/simply-journal-admin/venv`, installs the bundled wheel into it, and adds a
`/usr/bin/simply-journal-admin` wrapper. The system Python interpreter is never
modified.

### Windows

**Wheel (any Python 3.11+ environment):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install simply_journal_admin-2.0.0-py3-none-any.whl[windows]
```

The `[windows]` extra installs `pywin32`. Without it the CLI automatically falls
back to `wevtutil`.

**MSI (recommended):**

Double-click the installer or run it silently:

```powershell
msiexec /i simply-journal-admin-2.0.0.msi /qn
```

The MSI installs into `C:\Program Files\SimplyJournalAdmin\`, creates a venv at
`...\venv`, installs the bundled wheel plus `pywin32`, drops a launcher, and adds
the install root to `PATH`.

## Usage

The interface is identical on both platforms; only the platform-specific filters
differ.

Read the last hour as text:

```bash
simply-journal-admin --since-minutes 60
```

Read the last 30 minutes as pretty JSON, capped at 50 entries:

```bash
simply-journal-admin --since-minutes 30 --limit 50 --format json --pretty
```

Linux — filter by unit and severity:

```bash
simply-journal-admin --unit ssh.service --priority 4
```

Windows — choose the channel:

```powershell
simply-journal-admin --log-name System --priority 3
simply-journal-admin --log-name Application --format json
```

Follow (tail) mode:

```bash
simply-journal-admin --follow
```

Write output to a file:

```bash
simply-journal-admin --since-minutes 120 --format json --output-file report.json
```

### Exit codes

| Code | Meaning |
| ---- | ------- |
| 0 | Success |
| 2 | Bad command-line arguments |
| 3 | Missing backend dependency (`python3-systemd` / `pywin32`/`wevtutil`) |
| 4 | Permission denied reading a log |
| 5 | Invalid or inaccessible log/channel |
| 6 | Unexpected runtime error |
| 130 | Interrupted (Ctrl-C) |

## Services

### Linux (systemd)

The Debian package registers [simply-journal-admin.service](debian/simply-journal-admin.service),
a hardened, long-running unit that tails the journal as JSON from the venv:

```bash
sudo systemctl start simply-journal-admin.service
journalctl -u simply-journal-admin.service --since "1 hour ago"
```

The unit runs under `DynamicUser=yes` with the `systemd-journal` supplementary
group and a tightened sandbox (`ProtectSystem=strict`, `NoNewPrivileges`,
`PrivateTmp`, restricted syscalls), and restarts on failure.

### Windows

A Windows service named `SimplyJournalAdmin` (display name *Simply Journal
Admin*) can be registered via **NSSM** or a **pywin32** wrapper. See
[windows-installer/service/README.md](windows-installer/service/README.md) for
the trade-offs and commands.

## Development

The [Dockerfile.devEnv](Dockerfile.devEnv) provides the Linux development image
with `python3-systemd`, `uv`, and the Debian packaging tools. Open a shell with
the projects helper:

```bash
../build.sh build --path proj2_journal_admin/Dockerfile.devEnv
```

### Testing

The suite uses `pytest` with `pytest-cov` and never touches a real journal or a
real Event Log; both backends are exercised through dependency injection and
mocking.

```bash
pip install -e ".[windows]" pytest pytest-cov
pytest
```

Coverage of `cli.py` is kept above 90%.

### Linting

```bash
ruff check .
```

### Building the wheel

```bash
uv build --wheel --out-dir .build
```

## Packaging

### Debian package

The `.deb` embeds the prebuilt wheel and installs it into a per-package venv at
install time.

```bash
# 1. Build the wheel into the mounted artifact directory
uv build --wheel --out-dir .build

# 2. Build the binary .deb (picks up the wheel via debian/*.install)
dpkg-buildpackage -us -uc -b
```

Key packaging files:

| File | Purpose |
| ---- | ------- |
| [debian/control](debian/control) | Dependencies: `python3`, `python3-venv`, `python3-systemd`. |
| [debian/simply-journal-admin.install](debian/simply-journal-admin.install) | Ships the wheel under `/opt/simply-journal-admin/wheel` and the wrapper to `/usr/bin`. |
| [debian/simply-journal-admin.postinst](debian/simply-journal-admin.postinst) | Creates the venv and installs the wheel. |
| [debian/simply-journal-admin.postrm](debian/simply-journal-admin.postrm) | Removes the venv on uninstall. |
| [debian/simply-journal-admin.service](debian/simply-journal-admin.service) | Hardened systemd unit. |

### MSI package

The MSI is built inside a Windows container defined by
[Dockerfile.windows](Dockerfile.windows), which installs Python, uv, the WiX
Toolset, NSSM, and the Visual C++ build tools.

```powershell
# Build the image (Windows container host required)
docker build -f Dockerfile.windows -t sja-msi-builder .

# Copy the artifact out
docker run --rm -v ${PWD}\out:C:\out sja-msi-builder `
    powershell -Command "Copy-Item C:\build\*.msi C:\out"
```

The WiX sources and helper scripts live under
[windows-installer/](windows-installer/):

| Path | Purpose |
| ---- | ------- |
| `windows-installer/wix/Product.wxs` | WiX v3 product definition (files, PATH, custom actions). |
| `windows-installer/scripts/install-venv.ps1` | Creates the venv and installs the wheel + `pywin32`. |
| `windows-installer/scripts/uninstall-venv.ps1` | Removes the venv and launcher. |
| `windows-installer/scripts/build-msi.ps1` | Runs `candle` + `light` to compile the `.msi`. |
| `windows-installer/service/` | NSSM and pywin32 service definitions. |

## Architecture overview

```text
                         simply_journal_admin.cli
                                   │
                build_parser ──► main ──► read_entries (dispatch)
                                   │            │
                         is_windows()? ─────────┤
                              │                 │
                  ┌───────────┘                 └───────────┐
                  ▼                                         ▼
          read_linux_entries                       read_windows_entries
                  │                                         │
          systemd.journal.Reader            win32evtlog ──or──► wevtutil
                  │                                         │
                  └──────────► normalized records ◄─────────┘
                               {timestamp, unit, priority, message}
                                          │
                          format_text / json  ──►  stdout / --output-file
```

All paths, service names, package names, and venv locations are centralized in
[src/simply_journal_admin/constants.py](src/simply_journal_admin/constants.py)
so the application, the Debian packaging, and the Windows installer share one
source of truth.

## Migration notes (1.x → 2.0)

- **Install layout changed.** The Debian package no longer installs the wheel
  into the system interpreter with `--break-system-packages`. It now creates a
  dedicated venv at `/opt/simply-journal-admin/venv` and exposes
  `/usr/bin/simply-journal-admin`. Removing the old 1.x package and installing
  2.0 is the supported upgrade path.
- **Service behavior changed.** The systemd unit is now a long-running
  `--follow` service with `Restart=on-failure` and sandboxing, instead of a
  one-shot reporter.
- **CLI is backward compatible.** Existing flags (`--unit`, `--priority`,
  `--since-minutes`, `--format`) behave as before; `read_entries(..., reader=)`
  remains supported for embedding/testing. New flags (`--limit`, `--follow`,
  `--output-file`, `--pretty`, `--log-name`) are additive.
- **Default JSON is now compact**; pass `--pretty` for indented output.

