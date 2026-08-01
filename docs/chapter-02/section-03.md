# Python Containers

Python containers package an application together with the runtime files it needs to run. They help teams deploy the same application image across local machines, CI pipelines, and production platforms.

## Applied Project

### Project Setup

The applied project is a small utility library called `Docslug Project`. It turns headings and file names into stable slugs without any runtime dependencies beyond the Python standard library. This makes it a good fit for `venv` because a pure-Python library shows clearly how one project-local environment can isolate build and development tools while keeping the installed package itself lightweight.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_docslug/README.md).

## Building Blocks

### Overview

OCI container images are built distributions that package an application with its Python runtime, Python dependencies, operating-system libraries, and runtime configuration. The Open Container Initiative defines interoperable image and runtime specifications, allowing the same image to run with compatible tools across development, CI, and production. Containers are typically used for backend APIs, microservices, data pipelines, scheduled jobs, and cloud deployments that need a reproducible runtime environment.

Container distribution connects four building blocks: an OCI image stores immutable filesystem layers and image metadata, a build recipe describes how to assemble those layers, a container engine pulls and manages images, and a registry publishes image manifests and layer content. Tools such as Docker, Podman, Buildah, and Skopeo can participate in different parts of this workflow because they implement OCI-compatible formats and APIs.

| Building Block | Role | Common Examples |
|----------------|------|-----------------|
| Package Format | Stores the image manifest, configuration, and immutable filesystem layers. | OCI image, Docker image |
| Maintainer / Metadata File | Defines image build steps and records runtime settings, labels, and annotations. | `Dockerfile`, `Containerfile`, OCI image configuration |
| Package Manager | Builds, pulls, inspects, runs, and removes images on a host. | Docker, Podman, Buildah |
| Remote Repository | Stores image manifests and layers under repository names and tags. | Docker Hub, GitHub Container Registry, Amazon ECR, Quay.io |

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

The `Dockerfile` is the maintainer file for an OCI image. It selects the base image, copies application files, installs dependencies, and defines the process that starts when a container runs.

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

An OCI container image is a content-addressed collection of JSON metadata and immutable filesystem layers. Registries and container runtimes store these objects by digest rather than as one ordinary archive file. The image manifest connects the configuration document to the ordered layers that form the container filesystem.

```text
{image-name}:{tag}
├── manifest
│   ├── config digest
│   └── layer digests
├── configuration
│   ├── environment
│   ├── entry point
│   └── platform
└── filesystem layers
	├── base operating-system files
	├── runtime and dependencies
	└── application files
```

- Manifest: Identifies the image configuration and lists filesystem layers in order.
- Configuration: Records runtime settings, architecture, environment variables, and the command that starts the container.
- Filesystem layers: Store additions, changes, and deletions that combine into the container's root filesystem.

The repository name and tag provide a convenient reference, while the digest identifies exact image content. Exporting an image with `docker save` wraps its metadata and layers in a TAR archive for transfer or inspection.

## Packaging Workflow

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

An OCI container image is a structured image manifest, configuration document, and set of filesystem layers. When exported with `docker save`, that image becomes a TAR archive containing the manifest JSON, image configuration JSON, and compressed or uncompressed layer TAR files.

Inspect the image metadata that Docker stores for the local tag.

```bash
docker image inspect tiny-webserver:1.0.0
```

Show the image layer history and the Dockerfile instructions that produced each layer.

```bash
docker history tiny-webserver:1.0.0
```

Export the local image to a TAR archive for offline inspection.

```bash
docker save tiny-webserver:1.0.0 --output tiny-webserver-1.0.0.tar
```

List the files stored inside the exported image TAR archive.

```bash
tar -tf tiny-webserver-1.0.0.tar
```

### Publish the Container

To publish the image, you first authenticate with a container registry such as [Docker Hub](https://hub.docker.com):

```bash
docker login
```

Then push the tagged image:

```bash
docker push tiny-webserver:1.0.0
```

For production use, images are typically tagged with a registry namespace:

```bash
docker tag tiny-webserver:1.0.0 {DOCKER_HUB_USER}/tiny-webserver:1.0.0
docker push {DOCKER_HUB_USER}/tiny-webserver:1.0.0
```

> Replace `{DOCKER_HUB_USER}` with your Docker Hub user name.

## Consumer Workflow

### Install the Container

Once published, the image can be downloaded from Docker Hub:

```bash
docker pull {DOCKER_HUB_USER}/tiny-webserver:1.0.0
```

> Replace `{DOCKER_HUB_USER}` with your Docker Hub user name.

To run the packaged web server, you can leverage the `run` command:

```bash
docker run -p 8080:8080 {DOCKER_HUB_USER}/tiny-webserver:1.0.0
```

> Replace `{DOCKER_HUB_USER}` with your Docker Hub user name.
