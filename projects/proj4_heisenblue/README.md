# HeisenBlue

This section introduces *HeisenBlue* as a sample project that demonstrates how Conda manages both the Python interpreter and the package set, including native binary dependencies. It provides a small chemistry analysis library backed by RDKit and a native C++ scoring component exposed to Python through pybind11. The library accepts a molecular SMILES string, calculates a playful fictional Blue Score, maps the score to a shade of blue, and can render the result to a PNG image. The project runs inside an environment defined by `environment.yml` and is distributed as two Conda packages built from `recipe/meta.yaml`:

| Conda package | Contents |
| ------------- | -------- |
| `libheisenblue` | Standalone C++ shared library (`libheisenblue.so`/`.dylib`/`.dll`) and public header `heisenblue.hpp`. Consumable from any C/C++ project without Python. |
| `heisenblue-tools` | Python package `heisenblue` (analysis API, CLI, pybind11 extension `_native`). Runtime-depends on `libheisenblue` via an exact pin. |

## Project Components

| Component | Description |
| --------- | ----------- |
| [src/heisenblue/*](src/heisenblue/) | Python package with the analysis API, color conversion, PNG rendering, RDKit integration, and `heisenblue` CLI. |
| [cpp/*](cpp/) | C++ scoring library, public header, pybind11 bindings, and CMake build for `libheisenblue` and `_native`. |
| [environment.yml](environment.yml) | Defines the Conda environment and installs Python, RDKit, Pillow, build tools, and development tooling from `conda-forge`. |
| [Dockerfile.devEnv](Dockerfile.devEnv) | Provides the complete containerized development environment with Miniconda, Conda packaging tools, Cloudsmith CLI, C++ build tooling, and the project environment. |
| [recipe/meta.yaml](recipe/meta.yaml) | Multi-output Conda recipe that produces the `libheisenblue` and `heisenblue-tools` packages. |

## End-User Guide

This section shows how an end user installs and runs `heisenblue` from a proprietary Conda repository hosted on Cloudsmith.

### Requirements

- Miniconda or Anaconda.
- Access to the proprietary Cloudsmith Conda repository that publishes the `libheisenblue` and `heisenblue-tools` packages.

### Installation

Pick the package that matches your use case:

| Use case | Declare this dependency |
| -------- | ----------------------- |
| Use the Python API and CLI. | `heisenblue-tools` (pulls `libheisenblue` in automatically). |
| Link C/C++ code against `libheisenblue` without Python. | `libheisenblue`. |
| Both Python tooling and C/C++ development against the headers. | `libheisenblue` and `heisenblue-tools`. |

Add the packages to your project's `environment.yml` file:

```yaml
name: heisenblue-demo
channels:
    - {YOUR_CONDA_CHANNEL}
    - conda-forge
dependencies:
    - python=3.12
    - heisenblue-tools    # Python API + CLI
    # - libheisenblue     # only needed explicitly for C/C++ consumers
```

> `heisenblue-tools` declares an exact pin on `libheisenblue` via `pin_subpackage(..., exact=True)`, so Conda will always install a matching pair. Only add `libheisenblue` explicitly when a C/C++ consumer needs the headers or shared library without the Python stack.

> Use the channel URL and authentication settings from your Cloudsmith Conda repository. For private repositories, configure credentials in Conda or through your organization's standard secret-management workflow instead of committing tokens to `environment.yml`.

Create and activate the environment from that file:

```bash
conda env create -f environment.yml && conda activate heisenblue-demo
```

### Usage

Run the CLI with a SMILES string:

```bash
heisenblue "CCO"
```

Render a PNG summary:

```bash
heisenblue "CCO" --output ethanol.png
```

Render a PNG summary with a simple RDKit depiction:

```bash
heisenblue "CCO" --output ethanol.png --show-molecule
```

Use the Python API directly:

```python
from heisenblue import analyze, render

result = analyze("CCO")
print(result.score)
print(result.hex)
render(result, "ethanol.png")
```

The Blue Score and predicted color are a playful fictional model and are not a real prediction of the physical color of a chemical substance.

## Developer Guide

### Setup Environment

The [Dockerfile.devEnv](Dockerfile.devEnv) contains all required development tools. Developers should use the container so the host system does not need Python, Conda, RDKit, CMake, compilers, or Cloudsmith CLI installed. Build artifacts are stored on the host in `.build/`. Run the following command from the `projects` directory to open an interactive shell in the development image:

```bash
./build.sh build --path proj4_heisenblue/Dockerfile.devEnv
```

### Sync Environment

Within the running container, update the Conda environment to match `environment.yml`, removing any packages that are no longer listed:

```bash
conda env update -f environment.yml --prune
```

### Run Tests

Within the running container, run the test suite with Karva:

```bash
PYTHONPATH=src karva test tests/
```

### Build Guide

Install Conda packaging tools into the base environment:

```bash
conda install -n base -c conda-forge conda-build conda-package-handling
```

Build the packages from the project root. The multi-output recipe produces both `libheisenblue` and `heisenblue-tools` in a single invocation:

```bash
conda build recipe/ --channel conda-forge
```

Each resulting package contains platform-specific binaries (a native shared library for `libheisenblue`, a compiled pybind11 extension for `heisenblue-tools`), so neither may be published as `noarch`.

Authenticate the Cloudsmith CLI with an API key that can deploy to the Conda repository:

```bash
export CLOUDSMITH_API_KEY="<your-api-key>"
```

Resolve the exact built artifact paths instead of hard-coding a `noarch` location. `conda build --output` prints one path per output package:

```bash
mapfile -t PACKAGES < <(conda build recipe/ --channel conda-forge --output)
```

Upload each built package to your Cloudsmith Conda repository:

```bash
for PACKAGE in "${PACKAGES[@]}"; do
    cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$PACKAGE"
done
```

Verify that Cloudsmith can find both uploaded artifacts:

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "libheisenblue OR heisenblue-tools"
```