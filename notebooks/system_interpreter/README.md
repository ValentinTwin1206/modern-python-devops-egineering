# System Interpreter — Dependency Isolation Demonstration

A self-contained Dev Container plus a single Jupyter notebook that walks through
one of the oldest problems in Python packaging:

> **What happens when several users and several projects all try to share one
> system Python interpreter?**

The notebook progressively demonstrates three solutions:

1. **System-wide packages** — everyone shares one environment.
2. **`pip install --user`** — each Linux user gets their own package scope.
3. **Per-project virtual environments** — each project gets its own scope.

## Files in this directory

| Path | Description |
| --- | --- |
| `.devcontainer/Dockerfile` | Ubuntu 26.04 image with Python 3, `pip`, `venv`, JupyterLab, ipywidgets, `sudo`, and Bob's legacy dependency `requests==2.0.0` pre-installed system-wide. Creates two real Linux users, `bob` (sudo) and `alice` (no sudo). |
| `.devcontainer/devcontainer.json` | VS Code Dev Container config. Default user is `bob`. Installs the Python and Jupyter extensions and pins the default interpreter to `/usr/bin/python3`. |
| `system_interpreter.ipynb` | Everything else. The three demo applications are embedded in the notebook as Python strings and written to disk from a cell. |

## Version Notes and Discrepancies

The prompt asked for `requests==2.34.2` for Alice's projects. **That release
does not exist on PyPI** — the `requests` project has not published a 2.34.x
line. The notebook and demos therefore use the closest real, installable
release:

| Requested | Actually installed | Reason |
| --- | --- | --- |
| `requests==2.0.0` (Bob) | `requests==2.0.0` | Real, ships from 2013. |
| `requests==2.34.2` (Alice) | `requests==2.32.3` | `2.34.2` does not exist on PyPI. `2.32.3` is the current stable release and demonstrates the same conflict against Bob's `2.0.0`. |
| FastAPI for Alice v1 | `fastapi==0.68.2` | Older FastAPI on Pydantic v1. |
| FastAPI for Alice v2 | `fastapi==0.111.1` | Newer FastAPI on Pydantic v2. |

The notebook prints the actual versions from every environment so students
can see the substitution rather than trust the prose.

## Option A — Open in VS Code Dev Containers

1. Install [Docker](https://docs.docker.com/get-docker/) and the
   [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   extension for VS Code.
2. Open the repository root in VS Code.
3. Run **Dev Containers: Reopen in Container** and pick the
   `notebooks/system_interpreter` folder.
4. When the container is ready, open `system_interpreter.ipynb`.
5. Select the kernel **Python 3 — Ubuntu System** (this is
   `/usr/bin/python3`). Run cells top-to-bottom.

The default user inside the container is `bob`.

## Option B — Manual Docker + JupyterLab

Build the image from the `.devcontainer/` folder:

```bash
docker build \
    -t system-interpreter-demo \
    -f notebooks/system_interpreter/.devcontainer/Dockerfile \
    notebooks/system_interpreter/.devcontainer
```

Start the container, mount the notebook directory, and expose JupyterLab on
port 8888:

```bash
docker run --rm -it \
    --name system-interpreter-demo \
    -p 8888:8888 \
    -v "$(pwd)/notebooks/system_interpreter:/workspace" \
    -w /workspace \
    system-interpreter-demo \
    jupyter lab \
        --ip=0.0.0.0 \
        --port=8888 \
        --no-browser \
        --ServerApp.token='' \
        --ServerApp.password='' \
        --ServerApp.root_dir=/workspace
```

Open <http://localhost:8888> in your host browser and click
`system_interpreter.ipynb`.

> The empty token and password are intentional for a throwaway teaching
> container. Do not use this configuration outside of a local demo.

Stop it with `Ctrl+C` in the terminal that started it.

## What the notebook demonstrates

The notebook is organised into these sections. Every section prints the
Python executable and package versions actually in play, so nothing is
implicit.

1. The shared machine — one interpreter, one system site-packages.
2. Bob and Alice — two real Linux users, one has sudo, the other does not.
3. Three tiny embedded projects written to disk from a cell.
4. Bob's system Python works.
5. Alice upgrades `requests` for herself, system-wide, and breaks Bob.
6. The system environment is restored to `requests==2.0.0`.
7. Alice retries with `pip install --user`. Bob is now safe.
8. Alice hits the second wall: two projects with incompatible FastAPI
   requirements cannot both live in her `--user` scope.
9. Each project gets its own `python3 -m venv`. All three apps coexist.
10. An `ipywidgets` dropdown lets students switch between running commands
    as `bob` and `alice` from inside the notebook.
11. A summary table visualises how the isolation boundary tightens across
    the three approaches.

## Users

| User | Password | Home | Sudo |
| --- | --- | --- | --- |
| `bob` | `bar` | `/home/bob` | Yes (passwordless for demos). |
| `alice` | `foo` | `/home/alice` | No. |

Passwords are documented here only because this is an ephemeral teaching
image. The notebook never prints them.

## Cleanup

```bash
docker rm -f system-interpreter-demo 2>/dev/null || true
docker image rm system-interpreter-demo
```
