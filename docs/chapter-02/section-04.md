# Conda Packages

Conda packages distribute Python projects together with managed dependencies from the Conda ecosystem. Unlike Python wheels, which primarily distribute Python packages, Conda packages can bundle Python modules, native libraries, command-line tools, and software from multiple language ecosystems.

The Conda workflow connects project definition, multi-language dependency resolution, package building, package hosting, and local installation. A recipe declares Python modules and native libraries; the built `.conda` artifacts carry that dependency graph; a channel exposes package metadata through platform-specific indexes; and a local environment installs the Python and native components into one prefix.

## Applied Project

### Project Setup

The applied project is `RedSticks`, a small image-based lipstick shade suggestion library. It combines [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker), [RDKit](https://www.rdkit.org/), [Pillow](https://python-pillow.org/), [Rich](https://rich.readthedocs.io/), and a native [pybind11](https://pybind11.readthedocs.io/) extension. The project is a good Conda example because it combines Python packages, native libraries, local ML inference, and compiled C++ code in one distributable environment.

The recipe produces two Conda packages:

| Conda package | Contents |
| ------------- | -------- |
| `libredsticks` | Standalone C++ shared library (`libredsticks.so`, `.dylib`, or `.dll`) and the public `redsticks.hpp` header. |
| `redsticks-tools` | Python package, `redsticks` CLI, and pybind11 extension. It depends on the matching `libredsticks` build. |

### Run the Project

Application, test, lint, package-build, and shell-exit commands are documented in the [project README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_redsticks/README.md).

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
│   ├── redsticks.cpp
│   └── redsticks.hpp
├── recipe/
│   ├── build-libredsticks.bat
│   ├── build-libredsticks.sh
│   └── meta.yaml
├── samples/
├── src/
│   └── redsticks/
├── tests/
├── environment.yml
└── README.md
```

- `recipe/meta.yaml`: Defines the two Conda outputs, their dependencies, build steps, entry point, and package tests.
- `cpp/`: Contains the native C++ scoring library, public header, pybind11 bindings, and CMake configuration.
- `src/`: Contains the Python package and CLI.
- `environment.yml`: Defines the development environment, including runtime, native, and testing dependencies, plus the pip-only `mediapipe` package.

### Package Recipe

A Conda package is defined by a YAML recipe that declares package identity, source, build behavior, dependencies, tests, and descriptive metadata. RedSticks uses a multi-output recipe so the standalone native library and Python package remain separately reusable.

```yaml
outputs:
  - name: libredsticks
    script: build-libredsticks.sh
    build:
      run_exports:
        - {{ pin_subpackage('libredsticks', max_pin='x.x') }}
    requirements:
      build:
        - "{{ compiler('cxx') }}"
        - cmake
        - ninja

  - name: redsticks-tools
    # The current recipe builds the pybind11 extension directly with CMake.
    script: >-
      cmake -S "${SRC_DIR}/cpp" -B build-tools -G Ninja
      -DCMAKE_BUILD_TYPE=Release -DREDSTICKS_BUILD_BINDINGS=ON
      -DCMAKE_PREFIX_PATH="${PREFIX}"
      && cmake --build build-tools
      && mkdir -p "${SP_DIR}/redsticks"
      && cp "${SRC_DIR}"/src/redsticks/*.py "${SP_DIR}/redsticks/"
      && cp build-tools/_native*.so "${SP_DIR}/redsticks/"
    build:
      entry_points:
        - redsticks = redsticks.cli:main
    requirements:
      build:
        - "{{ compiler('cxx') }}"
        - cmake
        - ninja
      host:
        - python >=3.12
        - pybind11 >=2.12
        - {{ pin_subpackage('libredsticks', exact=True) }}
      run:
        - python >=3.12
        - click
        - rdkit
        - pillow
        - rich
        - numpy
        - {{ pin_subpackage('libredsticks', exact=True) }}
    test:
      imports:
        - redsticks
        - redsticks._native
      commands:
        - redsticks --help
```

- `libredsticks`: Builds the standalone C++ shared library and public header. Its `run_exports` entry provides a compatible library pin to downstream packages.
- `redsticks-tools`: Builds the Python package and pybind11 extension. Its exact `pin_subpackage` dependency ensures the extension uses the matching native library.
- `requirements.host`: Supplies Python and native build dependencies while the package is compiled.
- `requirements.run`: Records the dependencies needed by the installed application.
- `test`: Installs the PyPI-only MediaPipe dependency, then verifies that the extension imports and the generated CLI is available.

> MediaPipe is not available from `conda-forge`, so it is intentionally not
> listed in `requirements.run` for `redsticks-tools`. Install it from PyPI
> after installing the Conda package, as described in the consumer workflow.

### Package Layout

A `.conda` file is a ZIP container with separate compressed metadata and payload archives. RedSticks produces two packages from one recipe, allowing C/C++ consumers to install `libredsticks` without the Python stack while Python consumers install `redsticks-tools` and receive the native library automatically.

=== "`libredsticks` — C/C++ payload"

    ```text
    libredsticks-1.0.0-<build>.conda
    ├── metadata.json
    ├── info-*.tar.zst
    │   └── info/
    │       ├── about.json
    │       ├── index.json                 # depends: [] and run_exports
    │       └── recipe/meta.yaml
    └── pkg-*.tar.zst
        ├── include/
        │   └── redsticks.hpp
        └── lib/
            └── libredsticks.so
    ```

=== "`redsticks-tools` — Python payload"

    ```text
    redsticks-tools-1.0.0-<build>.conda
    ├── metadata.json
    ├── info-*.tar.zst
    │   └── info/index.json              # depends: libredsticks, rdkit, pillow, rich
    └── pkg-*.tar.zst
        ├── bin/
        │   └── redsticks
        └── site-packages/
            ├── redsticks/
            │   ├── __init__.py
            │   ├── cli.py
            │   ├── eye_color.py
            │   ├── iris.py
            │   ├── suggest.py
            │   └── _native.<platform>.so
    ```

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

From the `projects/` directory, use the already-built `mpe/proj4_redsticks`
image to create an interactive Bash session. The command mounts the project
source and build directory, then forwards the Cloudsmith configuration into
the container.

Create a host directory for package artifacts generated inside the container:

```bash
mkdir -p proj4_redsticks/.build
```

Start the container and mount the project and build directories:

```bash
docker run -it \
    -v "$PWD/proj4_redsticks:/app" \
    -v "$PWD/proj4_redsticks/.build:/build" \
    -e CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" \
    -e CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY" \
    mpe/proj4_redsticks \
    /bin/bash
```

> See [Development Workflow](./../chapter-01/section-03.md#development-workflow) for creating the image using the `build.sh` script


### Install Packaging Tools

Install the packaging tools in Conda's `base` environment rather than in the
project's `redsticks` environment. This separation keeps the *Packaging Workflow*
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

From the project root, build both packages with `conda-build`. The
`--channel conda-forge` option provides the public compilers, CMake, Python,
RDKit, Pillow, and other dependencies required by the recipe.

```bash
conda build recipe/ --channel conda-forge
```

- `libredsticks`: Provides the standalone native C++ library and public header.
- `redsticks-tools`: Provides the Python package, CLI, and pybind11 extension.

### Inspect the Package

The two archives have different payloads and dependency metadata, so inspect them separately. The native package should have an empty direct dependency list and a `run_exports` entry. The Python package should declare an exact dependency on the matching `libredsticks` build.

=== "libredsticks"

    Resolve the native package created in the previous step:

    ```bash
    LIBREDSTICKS_PKG="$(find "${CONDA_BLD_PATH:-$HOME/conda-bld}" -type f -name 'libredsticks-*.conda' -print -quit)"
    ```

    List the package contents:

    ```bash
    cph list "$LIBREDSTICKS_PKG"
    ```

    Extract and inspect its metadata:

    ```bash
    cph extract --info --dest /tmp/libredsticks-info "$LIBREDSTICKS_PKG"
    cat /tmp/libredsticks-info/info/index.json
    ```

=== "redsticks-tools"

    Resolve the Python package created in the previous step:

    ```bash
    REDSTICKS_TOOLS_PKG="$(find "${CONDA_BLD_PATH:-$HOME/conda-bld}" -type f -name 'redsticks-tools-*.conda' -print -quit)"
    ```

    List the package contents:

    ```bash
    cph list "$REDSTICKS_TOOLS_PKG"
    ```

    Extract and inspect its metadata:

    ```bash
    cph extract --info --dest /tmp/redsticks-tools-info "$REDSTICKS_TOOLS_PKG"
    cat /tmp/redsticks-tools-info/info/index.json
    ```

### Publish the Package

A compiled Conda package is built for a target platform. The channel organizes those artifacts under platform directories and exposes each directory through a generated `repodata.json` index. Because this recipe emits two outputs, each platform receives both a `libredsticks-*.conda` and a `redsticks-tools-*.conda` artifact.

```text
repository-root/
├── linux-64/
│   ├── repodata.json
│   ├── libredsticks-1.0.0-<build>.conda
│   └── redsticks-tools-1.0.0-<build>.conda
├── osx-arm64/
│   ├── repodata.json
│   ├── libredsticks-1.0.0-<build>.conda
│   └── redsticks-tools-1.0.0-<build>.conda
└── win-64/
    ├── repodata.json
    ├── libredsticks-1.0.0-<build>.conda
    └── redsticks-tools-1.0.0-<build>.conda
```

Upload the two archives created in the previous step so the exact native-library pin can be satisfied at install time:

```bash
mapfile -t PACKAGES < <(find "${CONDA_BLD_PATH:-$HOME/conda-bld}" -type f \( \
  -name 'libredsticks-*.conda' -o -name 'redsticks-tools-*.conda' \
\) -print)
for PACKAGE in "${PACKAGES[@]}"; do
    cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$PACKAGE"
done
```

Verify that Cloudsmith received both artifacts:

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "libredsticks OR redsticks-tools"
```

!!! info "Python Wheels"
    A wheel workflow can publish platform-specific files under one Python project name, but a Python index does not solve the native `libredsticks` dependency as a separate environment package. Conda keeps the native library, Python extension, and their dependency metadata visible to the solver.

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
mkdir redsticks-consumer && cd redsticks-consumer
```

Record the `redsticks-tools` package as an environment dependency:

```yaml
name: redsticks-demo
dependencies:
  - python=3.12
  - redsticks-tools
```

Then, create the environment:

```bash
conda env create --file environment.yml
```

> Both `redsticks-tools` and its exact `libredsticks` dependency get installed.

Activate the consumer environment:

```bash
conda activate redsticks-demo
```

Since `mediapipe` is not available from `conda-forge`, install it from PyPI:

```bash
conda run --name "redsticks-demo" python -m pip install mediapipe
```

The CLI accepts an eye-color image and can write a PNG shade swatch:

```bash
redsticks --image samples/blue-eye.png --output suggested-shade.png
```

The project also exposes a Python API:

```python
from redsticks import suggest

result = suggest("samples/blue-eye.png")
print(result.shade_name, result.hex)
```
