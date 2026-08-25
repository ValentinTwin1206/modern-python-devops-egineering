# Conda Packages

Conda packages distribute Python projects together with managed dependencies from the Conda ecosystem. Unlike Python wheels, which primarily distribute Python packages, Conda packages can bundle Python modules, native libraries, command-line tools, and software from multiple language ecosystems.

The Conda ecosystem applies a streamlined path from project definition through multi-language dependency resolution, package build, and package hosting to local installation. A recipe declares Python modules and native system libraries with the same syntax; the built `.conda` artifact carries that dependency graph in its metadata; the channel exposes the metadata through a platform-specific index; and the resulting local environment installs Python packages and native system packages side-by-side into a single prefix.

## Applied Project

### Project Setup

The applied project is a small chemistry analysis library called `HeisenBlue`. It is built on [RDKit](https://www.rdkit.org/), [Pillow](https://python-pillow.org/), and a native [pybind11](https://pybind11.readthedocs.io/) extension, making it a good fit for Conda because the workflow combines Python packages, native libraries, and a compiled extension in one distributable environment.

### Run the Project

Application, test, lint, package-build, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_heisenblue/README.md).

## Building Blocks

### Overview

Conda packages are built distributions for multi-language software. Modern Conda packages use the `.conda` format, while older releases may use `.tar.bz2`; both contain a pre-built payload together with package metadata so installation does not require compiling software on the target machine. Conda packages are commonly used for data science, machine learning, scientific computing, native extensions, and environments that combine Python with C, C++, R, CUDA, or other runtimes. This is especially helpful as system dependencies can be managed as first-class environment dependencies instead of hidden system prerequisites, which reduces missing-library failures during installation.

Conda distribution consists of four primary building blocks. A **package format** stores the application files and generated metadata, a **recipe** describes how the package is built and which dependencies it requires, a **package manager** resolves dependencies and creates isolated environments, and a **channel** stores packages together with searchable package indexes. Build tools such as `conda-build` and `rattler-build` transform a `meta.yaml` or `recipe.yaml` recipe into one or more platform-specific Conda packages before they are published to a channel. Because all packages in a channel include dependency metadata, Conda can automatically resolve compatible package versions across the entire environment rather than installing packages individually.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Stores the built payload together with generated package metadata. | `.conda`, `.tar.bz2` |
| Build Recipe | Defines package metadata, build instructions, dependencies, tests, and source locations. | `recipe/meta.yaml`, `recipe/recipe.yaml` |
| Package Manager | Resolves dependencies and creates or updates isolated environments. | `conda`, `mamba`, `micromamba`, `pixi` |
| Remote Repository | Publishes packages and channel indexes for supported platforms and architectures. | conda-forge, Anaconda.org, Cloudsmith |

### Project Layout

A Conda package is built using a dedicated recipe directory that exists alongside the project source code.

```text
{project_root}/
├── cpp/
│   ├── CMakeLists.txt
│   └── heisenblue.cpp
├── recipe/
│   └── meta.yaml
├── src/
│   └── heisenblue/
│       ├── __init__.py
│       ├── analysis.py
│       └── cli.py
├── tests/
├── environment.yml
├── pyproject.toml
└── README.md
```

- `recipe/meta.yaml`: Stores the project's [YAML-based Conda recipe](#package-recipe), which defines package metadata, source locations, build instructions, dependencies, and tests.
- `cpp/`: Contains the native C++ scoring component that is compiled into the Python package.
- `src/`: Contains the application source code.
- `pyproject.toml`: Defines the Python package metadata and the `scikit-build-core` build backend.
- `environment.yml`: Defines a reproducible development or testing environment, including channels and dependencies.

### Package Recipe

A Conda package is defined by a YAML-based recipe file, commonly `meta.yaml` or `recipe.yaml`, which declares the package identity, source, build behavior, dependencies, tests, and descriptive metadata used to create the Conda artifact. The excerpt below focuses on the entries that make Conda a strong fit for language-agnostic packages; project boilerplate such as `package`, `source`, and `about` is omitted.

```yaml
requirements:
  build:
    - "{{ compiler('cxx') }}"          # C/C++ toolchain resolved by Conda
    - cmake
    - ninja

outputs:
    - name: libheisenblue
      script: build-libheisenblue.sh     # builds the C/C++ library
      build:
        run_exports:
          - {{ pin_subpackage('libheisenblue', max_pin='x.x') }}
      requirements:
        build:
          - "{{ compiler('cxx') }}"
          - cmake
          - ninja

    - name: heisenblue-tools
      script: "{{ PYTHON }} -m pip install . --no-deps --no-build-isolation -vv"
      build:
        entry_points:
          - heisenblue = heisenblue.cli:main
      requirements:
        host:
          - python >=3.12
          - scikit-build-core >=0.10
          - pybind11 >=2.12
          - {{ pin_subpackage('libheisenblue', exact=True) }}
        run:
          - python >=3.12
          - rdkit
          - pillow
          - {{ pin_subpackage('libheisenblue', exact=True) }}
      test:
        imports:
          - heisenblue._native
        commands:
          - heisenblue --help
```

- `requirements.build`: Lists tools that run on the build machine.
  - `{{ compiler('cxx') }}`: Lets Conda select the C/C++ toolchain from the channel instead of relying on a system compiler.
  - `cmake` and `ninja`: Build the native C/C++ component.
- `outputs`: Defines a multi-output recipe, which is Conda's mechanism for chained project builds. Here the native C/C++ package is built first, then the Python package builds against it.
  - `libheisenblue`: Builds the native C/C++ package.
    - `script`: Runs `build-libheisenblue.sh`, which configures CMake, builds with Ninja, and installs the shared library and public header into the Conda prefix.
    - `build.run_exports`: Exports a compatible `libheisenblue` pin for downstream packages.
    - `requirements.build`: Reuses the compiler, CMake, and Ninja for this output.
  - `heisenblue-tools`: Builds the Python package and pybind11 extension.
    - `script`: Runs the inline `{{ PYTHON }} -m pip install . --no-deps --no-build-isolation -vv` command because the Python package build is a single step.
    - `build.entry_points`: Generates the `heisenblue` CLI entry point.
    - `requirements.host`: Provides Python build tools and pins the exact `libheisenblue` build during compilation.
    - `requirements.run`: Records Python, RDKit, Pillow, and the exact `libheisenblue` pin for the consumer environment.
    - `test`: Verifies the compiled extension import and generated CLI entry point.

### Package Layout

A modern Conda package is a ZIP container with a `.conda` extension that separates package metadata from the installable payload into two compressed TAR archives. In the usual Conda model, native packages such as RDKit are declared as first-class dependencies in the recipe and resolved through channel metadata instead of being hidden inside the package payload. A Python wheel can technically vendor the same native libraries, but installers treat them as opaque wheel content rather than separately solvable dependencies that `pip` or `uv` can resolve through the environment graph. That pushes ABI compatibility, rebuild coordination, security updates, and conflict management back to the package maintainer. Conda avoids that trade-off by carrying the same dependency metadata from the recipe to the package, channel index, and local environment, where Python modules and native system libraries are installed side-by-side into one solved prefix.

HeisenBlue applies this model by shipping two Conda outputs from a single multi-output recipe: `libheisenblue`, the standalone C++ shared library and its public header, and `heisenblue-tools`, the Python package whose `_native` pybind11 extension declares a run-time dependency on `libheisenblue` instead of vendoring it. The two archives shown below are produced side-by-side and installed side-by-side into the same environment prefix.

=== "`libheisenblue` — C/C++ payload"

    ```text
    libheisenblue-1.0.0-h2bc3f7f_0.conda
    ├── metadata.json
    ├── info-libheisenblue-1.0.0-h2bc3f7f_0.tar.zst
    │   └── info/
    │       ├── about.json
    │       ├── index.json                 # depends: []       run_exports: libheisenblue 1.0.*
    │       ├── ...
    │       └── recipe/
    │           └── meta.yaml
    └── pkg-libheisenblue-1.0.0-h2bc3f7f_0.tar.zst
        ├── include/
        │   └── heisenblue.hpp             # public C++ header
        └── lib/
            ├── libheisenblue.so
            ├── ...
    ```

=== "`heisenblue-tools` — Python payload"

    ```text
    heisenblue-tools-1.0.0-py314h2bc3f7f_0.conda
    ├── metadata.json
    ├── info-heisenblue-tools-1.0.0-py314h2bc3f7f_0.tar.zst
    │   └── info/
    │       ├── index.json                 # depends: [libheisenblue ==1.0.0 h2bc3f7f_0, rdkit, pillow, python >=3.12]
    │       ├── ...
    │       └── recipe/
    │           └── meta.yaml
    └── pkg-heisenblue-tools-1.0.0-py314h2bc3f7f_0.tar.zst
        ├── bin/
        │   └── heisenblue                 # CLI entry point
        └── lib/
            └── python3.14/
                └── site-packages/
                    ├── heisenblue/
                    │   ├── __init__.py
                    │   ├── analysis.py
                    │   ├── ...
                    │   └── _native.cpython-314-x86_64-linux-gnu.so   # NEEDS libheisenblue.so.1
                    └── heisenblue_tools-1.0.0.dist-info/
                        ├── ...
                        └── entry_points.txt
    ```

- `libheisenblue`: Contains only the C/C++ payload plus metadata that makes the package reusable outside Python.
    - `info/index.json`: Keeps `depends: []` and a `run_exports` pin of `libheisenblue 1.0.*`, which propagates the compatible shared-library version to downstream packages.
    - `include/`: Installs the public `heisenblue.hpp` header for C/C++ consumers.
    - `lib/`: Installs the versioned `libheisenblue.so*` chain.
- `heisenblue-tools`: Contains only the Python payload and declares a run-time dependency on the matching `libheisenblue` build.
    - `info/index.json`: Declares the exact `libheisenblue` dependency via `pin_subpackage(..., exact=True)`.
    - `bin/`: Installs the `heisenblue` CLI entry point.
    - `site-packages/`: Installs the `heisenblue` package and the `_native` pybind11 extension, whose `NEEDS libheisenblue.so.1` link is satisfied by the sibling package rather than vendored files.
- Together, the two `.conda` archives carry a single dependency graph from the recipe to the channel index to the installed environment. A C/C++ consumer installs `libheisenblue` alone; a Python consumer installs `heisenblue-tools` and Conda pulls in `libheisenblue` automatically. Neither audience pays for the other's runtime, and both share the same solved native library on disk.

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

### Create The Package

From the `projects/` directory, open the dedicated packaging container and forward the Cloudsmith configuration into the container session.

```bash
../build.sh build --path proj4_heisenblue/Dockerfile.devEnv \
  --cloudsmith-workspace "<cloudsmith-repo>" \
  --cloudsmith-api-key "$CLOUDSMITH_API_KEY"
```

Inside the running container, build the packages from the project root using the `recipe/` directory. The recipe is a **multi-output** recipe, so a single `conda build` invocation resolves the shared build environment once and then produces both `libheisenblue` and `heisenblue-tools` in dependency order. The `libheisenblue` package is built first as `heisenblue-tools` declares it as a host dependency through `pin_subpackage(..., exact=True)`. The `--channel conda-forge` flag is still part of the command because the public build and runtime dependencies in this course, such as compilers, CMake, Python, RDKit, and Pillow, are resolved from `conda-forge`; Cloudsmith is used later as the publish target.

```bash
conda build recipe/ --channel conda-forge
```

> In this Linux-based container, Conda writes the built `.conda` packages to its local build cache under `~/miniconda3/conda-bld/linux-64/`.

### Inspect The Package

A modern Conda package (`.conda`) is a ZIP container that stores two compressed TAR archives: an `info` archive containing package metadata and a `pkg` archive containing the installable payload. Older Conda packages use a single `.tar.bz2` archive, but both formats can be inspected with `conda-package-handling`.

The two archives carry different payloads and different `depends` metadata, so it is worth inspecting them individually. The `libheisenblue` archive should contain only C/C++ artifacts with an empty `depends` list plus a `run_exports` entry, while the `heisenblue-tools` archive should contain the Python payload and declare an exact pin on the matching `libheisenblue` build.

=== "libheisenblue"

    Resolve the shared-library package path.

    ```bash
    LIBHEISENBLUE_PKG="$(conda build recipe/ --channel conda-forge --output | grep '/libheisenblue-')"
    ```

    List all paths stored inside the package.

    ```bash
    cph list "$LIBHEISENBLUE_PKG"
    ```

    List only the metadata component.

    ```bash
    cph list --components info "$LIBHEISENBLUE_PKG"
    ```

    Extract the metadata archive.

    ```bash
    cph extract --info --dest /tmp/libheisenblue-info "$LIBHEISENBLUE_PKG"
    ```

    Read the generated package metadata and confirm `depends: []` plus the `run_exports` pin.

    ```bash
    cat /tmp/libheisenblue-info/info/index.json
    ```

=== "heisenblue-tools"

    Resolve the Python package path.

    ```bash
    HEISENBLUE_TOOLS_PKG="$(conda build recipe/ --channel conda-forge --output | grep '/heisenblue-tools-')"
    ```

    List all paths stored inside the package.

    ```bash
    cph list "$HEISENBLUE_TOOLS_PKG"
    ```

    List only the metadata component.

    ```bash
    cph list --components info "$HEISENBLUE_TOOLS_PKG"
    ```

    Extract the metadata archive.

    ```bash
    cph extract --info --dest /tmp/heisenblue-tools-info "$HEISENBLUE_TOOLS_PKG"
    ```

    Read the generated package metadata and confirm the exact `libheisenblue ==1.0.0 <build>` pin in `depends`.

    ```bash
    cat /tmp/heisenblue-tools-info/info/index.json
    ```

### Publish The Package

A compiled Conda package is built once per target platform, but the Conda channel organizes those artifacts under platform directories and exposes each directory through a generated `repodata.json` index. After upload, the repository extracts package metadata, including the name, version, build number, dependency rules, and checksum, then updates the matching index so Conda clients can resolve the right artifact for the current platform. Because the recipe emits two outputs, each platform directory receives **both** a `libheisenblue-*.conda` and a `heisenblue-tools-*.conda`.

```text
repository-root/
├── linux-64/
│   ├── repodata.json
│   ├── libheisenblue-1.0.0-<linux-build>.conda
│   └── heisenblue-tools-1.0.0-<linux-build>.conda
├── osx-arm64/
│   ├── repodata.json
│   ├── libheisenblue-1.0.0-<macos-build>.conda
│   └── heisenblue-tools-1.0.0-<macos-build>.conda
└── win-64/
    ├── repodata.json
    ├── libheisenblue-1.0.0-<windows-build>.conda
    └── heisenblue-tools-1.0.0-<windows-build>.conda
```

> The [Package create workflow](#create-the-package) above builds only the `linux-64` artifacts; `osx-arm64` and `win-64` are shown for illustration.

Upload each built package to the Cloudsmith Conda repository. The two packages must both be pushed so the exact pin in `heisenblue-tools` can be satisfied at install time.

=== "libheisenblue"

    Upload the shared-library package.

    ```bash
    cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$LIBHEISENBLUE_PKG"
    ```

    Check that Cloudsmith received and processed the package.

    ```bash
    cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "libheisenblue"
    ```

=== "heisenblue-tools"

    Upload the Python package.

    ```bash
    cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$HEISENBLUE_TOOLS_PKG"
    ```

    Check that Cloudsmith received and processed the package.

    ```bash
    cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "heisenblue-tools"
    ```

!!! info "Python Wheels"
    With a wheel workflow, the equivalent release usually means publishing multiple files under one project name in a Python package index:
      
      - `heisenblue-1.0.0-cp312-cp312-manylinux_2_28_x86_64.whl` (Linux)
      - `heisenblue-1.0.0-cp312-cp312-macosx_14_0_arm64.whl` (MacOS)
      - `heisenblue-1.0.0-cp312-cp312-win_amd64.whl` (WIndows)
      
    Package managers such as `uv` or `pip` then resolve the current platform automatically and download the compatible wheel; for example, `uv tool install heisenblue` selects the matching wheel for the current machine. That works, but the Python index does not solve non-Python runtime libraries in the same way a Conda channel does. Even when the package manager selects the correct wheel for Linux, macOS, or Windows, the host system may still be missing required native dependencies, so more compatibility responsibility stays with the package producer and the consumer's environment.


## Consumer Workflow

### Configure the Package Manager

When Conda creates or updates an environment, it consults the configured `channels` list to locate packages and resolve compatible dependency versions. The proprietary channel should appear before `conda-forge` so Conda can find `heisenblue` in the proprietary repository, then resolve public runtime dependencies such as Python, RDKit, and Pillow from `conda-forge`.

Keep authenticated URLs out of `environment.yml`, source control, and shell history. For one user, configure the authenticated channel in `~/.condarc`, while for a managed Debian-based system, use `/etc/conda/.condarc`. Cloudsmith authenticates private Conda repositories through the channel URL itself. For Cloudsmith, prefer an *Entitlement Token URL* like `https://token:<token>@conda.cloudsmith.io/<cloudsmith-repo>/`, although HTTP Basic authentication also works.

=== "User configuration (`~/.condarc`)"

    ```yaml
    channels:
        - https://token:<token>@conda.cloudsmith.io/<cloudsmith-repo>/
        - conda-forge
    channel_priority: strict
    ```

=== "System-wide configuration (`/etc/conda/.condarc`)"

    ```yaml
    channels:
        - https://token:<token>@conda.cloudsmith.io/<cloudsmith-repo>/
        - conda-forge
    channel_priority: strict
    ```

=== "CI or ephemeral machines"

    For CI or ephemeral machines, prefer an untracked Conda config file and point Conda to it with `CONDARC` instead of exposing the full authenticated channel through `CONDA_CHANNELS`.

    ```bash
    export CONDARC="$HOME/.config/conda/cloudsmith.condarc"
    ```

### Install The Package

After publication, users can create a small consumer project that records the runtime dependency in `environment.yml`. The package source comes from the Conda channels configured in [Configure the Package Manager](#configure-the-package-manager).

Create a new working directory for a small consumer project.

```bash
mkdir heisenblue-consumer && cd heisenblue-consumer
```

Add the project environment file.

```yaml
name: heisenblue-demo
dependencies:
  - python=3.12
  - heisenblue-tools
```

When `conda env create` reads `heisenblue-tools` from `environment.yml`, Conda first reads the platform index, such as `linux-64/repodata.json`, solves the full dependency set locally, and then downloads the selected `.conda` artifacts. This installs Python, C++ runtimes, RDKit, Pillow, system assets, `heisenblue-tools`, and its exact `libheisenblue` pin into one project environment without `sudo apt-get ...` or manual native-library setup.

Create the environment from `environment.yml`.

```bash
conda env create -f environment.yml
```

Activate the environment and run the installed command-line application.

```bash
conda activate heisenblue-demo
heisenblue "CCO" --output ethanol.png --show-molecule
```