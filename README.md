# Modern Python Engineering

This repository collects small, self-contained examples for teaching how
modern Python projects are packaged and how their development environments
are managed.

## System Requirements

- Linux-based operating system. Use a Linux host or Linux VM.
- Docker Desktop or Podman Desktop. Docker installer: https://docs.docker.com/desktop/setup/install/linux/ Podman installer: https://podman-desktop.io/downloads
- Dev Containers CLI. Install guide: https://containers.dev/supporting#devcontainer-cli

### Dev Containers CLI

Install on Linux (Debian based):

```bash
sudo apt-get update && sudo apt-get install -y nodejs npm
npm install -g @devcontainers/cli
```

Run it without a global install:

```bash
npx @devcontainers/cli up --workspace-folder chapter-01/section-04
```

## Chapter 1: Development Environments

This chapter compares common environment-management approaches, including
system-level Python, `venv`, `conda`, and Dev Containers.

| Section | Topic | Focus | Details |
| ------- | ----- | ----- | ------- |
| [section-01](./chapter-01/section-01/README.md) | Python system environment | APT-managed Linux Python with a `systemd.journal` admin CLI, `PATH`, `sys.path`, and system vs user installs | [README](./chapter-01/section-01/README.md) |
| [section-02](./chapter-01/section-02/README.md) | Python `venv` environments | standard-library virtual environments | [README](./chapter-01/section-02/README.md) |
| [section-03](./chapter-01/section-03/README.md) | Python `conda` environments | interpreter and non-Python dependency management | [README](./chapter-01/section-03/README.md) |
| [section-04](./chapter-01/section-04/README.md) | Python dev containers | VS Code Dev Containers, multiple runtimes, and a Nuitka binary container | [README](./chapter-01/section-04/README.md) |

## Chapter 2: Python Project Configuration

This chapter walks through the same small package across multiple packaging
eras, from early `distutils` through a `pyproject.toml`-based workflow.

| Section | Year | Era | Packaging shape | Details |
| ------- | ---- | --- | --------------- | ------- |
| [section-01](./chapter-02/section-01/README.md) | 2000 | Python 1.6 | `setup.py` with stdlib `distutils` | [README](./chapter-02/section-01/README.md) |
| [section-02](./chapter-02/section-02/README.md) | 2003 | Python 2.3 | `setup.py` with metadata-only dependency hints | [README](./chapter-02/section-02/README.md) |
| [section-03](./chapter-02/section-03/README.md) | 2004 | Python 2.4 | `setup.py` with early `setuptools` | [README](./chapter-02/section-03/README.md) |
| [section-04](./chapter-02/section-04/README.md) | 2010 | Python 2.7 | `setup.py` plus pinned `requirements.txt` | [README](./chapter-02/section-04/README.md) |
| [section-05](./chapter-02/section-05/README.md) | 2016 | Python 3.5 / 2016 workflow | `setup.py` + `setup.cfg` + `requirements*.txt` | [README](./chapter-02/section-05/README.md) |
| [section-06](./chapter-02/section-06/README.md) | 2022 | Python 3.11 / 2022 workflow | `pyproject.toml` only | [README](./chapter-02/section-06/README.md) |
