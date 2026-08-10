# Conda Packages

Conda packages distribute Python projects together with managed dependencies from the Conda ecosystem. Unlike Python wheels, which primarily distribute Python packages, Conda packages can bundle Python modules, native libraries, command-line tools, and software from multiple language ecosystems. This makes them especially useful for projects that depend on scientific libraries, native code, GPU toolkits, or platform-specific binaries.

## Applied Project

### Project Setup

The applied project is a small image-processing pipeline called `Image Processor Project`. It is built on [OpenCV](https://opencv.org/) and [NumPy](https://numpy.org/), making it a good fit for Conda because the workflow combines Python packages with native libraries that are easier to distribute and manage together in a single Conda environment.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_image_processor/README.md).

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
├── recipe/
│   └── meta.yaml
├── src/
│   └── image_processor/
│       ├── __init__.py
│       └── main.py
├── tests/
├── environment.yml
├── LICENSE
└── README.md
```

- `recipe/meta.yaml`: Defines package metadata, source locations, build instructions, dependencies, and tests.
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
    number: <build-number>
    script: <build-command>

requirements:
    host:
        - <build-dependency>
    run:
        - <runtime-dependency>

about:
    summary: <package-summary>
    license: <license-identifier>
```

- `package`: Defines the package name and version.
- `source`: Specifies the local directory or source archive used during the build.
- `build`: Defines the build number and commands that assemble the package.
- `requirements`: Separates build-time (`host`) dependencies from runtime (`run`) dependencies.
- `about`: Provides descriptive metadata such as the package summary and license.

### Package Layout

A modern Conda package is a ZIP container with a `.conda` extension. It contains two compressed TAR archives: one stores package metadata and one stores the installable payload.

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

The package filename combines the package name, version, build string, and target platform. Conda uses this metadata together with package indexes from configured channels to select compatible packages when creating or updating an environment.

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

### Create The Package

From the `projects/` directory, open the dedicated Conda packaging container and forward the Cloudsmith configuration into the container session.

```bash
../build.sh build --path proj4_image_processor/Dockerfile.devEnv \
    --cloudsmith-workspace "<cloudsmith-repo>" \
    --cloudsmith-api-key "$CLOUDSMITH_API_KEY"
```

Inside the running container, build the package from the project root using the `recipe/` directory and the `conda-forge` channel:

```bash
conda build recipe/ --channel conda-forge
```

> The output artifact is written to the local Conda build cache, typically under a platform-specific directory such as `noarch`, `linux-64`, `osx-64`, or `win-64`.

### Inspect The Package

A modern Conda package (`.conda`) is a ZIP container that stores two compressed TAR archives: an `info` archive containing package metadata and a `pkg` archive containing the installable payload. Older Conda packages use a single `.tar.bz2` archive, but both formats can be inspected with `conda-package-handling`.

List all paths stored inside the package.

```bash
cph list "$CONDA_DIR/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

List only the metadata component.

```bash
cph list --components info "$CONDA_DIR/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

Extract only the metadata archive.

```bash
cph extract --info --dest /tmp/image-processor-info "$CONDA_DIR/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

Read the generated package metadata.

```bash
cat /tmp/image-processor-info/info/index.json
```

### Publish The Package

Conda repositories organize packages by platform directory and expose each directory through a generated `repodata.json` index. A `noarch` package such as `image-processor` is stored under `noarch/`, while compiled packages are stored under platform-specific directories such as `linux-64/`, `osx-arm64/`, or `win-64/`. After upload, the repository extracts package metadata, including the name, version, build number, dependency rules, and checksum, then updates the matching `repodata.json` file so Conda clients can discover and resolve the package before downloading the artifact.

```text
repository-root/
└── noarch/
    ├── repodata.json
    └── image-processor-1.0.0-py_0.conda
```

When a user later installs `image-processor`, Conda first downloads the lightweight `noarch/repodata.json` index, solves dependencies locally, and only then downloads the selected `.conda` artifact.

Upload the built package to the Cloudsmith Conda repository.

```bash
cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$CONDA_DIR/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

Check that Cloudsmith received and processed the package.

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "image-processor"
```

## Consumer Workflow

### Configure the Package Manager

When Conda creates or updates an environment, it consults the configured `channels` list to locate packages and resolve compatible dependency versions. The proprietary channel should appear before `conda-forge` so Conda can find `image-processor` in the proprietary repository, then resolve public runtime dependencies such as Python, NumPy, and OpenCV from `conda-forge`.

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

After publication, users can create a small consumer project that records the runtime dependency in `environment.yml`. The package source comes from the Conda channels configured in [Configure the Package Manager](#configure-the-package-manager).

Create a new working directory for a small consumer project.

```bash
mkdir imageprocessor-consumer && cd imageprocessor-consumer
```

Add the project environment file.

```yaml
name: image-processor-demo
dependencies:
    - python=3.12
    - image-processor
```

Create the environment from `environment.yml`.

```bash
conda env create -f environment.yml
```

Activate the environment and run the installed command-line application.

```bash
conda activate image-processor-demo
image-processor --output edges.png
```