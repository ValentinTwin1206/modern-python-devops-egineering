# Conda Packages

Conda packages distribute Python projects together with managed dependencies from the Conda ecosystem. Unlike Python wheels, which primarily distribute Python packages, Conda packages can bundle Python modules, native libraries, command-line tools, and software from multiple language ecosystems. This advanced packaging capability is similar to [Python Containers](./section-03.md).

## Applied Project

### Project Setup

The applied project is a small chemistry analysis library called `HeisenBlue`. It is built on [RDKit](https://www.rdkit.org/), [Pillow](https://python-pillow.org/), and a native [pybind11](https://pybind11.readthedocs.io/) extension, making it a good fit for Conda because the workflow combines Python packages, native libraries, and a compiled extension in one distributable environment.

### Run the Project

Application, test, lint, package-build, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_heisenblue/README.md).

## Building Blocks

### Overview

Conda packages are built distributions that can contain Python modules, native libraries, command-line tools, and software from multiple language ecosystems. Modern packages use the `.conda` format, while older releases may use `.tar.bz2`; both contain a pre-built payload together with package metadata so installation does not require compiling software on the target machine. Conda packages are commonly used for data science, machine learning, scientific computing, native extensions, and environments that combine Python with C, C++, R, CUDA, or other runtimes. This is especially helpful as system dependencies can be managed as first-class environment dependencies instead of hidden system prerequisites, which reduces missing-library failures during installation.

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

A Conda package is defined by a YAML-based recipe file, commonly `meta.yaml` or `recipe.yaml`, which declares the package identity, source, build behavior, dependencies, tests, and descriptive metadata used to create the Conda artifact.

```yaml
package:
  name: heisenblue
  version: 1.0.0

source:
  path: ..
  # url: https://example.com/heisenblue-1.0.0.tar.gz
  # sha256: <source-archive-checksum>

build:
  number: 0
  script: "{{ PYTHON }} -m pip install . --no-deps -vv"
  # string: py312_0
  # noarch: python
  # entry_points:
  #   - heisenblue = heisenblue.cli:main

requirements:
  build:
    - "{{ compiler('cxx') }}"
    - cmake
    - ninja
  host:
    - python >=3.12
    - pip
    - scikit-build-core >=0.10
    - pybind11 >=2.12
    - rdkit
    - pillow
  run:
    - python >=3.12
    - rdkit
    - pillow
    # - pywin32            # [win]
    # - xorg-libx11        # [linux]

test:
  imports:
    - heisenblue
    - heisenblue._native
  commands:
    - heisenblue --help
    # - pytest -q

about:
  home: https://github.com/ValentinTwin1206/modern-python-engineering
  summary: RDKit and pybind11 sample library packaged as a platform-specific Conda artifact.
  license: Apache-2.0
```

- `package`: Defines the package name and version, which form the core of the package identity.
- `source`: Specifies the local directory, Git repository, or source archive used during the build.
- `build`: Defines how Conda assembles the package. The build number and optional build string help form the generated filename, such as `<name>-<version>-<build-string>.conda`, while scripts run the build steps. Target architecture directories, such as `linux-64` or `win-64`, are not hardcoded in `meta.yaml`; compiled projects such as `heisenblue` produce platform-specific artifacts rather than `noarch` packages. Expressions such as `# [win]` and `# [linux]` are Conda selectors written in comment position, so Conda evaluates them before normal YAML parsing and keeps or removes the matching line for the target platform. In contrast to a typical wheel workflow, the Conda recipe does not need a separate binary-repair phase to explain where native dependencies belong; the package recipe and channel metadata carry that information directly.
- `requirements`: Separates build-machine tools (`build`), host target environment dependencies (`host`), and runtime (`run`) dependencies, which are recorded in the package metadata and used during dependency resolution. This is where Conda is especially strong for C/C++ projects: compilers, C++ libraries, and platform-specific runtime packages can be declared as normal dependencies instead of being hidden in host setup scripts or manually bundled into wheel artifacts.
- `test`: Verifies that the package was constructed properly by running automated sanity checks, such as importing Python modules, immediately after building.
- `about`: Provides descriptive metadata such as the package summary and license identifier.

### Package Layout

The following section shows the inner layout of a typical Conda package and compares it with the already known [Python wheel structure](./section-01.md#package-layout). Both formats can distribute Python package files and compiled extension modules, but they organize metadata, entry points, installable files, and dependency expectations differently.

=== "Conda Package"

    A modern Conda package is a ZIP container with a `.conda` extension that separates package metadata from the installable payload into two compressed TAR archives. Technically, a maintainer could also vendor native dependencies such as RDKit directly into the package payload instead of declaring them as separate Conda dependencies.However, this approach is atypical, as the maintainer would then also own ABI compatibility, rebuild coordination, security updates, and conflict management that the Conda ecosystem normally handles through dependency metadata and shared packages.

    ```text
    heisenblue-1.0.0-py314h2bc3f7f_0.conda
    ├── metadata.json
    ├── info-heisenblue-1.0.0-py314h2bc3f7f_0.tar.zst
    │   └── info/
    │       ├── about.json
    │       ├── ...
    │       ├── recipe/
    │       │   ├── conda_build_config.yaml
    │       │   ├── meta.yaml
    │       │   └── meta.yaml.template
    │       └── test/
    │           ├── run_test.py
    │           └── run_test.sh
    └── pkg-heisenblue-1.0.0-py314h2bc3f7f_0.tar.zst
      ├── bin/
      │   └── heisenblue
      └── lib/
          └── python3.14/
              └── site-packages/
                  ├── heisenblue/
                  │   ├── __init__.py
                  │   ├── analysis.py
                  │   ├── ...
                  │   └── _native.cpython-314-x86_64-linux-gnu.so
                  └── heisenblue-1.0.0.dist-info/
                      ├── ...
                      └── entry_points.txt
    ```

    - `metadata.json`: Describes the Conda package format and references the contained archives.
    - `info-*.tar.zst`: Stores package metadata, dependency information, file records, licenses, tests, and the original recipe.
        - `recipe/`: Contains the embedded `meta.yaml` recipe, including the declared **runtime and system dependencies** that Conda installs into the target environment before the package is activated there.
    - `pkg-*.tar.zst`: Stores the installable payload copied into the Conda environment.
        - `bin/`: Contains command-line entry points such as the generated `heisenblue` script.
        - `lib/python3.14/site-packages/`: Contains the installed Python package, Python package metadata, and `_native`, a pybind11 C++ extension module loaded by Python.

=== "Python Wheel"

    A Python wheel can also bundle the compiled C extension, yet host dependencies such as RDKit or platform libraries may still be missing and must be installed separately before use, as shown in [Consumer Workflow](#install-the-package). The wheel also does not contain a preinstalled `bin/heisenblue` script; the installer generates that launcher from `entry_points.txt` during installation.

    ```text
    heisenblue-1.0.0-cp314-cp314-linux_x86_64.whl
    ├── heisenblue/
    │   ├── __init__.py
    │   ├── analysis.py
    │   ├── ...
    │   └── _native.cpython-314-x86_64-linux-gnu.so
    └── heisenblue-1.0.0.dist-info/
      ├── ...
      └── entry_points.txt
    ```

    - `heisenblue/`: Contains the Python source files and `_native`, a pybind11 C++ extension module loaded by Python rather than a standalone executable or static library.
    - `heisenblue-1.0.0.dist-info/`: Contains package metadata, dependency declarations, file records, and console-script entry points.

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

Inside the running container, build the package from the project root using the `recipe/` directory and the `conda-forge` channel. Add the optional `--target-platform` argument when you need to build for a platform other than the current container platform.

```bash
conda build recipe/ --channel conda-forge [--target-platform <platform>]
```

> The output artifact is written to the local Conda build cache under a platform-specific directory such as `linux-64`, `osx-arm64`, or `win-64`. Because `heisenblue` ships a compiled extension, the package is not `noarch`; each supported platform gets its own `.conda` artifact.

### Inspect The Package

A modern Conda package (`.conda`) is a ZIP container that stores two compressed TAR archives: an `info` archive containing package metadata and a `pkg` archive containing the installable payload. Older Conda packages use a single `.tar.bz2` archive, but both formats can be inspected with `conda-package-handling`.

Resolve the exact artifact path that `conda build` produced:

```bash
PACKAGE="$(conda build recipe/ --channel conda-forge --output)"
```

List all paths stored inside the package.

```bash
cph list "$PACKAGE"
```

List only the metadata component.

```bash
cph list --components info "$PACKAGE"
```

Extract only the metadata archive.

```bash
cph extract --info --dest /tmp/heisenblue-info "$PACKAGE"
```

Read the generated package metadata.

```bash
cat /tmp/heisenblue-info/info/index.json
```

### Publish The Package

A compiled Conda package such as `heisenblue` is still built once per target platform, but the Conda channel organizes those artifacts under platform directories and exposes each directory through a generated `repodata.json` index. After upload, the repository extracts package metadata, including the name, version, build number, dependency rules, and checksum, then updates the matching index so Conda clients can resolve the right artifact for the current platform.

```text
repository-root/
├── linux-64/
│   ├── repodata.json
│   └── heisenblue-1.0.0-<linux-build>.conda
├── osx-arm64/
│   ├── repodata.json
│   └── heisenblue-1.0.0-<macos-build>.conda
└── win-64/
  ├── repodata.json
  └── heisenblue-1.0.0-<windows-build>.conda
```

> The [Package create workflow](#create-the-package) above builds only the `linux-64` artifact; `osx-arm64` and `win-64` are shown for illustration.

When a user later installs `heisenblue`, Conda first downloads the lightweight platform index such as `linux-64/repodata.json`, solves dependencies locally, and only then downloads the selected `.conda` artifact. The advantage is not a single multi-platform archive; it is that the package, RDKit, Pillow, native runtime expectations, and platform metadata are solved together in the same Conda ecosystem.

Upload the built package to the Cloudsmith Conda repository.

```bash
cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$PACKAGE"
```

Check that Cloudsmith received and processed the package.

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "heisenblue"
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

For consumers, Conda provides **zero system-dependency setup** for advanced packages. Junior developers can run `conda env create` and get a working environment with Python, C++ runtimes, RDKit, Pillow, and system assets without using `sudo`, `apt-get`, `brew`, or manual native-library installation.

=== "With Conda"

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
      - heisenblue
    ```

    Create the environment from `environment.yml`.

    ```bash
    conda env create -f environment.yml
    ```

    Activate the environment and run the installed command-line application.

    ```bash
    conda activate heisenblue-demo
    heisenblue "CCO" --output ethanol.png --show-molecule
    ```

=== "Without Conda"

    Here we assume that `heisenblue` is delivered as a Python package (`.whl`) including its C/C++ component; this is technically possible through a platform-specific wheel. The workflow below shows how to install the remaining host dependencies, but unlike Conda-managed dependencies, these libraries and tools are **installed system-wide** by the OS package manager. That means the setup requires elevated permissions and the installed components are shared across projects, which can cause clashes when different projects need different native dependency versions. By contrast, once Conda itself is installed, `conda env create` typically runs as a normal user without additional root or `sudo` access.

    ```bash
    sudo apt-get update && sudo apt-get install -y \
      python3.12 \
      python3.12-venv \
      build-essential \
      cmake \
      ninja-build \
      fonts-dejavu-core \
      libxrender1 \
      libxext6
    ```

    Create a consumer project file that depends on the published Python package.

    ```toml
    [project]
    name = "heisenblue-consumer"
    version = "0.1.0"
    requires-python = ">=3.12"
    dependencies = [ "heisenblue" ]

    [tool.uv]

    [[tool.uv.index]]
    name = "pypi"
    url = "https://pypi.org/simple"

    [[tool.uv.index]]
    name = "modern-python-engineering"
    url = "https://dl.cloudsmith.io/public/<cloudsmith-repo>/python/simple/"
    ```

    Sync the project environment with `uv`.

    ```bash
    uv sync
    ```

    Run the installed command-line application.

    ```bash
    uv run heisenblue "CCO" --output ethanol.png --show-molecule
    ```