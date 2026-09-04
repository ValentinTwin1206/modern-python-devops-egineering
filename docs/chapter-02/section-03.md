# Python Containers

Python containers package an application together with the runtime files it needs to run. They help teams deploy the same application image across local machines, CI pipelines, and controlled runtime platforms in production.

## Applied Project

### Project Setup

The applied project is a small FastAPI service called `License Service`. It generates and validates license keys, stores them in a local SQLite database, and rate-limits its write endpoint with [PyGuard](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_pyguard/README.md) middleware installed from a Cloudsmith package index. This makes it a good fit for containers because the application, its Python runtime, and its dependencies can be packaged into one image that behaves the same on every host with a container engine.

### Run the Project

Application, install, and test commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj3_license_service/README.md).

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

A typical Python container project is structured to separate application code, dependency metadata, and build configuration:

```text
{project_root}/
├── main.py
├── database.py
├── helpers.py
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

- `main.py`: The FastAPI application, its routes, the PyGuard middleware wiring, and the `uvicorn` entrypoint that the container runs on startup.
- `database.py` and `helpers.py`: Supporting application modules copied into the image alongside `main.py`.
- `Dockerfile`: The **central build recipe** that defines how the container image is constructed. It describes the full build and deployment pipeline inside the image itself, including dependencies, build steps, and runtime configuration. It can also implement multi-stage builds, where the application is first built (for example as a Python wheel) and then packaged into a minimal runtime image that contains only the installed artifact and its runtime dependencies.
- `pyproject.toml` and `uv.lock`: The dependency metadata and lockfile that `uv sync` reads to install `fastapi`, `uvicorn`, and `pyguard` inside the image.

### Build Recipe

An OCI image is defined by a build recipe, commonly `Dockerfile` or `Containerfile`. In this project, the `Dockerfile` is the maintainer-edited source of truth. During the build, the container manager reads that recipe and turns it into image layers, runtime configuration, and manifest data such as `manifest.json`.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency metadata
COPY pyproject.toml uv.lock ./

# Install dependencies into a project-local virtual environment
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:${PATH}"

# Copy application source
COPY main.py database.py helpers.py ./

EXPOSE 8080

CMD ["python", "main.py"]
```

- `FROM`: Selects the base image and its version.
- `WORKDIR`: Sets the default directory for later build steps and container startup.
- `COPY`: Adds dependency metadata and application source to the image filesystem.
- `RUN`: Executes the `uv sync` install step, which resolves `pyguard` from the Cloudsmith package index declared in `pyproject.toml` and creates a project-local virtual environment at `/app/.venv`.
- `ENV`: Puts that virtual environment's `bin/` directory first on `PATH`, so the plain `python` command used by `CMD` resolves the packages `uv sync` installed.
- `CMD`: Defines the default command used at runtime. This Dockerfile has no separate `ENTRYPOINT`.

### Package Layout

OCI container images follow the [OCI Image Format Specification](https://github.com/opencontainers/image-spec/blob/main/spec.md), which defines how image manifests, metadata, configuration, and filesystem layers are structured and exchanged. Because they follow an open standard, OCI images can be created, stored, and consumed by different container tools such as *Docker*, *Podman*, etc.

On a host machine, an OCI image is not stored as one ordinary project file. It is persisted through the container manager's internal storage logic, which manages image metadata, shared filesystem layers, and writable container layers. To inspect or move that content as a file, use a dedicated export format such as the [**OCI image-layout TAR archive**](#inspect-the-package), [**Docker image TAR archive**](#inspect-the-package) or as a flat filesystem archive from a container (`docker export`).

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and access to its Docker registry. Set `CLOUDSMITH_REPOSITORY` to the Cloudsmith owner and repository path, such as `example-org/python-containers`, before you publish.

### Setup the Local Environment

First, confirm that Docker is installed and running on the host machine:

```bash
docker version
```

Move into the License Service project directory:

```bash
cd projects/proj3_license_service
```

Set the Cloudsmith repository that will receive the published image:

```bash
export CLOUDSMITH_REPOSITORY="<owner>/<repository>"
```

### Create the Container

The same `Dockerfile` can produce different output formats depending on the build command. The first workflow creates a normal local image managed by Docker, while the second creates a portable OCI image archive as a file on disk.

=== "Classical container image"

    This command builds the image from the `Dockerfile`, stores the resulting image layers and metadata in Docker's local image store, and assigns the tag `license-service:1.0.0`. The image can then be inspected, run, tagged for a registry, or pushed from the local Docker host.

    ```bash
    docker build -t license-service:1.0.0 .
    ```

    
    List local container images to confirm that the build produced the tagged image:

    ```bash
    docker image ls
    ```

=== "OCI image archive"

    This command uses BuildKit through `docker buildx` to build the image and write it directly to `image.tar` as an OCI image layout archive. The archive contains OCI metadata and content-addressed blobs, but it is not loaded into Docker's local image store unless you import it later.

    ```bash
    docker buildx build \
      --output type=oci,dest=license-service-1.0.0.tar \
      .
    ```

### Inspect The Package

The inspection command depends on the output format created in the previous step. A local Docker image is inspected through the container manager's image store, while an OCI image archive is inspected as files inside the TAR archive.

=== "Classical container image"

    Inspect the metadata that Docker stores for the local image tag:

    ```bash
    docker inspect license-service:1.0.0
    ```

    The output includes the image ID, content digests, environment variables, entry point, exposed ports, platform, and layer metadata that Docker uses to create containers from the image.

    Show the image layer history and the Dockerfile instruction associated with each layer:

    ```bash
    docker history license-service:1.0.0
    ```

=== "OCI image archive"

    Inspect the archive created by `docker buildx build --output type=oci` by listing the files inside the TAR archive:

    ```bash
    tar -tf license-service-1.0.0.tar
    ```

    The exported OCI archive has a structure similar to this:

    ```text
    license-service-1.0.0.tar
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

### Publish the Container

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
docker tag license-service:1.0.0 "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/license-service:1.0.0"
```

Then upload the tagged image:

```bash
docker push "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/license-service:1.0.0"
```

## Consumer Workflow

### Install the Container

Once published, the image can be downloaded from Cloudsmith:

```bash
docker pull "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/license-service:1.0.0"
```

To run the packaged service, you can leverage the `run` command:

```bash
docker run -p 8080:8080 "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/license-service:1.0.0"
```

Confirm that the service responds:

```bash
curl http://127.0.0.1:8080/
```
