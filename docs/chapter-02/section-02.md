# OS Packages

OS packages distribute Python applications through the package manager of an operating system, such as `apt` on Debian-based systems. They are useful when a Python tool must follow system-level installation, upgrade, and removal workflows.

## Applied Project

### Project Setup

The applied project is a small admin CLI called `simply_journal_admin`, exposed as the `simply-journal-admin` command, that reads recent `systemd` journal entries. It imports [`systemd.journal`](https://www.freedesktop.org/software/systemd/python-systemd/journal.html) from the APT package [`python3-systemd`](https://packages.ubuntu.com/noble/python3-systemd) and declares no PyPI runtime dependencies because the binding comes from the distribution package manager and links against `libsystemd` in `/usr/lib`. This makes it a good fit for the system environment because the runtime dependency is intentionally owned by the operating system package manager instead of a project-local environment.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj2_journal_admin/README.md).