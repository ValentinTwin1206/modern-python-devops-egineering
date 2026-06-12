# Tiny Webserver

This section introduces *Tiny Webserver* project as a simple Python-based web server that demonstrates how to use Python's standard-library `venv` environment to isolate dependencies inside a project-local directory, and how the same web server can be packaged and distributed as a Linux container image.

## Project Components

The table below lists the main files that support the `venv` example project.

| Component | Description |
| --------- | ----------- |
| [Dockerfile.devEnv](Dockerfile.devEnv) | This development image creates and activates a virtual environment at `/opt/venv`. It gives you a reproducible example of how the project and its tools are installed into an isolated interpreter. |
| [Dockerfile](Dockerfile) | This deployment image builds the project wheel and installs it into the same virtual-environment layout. It shows how the `venv` pattern carries from interactive development into container deployment. |
| [pyproject.toml](pyproject.toml) | This file defines the package metadata and dependencies for the example project. Those dependencies are what get installed into the virtual environment during the workflow shown below. |

## End-User Guide

This section shows how an end user installs and runs `tiny-webserver` as a published container image.

### Requirements

- Docker or Podman.

### Installation

Download the `tiny-webserver` image from Docker Hub:

```bash
docker pull {DOCKER_HUB_REPOSITORY}/tiny-webserver:latest
```

> Use `{DOCKER_HUB_REPOSITORY}` for the Docker Hub repository that publishes `tiny-webserver`.

### Uninstallation

Remove the package again when you are done experimenting:

```bash
docker rmi {DOCKER_HUB_REPOSITORY}/tiny-webserver:latest
```

> Use `{DOCKER_HUB_REPOSITORY}` for the Docker Hub repository that publishes `tiny-webserver`.

### Usage

Run the container detached and give it a name so you can manage it explicitly:

```bash
docker run -d --rm --name tiny-webserver -p 8080:8080 {DOCKER_HUB_REPOSITORY}/tiny-webserver:latest
```

Send a request from another terminal:

```bash
curl http://localhost:8080
```

Stop the detached container when you are done:

```bash
docker stop tiny-webserver
```

## Developer Guide

### Setup Environment

The [Dockerfile.devEnv](Dockerfile.devEnv) uses *Docker outside of Docker (DooD)* so you can build the deployment image from inside the development container through the host Docker daemon. It contains all required development tools, and build artifacts are stored on the host in `.build/`:

```bash
./build.sh build --path proj3_tiny_webserver/Dockerfile.devEnv -- \
	--group-add "$(stat -c '%g' /var/run/docker.sock)" \
	--volume /var/run/docker.sock:/var/run/docker.sock
```

This mounts the host Docker socket into the container and adds the socket's group ID so the Docker CLI inside the container can talk to the host daemon without `--privileged`.

### Sync Environment

Within the running container, you can sync the project environment with `uv`:

```bash
uv sync --all-groups
```

Then source the virtual environment so the installed tools are on `PATH`:

```bash
source .venv/bin/activate
```

### Run Tests

Within the running container, you can run the test suite with Karva:

```bash
karva test tests/
```

### Lint

Within the running container, you can run Ruff against the source tree:

```bash
ruff check .
```

### Build Guide

The deployment image in [Dockerfile](Dockerfile) is a two-stage build: it produces the project wheel with `uv build --wheel`, installs it into a virtual environment at `/opt/venv`, and starts the `tiny-webserver` console script on port 8080. Run the commands below from the project directory, on the host or from inside the [development image](#setup-environment) .

#### Build the Wheel

Inside the development image, run following command to build the wheel:

```bash
uv build --wheel
```

#### Build the Container Image

Inside the development image, run following command to build the final `tiny-webserver` container:

```bash
docker build --file Dockerfile --tag tiny-webserver .
```

#### Upload the Container Image

Tag the local image for your Docker Hub repository:

```bash
docker tag tiny-webserver:latest {DOCKER_HUB_REPOSITORY}/tiny-webserver:latest
```

Log in to Docker Hub from the same shell:

```bash
docker login
```

Push the image to Docker Hub:

```bash
docker push {DOCKER_HUB_REPOSITORY}/tiny-webserver:latest
```
