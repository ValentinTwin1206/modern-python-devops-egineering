# Python Conda environments

This page covers Conda, both as a package manager and as an environment manager. Conda can replace the usual `pip` plus `venv` workflow when you need one tool to manage Python, Python packages, and non-Python packages together.

## Applied Project

### Project Setup

The applied project is a small chemistry analysis library called `HeisenBlue`. It is built on [RDKit](https://www.rdkit.org/), [Pillow](https://python-pillow.org/), and a native [pybind11](https://pybind11.readthedocs.io/) extension. This makes it a good fit for Conda because the workflow combines Python packages, native libraries, and a compiled extension in one Conda environment.

### Run the Project

Application, test, lint, package-build, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_heisenblue/README.md).

## Conda environment model

Conda was first released in 2012 to solve environment and package management for Python projects that also depend on native libraries and non-Python packages. Unlike `venv`, it can manage the Python interpreter version itself and install non-Python dependencies from Conda channels, so one Conda environment can bundle the interpreter, Python packages, native shared libraries, headers, and other runtime files that would otherwise come from the host operating system.

### When to use Conda?

Because it can keep Python, native dependencies, and interpreter version constraints in one environment, Conda is a strong fit for computer vision, numerical computing, geospatial processing, machine learning, and Jupyter notebook workflows that need reproducible kernels and compiled packages across machines. The later [Environment layout](#environment-layout) and [Workflow](#workflow) sections show that structure in more detail.

### Tradeoffs

#### Pros

- ✅ Manages the Python version as part of the environment.
- ✅ Installs Python and non-Python packages together from Conda channels.
- ✅ Keeps Python bindings and native binaries in one environment prefix.
- ✅ Works well for scientific or compiled dependencies, including this OpenCV pipeline.
- ✅ Fits teams already using Anaconda or other Conda-based tooling.

#### Cons

- ⚠️ Heavier than `venv` in tooling footprint and environment size.
- ⚠️ Uses a separate ecosystem alongside PyPI, so you often need both `conda` and `pip`.
- ⚠️ Dependency solving can be slower than simpler PyPI-only workflows.
- ⚠️ Pure-Python projects are often simpler with `venv` plus `pip` or `uv`.

### Install Conda

On Linux, Windows, and macOS, a common starting point is Miniconda. It provides the minimal pieces needed to run `conda` without installing the full Anaconda distribution. User installs typically live under `~/miniconda3` on Unix-like systems, while this section's Docker image is based on `continuumio/miniconda3` where Miniconda already lives at `/opt/conda`.

=== "Linux (Debian-based)"

    Download the Miniconda installer:

    ```bash
    curl -LsSf -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    ```

    Run the installer into a user-local prefix:

    ```bash
    bash miniconda.sh -b -p "$HOME/miniconda3"
    ```

    Put Conda on `PATH` for the current shell:

    ```bash
    export PATH="$HOME/miniconda3/bin:$PATH"
    ```

    !!! warning

        To make `conda activate` work in future Bash shells, you can run:

        ```bash
        conda init bash
        ```

        This edits `~/.bashrc`. In a clean Ubuntu test, a new Bash shell came back with the `base` environment already active. Recommend this only when you plan to work solely with Conda rather than mixing Conda with `venv`, `pip`, or other environment techniques.

=== "Windows"

    Install Miniconda with Windows Package Manager:

    ```powershell
    winget install Anaconda.Miniconda3
    ```

    Check that Conda is available:

    ```powershell
    conda --version
    ```

    !!! warning

        To make `conda activate` work in future PowerShell sessions, you can run:

        ```powershell
        conda init powershell
        ```

        This changes future PowerShell startup behavior and can leave the `base` environment active by default. Recommend this only when you plan to work solely with Conda rather than mixing Conda with `venv`, `pip`, or other environment techniques.

=== "macOS"

    Download the Miniconda installer for Apple Silicon:

    ```bash
    curl -LsSf -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
    ```

    Run the installer into a user-local prefix:

    ```bash
    bash miniconda.sh -b -p "$HOME/miniconda3"
    ```

    Put Conda on `PATH` for the current shell:

    ```bash
    export PATH="$HOME/miniconda3/bin:$PATH"
    ```

    !!! warning

        To make `conda activate` work in future Zsh shells, you can run:

        ```bash
        conda init zsh
        ```

        This edits your shell startup file and can leave the `base` environment active by default. Recommend this only when you plan to work solely with Conda rather than mixing Conda with `venv`, `pip`, or other environment techniques.

### Environment layout

#### Environment name and location

Since Conda stores environments **outside** the project root, it is best practice to use a descriptive name such as `heisenblue-demo` instead of a generic name such as `venv` when creating a Conda environment:

```bash
conda create -y -n heisenblue-demo -c conda-forge python=3.12 rdkit pillow pip
```

By default, the environment is stored under `~/miniconda3` on Linux or macOS and `%UserProfile%\miniconda3` on Windows. 

=== "Linux (Debian-based)"

    ```text
    <conda-prefix>/
    ├── bin/
    │   └── conda
    ├── envs/
    │   └── heisenblue-demo/
    │       ├── bin/
    │       │   ├── heisenblue
    │       │   ├── python
    │       │   └── python3.12
    │       ├── conda-meta/
    │       ├── include/python3.12/
    │       ├── lib/python3.12/site-packages/
    │       └── x86_64-conda-linux-gnu/
    └── pkgs/
    ```

=== "Windows"

    ```text
    <conda-prefix>\
    ├── condabin\
    │   └── conda.bat
    ├── envs\
    │   └── heisenblue-demo\
    │       ├── python.exe
    │       ├── Scripts\
    │       │   ├── heisenblue.exe
    │       │   └── activate.bat
    │       ├── Lib\site-packages\
    │       ├── Library\bin\
    │       └── conda-meta\
    └── pkgs\
    ```

=== "macOS"

    ```text
    <conda-prefix>/
    ├── bin/
    │   └── conda
    ├── envs/
    │   └── heisenblue-demo/
    │       ├── bin/
    │       │   ├── heisenblue
    │       │   ├── python
    │       │   └── python3.12
    │       ├── conda-meta/
    │       ├── include/python3.12/
    │       ├── lib/python3.12/site-packages/
    │       └── lib/
    └── pkgs/
    ```

#### Key directories and files

- **Top-level Conda executable:** the main Conda command lives under the installation prefix, such as `~/miniconda3/bin/conda` on Linux or macOS, or `%UserProfile%\miniconda3\condabin\conda.bat` on Windows.

- **`<conda-prefix>/envs/<name>/`:** is the named environment directory.

- **Environment-local executables:** Linux and macOS store them under `bin/`, while Windows uses `python.exe` at the environment root together with `Scripts\` for `pip.exe`, activation scripts, and console entry points.

- **Python packages:** Linux and macOS store them under `lib/python3.12/site-packages/`, while Windows uses `Lib\site-packages\`. These directories contain Python packages installed from Conda channels or from `pip`.

- **Native runtime files:** Conda also installs shared libraries and other runtime files into the environment, such as `lib/` on Linux or macOS and `Library\bin\` on Windows.

- **`conda-meta/`:** stores Conda's package records and history for the environment.

- **`pkgs/`:** stores the shared package cache for the Conda installation prefix.

#### Environment definition (`environment.yml`)

The `environment.yml` file describes the [respective Conda environment](#environment-layout) from outside and is stored **within the project tree** next to the source code and other project files.

```yaml
name: heisenblue-demo
channels:
  - conda-forge
  # - defaults  # Served from repo.anaconda.com and added by default, so it usually does not need to be listed explicitly.
dependencies:
  - python=3.12
    - rdkit
    - pillow
    - pybind11
    - cmake
    - ninja
  - pip
    - pytest
    - karva
```

- `name`: sets the Conda environment name to `heisenblue-demo`.
- `channels`: tells Conda from where to resolve Conda-managed packages.

    | Source | Kind | Examples |
    | ------ | ---- | -------- |
        | `conda-forge` | Community Conda channel | `python`, `rdkit`, `pillow`, `pybind11` |
    | `defaults` | Anaconda-hosted Conda channel set, served from `repo.anaconda.com` | `python`, `numpy`, `pandas` |

- `dependencies`: lists the Conda-managed packages to install, including Python, RDKit, Pillow, the C++ build tools, and the project test tooling.

## Workflow

### Create and activate

The examples below show three ways to get to a working project setup. The Conda-based paths keep the Python bindings and native binaries inside the environment, while the non-Conda path splits Python packages and system libraries across different locations.

=== "Create from `environment.yml`"

    Create the environment from the section folder:

    ```bash
    conda env create -f environment.yml
    ```

    > This command creates the environment and installs the listed packages.

    Activate the environment:

    ```bash
    conda activate heisenblue-demo
    ```

    Filesystem excerpt:

    ```text
    ~/
    ├── miniconda3/envs/heisenblue-demo/    # environment, managed by conda
    │   ├── bin/python
    │   ├── lib/python3.12/site-packages/
    │   │   ├── heisenblue/
    │   │   ├── heisenblue/_native*.so
    │   │   ├── PIL/
    │   │   └── rdkit/
    │   └── lib/libRDKit*.so
    └── heisenblue/                         # project
        ├── environment.yml
        ├── cpp/
        └── src/heisenblue/
    ```
    
=== "Create from scratch"

    Create the same Conda-managed environment defined in `environment.yml`:

    ```bash
    conda create -y -n heisenblue-demo -c conda-forge \
        python=3.12 \
        rdkit \
        pillow \
        pybind11 \
        cmake \
        ninja \
        pip \
        pytest \
        karva
    ```

    Activate the environment:

    ```bash
    conda activate heisenblue-demo
    ```

    Install the project itself in editable mode:

    ```bash
    (heisenblue-demo) $ python -m pip install -e .
    ```

    Snapshot the environment requirements back to YAML:

    ```bash
    (heisenblue-demo) $ conda env export --from-history > environment.yml
    ```

    Filesystem excerpt:

    ```text
    ~/
    ├── miniconda3/envs/heisenblue-demo/    # environment, managed by conda
    │   ├── bin/python
    │   ├── lib/python3.12/site-packages/
    │   │   ├── heisenblue/
    │   │   ├── heisenblue/_native*.so
    │   │   ├── PIL/
    │   │   └── rdkit/
    │   └── lib/libRDKit*.so
    └── heisenblue/                         # project
        ├── environment.yml
        ├── cpp/
        └── src/heisenblue/
    ```

=== "Without `conda`"

    On Ubuntu-based systems where Python 3.12 is not yet available, add an external package source first:

    ```bash
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    ```

    Install Python 3.12, `venv` support, and the native build tools the project needs:

    ```bash
    sudo apt-get install -y \
        python3.12 \
        python3.12-venv \
        build-essential \
        cmake \
        ninja-build
    ```

    Create and activate a virtual environment:

    ```bash
    python3.12 -m venv .venv && source .venv/bin/activate
    ```

    Install the Python-side tooling into the virtual environment:

    ```bash
    pip install pillow pybind11 scikit-build-core pytest karva
    ```

    A separate RDKit installation still has to come from outside the virtual environment, which is one reason Conda is the easier and more reproducible workflow for this project.

    Filesystem excerpt:

    ```text
    ~/
    └── heisenblue/                          # project
        ├── .venv/                           # project environment, managed by venv/pip
        │   ├── bin/python
        │   └── lib/python3.12/site-packages/
        │       └── heisenblue/
        ├── cpp/
        └── src/heisenblue/

    /usr/                                 # OS filesystem
    ├── bin/python3.12
    ├── bin/cmake
    └── bin/c++
    ```

### Add packages

Ensure that the dedicated Conda environment is active (see [Create and activate](#create-and-activate)).

Add a package from a Conda channel:

```bash
(heisenblue-demo) $ conda install -c conda-forge <package>
```

Add a package from PyPI when it is not available from your chosen Conda channels:

```bash
(heisenblue-demo) $ python -m pip install <package>
```

## Inspection

Show the active environment name:

```bash
echo $CONDA_DEFAULT_ENV
```

List all Conda environments:

```bash
conda env list
```

After activation, the environment's Python becomes the first interpreter on `PATH`, and imports resolve from the environment-specific package directory under the [Conda prefix](#environment-layout) instead of from the [project tree](#environment-definition-environmentyml). Show the active interpreter inside the Conda environment:

```bash
(heisenblue-demo) $ python -c "import sys; print(sys.prefix); print(sys.executable)"
```
