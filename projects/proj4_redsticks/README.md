# RedSticks

This section introduces *RedSticks* as a sample project that demonstrates how Conda manages both the Python interpreter and the package set, including native binary dependencies. It provides a small library that suggests lipstick shades from eye-color images, backed by RDKit pigment chemistry and a native C++ CIELAB scoring component exposed to Python through pybind11. The library accepts a PNG or JPEG eye-color image, extracts the dominant color with Pillow, scores every catalog shade against it in CIELAB space, and reports the winning shade together with its pigment chemistry. The project is a **conda-only** build: the development environment is defined by `environment.yml` and the final product is built from `recipe/meta.yaml` — there is no `pyproject.toml`; the Python package is assembled directly by CMake inside the Conda recipe. This is a deliberate teaching simplification; the industry-standard pattern keeps a `pyproject.toml` as the build definition and lets the Conda recipe wrap it via pip. It is distributed as two Conda packages:

| Conda package | Contents |
| ------------- | -------- |
| `libredsticks` | Standalone C++ shared library (`libredsticks.so`/`.dylib`/`.dll`) and public header `redsticks.hpp`. Consumable from any C/C++ project without Python. |
| `redsticks-tools` | Python package `redsticks` (suggestion API, CLI, pybind11 extension `_native`). Runtime-depends on `libredsticks` via an exact pin. |

## Project Components

| Component | Description |
| --------- | ----------- |
| [src/redsticks/*](src/redsticks/) | Python package with the suggestion API, pigment catalog, RDKit integration, and `redsticks` CLI. |
| [cpp/*](cpp/) | C++ CIELAB scoring library, public header, pybind11 bindings, and CMake build for `libredsticks` and `_native`. |
| [environment.yml](environment.yml) | Defines the Conda environment and installs Python, RDKit, Pillow, build tools, and development tooling from `conda-forge`. |
| [Dockerfile.devEnv](Dockerfile.devEnv) | Provides the complete containerized development environment with Miniconda, Conda packaging tools, Cloudsmith CLI, C++ build tooling, and the project environment. |
| [recipe/meta.yaml](recipe/meta.yaml) | Multi-output Conda recipe that produces the `libredsticks` and `redsticks-tools` packages. The Python output is built inline with CMake — no pip or `pyproject.toml` involved. |

## End-User Guide

This section shows how an end user installs and runs `redsticks` from a proprietary Conda repository hosted on Cloudsmith.

### Requirements

- Miniconda or Anaconda.
- Access to the proprietary Cloudsmith Conda repository that publishes the `libredsticks` and `redsticks-tools` packages.

### Installation

Pick the package that matches your use case:

| Use case | Declare this dependency |
| -------- | ----------------------- |
| Use the Python API and CLI. | `redsticks-tools` (pulls `libredsticks` in automatically). |
| Link C/C++ code against `libredsticks` without Python. | `libredsticks`. |
| Both Python tooling and C/C++ development against the headers. | `libredsticks` and `redsticks-tools`. |

Add the packages to your project's `environment.yml` file:

```yaml
name: redsticks-demo
channels:
    - {YOUR_CONDA_CHANNEL}
    - conda-forge
dependencies:
    - python=3.12
    - redsticks-tools    # Python API + CLI
    # - libredsticks     # only needed explicitly for C/C++ consumers
```

> `redsticks-tools` declares an exact pin on `libredsticks` via `pin_subpackage(..., exact=True)`, so Conda will always install a matching pair. Only add `libredsticks` explicitly when a C/C++ consumer needs the headers or shared library without the Python stack.

> Use the channel URL and authentication settings from your Cloudsmith Conda repository. For private repositories, configure credentials in Conda or through your organization's standard secret-management workflow instead of committing tokens to `environment.yml`.

Create and activate the environment from that file:

```bash
conda env create -f environment.yml && conda activate redsticks-demo
```

### Usage

Run the CLI with an eye-color image (PNG or JPEG):

```bash
redsticks --image samples/green-eye.png
```

Additionally write a PNG shade swatch that includes the pigment structure:

```bash
redsticks --image samples/green-eye.png --output shade.png
```

Use the Python API directly:

```python
from redsticks import suggest

result = suggest("samples/green-eye.png")
print(result.shade_name)
print(result.hex)
print(result.harmony)
```

The harmony score and suggested shade are a playful fictional model and are not real cosmetic advice.

## Developer Guide

### Setup Environment

The [Dockerfile.devEnv](Dockerfile.devEnv) contains all required development tools. Developers should use the container so the host system does not need Python, Conda, RDKit, CMake, compilers, or Cloudsmith CLI installed. Build artifacts are stored on the host in `.build/`. Run the following command from the `projects` directory to open an interactive shell in the development image:

```bash
./build.sh build --path proj4_redsticks/Dockerfile.devEnv
```

Within the running container, the Conda environment is created solely from `environment.yml` using the Conda CLI:

```bash
conda env create -f environment.yml && conda activate redsticks-demo
```

### Sync Environment

Within the running container, update the Conda environment to match `environment.yml`, removing any packages that are no longer listed:

```bash
conda env update -f environment.yml --prune
```

### Local Development Build

The pybind11 extension `_native` must be compiled once (and after every C++ change) so the Python package can import it. Build it in-place with CMake and copy it into the package:

```bash
cmake -S cpp -B build-dev -G Ninja -DREDSTICKS_BUILD_BINDINGS=ON
cmake --build build-dev
cp build-dev/_native*.so src/redsticks/
```

Outside a Conda build, `libredsticks` is not pre-installed, so CMake automatically embeds the library sources into the extension (see `cpp/CMakeLists.txt`).

### Run Tests

Within the running container, run the test suite with pytest:

```bash
PYTHONPATH=src pytest
```

Alternatively, run the suite with Karva:

```bash
PYTHONPATH=src karva test tests/
```

### Build Guide

Install Conda packaging tools into the base environment:

```bash
conda install -n base -c conda-forge conda-build conda-package-handling
```

Build the packages from the project root. The multi-output recipe produces both `libredsticks` and `redsticks-tools` in a single invocation. The `libredsticks` output is built by `recipe/build-libredsticks.sh`, and the `redsticks-tools` output is built by an inline CMake command in `recipe/meta.yaml` that compiles `_native` and copies the Python sources into `site-packages` — the packaging pipeline is entirely conda-driven, with no pip or `pyproject.toml`:

```bash
conda build recipe/ --channel conda-forge
```

Each resulting package contains platform-specific binaries (a native shared library for `libredsticks`, a compiled pybind11 extension for `redsticks-tools`), so neither may be published as `noarch`.

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
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "libredsticks OR redsticks-tools"
```
