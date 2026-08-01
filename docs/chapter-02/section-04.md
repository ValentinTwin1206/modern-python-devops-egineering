# Conda Packages

Conda packages distribute Python projects with managed dependencies from the Conda ecosystem. They are especially useful when a project depends on scientific libraries, native code, or platform-specific binaries.

## Applied Project

### Project Setup

The applied project is a small image-processing pipeline called `Image Processor Project`. It is built on [OpenCV](https://opencv.org/) and [NumPy](https://numpy.org/). This makes it a good fit for Conda because the workflow combines Python packages with native libraries that are easier to manage together in one Conda environment.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_image_processor/README.md).

## Building Blocks

### Overview

Conda packages are built distributions that can contain Python modules, native libraries, command-line tools, and software from multiple language ecosystems. Modern packages use the `.conda` format, while older releases may use `.tar.bz2`; both carry a pre-built payload and metadata so installation does not require compiling dependencies on the target machine. Conda packages are typically used for data science, machine learning, scientific computing, native extensions, and environments that combine Python with C, C++, R, CUDA, or other runtimes.

Conda distribution connects four building blocks: the package archive carries the payload, a recipe defines how to build it and which dependencies it requires, a Conda-compatible package manager resolves environments, and a channel publishes package indexes and artifacts. Build tools such as `conda-build` and `rattler-build` turn `meta.yaml` or `recipe.yaml` recipes into packages before they are uploaded to a channel.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Stores the built payload and generated package metadata. | `.conda`, `.tar.bz2` |
| Maintainer / Metadata File | Defines package identity, source, build steps, dependencies, tests, and descriptive metadata. | `recipe/meta.yaml`, `recipe/recipe.yaml`, `info/index.json` |
| Package Manager | Resolves packages and creates or updates isolated environments. | `conda`, `mamba`, `micromamba`, `pixi` |
| Remote Repository | Publishes packages and channel indexes for supported platforms and architectures. | conda-forge, Anaconda.org, Cloudsmith |

### Project Layout

A Conda package is built using a dedicated recipe directory that exists alongside the source code.

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

- `recipe/meta.yaml`: Stores metadata, build requirements, and runtime dependencies.
- `src/`: Contains the core application source modules.
- `environment.yml`: The central configuration file for local environment replication. It defines the environment name, target channels, and deterministic dependencies used to stand up development and testing environments consistently across machines.

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

- `package`: Defines the package name and upstream version.
- `source`: Identifies the source archive or local source directory.
- `build`: Defines the build number and command used to assemble the package.
- `requirements`: Separates dependencies needed during the build from dependencies needed at runtime.
- `about`: Supplies descriptive and licensing metadata for repositories and package tools.

### Package Layout

A modern Conda package is a ZIP container with a `.conda` extension. It holds two compressed TAR archives: one for metadata and one for the files installed into a Conda environment.

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

- `metadata.json`: Identifies the two component archives and the Conda package format version.
- `info-*.tar.zst`: Stores package identity, dependencies, file records, licensing details, and build information under `info/`.
- `pkg-*.tar.zst`: Stores the payload placed into the target environment, such as Python modules, executables, shared libraries, or headers.

The filename combines the package name, version, and build string. Conda uses the metadata and build string to select a package compatible with the requested environment and platform.

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Replace `<cloudsmith-repo>` with your Cloudsmith repository slug, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

### Create The Package

From the `projects/` directory, open the dedicated Conda packaging container and forward the Cloudsmith configuration into the container session.

```bash
../build.sh build --path proj4_image_processor/Dockerfile.devEnv -- \
    --env CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" \
    --env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY"
```

Inside the running container, build the project from the repository root with the `recipe/` directory and the `conda-forge` channel enabled:

```bash
conda build recipe/ --channel conda-forge
```

> The output artifact will be written to your local Conda build cache, usually under a platform directory such as `noarch`, `linux-64`, or `win-64`.

### Inspect The Package

A modern Conda package (`.conda`) is a ZIP container that holds two compressed TAR components: an `info` component for package metadata and a `pkg` component for the installable payload. Older Conda packages use a single `.tar.bz2` TAR archive, but the inspection workflow is the same when using `conda-package-handling`.

List all paths stored inside the Conda package.

```bash
cph list "$CONDA_DIR/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

List only the metadata component that Conda uses for dependency solving and package records.

```bash
cph list --components info "$CONDA_DIR/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

Extract only the package metadata into a temporary inspection directory.

```bash
cph extract --info --dest /tmp/image-processor-info "$CONDA_DIR/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

Read the package index metadata produced by the Conda build.

```bash
cat /tmp/image-processor-info/info/index.json
```

### Publish The Package

Upload the built package to the Cloudsmith Conda repository:

```bash
cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$CONDA_DIR/conda-bld/noarch/image-processor-1.0.0-py_0.conda"
```

Verify that Cloudsmith can find the uploaded artifact:

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "image-processor"
```

!!! note
    For private repositories, use the channel URL and authentication settings shown by Cloudsmith. Keep API keys out of `environment.yml`, shared shell scripts, and command history whenever possible.

## Consumer Workflow

### Install The Package

After publication, users can target the Cloudsmith Conda channel to install the application.

Install the package into your current environment from the proprietary channel:

```bash
conda install -c https://conda.cloudsmith.io/<cloudsmith-repo>/ image-processor
```

For repeat installs, add the channel to `.condarc` or to an `environment.yml` file, then let Conda resolve `image-processor` together with its `conda-forge` dependencies.
