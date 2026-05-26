# Python `venv` environments

This page covers Python's standard-library `venv` module.

## Applied Project

### Project Setup

The applied project is a small web service called `Tiny Webserver Project`. It uses [Bottle](https://bottlepy.org/docs/dev/) as the runtime dependency. This makes it a good fit for `venv` because a small PyPI-based service shows clearly how one project-local environment can isolate application dependencies.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-02/README.md). The project components are documented in the [Project Components](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-02/README.md#project-components) section of the section README.

## `venv` environment model

`venv` has shipped with Python since Python 3.3 in 2012, when it was introduced to give Python a standard built-in tool for project-level isolation. It creates a project-local directory with a private interpreter, `pip`, a package directory, console scripts, and a `pyvenv.cfg` file, while activation is mostly a `PATH` change so the environment-local interpreter resolves first even though the standard library still comes from the base Python installation.

### When to use `venv`?

Because it is built in, lightweight, and close to standard Python packaging, `venv` is a good default for small web services, command-line tools, tutorials, libraries, and scripts whose dependencies come cleanly from PyPI. It is also a good fit when you want to inspect Python's environment mechanics directly.

### Tradeoffs

#### Pros

- ✅ Bundled with Python 
- ✅ Familiar to most Python users.
- ✅ Lightweight folder-based environment that is easy to inspect and remove.
- ✅ Clear `PATH` and `sys.path` behavior once the environment is activated.

#### Cons

- ⚠️ Does not manage Python versions by itself.
- ⚠️ Cannot install non-Python system libraries (e.g. compiler toolchains, etc.)
- ⚠️ Does not provide a built-in lockfile for fully reproducible installs.

### Install `venv`

`venv` is bundled with Python, so there is no separate PyPI package to install.

=== "Linux (Debian-based)"

    If `venv` support is absent, install the distribution-supported package with `apt`:

    ```bash
    sudo apt install python3-venv
    ```

=== "Windows"

    If Python is not installed yet, follow [Install Python](section-01.md#install-python).
    
=== "macOS"

    If Python is not installed yet, follow [Install Python](section-01.md#install-python).

### Environment layout

The exact directory names vary by operating system, but each `venv` still contains an environment-local interpreter, console scripts, a package directory, headers, and `pyvenv.cfg`.

=== "Linux"

    ```text
    .venv/
    ├── bin/
    │   ├── activate
    │   ├── activate.csh
    │   ├── activate.fish
    │   ├── pip
    │   ├── pip3
    │   ├── pip3.x
    │   ├── python
    │   ├── python3
    │   └── python3.x
    ├── include/
    │   └── python3.x/
    ├── lib/
    │   └── python3.x/
    │       └── site-packages/
    │           ├── pip/
    │           └── pip-*.dist-info/
    ├── lib64/
    └── pyvenv.cfg
    ```

=== "Windows"

    ```text
    .venv\
    ├── Include\
    ├── Lib\
    │   └── site-packages\
    │       ├── pip\
    │       └── pip-*.dist-info\
    ├── Scripts\
    │   ├── Activate.ps1
    │   ├── activate.bat
    │   ├── pip.exe
    │   ├── python.exe
    │   └── pythonw.exe
    └── pyvenv.cfg
    ```

=== "macOS"

    ```text
    .venv/
    ├── bin/
    │   ├── activate
    │   ├── activate.csh
    │   ├── activate.fish
    │   ├── pip
    │   ├── pip3
    │   ├── pip3.x
    │   ├── python
    │   ├── python3
    │   └── python3.x
    ├── include/
    │   └── python3.x/
    ├── lib/
    │   └── python3.x/
    │       └── site-packages/
    │           ├── pip/
    │           └── pip-*.dist-info/
    └── pyvenv.cfg
    ```

### Key directories and files

- **Executable directory:** on Linux and macOS, `.venv/bin/` contains the virtual environment's Python executables, `pip`, and shell activation scripts. On Windows, the equivalent directory is `.venv\Scripts\`, which holds `python.exe`, `pip.exe`, and activation scripts such as `Activate.ps1` and `activate.bat`. On Linux, a fresh `venv` commonly uses symlinks for the Python executables, so the environment-local `python3` can still point back to the base interpreter while the surrounding environment changes where packages and scripts are installed.

    Inspect the executable directory:

    ```bash
    ls -lah .venv/bin/
    ```

    A shortened output focused on the executable entries looks like this:

    ```text
    -rwxr-xr-x 1 user user  253 May  9 05:46 pip
    -rwxr-xr-x 1 user user  253 May  9 05:46 pip3
    -rwxr-xr-x 1 user user  253 May  9 05:46 pip3.12
    lrwxrwxrwx 1 user user    7 May  9 05:46 python -> python3
    lrwxrwxrwx 1 user user   16 May  9 05:46 python3 -> /usr/bin/python3
    lrwxrwxrwx 1 user user    7 May  9 05:46 python3.12 -> python3
    ```

    The arrows show the redirect chain. `python` points to `python3`, `python3.12` points to `python3`, and `python3` points to the base interpreter at `/usr/bin/python3`.

- **Header directory:** Linux and macOS store headers under `.venv/include/python3.x/`, while Windows uses `.venv\Include\`. These headers are used when native extensions compile against the interpreter inside the virtual environment.

- **Package directory:** Linux and macOS store installed packages under `.venv/lib/python3.x/site-packages/`, while Windows uses `.venv\Lib\site-packages\`. A fresh Python 3.x `venv` typically contains `pip/` and its `.dist-info` metadata and no project dependencies yet.

- **`lib64/`:** is a platform-specific library alias that appears on some Linux systems.

- **`pyvenv.cfg`:** stores the base interpreter reference and flags such as whether system site-packages are visible. When you run the environment-local `python3`, CPython reads this file early during startup. The `home` key points back to the base Python installation that owns the standard library, while `sys.prefix` and `sys.exec_prefix` are redirected to the local `.venv/` directory.

    A fresh `pyvenv.cfg` looks like this:

    ```ini
    home = /usr/bin
    include-system-site-packages = false
    version = 3.12.3
    executable = /usr/bin/python3.12
    command = /usr/bin/python3 -m venv /path/to/chapter-01/section-02/.venv
    ```

### Activation and import path

- **Environment-local interpreter:** activation puts the virtual environment's executable directory at the front of `PATH`. On Linux and macOS that means `.venv/bin/`; on Windows it means `.venv\Scripts\`. It does not change Python itself; it changes which executable the shell finds first when you run `python`, `python3`, `py`, or `pip`.

    ```text
    Before activation:
    PATH=/usr/local/bin:/usr/bin:/bin:...
    python3 -> /usr/bin/python3

    After activation:
    PATH=/path/to/project/.venv/bin:/usr/local/bin:/usr/bin:/bin:...
    python3 -> /path/to/project/.venv/bin/python3
    ```

- **Environment-local packages:** installed packages land under the environment-local `site-packages` directory, such as `.venv/lib/python3.x/site-packages/` on Linux or macOS and `.venv\Lib\site-packages\` on Windows. This keeps project dependencies separate from the base interpreter. A virtual environment does not replace the base standard library; it uses the base Python's standard library and puts the environment-local package directory ahead of any inherited package directories.

- **System package visibility:** with the default `include-system-site-packages = false` setting in `pyvenv.cfg`, system-wide package directories are normally omitted. That is why a `venv` feels isolated even though it still relies on the base standard library.

- **Prefix inspection:** `sys.prefix` points at the virtual environment, while `sys.base_prefix` still points at the underlying system Python.

    ```python
    import sys
    print(sys.prefix)
    print(sys.base_prefix)
    ```

### Technical Note: Why **`.venv/`** is not portable

You should treat the **`.venv/`** directory as disposable rather than movable. Virtual environments often contain absolute paths in **`pyvenv.cfg`**, console scripts under **`bin/`**, and shebang lines that point at the original interpreter location, so renaming or moving the directory can leave the environment pointing at paths that no longer exist.

In practice, rebuilding is safer than relocating. If the project moves, the usual fix is to remove **`.venv/`** and recreate it from the dependency files instead of trying to preserve the old directory byte-for-byte.

## Workflow

### Create and activate

Create the environment from the section folder:

=== "Linux and macOS"

    ```bash
    python3 -m venv .venv
    ```

    Activate it:

    ```bash
    source .venv/bin/activate
    ```

=== "Windows"

    ```powershell
    py -m venv .venv
    ```

    Activate it in PowerShell:

    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

The new environment starts with the `pip` version supplied by the Python installation. Upgrade it before installing project dependencies.

=== "pip"

	```bash
	pip install --upgrade pip
	```

=== "uv"

	```bash
	uv pip install --upgrade pip
	```

### Install the project

=== "pip"

	Install the project and its declared dependencies with `pip`:

	```bash
	pip install .
	```

=== "uv"

	Install the project and its declared dependencies with `uv` into the active virtual environment:

	```bash
	uv pip install .
	```

## Inspection

Show the active prefixes:

```bash
python3 -c "import sys; print(sys.prefix); print(sys.base_prefix)"
```

Show where installed packages live:

```bash
python3 -c "import bottle, tiny_webserver; print(bottle.__file__); print(tiny_webserver.__file__)"
```

