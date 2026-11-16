# Python Wheels

Python wheels are the standard built package format for Python projects. They let installers such as `pip` copy ready-to-install files instead of rebuilding the project every time.

## Applied Project

### Project Setup

The applied project is a small utility library called pAIguard [pie guard]. It inspects images with local moderation models before an application accepts them. This makes it a good fit for wheels because a pure-Python library shows clearly how a project can be built into a lightweight, platform-independent distribution artifact.

### Run the Project

Application, lint, build, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_paiguard/README.md).

## Building Blocks

### Overview

Python wheels are built distributions defined by PEP 427. A wheel contains installable Python code and metadata in a ZIP-based `.whl` artifact, so an installer can copy files into an environment without rebuilding the project from source. Wheels are typically used for Python libraries, command-line applications, SDKs, and frameworks; pure-Python wheels can work across operating systems, while wheels containing native extensions target specific Python versions, ABIs, and platforms.

Wheel distribution depends on four connected building blocks: the wheel artifact carries the installable payload, project and embedded metadata describe the release, a Python package manager resolves and installs it, and a remote repository makes releases discoverable. Build frontends such as `uv build` or `python -m build` use the backend declared in `pyproject.toml` to create the artifact before publication.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Stores the built Python package, compatibility tags, and embedded installation metadata. | `.whl` |
| Maintainer / Metadata File | Defines project metadata, dependencies, and the build backend; the wheel embeds generated metadata under `*.dist-info/`. | `pyproject.toml`, `METADATA`, `WHEEL`, `RECORD` |
| Package Manager | Resolves dependencies and installs wheels into a Python environment. | `pip`, `uv` |
| Remote Repository | Publishes package releases and exposes an index that package managers can query. | PyPI, Cloudsmith, Artifactory |

### Project Layout

A wheel is built from the project files, source code, and packaging metadata already in the repository.

```text
{project_root}/
├── src/
│   └── {module}/
│       ├── __init__.py
│       └── core.py
├── tests/
├── README.md
├── LICENSE
└── pyproject.toml
```

- `src/`: Contains the importable package code. This widely used `src` layout keeps the project root separate from Python modules, which helps prevent accidental local imports and makes development behavior match the installed package.
- `pyproject.toml`: The **central configuration file** for modern Python packaging. It stores the package metadata, dependency list, build backend settings, and CLI entry points in one place.
- `README.md`: Project description displayed on package repositories such as PyPI.
- `LICENSE`: Defines the legal terms under which the package can be used and distributed.

### Package Manifest

!!! note
    Chapter 04 covers [`pyproject.toml` project configuration](../chapter-04/section-01.md) in more detail.
    
The `pyproject.toml` file defines the project metadata, Python requirements, dependencies, command-line entry points, and build backend used to create the wheel.

```toml
[build-system]
requires = ["uv_build>=0.11.8,<0.12"]
build-backend = "uv_build"

[project]
name = "paiguard"
version = "0.1.0"
description = "Lightweight image content moderation for Python applications."
readme = "README.md"
requires-python = ">=3.11"
license = "Apache-2.0"
license-files = ["LICENSE"]
authors = [
    { name = "Julius Pravtchev" },
    { name = "Valentin Pravtchev" }
]

dependencies = [
    "pydantic>=2.0",
    "pillow>=10.0",
    "numpy>=1.26",
    "onnxruntime>=1.17",
    "torch>=2.2",
    "transformers>=4.49",
]

[dependency-groups]
dev = [
    "karva>=0.0.1a5",
    "pytest>=8",
    "ruff>=0.15.12",
]

# Install the CPU-only build of PyTorch. Only `torch` uses this index.
[tool.uv.sources]
torch = { index = "pytorch-cpu" }

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.ruff]
target-version = "py311"
line-length = 88
```

- `name`: Defines the distribution name used in package indexes and wheel filenames.
- `version`: Identifies the published release.
- `requires-python`: Declares compatible Python versions.
- `dependencies`: Lists packages required when the wheel is installed, including pAIguard's built-in inference runtime.
- `[build-system]`: Selects the build backend and the packages needed to run it.
- `[tool.uv.sources]` and `[[tool.uv.index]]`: Install the CPU-only build of `torch` from the PyTorch index. `explicit = true` keeps every other package on the default index. This setting applies to the project itself and is not stored in the wheel.

### Package Layout

A Python wheel is a ZIP archive with a `.whl` extension. It bundles the importable package, distribution metadata, and an installation record that lets Python package managers place and track the files in an environment.

```text
{name}-{version}-{python-tag}-{abi-tag}-{platform-tag}.whl
├── {import-package}/
│   ├── __init__.py
│   └── ...
└── {name}-{version}.dist-info/
    ├── METADATA
    ├── RECORD
    ├── WHEEL
    └── entry_points.txt
```

- `{import-package}/`: Contains the Python modules and package data installed into the environment.
- `METADATA`: Records package identity, Python requirements, dependencies, and descriptive metadata.
- `WHEEL`: Records the wheel format and compatibility tags.
- `RECORD`: Lists installed files and their hashes so the installer can track and uninstall them.

The filename tags tell the package manager which Python interpreter, ABI, and platform can use the wheel. A pure-Python wheel commonly ends in `py3-none-any.whl`, while a wheel with compiled extensions uses more specific tags.

## Tradeoffs

### Pros

- ✅ Standard Python package format
- ✅ Fast, build-free installation
- ✅ Portable for pure-Python projects
- ✅ Integrates with Python dependency solvers

### Cons

- ⚠️ Requires a compatible Python environment
- ⚠️ Native code needs platform-specific wheels
- ⚠️ System libraries remain unmanaged
- ⚠️ Applications still need environment management

## Packaging Workflow

### Create the Environment

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and API key. Set `CLOUDSMITH_REPOSITORY` to your Cloudsmith `<owner>/<repository>` path, export `CLOUDSMITH_API_KEY` on the host, and pass both values into the container.

The `Dockerfile.devEnv` image uses Ubuntu 24.04 with Python 3.12, `python3-venv`,
`sudo`, `unzip`, and `uv`, then copies the project into `/app`. Cloudsmith CLI
is installed in the workflow because it is only needed for publication.
Choose the workflow that matches the local `mpe/proj1_paiguard` image:

=== "Image does not exist"

    From the `projects/` directory, use `build.sh` to build and open the
    interactive pAIguard packaging container:

    ```bash
    ./build.sh build \
        --path proj1_paiguard/Dockerfile.devEnv \
        --cloudsmith-workspace "<owner>/<repository>" \
        --cloudsmith-api-key "$CLOUDSMITH_API_KEY"
    ```

=== "Image already exists"

    From the `projects/` directory, create the host directory for package
    artifacts and run the existing image:

    ```bash
    mkdir -p proj1_paiguard/.build
    docker run -it \
        -v "$PWD/proj1_paiguard:/app" \
        -v "$PWD/proj1_paiguard/.build:/build" \
        --env CLOUDSMITH_REPOSITORY="<cloudsmith-repo>" \
        --env CLOUDSMITH_API_KEY="$CLOUDSMITH_API_KEY" \
        mpe/proj1_paiguard \
        /bin/bash
    ```

Install the project dependencies and the publication tool inside the running
container:

```bash
uv sync --all-groups
uv tool install cloudsmith-cli
```

### Create the Package

Modern Python builds split responsibilities between a **build frontend** and a **build backend**. The frontend is the command-line tool you run, while the backend is the project-specific implementation that produces the wheel (`.whl`) and source distribution (`.tar.gz`). PEP 517 defines the interface between both sides, and PEP 518 defines the `[build-system]` table in `pyproject.toml` where the backend and its requirements are declared.

In this project, the build backend is `uv_build`. It is declared in `pyproject.toml`, which tells the build frontend which backend to load and which packages must be installed before the build starts. Popular build backends include `uv_build`, `hatchling`, `setuptools.build_meta`, `poetry.core.masonry.api`, etc.

```toml
[build-system]
requires = ["uv_build>=0.11.8,<0.12"]
build-backend = "uv_build"
```

In this project, the build frontend is `uv build`. It creates the isolated build environment, installs the backend requirements, and invokes `uv_build` to create the final artifacts. The command accepts a source directory, so the `pyproject.toml` file is discovered from that project path. Popular build frontends include `uv build`, `python -m build`, `pip wheel`, `pip install`, `hatch build`, `poetry build`, etc.

```bash
uv build <path-to-project-root>
```

List the generated distribution files in the `dist/` directory.

```bash
ls dist/
```

### Inspect the Package

A wheel (`.whl`) is a **ZIP archive** with Python modules and a `*.dist-info/` metadata directory. The source distribution created next to it is a gzip-compressed TAR archive (`.tar.gz`) that stores the source tree used to rebuild the package.

List the files inside the wheel archive without extracting it.

```bash
zipinfo -1 dist/paiguard-0.1.0-py3-none-any.whl
```

Read the wheel metadata that describes the wheel format version, generator, root layout, and compatibility tags.

```bash
unzip -p dist/paiguard-0.1.0-py3-none-any.whl paiguard-0.1.0.dist-info/WHEEL
```

Read the package metadata that installers and package indexes use for the project name, version, description, and dependency declarations.

```bash
unzip -p dist/paiguard-0.1.0-py3-none-any.whl paiguard-0.1.0.dist-info/METADATA
```

List the files inside the source distribution TAR archive.

```bash
tar -tzf dist/paiguard-0.1.0.tar.gz
```

### Publish the Package

Once you have inspected the wheel package, upload it to the proprietary Python repository hosted on Cloudsmith.

Publish the package to the Cloudsmith PyPI repository with `uv`.

```bash
uv publish --publish-url "https://python.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/" --token "$CLOUDSMITH_API_KEY"
```

Check that the uploaded release is visible through the Cloudsmith `/simple/` API used by installers.

```bash
curl -fsSL "https://dl.cloudsmith.io/basic/${CLOUDSMITH_REPOSITORY}/python/simple/paiguard/" | grep "paiguard-0.1.0"
```

## Consumer Workflow

### Install the Package

After publication, users can create a small project, install `paiguard` from the Cloudsmith PyPI repository, and run a short server in the created environment.

Create a new working directory for a small consumer project.

```bash
mkdir paiguard-consumer && cd paiguard-consumer
```

=== "`pyproject.toml`"

    Add `paiguard` to the project's `[project].dependencies`. Update the
    `[tool.uv.sources]` table and the `[[tool.uv.index]]` entries to point to the
    appropriate package indexes. Replace `<owner>/<repository>` with your Cloudsmith
    repository path and configure Cloudsmith credentials before running `uv sync`.

    ```toml
    [project]
    name = "paiguard-consumer"
    version = "0.1.0"
    requires-python = ">=3.12"
    dependencies = [
        "paiguard==0.1.0",
        "fastapi",
        "uvicorn",
        "python-multipart",
    ]

    [tool.uv.sources]
    paiguard = { index = "modern-python-engineering" }
    torch = { index = "pytorch-cpu" }

    [[tool.uv.index]]
    name = "modern-python-engineering"
    url = "https://dl.cloudsmith.io/basic/<owner>/<repository>/python/simple/"
    explicit = true

    [[tool.uv.index]]
    name = "pytorch-cpu"
    url = "https://download.pytorch.org/whl/cpu"
    explicit = true
    ```

=== "`server.py`"

    Create `server.py` with the moderation endpoint, using pAIguard's `PaiGuard.inspect()` to
    inspect uploaded images:

    ```python
    from fastapi import FastAPI, UploadFile
    from PIL import Image

    from paiguard import PaiGuard
    from paiguard.rules import PaiNsfwDetection, PaiViolenceDetection

    app = FastAPI()

    guard = PaiGuard(
        rules=[
            PaiNsfwDetection(threshold=0.80),
            PaiViolenceDetection(threshold=0.85),
        ]
    )


    @app.post("/moderations")
    def moderate(image: UploadFile):
        picture = Image.open(image.file).convert("RGB")
        result = guard.inspect(picture)

        return {
            "decision": result.decision,
            "is_safe": result.is_safe,
            "violations": result.violations,
        }
    ```

Install the dependencies from the complete project configuration:

```bash
uv sync
```

### Install Models

Set `PAIGUARD_MODEL_DIR` to the directory where pAIguard should find its local
model files:

```bash
export PAIGUARD_MODEL_DIR="${PAIGUARD_MODEL_DIR:-$PWD/models}"
```

The SigLIP2 base model encodes images for violence moderation. To download the
model and its weights, use `curl`:

```bash
mkdir -p "$PAIGUARD_MODEL_DIR/siglip2-base"
BASE_URL="https://huggingface.co/google/siglip2-base-patch16-256/resolve/3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab"
curl -fsSL "$BASE_URL/config.json" -o "$PAIGUARD_MODEL_DIR/siglip2-base/config.json"
curl -fsSL "$BASE_URL/preprocessor_config.json" -o "$PAIGUARD_MODEL_DIR/siglip2-base/preprocessor_config.json"
curl -fsSL "$BASE_URL/model.safetensors" -o "$PAIGUARD_MODEL_DIR/siglip2-base/model.safetensors"
```

The SigLIP2 moderation head classifies image embeddings for violence. To
download the model and its weights, use `curl`:

```bash
mkdir -p "$PAIGUARD_MODEL_DIR/siglip2-heads"
BASE_URL="https://huggingface.co/khasinski/siglip2-moderation-heads/resolve/b88fe03369e3dc6aa9887cd3b4cd3e9b7cf76ee5"
curl -fsSL "$BASE_URL/violence_head.onnx" -o "$PAIGUARD_MODEL_DIR/siglip2-heads/violence_head.onnx"
curl -fsSL "$BASE_URL/violence_head.onnx.data" -o "$PAIGUARD_MODEL_DIR/siglip2-heads/violence_head.onnx.data"
```

The Falconsai classifier detects NSFW content. To download the model and its
weights, use `curl`:

```bash
mkdir -p "$PAIGUARD_MODEL_DIR/falconsai-nsfw"
BASE_URL="https://huggingface.co/Falconsai/nsfw_image_detection/resolve/96cb0d0342c7afb80cab76ecc58b265fa44da256"
curl -fsSL "$BASE_URL/config.json" -o "$PAIGUARD_MODEL_DIR/falconsai-nsfw/config.json"
curl -fsSL "$BASE_URL/preprocessor_config.json" -o "$PAIGUARD_MODEL_DIR/falconsai-nsfw/preprocessor_config.json"
curl -fsSL "$BASE_URL/model.safetensors" -o "$PAIGUARD_MODEL_DIR/falconsai-nsfw/model.safetensors"
```

### Use pAIguard Image Moderation

Run the server from the same virtual environment.

```bash
.venv/bin/uvicorn server:app
```

Send an image to the server from a second terminal.

```bash
curl -F 'image=@portrait.png' http://127.0.0.1:8000/moderations
```

## Useful Links

- [PEP 517 - A build-system independent format for source trees](https://peps.python.org/pep-0517/)
- [PEP 518 - Specifying Minimum Build System Requirements for Python Projects](https://peps.python.org/pep-0518/)
