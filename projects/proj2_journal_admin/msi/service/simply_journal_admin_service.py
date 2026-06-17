"""Windows service wrapper for Simply Journal Admin (pywin32 approach).

This wraps the ``simply-journal-admin`` console script as a native Windows
service using ``win32serviceutil``. The service launches the console script
from the dedicated virtual environment in ``--follow`` mode and writes the
JSON stream to a log file under the install root.

Install / manage (from an elevated prompt, using the venv Python so that
pywin32 is available)::

    "C:\\Program Files\\SimplyJournalAdmin\\venv\\Scripts\\python.exe" ^
        simply_journal_admin_service.py install
    "C:\\Program Files\\SimplyJournalAdmin\\venv\\Scripts\\python.exe" ^
        simply_journal_admin_service.py start
    "...python.exe" simply_journal_admin_service.py stop
    "...python.exe" simply_journal_admin_service.py remove
"""

from __future__ import annotations

import os
import subprocess

import servicemanager
import win32event
import win32service
import win32serviceutil

#: Configurable install locations (kept in sync with the package constants).
INSTALL_ROOT = r"C:\Program Files\SimplyJournalAdmin"
VENV_EXE = os.path.join(INSTALL_ROOT, "venv", "Scripts", "simply-journal-admin.exe")
LOG_FILE = os.path.join(INSTALL_ROOT, "simply-journal-admin.log")


class SimplyJournalAdminService(win32serviceutil.ServiceFramework):
    """Native Windows service that tails the Event Log via the CLI."""

    _svc_name_ = "SimplyJournalAdmin"
    _svc_display_name_ = "Simply Journal Admin"
    _svc_description_ = (
        "Continuously tails the Windows Event Log and records entries as JSON "
        "using simply-journal-admin."
    )

    def __init__(self, args):
        super().__init__(args)
        self._stop_event = win32event.CreateEvent(None, 0, 0, None)
        self._process: subprocess.Popen | None = None

    def SvcStop(self):
        """Signal the service to stop and terminate the child process."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self._process and self._process.poll() is None:
            self._process.terminate()
        win32event.SetEvent(self._stop_event)

    def SvcDoRun(self):
        """Run the CLI in follow mode until the service is stopped."""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        command = [
            VENV_EXE,
            "--follow",
            "--format",
            "json",
            "--output-file",
            LOG_FILE,
        ]
        self._process = subprocess.Popen(command)
        win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)


if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(SimplyJournalAdminService)
