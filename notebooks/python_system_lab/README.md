# Python System Environment — The Raise of Python

Alice, a young software engineer, visits Bob, the grumpy, old-fashioned IT administrator, with a gift of chocolate and a request for a remote Ubuntu development environment. Her project will bring IrisLab's iris-color analysis model to users through a REST API, protected by middleware and accessible from a CLI. Bob is confident that one system Python is enough for everyone, but Alice wants to understand what the shared server provides before installing anything. Together, they examine Ubuntu's Python installation and discover how its package locations affect different users and projects.

![Python System Environment project logo](./project_logo.png)

## Overview

- Ubuntu's distribution-managed Python interpreter and development packages.
- The Python installation footprint, including the standard library, headers, and package directories.
- Shell `PATH`, Python's `sys.path`, and import resolution.
- APT-managed, administrator, and user package installation targets and their visibility.
- The tradeoffs of sharing one system interpreter across users and projects.

## Documentation

- [Chapter 01, Section 01: Python System Environment](../../docs/chapter-01/section-01.md)
- [Open the notebook](./python_system_lab.ipynb); continue with [The Isolation Awakens](../python_venv_lab/python_venv_lab.ipynb).

To run the lab, open `notebooks/python_system_lab` in VS Code with Docker and the Dev Containers extension, then select **Dev Containers: Reopen in Container**. Open the notebook, select **Python 3 - System Lab**, and run the cells in order. The Ubuntu container supplies Python and Jupyter; the notebook installs an APT package and a user package inside the container, requiring network access. Rebuild the container to reset those installations.
