# Python Wheels

Python wheels are the standard built package format for Python projects. They let installers such as `pip` copy ready-to-install files instead of rebuilding the project every time.

## Applied Project

The applied project is a packaged Python library called `pAIguard` *[pie guard]*. It runs local image classifiers to screen uploaded images for NSFW ("*not safe for work*") content and violence; the *IrisLab-API* uses these checks to moderate uploads before iris analysis. pAIguard adapts the `src`-layout structure typical for "packaged-typed" projects, keeping its importable package separate from tests and project configuration. As pAIguard's own code is pure Python and does not require separately managed system libraries or a cross-language build toolchain, it is a good fit for `venv`. Its Python dependencies and development tools can be isolated in a project-local environment. PyTorch is installed from its CPU index, and model weights are downloaded separately.

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

### Package API (Interface)

A Python package exposes its functionality through a **public interface** (Python API), which defines the classes and functions that other projects can import and use. A well-defined public interface provides consumers with a stable entry point while keeping internal implementation details encapsulated. 
In pAIguard, `__init__.py` acts as the package facade by re-exporting selected classes and exceptions from their respective implementation modules. This allows consumers to import them directly from `paiguard` package rather than having to know the internal module structure. The `__all__` attribute explicitly defines which names belong to the supported public interface.

```python
from .guard import PaiGuard
from .models import ModelNotFoundError
from .results import InspectionResult, RuleResult
from .rules import (
    PaiDetectionRule,
    PaiNsfwDetection,
    PaiRule,
    PaiViolenceDetection,
)

__all__ = [
    "InspectionResult",
    "ModelNotFoundError",
    "PaiDetectionRule",
    "PaiGuard",
    "PaiNsfwDetection",
    "PaiRule",
    "PaiViolenceDetection",
    "RuleResult",
]
```

The central component of this interface is the `PaiGuard` class, which provides the main entry point for image moderation. Consumers instantiate it with a collection of detection rules and use its `inspect()` method to evaluate a decoded Pillow image. The shared `PaiDetectionRule` class provides common functionality for scoring and threshold evaluation, while specialized rules such as `PaiNsfwDetection` and `PaiViolenceDetection` implement category-specific detection logic and define their respective default models.

The following tabs explore the implementation behind this public API. The module `guard.py` contains the main inspection logic, while the individual `rules_*.py` modules define the detection rules that can be passed to an instance of `PaiGuard`.

=== "guard.py"

    ```python
    import logging

    from PIL import Image

    from .results import InspectionResult, RuleResult
    from .rules.base import PaiRule

    logger = logging.getLogger("paiguard")


    class PaiGuard:
        def __init__(self, rules: list[PaiRule] | None = None):
            self.rules = rules or []

        @staticmethod
        def _decide(results: list[RuleResult]) -> str:
            for result in results:
                if result.detected:
                    return "block"
            for result in results:
                if result.needs_review:
                    return "review"
            return "allow"

        def inspect(self, image: Image.Image) -> InspectionResult:
            if not isinstance(image, Image.Image):
                raise TypeError("PaiGuard.inspect() expects a PIL.Image.Image")
            if image.mode != "RGB":
                image = image.convert("RGB")

            results = [rule.inspect(image) for rule in self.rules]
            decision = self._decide(results)
            if decision != "allow":
                scores = {
                    result.category: round(result.score, 3) for result in results
                }
                logger.warning("Image decision is '%s' with scores %s", decision, scores)
            return InspectionResult(decision=decision, results=results)
    ```

=== "nsfw_rules.py"

    ```python
    from .base import PaiDetectionRule
    from ..models import FalconsaiNsfwModel


    class PaiNsfwDetection(PaiDetectionRule):
        """Detect NSFW / explicit content."""

        category = "nsfw"

        def __init__(self, threshold: float = 0.80, review_threshold=None, model=None):
            super().__init__(threshold, review_threshold, model)

        def create_default_model(self):
            return FalconsaiNsfwModel()
    ```

=== "violence_rules.py"

    ```python
    from .base import PaiDetectionRule
    from ..models import SiglipViolenceModel


    class PaiViolenceDetection(PaiDetectionRule):
        """Detect violent content."""

        category = "violence"

        def __init__(self, threshold: float = 0.85, review_threshold=None, model=None):
            super().__init__(threshold, review_threshold, model)

        def create_default_model(self):
            return SiglipViolenceModel()
    ```

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
version = "0.0.1"
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
]

[project.optional-dependencies]
models = [
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

[tool.uv.build-backend]
module-root = "src"
```

- `name`: Defines the distribution name used in package indexes and wheel filenames.
- `version`: Identifies the published release.
- `requires-python`: Declares compatible Python versions.
- `dependencies`: Lists packages required when the wheel is installed, including pAIguard's built-in inference runtime.
- `[build-system]`: Selects the build backend and the packages needed to run it.
- `[tool.uv.sources]` and `[[tool.uv.index]]`: Install the CPU-only build of `torch` from the PyTorch index. `explicit = true` keeps every other package on the default index. This setting applies to the project itself and is not stored in the wheel.
- `[tool.uv.build-backend]`: Tells `uv_build` that importable modules live under `src/`.

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

The `Dockerfile.devEnv` image uses Ubuntu 24.04 with Python 3.12, `python3-venv`,
`sudo`, `unzip`, and `uv`, then copies the project into `/app`.
Choose the workflow that matches the local `mpe/proj1_paiguard` image:

=== "Build and package locally"

    From the `projects/` directory, use `build.sh` to build the pAIguard
    packaging image and open a shell:

    ```bash
    ./build.sh build \
        --path proj1_paiguard/Dockerfile.devEnv
    ```

=== "Reuse an existing image"

    From the `projects/` directory, create the host directory for package
    artifacts and run the existing image:

    ```bash
    mkdir -p proj1_paiguard/.build
    docker run -it \
        -v "$PWD/proj1_paiguard:/app" \
        -v "$PWD/proj1_paiguard/.build:/build" \
        mpe/proj1_paiguard \
        /bin/bash
    ```

Install the project dependencies inside the running container:

```bash
uv sync --all-groups
```

### Create the Package

The project is currently versioned `0.0.1`. Build this version for the requested upload; for a future release, update `[project].version` before building because published version files cannot be overwritten.

| File | Version change |
|------|----------------|
| [`pyproject.toml`](../../projects/proj1_paiguard/pyproject.toml) | Keep `[project].version` at `0.0.2` for this upload. |

Modern Python builds split responsibilities between a **build frontend** and a **build backend**. The frontend is the command-line tool you run, while the backend is the project-specific implementation that produces the wheel (`.whl`) and source distribution (`.tar.gz`). PEP 517 defines the interface between both sides, and PEP 518 defines the `[build-system]` table in `pyproject.toml` where the backend and its requirements are declared.

In this project, the build backend is `uv_build`. It is declared in `pyproject.toml`, which tells the build frontend which backend to load and which packages must be installed before the build starts. Popular build backends include `uv_build`, `hatchling`, `setuptools.build_meta`, `poetry.core.masonry.api`, etc.

```toml
[build-system]
requires = ["uv_build>=0.11.8,<0.12"]
build-backend = "uv_build"
```

In this project, the build frontend is `uv build`. It creates the isolated build environment, installs the backend requirements, and invokes `uv_build` to create the final artifacts. The command accepts a source directory, so the `pyproject.toml` file is discovered from that project path. Popular build frontends include `uv build`, `python -m build`, `pip wheel`, `pip install`, `hatch build`, `poetry build`, etc.

```bash
uv build --no-sources
```

List the generated distribution files in the `dist/` directory.

```bash
ls dist/
```

### Inspect the Package

A wheel (`.whl`) is a **ZIP archive** with Python modules and a `*.dist-info/` metadata directory. The source distribution created next to it is a gzip-compressed TAR archive (`.tar.gz`) that stores the source tree used to rebuild the package.

List the files inside the wheel archive without extracting it.

```bash
zipinfo -1 dist/paiguard-0.0.2-py3-none-any.whl
```

Read the wheel metadata that describes the wheel format version, generator, root layout, and compatibility tags.

```bash
unzip -p dist/paiguard-0.0.2-py3-none-any.whl paiguard-0.0.2.dist-info/WHEEL
```

Read the package metadata that installers and package indexes use for the project name, version, description, and dependency declarations.

```bash
unzip -p dist/paiguard-0.0.2-py3-none-any.whl paiguard-0.0.2.dist-info/METADATA
```

List the files inside the source distribution TAR archive.

```bash
tar -tzf dist/paiguard-0.0.2.tar.gz
```

### Publish the Package (Optional)

!!! info "Upload To Cloudsmith"
    Uploading to Cloudsmith is optional and requires a valid Cloudsmith account. You can build and inspect the artifacts locally without a Cloudsmith account or API key. The project's `Dockerfile.devEnv` defines a development image with the tools needed to build and inspect the package locally.

Before publishing, set the repository slug and enter your API key in the development container. The key is hidden while you type:

```bash
export CLOUDSMITH_REPOSITORY="<owner>/<repository>"
read -rsp "Cloudsmith API key: " CLOUDSMITH_API_KEY
printf '\n'
export CLOUDSMITH_API_KEY
```

Cloudsmith's PyPI upload endpoint uses HTTP basic authentication. Configure `uv` with the literal username `token` and the API key as its password:

```bash
export UV_PUBLISH_USERNAME=token
export UV_PUBLISH_PASSWORD="$CLOUDSMITH_API_KEY"
```

Once you have inspected the wheel package, upload it to the proprietary Python repository hosted on Cloudsmith.

Publish the package to the Cloudsmith PyPI repository with `uv`.

```bash
uv publish \
    --publish-url "https://python.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/" \
    dist/paiguard-0.0.2-py3-none-any.whl dist/paiguard-0.0.2.tar.gz
```

Check that the uploaded release is visible through the Cloudsmith `/simple/` API used by installers.

```bash
curl -fsSL "https://dl.cloudsmith.io/public/${CLOUDSMITH_REPOSITORY}/python/simple/paiguard/" | grep "paiguard-0.0.2"
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
        "paiguard[models]==0.0.1",
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

    Create `server.py` with FastAPI middleware that uses pAIguard's
    `PaiGuard.inspect()` to inspect uploaded images before the endpoint handles them:

    ```python
    from io import BytesIO

    from fastapi import FastAPI, Request, UploadFile
    from fastapi.responses import JSONResponse
    from PIL import Image
    from starlette.datastructures import UploadFile as StarletteUploadFile

    from paiguard import (
        ModelNotFoundError,
        PaiGuard,
        PaiNsfwDetection,
        PaiViolenceDetection,
    )

    app = FastAPI()
    app.state.moderation_guard = PaiGuard(
        rules=[
            PaiNsfwDetection(threshold=0.80),
            PaiViolenceDetection(threshold=0.85, review_threshold=0.50),
        ]
    )


    @app.middleware("http")
    async def moderate_upload(request: Request, call_next):
        if request.method == "POST" and request.url.path == "/moderations":
            # Cache the body so FastAPI can parse the upload again in the endpoint.
            await request.body()
            form = await request.form()
            result = None
            try:
                upload = form.get("image")
                if isinstance(upload, StarletteUploadFile):
                    with Image.open(BytesIO(await upload.read())) as image:
                        result = request.app.state.moderation_guard.inspect(
                            image.convert("RGB")
                        )
            except OSError:
                return JSONResponse(
                    status_code=415,
                    content={"detail": "Upload must be a readable image"},
                )
            except ModelNotFoundError:
                return JSONResponse(
                    status_code=503,
                    content={"detail": "pAIguard models are unavailable"},
                )
            finally:
                await form.close()

            if result is not None and not result.is_safe:
                return JSONResponse(
                    status_code=422,
                    content={
                        "detail": (
                            f"Image rejected ({result.decision}): "
                            f"{', '.join(result.violations)}"
                        )
                    },
                )

        return await call_next(request)


    @app.post("/moderations")
    async def moderate(image: UploadFile):
        return {"filename": image.filename, "decision": "allow"}
    ```

Install the dependencies from the complete project configuration:

```bash
uv sync
```

**Install Models**

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

### Use the Package

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
