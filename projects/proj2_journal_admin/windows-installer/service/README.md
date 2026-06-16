# Windows Service Options

Simply Journal Admin can run as a long-lived Windows service that tails the
Windows Event Log in `--follow` mode and records entries as JSON. Two
approaches are provided; pick one.

## Files

| File | Purpose |
| ---- | ------- |
| [install-service.ps1](install-service.ps1) | Register the service with **NSSM**. |
| [uninstall-service.ps1](uninstall-service.ps1) | Stop and remove the NSSM service. |
| [simply_journal_admin_service.py](simply_journal_admin_service.py) | Native **pywin32** service wrapper. |

Both approaches launch the console script from the dedicated virtual
environment:

```
C:\Program Files\SimplyJournalAdmin\venv\Scripts\simply-journal-admin.exe --follow --format json
```

- **Service name:** `SimplyJournalAdmin`
- **Display name:** `Simply Journal Admin`

## Option 1 — NSSM (recommended)

NSSM wraps any executable as a service and handles auto-start, restart-on-crash,
and stdout/stderr redirection without writing service code.

```powershell
# from an elevated prompt, after the MSI/venv install
powershell -ExecutionPolicy Bypass -File install-service.ps1
```

**Pros**

- No service-specific Python code; wraps the venv launcher directly.
- Built-in restart throttling (`AppRestartDelay`) and log redirection.
- Trivial to install/remove; resilient to non-graceful exits.

**Cons**

- Requires bundling the third-party `nssm.exe` (MIT/public-domain).
- One more moving part to ship and version.

## Option 2 — pywin32 service wrapper

`simply_journal_admin_service.py` implements a native service via
`win32serviceutil.ServiceFramework`. It must be installed with the **venv**
Python so that `pywin32` is importable.

```powershell
$py = "C:\Program Files\SimplyJournalAdmin\venv\Scripts\python.exe"
& $py simply_journal_admin_service.py install
& $py simply_journal_admin_service.py start
```

**Pros**

- Pure Python; no external service helper to ship.
- Full control over start/stop lifecycle and event-log reporting.

**Cons**

- Requires `pywin32` (the `windows` extra) in the venv.
- More code to maintain; restart-on-failure must be configured separately
  (e.g. `sc.exe failure SimplyJournalAdmin reset= 60 actions= restart/5000`).
- Service classes are notoriously fiddly to debug.

## Restart-on-failure for the pywin32 service

```powershell
sc.exe failure SimplyJournalAdmin reset= 60 actions= restart/5000
```
