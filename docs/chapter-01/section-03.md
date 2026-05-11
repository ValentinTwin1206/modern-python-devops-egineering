# Python `Conda` environments

This page covers Conda, both as a package manager and as an environment manager. Conda can replace the usual `pip` plus `venv` workflow when you need one tool to manage Python, Python packages, and non-Python packages together.

## Image Processor Project

### Project Setup

The [Image Processor Project](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/README.md) is a small image-processing pipeline built on [OpenCV](https://opencv.org/) and [NumPy](https://numpy.org/), with [Karva](https://matthewmckee4.github.io/karva/) and [Ruff](https://docs.astral.sh/ruff/) as project tools. The project files below show how [Conda](https://docs.conda.io/) declares and reproduces that environment in development and deployment.

| Component            | Description |
| -------------------- | ----------- |
| [`src/image_processor/main.py`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/src/image_processor/main.py) | This module generates a synthetic grayscale image, blurs it, runs Canny edge detection, and writes the result to disk. It is intentionally short so the focus stays on the binary dependencies the environment supplies. |
| [`environment.yml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/environment.yml) | This file declares the Conda environment for the example project. It pins the interpreter, NumPy, and OpenCV from `conda-forge`, and records extra Python tools installed through `pip`. |
| [`Dockerfile.devEnv`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/Dockerfile.devEnv) | This development image is based on `continuumio/miniconda3` and creates the named environment with `conda env create`. It provides a reproducible Conda setup with OpenCV, NumPy, and dev tools pre-configured. |
| [`Dockerfile`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/Dockerfile) | This deployment image builds the project wheel and runs it inside a dedicated Conda environment. It shows how the same environment model can be used beyond local inspection. |
| [`pyproject.toml`](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/pyproject.toml) | This file defines the Python package metadata for the image processor. It is the source of the package that later gets installed into the Conda environment. |

### Run the project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/chapter-01/section-03/README.md).

## `Conda` environment model

Conda was first released in 2012 to solve environment and package management for Python projects that also depend on native libraries and non-Python packages. 

Unlike `venv`, it can manage the Python interpreter version itself and install non-Python dependencies from Conda channels. A Conda environment can bundle the interpreter, Python packages, native shared libraries, headers, and other runtime files that would otherwise come from the host operating system, which is why it is common in data-science and Jupyter notebook workflows as well as application projects.

### When to use `Conda`?

Because it can keep Python, native dependencies, and interpreter version constraints in one environment, Conda is a strong fit for computer vision, numerical computing, geospatial processing, machine learning, and Jupyter notebook workflows that need reproducible kernels and compiled packages across machines. The later [Environment layout](#environment-layout) and [Practical demo: one install, two models](#practical-demo-one-install-two-models) sections show that structure in more detail.

### Tradeoffs

#### Pros

- ✅ Manages Python interpreter versions as part of the environment definition.
- ✅ Installs non-Python packages (such as the native libraries OpenCV needs) from Conda channels alongside Python packages.
- ✅ Works well for scientific or compiled dependencies that are awkward in plain `pip` workflows, which is exactly the case for the OpenCV pipeline used here.
- ✅ Fits teams that already use Anaconda or Conda-based tooling across platforms and languages.

#### Cons

- ⚠️ Heavier than `venv` in both tooling footprint and environment size.
- ⚠️ Maintains a separate ecosystem alongside PyPI, which means you often need to understand both `conda` and `pip`.
- ⚠️ Dependency solving can be slower than simpler PyPI-only workflows.
- ⚠️ Pure-Python projects with straightforward PyPI dependencies are often simpler with `venv` and `pip` or `uv`.

### Install `Conda`

On Debian-based Linux, a common starting point is Miniconda. It provides the minimal pieces needed to run `conda` without installing the full Anaconda distribution. User installs typically live under `~/miniconda3`, while this section's Docker image is based on `continuumio/miniconda3` where Miniconda already lives at `/opt/conda`.

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

Initialize Conda for future Bash shells:

```bash
conda init bash
```

### Environment layout

Because environments are usually stored centrally, environment names need to be unique within one Conda installation. Use descriptive names such as `image-processor` instead of generic names such as `venv`. A fresh Conda environment created with `conda create -n fresh-env python=3.12 pip` looks like this:

```text
<conda-prefix>/
├── bin/
│   └── conda
├── envs/
│   └── fresh-env/
│       ├── bin/
│       │   ├── pip
│       │   ├── pip3
│       │   ├── python
│       │   ├── python3
│       │   └── python3.12
│       ├── compiler_compat/
│       ├── conda-meta/
│       ├── etc/
│       ├── include/
│       │   └── python3.12/
│       ├── lib/
│       │   └── python3.12/
│       │       └── site-packages/
│       │           ├── packaging/
│       │           ├── pip/
│       │           ├── setuptools/
│       │           └── wheel/
│       ├── man/
│       ├── share/
│       ├── ssl/
│       └── x86_64-conda-linux-gnu/
└── pkgs/
```

### Key directories and files

- **`/opt/conda/bin/conda`:** is the top-level Conda executable that manages environments and packages.

- **`<conda-prefix>/envs/<name>/`:** is the named environment directory; in this section's development image that path is `/opt/conda/envs/image-processor`.

- **`bin/`:** contains the environment-local executables, including Python, `pip`, and any console scripts installed into the environment.

- **`lib/python3.12/site-packages/`:** contains the Python packages installed into the Conda environment, regardless of whether they came from Conda channels or from `pip`.

- **`conda-meta/`:** stores Conda's package records and history for the environment.

- **`compiler_compat/`:** contains linker and compiler-compatibility helpers bundled into the environment.

- **`pkgs/`:** stores the shared package cache for the Conda installation prefix.

### Activation and import path

- **Environment-local interpreter:** after `conda activate image-processor`, the environment's `python3` becomes the first interpreter on `PATH`.

- **Environment-local packages:** imports resolve from `/opt/conda/envs/image-processor/lib/python3.12/site-packages/` in this section's Docker image.

- **Environment location:** unlike `venv`, the environment does not live inside the project folder by default; it lives under the Conda installation prefix.

  ```python
  import sys
  print(sys.prefix)
  print(sys.executable)
  ```

### Environment definition

The environment is described in `environment.yml`:

```yaml
name: image-processor
channels:
  - conda-forge
dependencies:
  - python=3.12
  - numpy=2.1.3
  - opencv=4.10.0
  - ruff=0.15.12
  - pip
  - pip:
      - karva>=0.0.1a5
```

NumPy and OpenCV come from `conda-forge`, which provides their compiled native libraries. Karva is installed through `pip` because it is published on PyPI and is not part of any Conda channel used here.

### Package sources

Conda does not download packages from `pypi.org` by default. In its default configuration, it installs packages from Anaconda-hosted Conda channels such as `repo.anaconda.com`, and many projects use community channels such as `conda-forge` for broader package availability.

Those Conda channels are package repositories, but they are not mirrors of the Python Package Index at `pypi.org`. Some packages are available from Conda channels and not from PyPI, especially compiled or data-science-oriented packages. Other Python packages are available on PyPI but not from the Conda channels you use, which is why Conda environments often include `pip` as a fallback.

| Source type            | Typical tool      | Best fit                                                       |
| ---------------------- | ----------------- | -------------------------------------------------------------- |
| Conda channel package  | `conda install`   | Python itself, native libraries, and packages published to Conda channels |
| PyPI package           | `pip install`     | Packages downloaded from `pypi.org` when Conda channels do not provide them |

Using both tools in one environment is normal in Conda workflows, but it helps to install Conda packages first and use `pip` only for packages that Conda does not provide. That keeps Conda's package records in `conda-meta/` as complete as possible before PyPI packages are layered on top.

### Practical demo: one install, two models

The benefit of Conda is easiest to see when a single `conda install` pulls a Python package together with the compiled C and C++ libraries it depends on. The walkthrough below uses one of the project's showcase packages: `opencv` from `conda-forge`.

The commands differ most clearly when shown side by side:

=== "With `Conda`"

    Create the environment and install Python and OpenCV from `conda-forge` in one step:

    ```bash
    conda create -y -n demo -c conda-forge python=3.12 opencv
    ```

    Conda solves the environment, downloads the packages, and installs everything under `/opt/conda/envs/demo` (or `~/miniconda3/envs/demo` for a user install).

=== "Without `Conda`"

    Update the system package index first:

    ```bash
    sudo apt-get update
    ```

    Install the system libraries OpenCV depends on:

    ```bash
    sudo apt-get install -y python3.12 python3.12-venv libopencv-dev libjpeg-dev libpng-dev libtiff-dev
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

#### Filesystem tree after the install

After that single command, the new environment contains the Python interpreter, the `cv2` Python bindings, the OpenCV C++ shared libraries, and the image-format native libraries OpenCV links against. The relevant parts of the tree look like this:

```text
/opt/conda/envs/demo/
├── bin/
│   └── python3.12
├── conda-meta/
├── lib/
│   ├── libjpeg.so -> libjpeg.so.8.3.2
│   ├── libjpeg.so.8
│   ├── libjpeg.so.8.3.2
│   ├── libpng16.so -> libpng16.so.16.58.0
│   ├── libpng16.so.16
│   ├── libpng16.so.16.58.0
│   ├── libtiff.so -> libtiff.so.6.2.0
│   ├── libtiff.so.6
│   ├── libtiff.so.6.2.0
│   ├── libopencv_core.so -> libopencv_core.so.413
│   ├── libopencv_core.so.4.13.0
│   ├── libopencv_core.so.413
│   ├── libopencv_imgproc.so
│   ├── libopencv_imgcodecs.so
│   ├── libopencv_highgui.so
│   ├── ... (about 56 libopencv_*.so libraries in total)
│   └── python3.12/
│       └── site-packages/
│           ├── cv2/
│           │   ├── __init__.py
│           │   ├── __init__.pyi
│           │   ├── config.py
│           │   ├── config-3.12.py
│           │   └── python-3.12/
│           │       └── cv2.cpython-312-x86_64-linux-gnu.so
│           └── numpy/
└── share/
```

The Python `cv2` extension under `site-packages/cv2/python-3.12/` resolves its OpenCV symbols against the `libopencv_*.so` files that sit two directories above it. Both halves were installed by the same command, into the same environment prefix.

By contrast, a plain `venv` plus `pip` workflow does not install native libraries. The Python wheel for OpenCV needs the system to provide the matching C and C++ libraries, so the resulting layout is split across the host and the project:

```text
/usr/                                 # system, managed by apt
├── include/opencv4/
├── lib/x86_64-linux-gnu/
│   ├── libjpeg.so*
│   ├── libpng16.so*
│   ├── libtiff.so*
│   └── libopencv_*.so*
└── bin/python3.12

.venv/                                # project, managed by pip
└── lib/python3.12/site-packages/
    └── cv2/
        ├── __init__.py
        └── cv2.abi3.so               # bundled or links to /usr/lib/...
```

Two package managers now own different parts of the same dependency. `apt` manages the C and C++ libraries on the host, `pip` manages the Python bindings inside the project. Reproducing that combination on another machine means matching both the system package versions and the PyPI package versions.

## Workflow

### Create and activate

Create a fresh environment with Python and `pip`:

```bash
conda create -y -n fresh-env python=3.12 pip
```

Create the environment from the section folder:

```bash
conda env create -f environment.yml
```

Activate the environment:

```bash
conda activate image-processor
```

### Add packages

=== "Conda channel"

    Add a package from a Conda channel:

    ```bash
    conda install -c conda-forge <package>
    ```

=== "PyPI package"

    Add a package from PyPI when it is not available from your chosen Conda channels:

    ```bash
    python -m pip install <package>
    ```

Snapshot the environment requirements back to YAML:

```bash
conda env export --from-history > environment.yml
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

Show the active interpreter inside the Conda environment:

```bash
python3 -c "import sys; print(sys.prefix); print(sys.executable)"
```

