"""Central configuration constants for simply-journal-admin.

All paths, package names, and virtual-environment locations are defined here so
that the application code and the native packaging can share a single source of
truth. Keeping these values in one module makes the project reproducible and
easy to retarget.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Identity
# --------------------------------------------------------------------------- #

#: Distribution / package name as published on disk and in package managers.
PACKAGE_NAME = "simply-journal-admin"

#: Importable Python package name.
MODULE_NAME = "simply_journal_admin"

#: Console-script / launcher name installed on PATH.
CONSOLE_SCRIPT = "simply-journal-admin"

#: Human-readable application name.
DISPLAY_NAME = "Simply Journal Admin"

#: Project version. Kept in sync with pyproject.toml and debian/changelog.
VERSION = "2.0.0"

# --------------------------------------------------------------------------- #
# Linux install layout
# --------------------------------------------------------------------------- #

#: Root directory the Debian package installs into.
LINUX_INSTALL_ROOT = "/opt/simply-journal-admin"

#: Virtual environment created by the Debian postinst script.
LINUX_VENV_DIR = f"{LINUX_INSTALL_ROOT}/venv"

#: Directory inside the package that ships the prebuilt wheel.
LINUX_WHEEL_DIR = f"{LINUX_INSTALL_ROOT}/wheel"

#: Console script inside the managed virtual environment.
LINUX_VENV_BIN = f"{LINUX_VENV_DIR}/bin/{CONSOLE_SCRIPT}"

#: User-facing wrapper installed on PATH.
LINUX_WRAPPER_PATH = f"/usr/bin/{CONSOLE_SCRIPT}"

# --------------------------------------------------------------------------- #
# Windows install layout
# --------------------------------------------------------------------------- #

#: Root directory the MSI installs into.
WINDOWS_INSTALL_ROOT = r"C:\Program Files\SimplyJournalAdmin"

#: Virtual environment created by the MSI custom action.
WINDOWS_VENV_DIR = WINDOWS_INSTALL_ROOT + r"\venv"

#: Directory inside the install root that ships the prebuilt wheel.
WINDOWS_WHEEL_DIR = WINDOWS_INSTALL_ROOT + r"\wheel"

#: Launcher inside the managed virtual environment.
WINDOWS_VENV_BIN = WINDOWS_VENV_DIR + r"\Scripts\simply-journal-admin.exe"

# --------------------------------------------------------------------------- #
# Defaults
# --------------------------------------------------------------------------- #

#: Default look-back window in minutes.
DEFAULT_SINCE_MINUTES = 60

#: Default maximum number of entries returned.
DEFAULT_LIMIT = 100

#: Default Windows event log channel.
DEFAULT_WINDOWS_LOG_NAME = "Application"

#: Valid Windows event log channels exposed through ``--log-name``.
WINDOWS_LOG_NAMES = ("Application", "System", "Security")

#: Poll interval in seconds used by ``--follow`` on Windows.
WINDOWS_FOLLOW_POLL_SECONDS = 2.0

# --------------------------------------------------------------------------- #
# Priority handling
# --------------------------------------------------------------------------- #

#: Syslog priority numbers to human-readable names (shared by both platforms).
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

# --------------------------------------------------------------------------- #
# Exit codes
# --------------------------------------------------------------------------- #

EXIT_OK = 0
EXIT_USAGE = 2  # argparse default for bad arguments
EXIT_MISSING_DEPENDENCY = 3  # systemd/pywin32 not available
EXIT_PERMISSION_DENIED = 4  # insufficient privileges to read a log
EXIT_INVALID_LOG = 5  # invalid or inaccessible log/channel
EXIT_RUNTIME_ERROR = 6  # unexpected runtime failure
EXIT_INTERRUPTED = 130  # Ctrl-C during --follow
