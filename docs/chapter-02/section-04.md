# Conda Packages

Conda packages distribute Python projects together with managed dependencies from the Conda ecosystem. Unlike Python wheels, which primarily distribute Python packages, Conda packages can bundle Python modules, native libraries, command-line tools, and software from multiple language ecosystems. This advanced packaging capability is similar to [Python Containers](./section-03.md), although the typical target environment is different. Containers are more often used for cloud-native application deployment into controlled runtime platforms, whereas Conda packages more often target user-managed scientific or engineering environments.

## Applied Project

### Project Setup

The applied project is a small chemistry analysis library called `HeisenBlue`. It is built on [RDKit](https://www.rdkit.org/), [Pillow](https://python-pillow.org/), and a native [pybind11](https://pybind11.readthedocs.io/) extension, making it a good fit for Conda because the workflow combines Python packages, native libraries, and a compiled extension in one distributable environment.

### Run the Project

Application, test, lint, package-build, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_heisenblue/README.md).

## Building Blocks

### Overview

Conda packages are built distributions that can contain Python modules, native libraries, command-line tools, and software from multiple language ecosystems. Modern packages use the `.conda` format, while older releases may use `.tar.bz2`; both contain a pre-built payload together with package metadata so installation does not require compiling software on the target machine. Conda packages are commonly used for data science, machine learning, scientific computing, native extensions, and environments that combine Python with C, C++, R, CUDA, or other runtimes.

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
├── pyproject.toml
├── recipe/
│   └── meta.yaml
├── src/
│   └── heisenblue/
│       ├── __init__.py
│       ├── analysis.py
│       └── cli.py
├── tests/
├── environment.yml
└── README.md
```

- `recipe/meta.yaml`: Defines package metadata, source locations, build instructions, dependencies, and tests.
- `cpp/`: Contains the native C++ scoring component that is compiled into the Python package.
- `pyproject.toml`: Defines the Python package metadata and the `scikit-build-core` build backend.
- `src/`: Contains the application source code.
- `environment.yml`: Defines a reproducible development or testing environment, including channels and dependencies.

### Package Manifest

The Conda recipe in `meta.yaml` defines the package identity, source, build behavior, dependencies, tests, and descriptive metadata used to create a Conda package.

```yaml
package:
  name: <package-name>
  version: <package-version>

source:
  path: <source-path>

build:
  number: <build-number> # e.g. 0
  string: <build-string> # e.g. py312_0
  noarch: <noarch-kind> # e.g. python
  entry_points:
    - <command-name> = <module-path>:<callable> # Example: heisenblue = heisenblue.cli:main
  script: |
    <build-command-1>
    <build-command-2>

requirements:
  host:
    - <host-dependency> # e.g. python >=3.12
  run:
    - <runtime-dependency> # Example: python >=3.12
    - pywin32              # [win]
    - xorg-libx11          # [linux]

test:
  imports:
    - <import-name> # Example: heisenblue
  commands:
    - <test-command> # Example: heisenblue --help

about:
  summary: <package-summary>
  license: <license-identifier>
```

- `package`: Defines the package name and version, which form the core of the package identity.
- `source`: Specifies the local directory, Git repository, or source archive used during the build.
- `build`: Defines how Conda assembles the package. The build number and optional build string help form the generated filename, such as `<name>-<version>-<build-string>.conda`, while scripts run the build steps. Target architecture directories, such as `linux-64` or `win-64`, are not hardcoded in `meta.yaml`; compiled projects such as `heisenblue` produce platform-specific artifacts rather than `noarch` packages. Expressions such as `# [win]` and `# [linux]` are Conda selectors written in comment position, so Conda evaluates them before normal YAML parsing and keeps or removes the matching line for the target platform.
- `requirements`: Separates build-machine tools (`build`), host target environment dependencies (`host`), and runtime (`run`) dependencies, which are recorded in the package metadata and used during dependency resolution.
- `test`: Verifies that the package was constructed properly by running automated sanity checks, such as importing Python modules, immediately after building.
- `about`: Provides descriptive metadata such as the package summary and license identifier.

### Package Layout

A modern Conda package is a ZIP container with a `.conda` extension. It contains two compressed TAR archives: one stores package metadata and one stores the installable payload. The package filename combines the package name, version, build string, and target platform, and Conda uses this metadata together with package indexes (`repodata.json`) from configured channels to select compatible packages when creating or updating an environment.

```text
{name}-{version}-{build}.conda
├── metadata.json
├── info-{checksum}.tar.zst
│   └── info/
│       ├── index.json
│       ├── paths.json
│       ├── about.json
│       └── recipe/
└── pkg-{checksum}.tar.zst
    ├── bin/ or Scripts/
    ├── lib/ or Library/
    └── site-packages/
```

- `metadata.json`: Describes the package format and references the contained archives.
- `info-*.tar.zst`: Stores package metadata, dependency information, file records, licenses, and the original recipe.
- `pkg-*.tar.zst`: Stores the files installed into the Conda environment, including Python modules, executables, shared libraries, and other resources.

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

### Create The Package

From the `projects/` directory, open the dedicated Conda packaging container and forward the Cloudsmith configuration into the container session.

```bash
../build.sh build --path proj4_heisenblue/Dockerfile.devEnv \
    --cloudsmith-workspace "<cloudsmith-repo>" \
    --cloudsmith-api-key "$CLOUDSMITH_API_KEY"
```

Inside the running container, build the package from the project root using the `recipe/` directory and the `conda-forge` channel. Add the optional `--target-platform` argument when you need to build for a platform other than the current container platform.

```bash
conda build recipe/ --channel conda-forge [--target-platform <platform>]
```

> The output artifact is written to the local Conda build cache under a platform-specific directory such as `linux-64`, `osx-arm64`, or `win-64`. Because `heisenblue` ships a compiled extension, the package is not `noarch`.

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

Conda repositories organize packages by platform directory and expose each directory through a generated `repodata.json` index. A compiled package such as `heisenblue` is stored under a platform-specific directory such as `linux-64/`, `osx-arm64/`, or `win-64/`. After upload, the repository extracts package metadata, including the name, version, build number, dependency rules, and checksum, then updates the matching `repodata.json` file so Conda clients can discover and resolve the package before downloading the artifact.

```text
repository-root/
└── linux-64/
    ├── repodata.json
    └── heisenblue-1.0.0-<build-string>.conda
```

When a user later installs `heisenblue`, Conda first downloads the lightweight platform index such as `linux-64/repodata.json`, solves dependencies locally, and only then downloads the selected `.conda` artifact.

Upload the built package to the Cloudsmith Conda repository.

```bash
cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$PACKAGE"
```

Check that Cloudsmith received and processed the package.

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "heisenblue"
```

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

For CI or ephemeral machines, prefer an untracked Conda config file and point Conda to it with `CONDARC` instead of exposing the full authenticated channel through `CONDA_CHANNELS`.

```bash
export CONDARC="$HOME/.config/conda/cloudsmith.condarc"
```

### Install The Package

For consumers, a Conda environment removes much of the setup work that advanced projects usually push onto the host machine. Instead of asking users to match a Python version, install native runtime libraries, find compatible RDKit builds, provide image-rendering dependencies, and keep those pieces aligned with the package, the Conda solver installs a compatible environment from one dependency declaration.

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

    Here we assume that `heisenblue` is delivered as a Python package (`.whl`) including its C/C++ component; this is technically possible through a platform-specific wheel. The workflow below shows how to install the remaining host dependencies, but unlike Conda-managed dependencies, these libraries and tools are **installed system-wide** by the OS package manager. Hence, they are shared across projects and can clash when different projects need different native dependency versions.

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