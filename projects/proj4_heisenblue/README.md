# HeisenBlue

This section introduces *HeisenBlue* as a sample project that demonstrates how Conda manages both the Python interpreter and the package set, including native binary dependencies. It provides a small chemistry analysis library backed by RDKit and a native C++ scoring component exposed to Python through pybind11. The library accepts a molecular SMILES string, calculates a playful fictional Blue Score, maps the score to a shade of blue, and can render the result to a PNG image. The project runs inside an environment defined by `environment.yml` and can be distributed as a Conda package built from `recipe/meta.yaml`.

## Project Components

| Component | Description |
| --------- | ----------- |
| [src/heisenblue/analysis.py](src/heisenblue/analysis.py) | Provides the high-level chemistry analysis API. It parses SMILES strings with RDKit, calculates molecular descriptors, invokes the native C++ scoring engine, and returns the analysis result. |
| [src/heisenblue/color.py](src/heisenblue/color.py) | Converts the fictional Blue Score into RGB and HEX color values. |
| [src/heisenblue/render.py](src/heisenblue/render.py) | Renders the analysis result to PNG using Pillow and optionally includes an RDKit molecular depiction. |
| [src/heisenblue/cli.py](src/heisenblue/cli.py) | Implements the `heisenblue` command line interface. |
| [cpp/heisenblue.cpp](cpp/heisenblue.cpp) | Implements the native C++ Blue Score calculation. |
| [cpp/heisenblue.hpp](cpp/heisenblue.hpp) | Declares the native C++ scoring interface. |
| [cpp/CMakeLists.txt](cpp/CMakeLists.txt) | Defines the CMake build for the C++ component and its pybind11 Python extension. |
| [environment.yml](environment.yml) | Defines the Conda environment and installs Python, RDKit, Pillow, build tools, and development tooling from `conda-forge`. |
| [Dockerfile.devEnv](Dockerfile.devEnv) | Provides the complete containerized development environment with Miniconda, Conda packaging tools, Cloudsmith CLI, C++ build tooling, and the project environment. |
| [recipe/meta.yaml](recipe/meta.yaml) | Defines the Conda package build, including the compiled C++ extension and Python runtime dependencies. |

## End-User Guide

This section shows how an end user installs and runs `heisenblue` from a proprietary Conda repository hosted on Cloudsmith.

### Requirements

- Miniconda or Anaconda.
- Access to the proprietary Cloudsmith Conda repository that publishes `heisenblue`.

### Installation

Add `heisenblue` to your project's `environment.yml` file:

```yaml
name: heisenblue-demo
channels:
    - {YOUR_CONDA_CHANNEL}
    - conda-forge
dependencies:
    - python=3.12
    - heisenblue
```

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

Build the package from the project root:

```bash
conda build recipe/ --channel conda-forge
```

The resulting package contains a compiled C++ extension, so it is platform-specific and must not be published as `noarch`.

Authenticate the Cloudsmith CLI with an API key that can deploy to the Conda repository:

```bash
export CLOUDSMITH_API_KEY="<your-api-key>"
```

Resolve the exact built artifact path instead of hard-coding a `noarch` location:

```bash
PACKAGE="$(conda build recipe/ --channel conda-forge --output)"
```

Upload the built package to your Cloudsmith Conda repository:

```bash
cloudsmith push conda "${CLOUDSMITH_REPOSITORY}" "$PACKAGE"
```

Verify that Cloudsmith can find the uploaded artifact:

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "heisenblue"
```