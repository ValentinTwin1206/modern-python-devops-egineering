# Python Conda environments

This page covers Conda, both as a package manager and as an environment manager. Conda can replace the usual `pip` plus `venv` workflow when you need one tool to manage Python, Python packages, and non-Python packages together.

## Applied Project

### Project Setup

The applied project is a small image-processing pipeline called `Image Processor Project`. It is built on [OpenCV](https://opencv.org/) and [NumPy](https://numpy.org/). This makes it a good fit for Conda because the workflow combines Python packages with native libraries that are easier to manage together in one Conda environment.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_image_processor/README.md).

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

Since Conda stores environments **outside** the project root, it is best practice to use a descriptive name such as `image-processor` instead of a generic name such as `venv` when creating a Conda environment:

```bash
conda create -y -n image-processor python=3.12 pip
```

By default, the environment is stored under `~/miniconda3` on Linux or macOS and `%UserProfile%\miniconda3` on Windows. 

=== "Linux (Debian-based)"

    ```text
    <conda-prefix>/
    ├── bin/
    │   └── conda
    ├── envs/
    │   └── image-processor/
    │       ├── bin/
    │       │   ├── pip
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
    │   └── image-processor\
    │       ├── python.exe
    │       ├── Scripts\
    │       │   ├── pip.exe
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
    │   └── image-processor/
    │       ├── bin/
    │       │   ├── pip
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
name: image-processor
channels:
  - conda-forge
  # - defaults  # Served from repo.anaconda.com and added by default, so it usually does not need to be listed explicitly.
dependencies:
  - python=3.12
  - numpy=2.1.3
  - opencv=4.10.0
  - pip
  - pip:
      - ruff>=0.15.12
      - karva>=0.0.1a5
```

- `name`: sets the Conda environment name to `image-processor`.
- `channels`: tells Conda from where to resolve Conda-managed packages.

    | Source | Kind | Examples |
    | ------ | ---- | -------- |
    | `conda-forge` | Community Conda channel | `numpy`, `opencv`, `python` |
    | `defaults` | Anaconda-hosted Conda channel set, served from `repo.anaconda.com` | `python`, `numpy`, `pandas` |

- `dependencies`: lists the Conda-managed packages to install, including Python, NumPy, OpenCV, and `pip` itself.
- `dependencies.pip`: lists the PyPI-only project tools to install through the nested `pip:` block. PyPI sources, including proprietary ones, do not belong in `channels:`; configure them through `pip`, for example with `--index-url` or `--extra-index-url` entries inside the nested `pip:` list or through standard `pip` configuration.

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
    conda activate image-processor
    ```

    Filesystem excerpt:

    ```text
    ~/
    ├── miniconda3/envs/image-processor/    # environment, managed by conda
    │   ├── bin/python
    │   ├── lib/python3.12/site-packages/
    │   │   ├── cv2/
    │   │   ├── numpy/
    │   │   ├── ruff/
    │   │   └── karva/
    │   └── lib/libopencv_*.so
    └── image-processor/                    # project
        ├── environment.yml
        └── src/image_processor/
    ```
    
=== "Create from scratch"

    Create the same Conda-managed environment defined in `environment.yml`:

    ```bash
    conda create -y -n image-processor -c conda-forge \
        python=3.12 \
        numpy=2.1.3 \
        opencv=4.10.0 \
        pip
    ```

    Activate the environment:

    ```bash
    conda activate image-processor
    ```

    Install the PyPI-only tools:

    ```bash
    (image-processor) $ python -m pip install "ruff>=0.15.12" "karva>=0.0.1a5"
    ```

    Snapshot the environment requirements back to YAML:

    ```bash
    (image-processor) $ conda env export --from-history > environment.yml
    ```

    Filesystem excerpt:

    ```text
    ~/
    ├── miniconda3/envs/image-processor/    # environment, managed by conda
    │   ├── bin/python
    │   ├── lib/python3.12/site-packages/
    │   │   ├── cv2/
    │   │   ├── numpy/
    │   │   ├── ruff/
    │   │   └── karva/
    │   └── lib/libopencv_*.so
    └── image-processor/                    # project
        ├── environment.yml
        └── src/image_processor/
    ```

=== "Without `conda`"

    On Ubuntu-based systems where Python 3.12 is not yet available, add an external package source first:

    ```bash
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    ```

    Install Python 3.12, `venv` support, and the system libraries OpenCV depends on:

    ```bash
    sudo apt-get install -y \
        python3.12 \
        python3.12-venv \
        libopencv-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev
    ```

    Create and activate a virtual environment:

    ```bash
    python3.12 -m venv .venv && source .venv/bin/activate
    ```

    Install the Python bindings from PyPI:

    ```bash
    pip install opencv-python
    ```

    This split workflow leaves Python packages in `.venv/` while the native libraries stay under `/usr/`.

    Filesystem excerpt:

    ```text
    ~/
    └── image-processor/                     # project
        ├── .venv/                           # project environment, managed by venv/pip
        │   ├── bin/python
        │   └── lib/python3.12/site-packages/
        │       └── cv2/
        └── src/image_processor/

    /usr/                                 # OS filesystem
    ├── bin/python3.12
    ├── include/opencv4/
    └── lib/x86_64-linux-gnu/libopencv_*.so*
    ```

### Add packages

Ensure that the dedicated Conda environment is active (see [Create and activate](#create-and-activate)).

Add a package from a Conda channel:

```bash
(image-processor) $ conda install -c conda-forge <package>
```

Add a package from PyPI when it is not available from your chosen Conda channels:

```bash
(image-processor) $ python -m pip install <package>
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
(image-processor) $ python -c "import sys; print(sys.prefix); print(sys.executable)"
```
