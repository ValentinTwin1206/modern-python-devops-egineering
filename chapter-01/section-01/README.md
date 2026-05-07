# Tiny Webserver System Environment

This project explains how Python is laid out on a Linux system. It
uses a tiny `bottle` web server, `uv`, a `karva` test and `ruff` linting,
partly to reflect the recent Rust footprint in Python tooling.

The `Dockerfile.devEnv` is the important system-level demonstration. It
inspects a real Ubuntu-based Python installation:

- It starts from `ubuntu:24.04`
- It installs `python3` and `python3-pip` via APT.
- It installs `karva` and `ruff` with `pip3 install --user`.
- It installs `uv`
- It installs `bottle` with `uv` at system level
- It drops into an interactive shell so you can inspect the Python
  filesystem layout directly.

The companion `Dockerfile` is the deployment image. It builds a wheel
for `tiny-webserver`, installs that wheel into Ubuntu's system Python,
and starts the dedicated `tiny-webserver` console entry point.

Start the container with a bind mount so the project files appear under
`/app` at runtime:

```sh
docker build -f Dockerfile.devEnv -t py-sys-env chapter-01/section-01
docker run --rm -it -v "$PWD/chapter-01/section-01:/app" py-sys-env
```

Build and run the deploy image:

```sh
docker build -t tiny-webserver-system chapter-01/section-01
docker run --rm -p 8080:8080 tiny-webserver-system
```

## Python System Footprint

### Overview

A Python installation is more than one executable. It includes the
CPython interpreter, standard library modules, package directories,
build and configuration files, native-extension headers, and shell
integration through `PATH`.

On Debian and Ubuntu, the system interpreter is usually exposed as
`/usr/bin/python3` and managed by APT under `/usr`. Another common path
is `/usr/local/bin/python`, often used by manually installed Python
builds or container images such as `python:3.11-slim`. In this Ubuntu
example, Python is installed under `/usr` through APT.

On Ubuntu, `python3` is normally pre-installed (see table below), while 
the bare `python` command may not exist unless an alias or package 
provides it. You can check the resolved executable with `which python3` 
or `which python`.

| Ubuntu release | APT suite | Bundled `python3` |
| --- | --- | --- |
| 22.04 LTS | `jammy` | Python 3.10 |
| 24.04 LTS | `noble` | Python 3.12 |

### Python Installation Folder Structure

On Ubuntu, those Python components are split across several directories
depending on their role and how they were installed:

- **Interpreters** live under `/usr/bin/`.
  The main system executable is usually `/usr/bin/python3`.

- **Standard library modules** live under `/usr/lib/python3.x/`.
  This is where bundled modules such as `os`, `sys`, `json`, and
  `pathlib` are stored. Imports such as the following work because they
  ship with Python itself:

  ```python
  import os
  import sys
  ```

- **System-managed Python packages** live under
  `/usr/lib/python3/dist-packages/`.
  Ubuntu's package manager installs Python libraries there for
  system-wide use. For example, `apt install python3-pip` places the
  `pip` package under `/usr/lib/python3/dist-packages/pip/` and the
  `pip3` command under `/usr/bin/pip3`, and
  `python3-apt` places the `apt` package under
  `/usr/lib/python3/dist-packages/apt/`.

- **User-installed packages** live under
  `~/.local/lib/python3.x/site-packages/`.
  This is where `pip install --user` writes packages without modifying
  the system interpreter. In this container,
  `pip3 install --user karva ruff` places those packages under
  `/root/.local/lib/python3.12/site-packages/` and exposes the `karva`
  and `ruff` commands under `/root/.local/bin/`.

- **Globally installed third-party packages** commonly live under
  `/usr/local/lib/python3.x/dist-packages/`.
  This is the usual destination for administrative `pip` or `uv`
  installs outside APT. In this container, `uv` installs `bottle`
  there. Third-party imports such as the following only work when those
  packages have been installed into one of the active package
  directories:

  ```python
  import bottle
  import karva
  ```

- **Header files** live under `/usr/include/python3.x/`.
  They are used when compiling extension modules and other native
  bindings against Python's C API.

- **Build configuration and Makefile fragments** live under
  `/usr/lib/python3.x/config-3.x-<arch>/`.
  These files describe how that Python build was compiled for the
  current architecture.

- **Installed package metadata** often appears as directories such as
  `bottle-0.13.4.dist-info/` and `ruff-0.15.12.dist-info/` inside the
  active package directory. These metadata directories record version
  information, dependencies, entry points, and installed files.

### PATH And Execution

When you type a command, the shell searches `PATH` from left to right.
It does not search the whole filesystem.

```sh
echo $PATH
which python3
which ruff
```

If `/usr/local/bin` appears before `/usr/bin`, a manually installed
Python in `/usr/local/bin/python` may win over an APT-managed Python in
`/usr/bin/python3`. If a virtual environment is active, `.venv/bin`
usually appears first.

Python imports have their own search path, `sys.path`:

```sh
python3 -c "import sys; print(sys.path)"
```

Executables are resolved by the shell through `PATH`. Imports are
resolved by Python through `sys.path`.

## Python Package Installation

Installing a Python package means placing importable files and package
metadata somewhere on Python's import path. The installation target
decides who can import the package and which projects are affected by
future version changes.

### System-Level Installations

#### Installation Target

System installations write into directories owned by the operating
system interpreter. On Ubuntu, that usually means paths such as
`/usr/lib/python3/dist-packages/` or, for administrator-managed local
installs, `/usr/local/lib/python3.x/dist-packages/`.

#### When To Use It

Use this setup when a container, base image, or dedicated machine is
meant to expose one shared Python environment.

#### Command Patterns

##### uv

Use `uv` with an explicit `--system` target when packages should be
installed into the system interpreter. Modern Debian and Ubuntu 
mark the APT-managed interpreter as externally managed through 
PEP 668, so the practical system-level pattern is:

```sh
uv pip install --system --break-system-packages bottle
```

##### pip

`pip` can also target the system interpreter, but on current Debian and
Ubuntu it needs the same explicit override:

```sh
pip3 install --break-system-packages bottle
```

##### apt

APT-managed Python packages are system-level installations as well. Use
this when the package is shipped by the distribution, for example with
`python3-systemd`.

```sh
sudo apt install python3-systemd
```

#### Tradeoffs

##### Pros

System installs are simple for containers and base images because
there is only one interpreter to inspect and run.

##### Cons

They are risky on developer machines and shared servers because 
one package upgrade can affect operating system tools or unrelated 
applications.

### User-Level Installations

#### Installation Target

User installations write below the current user's home directory. Python
packages normally go under `~/.local/lib/python3.x/site-packages/`, while
command-line scripts go under `~/.local/bin/`.

#### When To Use It

Use this setup when one user needs extra tools or libraries without
administrative access and without changing APT-managed directories. It
works well for personal CLI tools, but it is weaker for reproducible
project development.

#### Command Patterns

##### uv

`uv` also supports `--user`, but this container uses `pip3` for the
user-level example so the distinction from the system-level `uv`
installation stays obvious.

##### pip

`pip` supports the same user-level pattern through the active system
interpreter.

```sh
pip3 install --user karva ruff
```

`apt` does not fit here because it installs distribution-managed packages
into the system interpreter rather than into one user's home directory.

#### Tradeoffs

##### Pros

User installs avoid administrative permissions and leave APT-owned
files alone.

##### Cons

They still share one user-level package directory, so different
projects can accidentally depend on or overwrite the same package
versions. Scripts also require `~/.local/bin` to appear on `PATH`.

### Virtual Environment Installations

Virtual environments keep dependencies inside a project-local directory
such as `.venv/`, with their own interpreter and `site-packages`, and
they are the normal choice when dependencies should stay isolated from
the system interpreter and from other projects. For the detailed
comparison and setup instructions, see
[`../section-02/README.md`](../section-02/README.md) and the
tool-specific guides for
[`venv`](../section-02/venv/README.md),
[`conda`](../section-02/conda/README.md), and
[`pipenv`](../section-02/pipenv/README.md).

## Useful Inspection Commands

Use these command patterns inside the container to inspect the Python
installation:

### Resolved Interpreter

Show which executable the shell resolves from `PATH`.

```sh
which python3
```

Expected output:

```text
/usr/bin/python3
```

### pip3 Command

Show that the APT-installed `pip3` command is available directly on the
shell path.

```sh
which pip3
```

Expected output:

```text
/usr/bin/pip3
```

### Python Version

Show the Python version installed by APT.

```sh
python3 --version
```

Expected output:

```text
Python 3.12.x
```

### Site Configuration

Show Python's site configuration, including user and system package
directories.

```sh
python3 -m site
```

Expected output:

```text
sys.path = [
    '/app/src',
  '/usr/lib/python314.zip',
  '/usr/lib/python3.12',
  '/usr/lib/python3.12/lib-dynload',
  '/root/.local/lib/python3.12/site-packages',
  '/usr/local/lib/python3.12/dist-packages',
    '/usr/lib/python3/dist-packages',
]
USER_BASE: '/root/.local' (exists)
USER_SITE: '/root/.local/lib/python3.12/site-packages' (exists)
ENABLE_USER_SITE: True
```

### Import Path

Print every entry on Python's import path.

```sh
python3 -c "import sys; [print(path) for path in sys.path]"
```

Expected output:

```text
/app/src
/usr/lib/python314.zip
/usr/lib/python3.12
/usr/lib/python3.12/lib-dynload
/root/.local/lib/python3.12/site-packages
/usr/local/lib/python3.12/dist-packages
/usr/lib/python3/dist-packages
```

### APT-Managed Package Files

Show where Debian places the files owned by `python3-pip`.

```sh
dpkg -L python3-pip | grep -E '/usr/bin/pip3$|/dist-packages/pip(/|$)' | head
```

Expected output:

```text
/usr/bin/pip3
/usr/lib/python3/dist-packages/pip
/usr/lib/python3/dist-packages/pip/__init__.py
```

### Another APT-Managed Python Package

Show where Debian places the files owned by `python3-apt`.

```sh
dpkg -L python3-apt | grep -E '/dist-packages/(apt|apt_pkg)(\.|/|$)' | head
```

Expected output:

```text
/usr/lib/python3/dist-packages/apt
/usr/lib/python3/dist-packages/apt/__init__.py
/usr/lib/python3/dist-packages/apt/cache.py
```

### Sysconfig Directories

Show the active `sysconfig` directories for the standard library,
packages, and headers.

```sh
python3 -c "import sysconfig; print('stdlib =', sysconfig.get_path('stdlib')); print('purelib =', sysconfig.get_path('purelib')); print('platlib =', sysconfig.get_path('platlib')); print('include =', sysconfig.get_path('include'))"
```

Expected output:

```text
stdlib = /usr/lib/python3.12
purelib = /usr/local/lib/python3.12/dist-packages
platlib = /usr/local/lib/python3.12/dist-packages
include = /usr/include/python3.12
```

### Installed Package Locations

Show where the `uv`-installed system-level package physically lives.

```sh
python3 -c "import bottle; print('bottle =', bottle.__file__)"
```

Expected output:

```text
bottle = /usr/local/lib/python3.12/dist-packages/bottle.py
```

### User-Installed Package Locations

Show where the `pip3 --user` example packages and their console scripts
live.

```sh
python3 -c "import karva, ruff; print('karva =', karva.__file__); print('ruff =', ruff.__file__)" && which karva && which ruff
```

Expected output:

```text
karva = /root/.local/lib/python3.12/site-packages/karva/__init__.py
ruff = /root/.local/lib/python3.12/site-packages/ruff/__init__.py
/root/.local/bin/karva
/root/.local/bin/ruff
```

### Project Tree

Show the bind-mounted project tree inside the container.

```sh
tree -L 4 /app
```

Expected output:

```text
/app
|-- pyproject.toml
|-- uv.lock
|-- src
|   `-- tiny_webserver
|       |-- __init__.py
|       `-- app.py
`-- tests
    `-- test_app.py
```