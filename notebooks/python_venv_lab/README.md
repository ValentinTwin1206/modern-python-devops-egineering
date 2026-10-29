# Python `venv` Environments — The Isolation Awakens

Alice shows Bob how project-local virtual environments share a base Python but
isolate installed packages. The technical companion is
[Chapter 01, Section 02](../../docs/chapter-01/section-02.md); the story starts
in [The Raise of Python](../python_system_lab/python_system_lab.ipynb).

![Python venv project logo](./project_logo.png)

## Run the lab

1. Install Docker and the VS Code Dev Containers extension.
2. Open `notebooks/python_venv_lab` as the workspace and select **Dev Containers: Reopen in Container**.
3. Open `python_venv_lab.ipynb`, select **Python 3 - venv Lab**, and run the cells in order.

The Ubuntu 24.04 container provides system Python, `venv`, pip, and Jupyter.
The notebook creates two environments under the ignored `lab/` directory. Its
first setup cell removes that directory on reruns, so keep unrelated work
elsewhere. Downloading the demonstration packages requires network access.
The notebook kernel stays in `/opt/jupyter`; the cells explicitly invoke each
environment's interpreter. Documentation links are accessible when browsing the
repository; the workspace mount contains only this lab directory.
