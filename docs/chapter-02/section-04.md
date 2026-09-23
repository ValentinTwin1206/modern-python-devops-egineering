# Conda Packages

Conda packages distribute Python projects together with managed dependencies from the Conda ecosystem. Unlike Python wheels, which primarily distribute Python packages, Conda packages can bundle Python modules, native libraries, command-line tools, and software from multiple language ecosystems.

The Conda workflow connects project definition, multi-language dependency resolution, package building, package hosting, and local installation. A recipe declares Python modules and native libraries; the built `.conda` artifacts carry that dependency graph; a channel exposes package metadata through platform-specific indexes; and a local environment installs the Python and native components into one prefix.

## Applied Project

### Project Setup

The applied project is `IrisLab`, a small image-based iris color analysis application. It uses MediaPipe Face Landmarker with a **local machine-learning model** to locate the irises in real photos, then analyzes the extracted pixels with NumPy and CIELAB color space to determine perceptual color features and classify the eye color. The resulting color profile is compared with reference colors using a native C++ library that calculates CIE ΔE color distances and is exposed to Python through `pybind11`. This makes `IrisLab` a good fit for Conda because a single environment manages Python packages, native libraries, compiled C++ code, and local machine-learning dependencies together.

The recipe produces two Conda packages:

| Conda package | Contents |
| ------------- | -------- |
| `libirislab` | Standalone C++ shared library (`libirislab.so`, `.dylib`, or `.dll`) and the public `irislab.hpp` header. |
| `irislab-tools` | Python package, `irislab` CLI, and pybind11 extension. It depends on the matching `libirislab` build. |

### Run the Project

Application, test, lint, package-build, and shell-exit commands are documented in the [project README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_irislab/README.md).

## Building Blocks

### Overview

Conda packages are built distributions for multi-language software. Modern Conda packages use the `.conda` format, while older releases may use `.tar.bz2`; both contain a pre-built payload and package metadata so installation does not require compiling software on the target machine. Conda is commonly used for data science, scientific computing, native extensions, and environments that combine Python with C, C++, R, CUDA, or other runtimes.

Conda distribution has four primary building blocks. A **package format** stores the payload and generated metadata, a **recipe** describes how the package is built and which dependencies it requires, a **package manager** resolves dependencies and creates isolated environments, and a **channel** stores packages with searchable indexes. Build tools such as `conda-build` transform a recipe into platform-specific Conda packages before they are published to a channel.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Stores the built payload together with generated package metadata. | `.conda`, `.tar.bz2` |
| Build Recipe | Defines package metadata, build instructions, dependencies, and tests. | `recipe/meta.yaml`, `recipe/recipe.yaml` |
| Package Manager | Resolves dependencies and creates or updates isolated environments. | `conda`, `mamba`, `micromamba`, `pixi` |
| Remote Repository | Publishes packages and channel indexes for supported platforms and architectures. | conda-forge, Anaconda.org, Cloudsmith |

### Project Layout

A Conda package is built with a dedicated recipe directory alongside the project source code.

```text
{project_root}/
├── cpp/
│   ├── CMakeLists.txt
│   ├── bindings.cpp
│   ├── iriscolor.cpp
│   └── iriscolor.hpp
├── recipe/
│   ├── build-libirislab.bat
│   ├── build-libirislab.sh
│   └── meta.yaml
├── samples/
├── src/
│   └── irislab/
├── tests/
├── environment.yml
└── README.md
```

- `recipe/meta.yaml`: Defines the two Conda outputs, their dependencies, build steps, entry point, and package tests.
- `cpp/`: Contains the native C++ scoring library, public header, pybind11 bindings, and CMake configuration.
- `src/`: Contains the Python package and CLI.
- `environment.yml`: Defines the development environment, including runtime, native, and testing dependencies, plus the pip-only `mediapipe` package.

### Package Recipe

A Conda package is defined by a YAML recipe that declares package identity, source, build behavior, dependencies, tests, and descriptive metadata. `IrisLab` uses a multi-output recipe so the standalone native library and Python package remain separately reusable.

```yaml
outputs:
  # -------------------------------------------------------------------------
  # libirislab: standalone C++ shared library and headers.
  # -------------------------------------------------------------------------
  - name: libirislab
    script: build-libirislab.sh

    build:
      run_exports:
        - {{ pin_subpackage('libirislab', max_pin='x.x') }}

    requirements:
      build:
        - "{{ compiler('cxx') }}"
        - cmake
        - ninja

  # -------------------------------------------------------------------------
  # irislab-tools: Python package, CLI, and pybind11 extension.
  #
  # The extension is built directly with CMake and links against libirislab.
  # -------------------------------------------------------------------------
  - name: irislab-tools

    script: >-
      cmake -S "${SRC_DIR}/cpp" -B build-tools -G Ninja
      -DCMAKE_BUILD_TYPE=Release
      -DIRISLAB_BUILD_BINDINGS=ON
      -DCMAKE_PREFIX_PATH="${PREFIX}"
      && cmake --build build-tools
      && mkdir -p "${SP_DIR}/irislab"
      && cp "${SRC_DIR}"/src/irislab/*.py "${SP_DIR}/irislab/"
      && cp build-tools/_native*.so "${SP_DIR}/irislab/"

    build:
      entry_points:
        - irislab = irislab.cli:main

    requirements:
      build:
        - "{{ compiler('cxx') }}"
        - cmake
        - ninja

      host:
        - python >=3.12
        - pybind11 >=2.12
        - {{ pin_subpackage('libirislab', exact=True) }}

      run:
        - python >=3.12
        - click
        - pillow
        - rich
        - numpy
        - glib
        - libgl
        - libegl
        - libgles
        - {{ pin_subpackage('libirislab', exact=True) }}

    test:
      requires:
        - pip

      imports:
        - irislab
        - irislab._native

      commands:
        - python -m pip install mediapipe
        - irislab --help
```

- `libirislab`: Builds the standalone C++ shared library and public header. Its `run_exports` entry provides a compatible library pin to downstream packages.
- `irislab-tools`: Builds the Python package and pybind11 extension. Its exact `pin_subpackage` dependency ensures the extension uses the matching native library.
- `requirements.host`: Supplies Python and native build dependencies while the package is compiled.
- `requirements.run`: Records the dependencies needed by the installed application.
- `test`: Installs the PyPI-only MediaPipe dependency, then verifies that the extension imports and the generated CLI is available.

### Package Layout

A `.conda` file is a ZIP container with separate compressed metadata and payload archives. `IrisLab` produces two packages from one recipe, allowing C/C++ consumers to install `libirislab` without the Python stack while Python consumers install `irislab-tools` and receive the native library automatically.

=== "`libirislab` — C/C++ payload"

    ```text
    libirislab-1.0.0-<build>.conda
    ├── metadata.json
    ├── info-*.tar.zst
    │   └── info/
    │       ├── about.json
    │       ├── index.json                 # depends: [] and run_exports
    │       └── recipe/meta.yaml
    └── pkg-*.tar.zst
        ├── include/
        │   └── iriscolor.hpp
        └── lib/
            └── libirislab.so
    ```

=== "`irislab-tools` — Python payload"

    ```text
    irislab-tools-1.0.0-<build>.conda
    ├── metadata.json
    ├── info-*.tar.zst
    │   └── info/index.json              # depends: libirislab, pillow, rich
    └── pkg-*.tar.zst
        ├── bin/
        │   └── irislab
        └── site-packages/
            ├── irislab/
            │   ├── __init__.py
            │   ├── cli.py
            │   ├── eye_color.py
            │   ├── iris.py
            │   ├── analyze.py
            │   └── _native.<platform>.so
    ```

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

From the `projects/` directory, use the already-built `mpe/proj4_irislab` image to create an interactive 
Bash session. The command mounts the project source and build directory, then forwards the Cloudsmith 
configuration into the container.

Create a host directory for package artifacts generated inside the container:

```bash
mkdir -p proj4_irislab/.build
```

Start the container and mount the project and build directories:

```bash
docker run -it \
    -v "$PWD/proj4_irislab:/app" \
    -v "$PWD/proj4_irislab/.build:/build" \
    -e CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" \
    -e CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY" \
    mpe/proj4_irislab \
    /bin/bash
```

> See [Development Workflow](./../chapter-01/section-03.md#development-workflow) for creating the image using the `build.sh` script


### Install Packaging Tools

Install the packaging tools in Conda's `base` environment rather than in the
project's `irislab` environment. This separation keeps the *Packaging Workflow*
independent from the *Development Workflow*. The installed `conda-build` package
is the recipe-driven build tool, and `conda-package-handling` provides the `cph`
command for listing package archives and inspecting their metadata and contents.

```bash
conda install \
    --name base \
    --channel conda-forge \
    conda-build \
    conda-package-handling
```

The following command runs `pip` in Conda's `base` environment. It downloads
the `cloudsmith-cli` package from PyPI and installs it for uploading packages
to the configured Cloudsmith repository.

```bash
conda run --name base python -m pip install cloudsmith-cli==1.26.0
```

### Create the Package

Activate the `base` environment before running the packaging command:

```bash
conda activate base
```

From the project root, build both packages with `conda-build`. The `--channel conda-forge` option 
provides the public compilers, CMake, Python, Pillow, and other dependencies required by the recipe.

```bash
conda build recipe/ --channel conda-forge
```

- `libirislab`: Provides the standalone native C++ library and public header.
- `irislab-tools`: Provides the Python package, CLI, and pybind11 extension.

### Inspect the Package

The two archives have different payloads and dependency metadata, so inspect them separately. The native package should have an empty direct dependency list and a `run_exports` entry. The Python package should declare an exact dependency on the matching `libirislab` build.

=== "libirislab"

    Resolve the native package created in the previous step:

    ```bash
    LIBIRISLAB_PKG="$(find "${CONDA_BLD_PATH:-$HOME/conda-bld}" -type f -name 'libirislab-*.conda' -print -quit)"
    ```

    List the package contents:

    ```bash
    cph list "$LIBIRISLAB_PKG"
    ```

    Extract and inspect its metadata:

    ```bash
    cph extract --info --dest /tmp/libirislab-info "$LIBIRISLAB_PKG"
    cat /tmp/libirislab-info/info/index.json
    ```

=== "irislab-tools"

    Resolve the Python package created in the previous step:

    ```bash
    IRISLAB_TOOLS_PKG="$(find "${CONDA_BLD_PATH:-$HOME/conda-bld}" -type f -name 'irislab-tools-*.conda' -print -quit)"
    ```

    List the package contents:

    ```bash
    cph list "$IRISLAB_TOOLS_PKG"
    ```

    Extract and inspect its metadata:

    ```bash
    cph extract --info --dest /tmp/irislab-tools-info "$IRISLAB_TOOLS_PKG"
    cat /tmp/irislab-tools-info/info/index.json
    ```

### Publish the Package

A compiled Conda package is built for a target platform. The channel organizes those artifacts under platform directories and exposes each directory through a generated `repodata.json` index. Because this recipe emits two outputs, each platform receives both a `libirislab-*.conda` and a `irislab-tools-*.conda` artifact.

```text
repository-root/
├── linux-64/
│   ├── repodata.json
│   ├── libirislab-1.0.0-<build>.conda
│   └── irislab-tools-1.0.0-<build>.conda
├── osx-arm64/
│   ├── repodata.json
│   ├── libirislab-1.0.0-<build>.conda
│   └── irislab-tools-1.0.0-<build>.conda
└── win-64/
    ├── repodata.json
    ├── libirislab-1.0.0-<build>.conda
    └── irislab-tools-1.0.0-<build>.conda
```

Upload the two archives created in the previous step so the exact native-library pin can be satisfied at install time:

```bash
mapfile -t PACKAGES < <(find "${CONDA_BLD_PATH:-$HOME/conda-bld}" -type f \( \
  -name 'libirislab-*.conda' -o -name 'irislab-tools-*.conda' \
\) -print)
for PACKAGE in "${PACKAGES[@]}"; do
    cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$PACKAGE"
done
```

Verify that Cloudsmith received both artifacts:

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "libirislab OR irislab-tools"
```

!!! info "Python Wheels"
    A wheel workflow can publish platform-specific files under one Python project name, but a Python index does not solve the native `libirislab` dependency as a separate environment package. Conda keeps the native library, Python extension, and their dependency metadata visible to the solver.

## Consumer Workflow

### Configure the Package Manager

Configure `.condarc` before creating the environment. Replace `<cloudsmith-repo>` with the repository slug. Conda creates `.condarc` automatically when the first command writes to it.

Expose the Cloudsmith channel URL to your local environment:

```bash
CLOUDSMITH_CHANNEL="https://token:${CLOUDSMITH_API_KEY}@conda.cloudsmith.io/<cloudsmith-repo>/"
```

Clear existing channels:

```bash
conda config --remove-key channels
```

Add the required channels:

```bash
conda config --add channels nodefaults
conda config --add channels conda-forge
conda config --add channels "$CLOUDSMITH_CHANNEL"
```

Set strict channel priority:

```bash
conda config --set channel_priority strict
```

### Install the Package

Create a small consumer project:

```bash
mkdir irislab-consumer && cd irislab-consumer
```

Record the `irislab-tools` package as an environment dependency:

```yaml
name: irislab-demo
dependencies:
  - python=3.12
  - irislab-tools
```

Then, create the environment:

```bash
conda env create --file environment.yml
```

> Both `irislab-tools` and its exact `libirislab` dependency get installed.

Activate the consumer environment:

```bash
conda activate irislab-demo
```

Since `mediapipe` is not available from `conda-forge`, install it from PyPI:

```bash
conda run --name "irislab-demo" python -m pip install mediapipe
```

The CLI accepts a portrait image and analyzes the detected iris color:

```bash
irislab --image samples/blue-eyes.png
```

The project also exposes a Python API:

```python
from irislab import analyze

result = analyze("samples/blue-eye.png")

print(result.eye_color)
print(result.lab)
print(result.closest_profile)
print(result.delta_e)
```