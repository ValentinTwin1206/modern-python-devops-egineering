# Conda Packages

Conda packages distribute Python projects together with managed dependencies from the Conda ecosystem. Unlike Python wheels, which primarily distribute Python packages, Conda packages can bundle Python modules, native libraries, command-line tools, and software from multiple language ecosystems.

The Conda workflow connects project definition, multi-language dependency resolution, package building, package hosting, and local installation. A recipe declares Python modules and native libraries; the built `.conda` artifacts carry that dependency graph; a channel exposes package metadata through platform-specific indexes; and a local environment installs the Python and native components into one prefix.

## Applied Project

### Project Setup

The applied project is `RedSticks`, a small image-based lipstick shade suggestion library. It combines [RDKit](https://www.rdkit.org/), [Pillow](https://python-pillow.org/), [Rich](https://rich.readthedocs.io/), and a native [pybind11](https://pybind11.readthedocs.io/) extension. The project is a good Conda example because it combines Python packages, native libraries, and compiled C++ code in one distributable environment.

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
├── pyproject.toml
└── README.md
```

- `recipe/meta.yaml`: Defines the two Conda outputs, their dependencies, build steps, entry point, and package tests.
- `cpp/`: Contains the native C++ scoring library, public header, pybind11 bindings, and CMake configuration.
- `src/`: Contains the Python package and CLI.
- `pyproject.toml`: Defines the Python package metadata and `scikit-build-core` backend.
- `environment.yml`: Defines the development environment, including Conda dependencies and the pip-only `karva` test tool.

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
    script: "{{ PYTHON }} -m pip install . --no-deps --no-build-isolation -vv"
    build:
      entry_points:
        - redsticks = redsticks.cli:main
    requirements:
      host:
        - python >=3.12
        - pip
        - scikit-build-core >=0.10
        - pybind11 >=2.12
        - {{ pin_subpackage('libredsticks', exact=True) }}
      run:
        - python >=3.12
        - rdkit
        - pillow
        - rich
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
- `test`: Verifies that the extension imports and that the generated CLI is available.

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
            │   └── _native.<platform>.so
            └── redsticks-1.0.0.dist-info/
    ```

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

From the `projects/` directory, open the dedicated packaging container and forward the Cloudsmith configuration into the container session:

```bash
../build.sh build --path proj4_redsticks/Dockerfile.devEnv \
  --cloudsmith-workspace "<cloudsmith-repo>" \
  --cloudsmith-api-key "$CLOUDSMITH_API_KEY"
```

Inside the running container, build both outputs from the project root. A single `conda build` invocation resolves the shared build environment and produces `libredsticks` and `redsticks-tools` in dependency order:

```bash
conda build recipe/ --channel conda-forge
```

The `--channel conda-forge` option supplies public compilers, CMake, Python, RDKit, Pillow, and other build dependencies. Cloudsmith is the publication target for the finished packages.

### Inspect the Package

The two archives have different payloads and dependency metadata, so inspect them separately. The native package should have an empty direct dependency list and a `run_exports` entry. The Python package should declare an exact dependency on the matching `libredsticks` build.

=== "libredsticks"

    Resolve the native package path:

    ```bash
    LIBREDSTICKS_PKG="$(conda build recipe/ --channel conda-forge --output | grep '/libredsticks-')"
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

    Resolve the Python package path:

    ```bash
    REDSTICKS_TOOLS_PKG="$(conda build recipe/ --channel conda-forge --output | grep '/redsticks-tools-')"
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

Upload both outputs so the exact native-library pin can be satisfied at install time:

```bash
mapfile -t PACKAGES < <(conda build recipe/ --channel conda-forge --output)
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

When Conda creates or updates an environment, it consults the configured `channels` list. Put the authenticated Cloudsmith channel before `conda-forge` so Conda can find `redsticks-tools` and its matching `libredsticks` package, then resolve public runtime dependencies from `conda-forge`.

Keep authenticated URLs out of `environment.yml`, source control, and shell history. Configure the channel in `~/.condarc`, `/etc/conda/.condarc`, or an untracked CI configuration file.

```yaml
channels:
  - https://token:<token>@conda.cloudsmith.io/<cloudsmith-repo>/
  - conda-forge
channel_priority: strict
```

### Install the Package

Create a small consumer project and record the Python package as an environment dependency:

```bash
mkdir redsticks-consumer && cd redsticks-consumer
```

```yaml
name: redsticks-demo
channels:
  - https://token:<token>@conda.cloudsmith.io/<cloudsmith-repo>/
  - conda-forge
dependencies:
  - python=3.12
  - redsticks-tools
```

Create and activate the environment:

```bash
conda env create -f environment.yml
conda activate redsticks-demo
```

The solver installs the Python runtime, C++ runtime, RDKit, Pillow, Rich, `redsticks-tools`, and its exact `libredsticks` dependency into one environment.

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
