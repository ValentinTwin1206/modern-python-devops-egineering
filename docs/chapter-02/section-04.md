# Python Containers

Python containers package an application together with the runtime files it needs to run. They help teams deploy the same application image across local machines, CI pipelines, and controlled runtime platforms in production.

## Applied Project

### Project Setup

The applied project is the `IrisLab API`, a FastAPI service exposing the [IrisLab](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj3_irislab/README.md) iris-color analysis application over HTTP. Its container image delivers the API together with Python, the scientific libraries, the native extension, and the local MediaPipe model needed for inference.

### Run the Project

Application, build, and test commands are documented in the [project README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj2_irislab_api/README.md).

## Building Blocks

### Overview

In contrast to Python wheels, operating-system packages, or Conda packages, OCI container images are not primarily package archives but complete runtime environments. They package an application together with everything required to execute it, including the operating system components, language runtime, libraries, configuration, and application code. In addition, **container managers** are more comprehensive than classical package managers, as they do not only build and install images, but also  pull, push, store, inspect, create, and run containers, and manage their lifecycle on the host.

The [Open Container Initiative (OCI)](https://github.com/opencontainers) defines open standards that make container images portable across different tools and environments. The three core specifications cover different parts of the container lifecycle:

- **OCI Image Format Specification**: Defines the structure of a container image, including its manifest, image configuration, and immutable filesystem layers.
- **OCI Distribution Specification**: Defines how container images are stored and exchanged through registries, including operations such as pushing and pulling manifests and layers.
- **OCI Runtime Specification**: Defines how a container is configured and executed, including the runtime bundle and settings such as the process, environment, mounts, and isolation.

At a high level, container distribution consists of five building blocks: a **build recipe** (`Dockerfile` or `Containerfile`) that describes how an image is assembled, an **OCI image** that packages the application and its runtime environment, a **container registry** that stores and distributes images, a **container manager** that builds, stores, pulls, and runs images on a host, and an **OCI runtime** that creates and executes containers. Because these building blocks follow OCI standards, different tools can participate in the same workflow while remaining interoperable across development, CI/CD, and production environments.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Container Format | Packages an application as immutable filesystem layers together with OCI image metadata. | OCI image, Docker image |
| Build Recipe | Describes how the image is assembled. | `Dockerfile`, `Containerfile` |
| Maintainer / Metadata File | OCI metadata generated during the image build. Package maintainers typically do **not** edit these files directly. | OCI image manifest, OCI image configuration (`config.json`), image index |
| Container Manager | Builds, stores, pulls, pushes, inspects, and runs OCI images on a host. | Docker, Podman |
| Remote Repository | Stores and distributes OCI images using repositories and tags. | Docker Hub, GitHub Container Registry, Amazon ECR, Cloudsmith, Quay.io |

### Project Layout

The API layout separates HTTP routes, response schemas, application services, and container configuration:

```text
proj2_irislab_api/
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── src/irislab_api/
│   ├── main.py
│   ├── api/routes/
│   ├── schemas/
│   └── services/
├── tests/
└── README.md
```

- `src/irislab_api/`: The FastAPI application, routes, response schemas, and an adapter to the IrisLab analysis function.
- `Dockerfile`: The **central build recipe** that defines how the container image is constructed. It describes the full build and deployment pipeline inside the image itself, including dependencies, build steps, and runtime configuration. It can also implement multi-stage builds, where the application is first built (for example as a Python wheel) and then packaged into a minimal runtime image that contains only the installed artifact and its runtime dependencies.
- `pyproject.toml` and `uv.lock`: The API's Python dependency metadata and lockfile for FastAPI and Uvicorn. IrisLab is installed separately from a Conda channel.
- `tests/`: API contract tests for the routes and their error responses.

### Build Recipe

An OCI image is assembled from a build recipe, commonly called a `Dockerfile` or `Containerfile`. The container manager reads its instructions to create filesystem layers and image configuration. The [IrisLab API Dockerfile](../../projects/proj2_irislab_api/Dockerfile) is the source of truth for this example.

The recipe combines two common techniques: selecting a **base image** with the tools the project needs and using a **multi-stage build** to separate preparation from the final runtime. The runtime stage copies the prepared environments and model from the build stage, leaving build-only tools behind. Both stages start from `mambaorg/micromamba:2.3.3`, which provides `micromamba`, a Conda-compatible package manager, without requiring a separate installation. The build stage follows a **Conda-first** approach, then installs `mediapipe` with `pip` as in the [Conda consumer workflow](section-03.md#consumer-workflow). Micromamba installs `irislab-tools` using the provided `IRISLAB_CHANNEL`:

```bash
micromamba create --yes --prefix /opt/conda/envs/irislab-api \
    python=3.12 irislab-tools=1.0.0 libglib pip
```

The build stage also installs `curl` with `micromamba` and uses it to download and verify the `face_landmarker.task` model. It then installs `irislab-api` as a regular Python package (`--no-editable`) from the committed lockfile (`--locked`) in a separate `uv` environment that can access the Conda packages. The lockfile does not cover the Conda solve, MediaPipe's transitive dependencies, or the model. The API installation uses the following command (see [Chapter 03, Section 02](../chapter-03/section-02.md#synchronizing)):

```bash
uv sync --locked --no-dev --no-editable
```

The following `Dockerfile` contains the complete build and installation steps for running the IrisLab API alongside IrisLab in one portable container environment:

```dockerfile
# 
# BUILD STAGE
# # # # # #
FROM mambaorg/micromamba:2.3.3 AS build

ARG IRISLAB_CHANNEL
USER root

# uv installs the API; pip supplies MediaPipe, which is not in the recipe.
COPY --from=ghcr.io/astral-sh/uv:0.11.1 /uv /usr/local/bin/uv

# Configure channel priority just as in the Chapter 02 consumer workflow.
# The channel URL is public and must not contain credentials.
RUN micromamba config prepend channels conda-forge \
    && micromamba config prepend channels "${IRISLAB_CHANNEL}" \
    && micromamba config set channel_priority strict

# Install IrisLab and its declared runtime dependencies, including the exact
# libirislab build. libglib is required by MediaPipe's PyPI OpenCV wheel.
RUN micromamba create \
    --yes \
    --prefix /opt/conda/envs/irislab-api \
        python=3.12 \
        irislab-tools=1.0.0 \
        libglib \
        pip \
    && micromamba clean --all --yes

# The Conda recipe does not depend on MediaPipe, which is distributed on PyPI.
# Let pip resolve its Python dependencies, as in the consumer workflow.
RUN /opt/conda/envs/irislab-api/bin/python -m pip install \
        mediapipe==0.10.35

# Install curl via conda:
#   - adds curl to the build stage's base Conda environment
#   - downloads and verifies the Face Landmarker model for the runtime image
RUN micromamba install \
    --yes \
    --name base \
    --channel conda-forge curl \
    && micromamba clean --all --yes

#
# Download the MediaPipe Face Landmarker model used by iris.py.
#
# The model is stored outside the Python source tree and inference runs
# locally inside the container.
#
RUN mkdir -p /opt/irislab \
    && /opt/conda/bin/curl -fsSL \
        https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task \
        -o /opt/irislab/face_landmarker.task \
    && echo '64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff  /opt/irislab/face_landmarker.task' | sha256sum -c -

# Use /app as the project directory so later relative paths, such as src, resolve
# from this location.
WORKDIR /app

# Configure uv:
#   - keeps uv-managed packages separate from Conda
#   - uses Conda's Python instead of downloading another interpreter
#   - copies packages into the environment
ENV UV_PROJECT_ENVIRONMENT=/opt/irislab-api-venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY src ./src

# Create the uv environment with Conda's Python:
#   - uses Conda's interpreter instead of downloading another Python
#   - exposes Conda-installed packages, including IrisLab and MediaPipe
RUN uv venv --python /opt/conda/envs/irislab-api/bin/python \
    --system-site-packages "${UV_PROJECT_ENVIRONMENT}"

# Install 'irislab-api':
#   - installs the production dependencies recorded in uv.lock
#   - leaves the lockfile unchanged and skips development dependencies
#   - checks that installed package requirements are compatible
RUN uv sync \
    --locked \
    --no-dev \
    --no-editable \
    && /opt/irislab-api-venv/bin/python -m pip check

#
# RUNTIME STAGE
# # # # # #
FROM mambaorg/micromamba:2.3.3 AS runtime

# Root is needed to copy the environment and model into system-owned paths.
USER root

# Use the prepared Conda environment and configure the application runtime.
ENV PATH="/opt/irislab-api-venv/bin:/opt/conda/envs/irislab-api/bin:${PATH}" \
    LD_LIBRARY_PATH=/opt/conda/envs/irislab-api/lib \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    IRISLAB_MODEL_PATH=/opt/irislab/face_landmarker.task

# Copy the runtime components from the build stage:
#   - the Conda environment
#   - the uv environment containing the installed API
#   - the Face Landmarker model
COPY --from=build /opt/conda/envs/irislab-api /opt/conda/envs/irislab-api
COPY --from=build /opt/irislab-api-venv /opt/irislab-api-venv
COPY --from=build /opt/irislab/face_landmarker.task /opt/irislab/face_landmarker.task

# Run the API as the unprivileged user provided by the base image.
USER $MAMBA_USER
WORKDIR /app
EXPOSE 8080
ENTRYPOINT []
CMD ["uvicorn", "irislab_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

- `FROM` starts each stage from the specified base image. The `AS` names allow later instructions to refer to a stage.
- `ARG` accepts the public Conda channel URL at build time.
- `RUN` executes commands during the build, including dependency installation and model download and verification.
- `ENV` sets environment variables. In the runtime stage, these select the Python and native-library paths and the model location.
- `WORKDIR` sets the working directory for subsequent instructions.
- `COPY` adds project files to the build stage or copies files from another image or stage. Both environments keep their original paths because the API environment depends on the Conda interpreter and packages.
- `USER` selects the user for subsequent instructions. The runtime switches from root to the base image's unprivileged user before starting the API.
- `EXPOSE` documents the container port; publishing it to the host requires a run option such as `-p 8080:8080`.
- `ENTRYPOINT` clears the base image's entrypoint, and `CMD` supplies the default Uvicorn command.

### Package Layout

OCI container images follow the [OCI Image Format Specification](https://github.com/opencontainers/image-spec/blob/main/spec.md), which defines how image manifests, metadata, configuration, and filesystem layers are structured and exchanged. Because they follow an open standard, OCI images can be created, stored, and consumed by different container tools such as *Docker*, *Podman*, etc.

On a host machine, an OCI image is not stored as one ordinary project file. It is persisted through the container manager's internal storage logic, which manages image metadata, shared filesystem layers, and writable container layers. To inspect or move that content as a file, use a dedicated export format such as the [**OCI image-layout TAR archive**](#inspect-the-package), [**Docker image TAR archive**](#inspect-the-package) or as a flat filesystem archive from a container (`docker export`).

## Tradeoffs

### Pros

- ✅ Bundles the application and runtime
- ✅ Isolates dependencies from the host
- ✅ Runs consistently across container platforms
- ✅ Supports reliable rollbacks

### Cons

- ⚠️ Requires container infrastructure
- ⚠️ Images can be large
- ⚠️ Base images require regular patching
- ⚠️ Data and secrets need separate management

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and access to its Docker registry. Set `CLOUDSMITH_REPOSITORY` to the Cloudsmith owner and repository path, such as `example-org/python-containers`, before you publish.

### Create the Environment

The IrisLab API uses a runtime `Dockerfile`. Publish both Conda artifacts for
Linux and Python 3.12 using the current recipe in [Section 03](section-03.md)
before building. Older packages may not support the configured model path.

First, confirm that Docker is installed and running on the host machine:

```bash
docker version
```

Move into the API directory, which provides the build context:

```bash
cd projects/proj2_irislab_api
```

Set the Cloudsmith repository that will receive the published image:

```bash
export CLOUDSMITH_REPOSITORY="<owner>/<repository>"
```

Set the public Conda channel containing the IrisLab packages separately. Do not
put credentials in a build argument:

```bash
export IRISLAB_CHANNEL="https://conda.cloudsmith.io/<owner>/<repository>/"
```

### Create the Package

The same `Dockerfile` can produce different output formats depending on the build command. The first workflow creates a normal local image managed by Docker, while the second creates a portable OCI image archive as a file on disk.

=== "Classical container image"

    This command builds the image from the API `Dockerfile`, stores the resulting image layers and metadata in Docker's local image store, and assigns the tag `irislab-api:1.0.0`.

    ```bash
    docker build --build-arg "IRISLAB_CHANNEL=$IRISLAB_CHANNEL" -t irislab-api:1.0.0 .
    ```


    List local container images to confirm that the build produced the tagged image:

    ```bash
    docker image ls
    ```

=== "OCI image archive"

    This command uses BuildKit through `docker buildx` to write the image as an OCI image layout archive. The archive contains OCI metadata and content-addressed blobs, but it is not loaded into Docker's local image store unless you import it later.

    ```bash
    docker buildx build \
      --build-arg "IRISLAB_CHANNEL=$IRISLAB_CHANNEL" \
      --output type=oci,dest=irislab-api-1.0.0.tar \
      .
    ```

### Inspect the Package

The inspection command depends on the output format created in the previous step. A local Docker image is inspected through the container manager's image store, while an OCI image archive is inspected as files inside the TAR archive.

=== "Classical container image"

    Inspect the metadata that Docker stores for the local image tag:

    ```bash
    docker inspect irislab-api:1.0.0
    ```

    The output includes the image ID, content digests, environment variables, entry point, exposed ports, platform, and layer metadata that Docker uses to create containers from the image.

    Show the image layer history and the Dockerfile instruction associated with each layer:

    ```bash
    docker history irislab-api:1.0.0
    ```

=== "OCI image archive"

    Inspect the archive created by `docker buildx build --output type=oci` by listing the files inside the TAR archive:

    ```bash
    tar -tf irislab-api-1.0.0.tar
    ```

    The exported OCI archive has a structure similar to this:

    ```text
    irislab-api-1.0.0.tar
    ├── blobs/
    │   └── sha256/
    │       ├── <digest> (manifest JSON)
    │       ├── <digest> (configuration JSON)
    │       ├── <digest> (filesystem layer)
    │       └── ...
    ├── index.json
    └── oci-layout
    ```

    - `oci-layout`: Identifies the archive as an OCI image layout and records the layout version.
    - `index.json`: Acts as the archive entry point. It points to the image manifest stored under `blobs/sha256/` and can associate that manifest with a tag.
    - `blobs/sha256/<digest>`: Stores all content-addressed image objects. Some blobs are JSON documents, such as the image manifest and image configuration, while other blobs are compressed filesystem layers.

### Publish the Package

Published images are addressed by a repository and tag, such as `python:3.12-slim`, while registries resolve that tag to an immutable digest such as `sha256:<digest>`. Tags are readable and convenient, but they can be reassigned; pulling by digest, for example `docker pull python@sha256:<digest>`, guarantees the same image content across environments.

To publish the image, set `CLOUDSMITH_REPOSITORY` to the Cloudsmith owner and repository path, such as `example-org/python-containers`. Do not include the registry host or image name in this value.

```bash
export CLOUDSMITH_REPOSITORY="<owner>/<repository>"
```

Then authenticate with Cloudsmith's Docker registry:

```bash
docker login docker.cloudsmith.io
```

Tag the local image with the Cloudsmith registry path:

```bash
docker tag irislab-api:1.0.0 "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/irislab-api:1.0.0"
```

Then upload the tagged image:

```bash
docker push "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/irislab-api:1.0.0"
```

## Consumer Workflow

### Install the Container

Once published, the image can be downloaded from Cloudsmith:

```bash
docker pull "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/irislab-api:1.0.0"
```

To run the packaged service, you can leverage the `run` command:

```bash
docker run -p 8080:8080 "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/irislab-api:1.0.0"
```

Confirm that the service responds:

```bash
curl http://127.0.0.1:8080/health/live
```
