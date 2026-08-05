# Python Containers

Python containers package an application together with the runtime files it needs to run. They help teams deploy the same application image across local machines, CI pipelines, and production platforms.

## Applied Project

### Project Setup

The applied project is a small HTTP server called `Tiny Webserver Project`. It serves a single route with [Bottle](https://bottlepy.org/) and starts from a console entry point. This makes it a good fit for containers because the application, its Python runtime, and its dependencies can be packaged into one image that behaves the same on every host with a container engine.

### Run the Project

Application, test, lint, and build commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj3_tiny_webserver/README.md).

## Building Blocks

### Overview

OCI container images are built distributions that package an application with its Python runtime, Python dependencies, operating-system libraries, and runtime configuration. The Open Container Initiative defines interoperable image and runtime specifications, allowing the same image to run with compatible tools across development, CI, and production. Containers are typically used for backend APIs, microservices, data pipelines, scheduled jobs, and cloud deployments that need a reproducible runtime environment.

Container distribution connects four building blocks: an OCI image stores immutable filesystem layers and image metadata, a build recipe describes how to assemble those layers, a container engine pulls and manages images, and a registry publishes image manifests and layer content. Tools such as Docker, Podman, Buildah, and Skopeo can participate in different parts of this workflow because they implement OCI-compatible formats and APIs.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Stores the image manifest, configuration, and immutable filesystem layers. | OCI image, Docker image |
| Maintainer / Metadata File | Defines image build steps and records runtime settings, labels, and annotations. | `Dockerfile`, `Containerfile`, OCI image configuration |
| Package Manager | Builds, pulls, inspects, runs, and removes images on a host. | Docker, Podman, Buildah |
| Remote Repository | Stores image manifests and layers under repository names and tags. | Cloudsmith, GitHub Container Registry, Amazon ECR, Quay.io |

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

OCI container images are more sophisticated than the package formats introduced earlier in this chapter. While a wheel, Debian package, or Conda package is typically a single archive containing files and metadata, a container image resembles a small filesystem distribution. It consists of metadata, runtime configuration, and a stack of immutable filesystem layers, each recording changes such as the base operating system, Python runtime, installed dependencies, or application code. Because layers are content-addressed by digest and shared across images, they can be reused efficiently, reducing storage requirements and accelerating image pulls and pushes. This layout is standardized by the [OCI Image Specification](https://github.com/opencontainers/image-spec/blob/main/spec.md), which defines how images, metadata, layers, and manifests are represented and exchanged between container tools and registries.

Container images are typically referenced by a **repository** and a **tag**, for example the official Python image `python:3.12-slim`. The repository identifies the image, while the tag is a human-readable label. In this example, `3.12-slim` selects the Python 3.12 image variant based on a slim Debian runtime. Developers usually build, push, and pull images using a repository and tag because they are easy to read and remember. Internally, however, every image is identified by a **digest**: a cryptographic hash that uniquely represents its exact contents. When an image is pulled, the registry resolves the tag to the corresponding digest, ensuring the correct image is downloaded. Unlike tags, which can be reassigned to newer image versions, a digest is immutable and always refers to the same image.

| Component | Example | Purpose |
| ---------- | ------- | ------- |
| Repository | `python` | Identifies the official Python image repository. |
| Tag | `3.12-slim` | Human-readable label that selects the Python version and image variant. |
| Digest | `sha256:<digest>` | Immutable identifier for the exact image contents. |
| Image (tag) | `python:3.12-slim` | Convenient reference used by developers. |
| Image (digest) | `python@sha256:<digest>` | Immutable reference that always resolves to the same image. |

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
├── manifest.json
├── repositories
├── <image-config-digest>.json
├── <layer-digest>/
│   ├── VERSION
│   ├── json
│   └── layer.tar
└── ...
```

- `manifest.json`: Connects the image tag to the configuration document and ordered layer list.
- `<image-config-digest>.json`: Records runtime configuration such as environment variables, exposed ports, entry point, command, architecture, and operating system.
- `<layer-digest>/layer.tar`: Contains one immutable filesystem layer. Docker applies these layers in manifest order to assemble the container root filesystem.

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
