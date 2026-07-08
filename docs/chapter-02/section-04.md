# Conda Packages

Conda packages distribute Python projects with managed dependencies from the Conda ecosystem. They are especially useful when a project depends on scientific libraries, native code, or platform-specific binaries.

## Applied Project

### Project Setup

The applied project is a small image-processing pipeline called `Image Processor Project`. It is built on [OpenCV](https://opencv.org/) and [NumPy](https://numpy.org/). This makes it a good fit for Conda because the workflow combines Python packages with native libraries that are easier to manage together in one Conda environment.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj4_image_processor/README.md).

## Distribution Fundamentals

### Overview

A Conda package is a tarball archive (compressed with `.tar.bz2` or `.conda`) containing pre-compiled binaries, libraries, and metadata. It lets the `conda` package manager install software without relying on system-level compilers.

- ✅ Data Science & ML pipelines
- ✅ C/C++ native extensions
- ✅ Multi-language environments (Python, R, C, CUDA)

### Conda Packaging Ecosystem

Conda uses recipes to explicitly define how a package is built, its dependencies, and its target channels. Unlike standard Python tools that read `pyproject.toml`, Conda builds look for a recipe file named `meta.yaml` or `recipe.yaml` inside a `recipe/` folder.

The build metadata and dependencies are strictly defined in the `meta.yml`:

```yaml
package:
  name: image-processor
  version: 1.0.0

source:
  # Build from the project root next to this recipe directory.
  path: ..

build:
  number: 0
  noarch: python
  entry_points:
    - image-processor = image_processor.main:main
  script: |
    mkdir -p ${SP_DIR}/image_processor
    cp -r src/image_processor/. ${SP_DIR}/image_processor/

requirements:
  host:
    - python >=3.12
  run:
    - python >=3.12
    - numpy >=2.1
    - py-opencv >=4.10

test:
  imports:
    - image_processor
  commands:
    - image-processor --help

about:
  home: https://github.com/ValentinTwin1206/modern-python-devops-egineering
  summary: OpenCV image-processing showcase distributed as a Conda package.
  license: MIT
```

Common frontend and backend tools in the Conda ecosystem include build engines, package managers, and workflow tools:

|   Type   |       Tool       | Description |
|----------|------------------|-------------|
| Frontend | `conda-build`    | Classic reference build engine for Conda packages           |
| Frontend | `rattler-build`  | Modern, fast, and secure declarative build tool             |
| Backend | `conda` / `mamba` | Package managers used to resolve and install dependencies   |
| Backend | `pixi`            | High-performance workflow tool built on the Conda ecosystem |


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

### Package Layout

A Conda package file adheres to a structured compression format. Its filename structure is straightforward:

```text
{NAME}-{VERSION}-{BUILD_STRING}.conda
```

The individual identifiers have the following meaning:

- `{NAME}`: The lowercase identifier of the package.
- `{VERSION}`: The specific semantic version of the application.
- `{BUILD_STRING}`: A unique string identifying the Python version, variant, and build number (e.g., `py310h1234567_0`). This specifies the exact binary compatibility matrix.

Typical extracted Conda package contents look like this:

```text
image_processor-1.0.0-py310_0.conda
├── info/
│   ├── about.json
│   ├── index.json
│   ├── paths.json
│   ├── recipe/
│   └── files
└── site-packages/
    └── image_processor/
```

The distinct package artifacts are:

- `info/`: The internal metadata directory that stores package identity, dependency metadata, file manifests, and the original build recipe. Conda reads this data to resolve dependencies, verify compatibility, and track which files belong to the installed package.
- `site-packages/` (or `lib/`, `bin/`, `Scripts/`, or `Library/` on other builds): The payload area that contains the files installed into the target environment. For a `noarch: python` package like this one, that usually means Python modules under `site-packages/`, while platform-specific packages may also ship shared libraries, executables, headers, or other runtime assets.

## Packaging Workflow

### Install Packaging Tools

The project development image includes JFrog CLI for publishing package artifacts. Install the required Conda packaging tools into the base environment:

```bash
conda install -n base -c conda-forge conda-build
```

### Create The Package

Build the project from the repository root with the `recipe/` directory and the `conda-forge` channel enabled:

```bash
conda build recipe/ --channel conda-forge
```

> The output artifact will be written to your local Conda build cache, usually under a platform directory such as `noarch`, `linux-64`, or `win-64`.

### Publish The Package

Once a Conda package passes validation, upload it to the proprietary Conda repository hosted on JFrog Artifactory. A private Artifactory channel is useful when a package should stay inside an organization but still install through normal Conda workflows.

|  Repository  | Type | Purpose |
|--------------|------|---------|
| Conda-Forge  | Public | Dominant community-driven repository for automated packages |
| JFrog Artifactory | Private | Proprietary Conda repository for controlled enterprise package distribution |
| Quetz | Private | Open-source Conda server for self-hosted package distribution |

Configure the JFrog CLI with an access token that can deploy to the Conda repository:

```bash
jf c add modern-python --url "https://<tenant>.jfrog.io" --access-token "$JFROG_ACCESS_TOKEN" --interactive=false
```

Upload the built package to the `noarch` subdirectory of the Artifactory Conda repository:

```bash
jf rt upload "$CONDA_PREFIX/conda-bld/noarch/image-processor-1.0.0-py_0.conda" "conda-local/noarch/"
```

Verify that Artifactory can find the uploaded artifact:

```bash
jf rt search "conda-local/noarch/image-processor-1.0.0-py_0.conda"
```

!!! note
    For private repositories, use the channel URL and authentication settings shown by Artifactory. Keep access tokens out of `environment.yml`, shared shell scripts, and command history whenever possible.

### Install The Package

After publication, users can target the Artifactory Conda channel to install the application.

Install the package into your current environment from the proprietary channel:

```bash
conda install -c https://<tenant>.jfrog.io/artifactory/api/conda/conda-local image-processor
```

For repeat installs, add the channel to `.condarc` or to an `environment.yml` file, then let Conda resolve `image-processor` together with its `conda-forge` dependencies.
