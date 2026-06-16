# Python Containers

Python containers package an application together with the runtime files it needs to run. They help teams deploy the same application image across local machines, CI pipelines, and production platforms.

## Applied Project

### Project Setup

The applied project is a small utility library called `Docslug Project`. It turns headings and file names into stable slugs without any runtime dependencies beyond the Python standard library. This makes it a good fit for `venv` because a pure-Python library shows clearly how one project-local environment can isolate build and development tools while keeping the installed package itself lightweight.

### Run the Project

Application, test, lint, and shell-exit commands are documented in the [section README](https://github.com/ValentinTwin1206/modern-python-devops-egineering/blob/main/projects/proj1_docslug/README.md).

## Distribution Fundamentals

### Overview

A Python container distribution packages an application and its full runtime environment into a portable *Open Container Initiative (OCI)* image. Instead of distributing only source code or binaries, it bundles the Python interpreter, application code, system dependencies (such as Linux libraries), required Python packages, and runtime configuration into a **single self-contained unit** that can run on any OCI-compliant runtime without relying on the host system’s Python or environment setup.

- ✅ Backend APIs (FastAPI, Django, Flask)
- ✅ Microservices
- ✅ Data pipelines
- ✅ Cloud-based production deployments

### Container Ecosystem

Due to the Open Container Initiative (OCI) standard, container images are portable and can be built, run, and managed interchangeably across different tools in the ecosystem. While Docker is the most widely used container manager, there are many other compatible solutions that serve different roles in building, running, and operating containers.

|    Tool    | Description |
|------------|-------------|
| *Buildah*    | Specialized tool for building OCI container images without requiring a full container runtime |
| *Docker*     | Most widely used container engine and CLI tool |
| *Kubernetes* | Container orchestration system for deploying, scaling, and managing containers in production |
| *Podman*     | Daemonless, rootless OCI-compatible container engine (Docker alternative) |
| *Skopeo*     | Tool for inspecting, copying, and managing container images across registries without running containers |

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

### Package Layout

The result of a container build is an ***OCI-compliant*** container image. Unlike wheels or source distributions, a container image is not typically represented as a single file inside the project directory. Instead, it is stored internally by the container runtime as a collection of immutable filesystem layers and associated metadata.

These layers together encapsulate the complete application environment, including the installed Python package or wheel, runtime dependencies, operating-system libraries, configuration, and execution entry point.

Container images are identified by a repository name and tag:

```text
tiny-webserver:1.0.0
```

- `tiny-webserver`: Image name or repository.
- `1.0.0`: Image tag, typically representing a version.

Container images can be published to container registries such as Docker Hub, GitHub Container Registry (GHCR), Amazon ECR, or other OCI-compatible registries, where they can be downloaded and executed on any compatible container runtime.

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
