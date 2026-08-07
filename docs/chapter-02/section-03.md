# Python Containers

Python containers package an application together with the runtime files it needs to run. They help teams deploy the same application image across local machines, CI pipelines, and production platforms.

## Applied Project

### Project Setup

The applied project is a small HTTP server called `Tiny Webserver Project`. It serves a single route with [Bottle](https://bottlepy.org/) and starts from a console entry point. This makes it a good fit for containers because the application, its Python runtime, and its dependencies can be packaged into one image that behaves the same on every host with a container engine.

### Run the Project

Application, test, lint, and build commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj3_tiny_webserver/README.md).

## Building Blocks

### Overview

In contrast to Python wheels, operating-system packages, or Conda packages, OCI container images are not primarily package archives but complete runtime environments. They package an application together with everything required to execute it, including the operating system components, language runtime, libraries, configuration, and application code. For example, a Python container image typically includes the Python interpreter and its dependencies, while a Java container image includes a Java runtime.

The [Open Container Initiative (OCI)](https://github.com/opencontainers) defines open standards for building, distributing, and running container images. The **OCI Image Format Specification** describes how images are represented using immutable filesystem layers together with image metadata, while the **OCI Runtime Specification** defines how containers are executed. The **OCI Distribution Specification** defines how images are pushed to and pulled from container registries.

At a high level, container distribution consists of five building blocks: a **build recipe** (`Dockerfile` or `Containerfile`) that describes how an image is assembled, an **OCI image** that packages the application and its runtime environment, a **container registry** that stores and distributes images, a **container manager** that builds, stores, pulls, and runs images on a host, and an **OCI runtime** that creates and executes containers. Because these building blocks follow OCI standards, different tools can participate in the same workflow while remaining interoperable across development, CI/CD, and production environments.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Packages an application as immutable filesystem layers together with OCI image metadata. | OCI image, Docker image |
| Build Recipe | Describes how the image is assembled. | `Dockerfile`, `Containerfile` |
| Maintainer / Metadata File | OCI metadata generated during the image build. Package maintainers typically do **not** edit these files directly. | OCI image manifest, OCI image configuration (`config.json`), image index |
| Package Manager | Builds, stores, pulls, pushes, inspects, and runs OCI images on a host. | Docker, Podman |
| Remote Repository | Stores and distributes OCI images using repositories and tags. | Docker Hub, GitHub Container Registry, Amazon ECR, Cloudsmith, Quay.io |


### Project Layout

A typical Python container project is structured to separate application code, build configuration, and container-specific instructions:

```text
{project_root}/
├── src/
├── Dockerfile
├── .dockerignore
├── LICENSE
├── pyproject.toml
└── README.md
```

- `src/`: Contains the application source code.
- `Dockerfile`: The **central build recipe** that defines how the container image is constructed. It describes the full build and deployment pipeline inside the image itself, including dependencies, build steps, and runtime configuration. It can also implement multi-stage builds, where the application is first built (for example as a Python wheel) and then packaged into a minimal runtime image that contains only the installed artifact and its runtime dependencies.
- `.dockerignore`: Defines files and directories excluded from the build context to reduce image size and improve build speed.
- `pyproject.toml`: The central configuration file for modern Python packaging, defining metadata, dependencies, and build system configuration.

### Package Manifest

The `Dockerfile` is not the package manifest itself. It is the build recipe and the single source of truth that project maintainers work with. During the build, the container manager reads that recipe and turns it into image layers, runtime configuration, and manifest data such as `manifest.json`. The `Dockerfile` tells the builder what to do: select a base image, copy application files, install dependencies, and define the process that starts when a container runs.

```dockerfile
FROM <base-image>:<tag>

WORKDIR <application-directory>
COPY <source-path> <destination-path>
RUN <dependency-install-command>

ENTRYPOINT ["<executable>"]
CMD ["<default-argument>"]
```

- `FROM`: Selects the base image and its version.
- `WORKDIR`: Sets the default directory for later build steps and container startup.
- `COPY`: Adds the application or built artifacts to the image filesystem.
- `RUN`: Executes build-time installation or configuration commands.
- `ENTRYPOINT` and `CMD`: Define the executable and default arguments used at runtime.

### Package Layout

OCI container images follow the [OCI Image Format Specification](https://github.com/opencontainers/image-spec/blob/main/spec.md), which defines how image manifests, metadata, configuration, and filesystem layers are structured and exchanged. Unlike wheels, Debian packages, or Conda packages, container images represent complete execution environments consisting of operating system components, runtime, dependencies, application code, and runtime configuration. Because they follow an open standard, OCI images can be created, stored, and consumed by different container tools such as Docker, Podman, and containerd.

When an image is pulled from a registry, the container manager stores its metadata and filesystem layers locally using its own internal storage mechanism. These components are managed as shared image layers, image metadata, and writable container layers rather than as a single archive file. To inspect an image as a portable file, it can be exported from the container manager. The `docker save` command creates a TAR archive (see [Inspect The Package](#inspect-the-package)) containing the complete image, including its layers and metadata. In contrast, `docker export` creates a flat filesystem archive from a running container and does not preserve image metadata, layer history, or runtime configuration. Registries provide the remote equivalent of this workflow by storing and distributing the same image metadata and layers so that other hosts can pull and recreate the image locally.

Container images are usually referenced using a **repository**, a **tag**, or a **digest**:

- **Repository** identifies the image source, for example `python`.
- **Tag** is a human-readable label that selects an image variant, for example `3.12-slim`.
- **Digest** is an immutable cryptographic hash that uniquely identifies the exact image contents, for example `sha256:<digest>`.

Developers typically use repository and tag references because they are easy to read and remember, for example `docker pull python:3.12-slim`. Internally, the registry resolves the tag to the corresponding digest. Unlike tags, which can be reassigned to newer image versions, a digest always refers to the same image. Pulling an image by digest, for example `docker pull python@sha256:<digest>`, guarantees that the exact same image is retrieved across different environments, making deployments reproducible.

## Packaging Workflow

!!! info
    This workflow assumes that you have a valid Cloudsmith repository and access to its Docker registry. Set `CLOUDSMITH_REPOSITORY` to the Cloudsmith owner and repository path, such as `example-org/python-containers`, before you publish.

The development environment for this section is a Dev Container that uses *Docker outside of Docker*. The commands below run inside the Dev Container, while image builds are handled by the host Docker daemon.

### Prepare the Development Environment

First, confirm that Docker is installed and running on the host machine:

```bash
docker version
```

Install Node.js and npm if the host does not already have them:

```bash
sudo apt-get update && sudo apt-get install -y nodejs npm
```

Install the Dev Container CLI with npm:

```bash
sudo npm install -g @devcontainers/cli
```

Move into the Tiny Webserver project directory:

```bash
cd projects/proj3_tiny_webserver
```

Set the Cloudsmith repository that will receive the published image:

```bash
export CLOUDSMITH_REPOSITORY="<owner>/<repository>"
```

### Boot the Development Environment

Build and start the Dev Container workspace:

```bash
devcontainer up --workspace-folder .
```

Open an interactive shell inside the running Dev Container:

```bash
devcontainer exec --workspace-folder . bash
```

Inside that shell, confirm that the Docker CLI can reach the host Docker daemon:

```bash
docker version
```

Run the remaining workflow commands from inside this Dev Container shell.

### Create the Container

The container image is built using a `Dockerfile`-based build process, which produces a tagged image:

```bash
docker build -t tiny-webserver:1.0.0 .
```

List local container images to confirm that the build produced the tagged image:

```bash
docker image ls
```

### Inspect The Package

An OCI container image is a structured image manifest, configuration document, and set of filesystem layers. Docker stores these pieces behind the local image tag, and inspection commands let you see different views of that structure.

Inspect the image metadata that Docker stores for the local tag.

```bash
docker inspect tiny-webserver:1.0.0
```

The output includes the image ID, content digests, environment variables, entry point, exposed ports, platform, and layer metadata that Docker uses to create containers from the image.

Show the image layer history and the Dockerfile instructions that produced each layer.

```bash
docker history tiny-webserver:1.0.0
```

Export the local image to a TAR archive for offline inspection. This archive is Docker's portable image export format; it exposes the same main ideas: a manifest, a configuration JSON document, and layer TAR files.

```bash
docker save tiny-webserver:1.0.0 --output tiny-webserver-1.0.0.tar
```

List the files stored inside the exported image TAR archive.

```bash
tar -tf tiny-webserver-1.0.0.tar
```

The exported archive has a structure similar to this:

```text
tiny-webserver-1.0.0.tar
├── index.json
├── manifest.json
├── oci-layout
└── blobs/sha256
    ├── <sha256>.json (config)
    ├── <sha256>.json (layer1)
    ├── <sha256>.json (layer2)
    └── ...
```

- `oci-layout`: Identifies the archive as an OCI image layout and records the layout version.
- `index.json`: Acts as the archive entry point. It points to one or more image manifests and can associate those manifests with tags.
- `manifest.json`: Preserves Docker-compatible image metadata for saved images, including the configuration object and ordered layer list.
- `blobs/sha256/<digest>`: Stores content-addressed image objects. JSON blobs hold metadata such as the image configuration or manifest, while layer blobs hold the filesystem changes that Docker applies in order to assemble the container root filesystem.

### Publish the Container

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
docker tag tiny-webserver:1.0.0 "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/tiny-webserver:1.0.0"
```

Then upload the tagged image:

```bash
docker push "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/tiny-webserver:1.0.0"
```

## Consumer Workflow

### Install the Container

Once published, the image can be downloaded from Cloudsmith:

```bash
docker pull "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/tiny-webserver:1.0.0"
```

To run the packaged web server, you can leverage the `run` command:

```bash
docker run -p 8080:8080 "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/tiny-webserver:1.0.0"
```
