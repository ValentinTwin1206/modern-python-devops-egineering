# Tiny Webserver

This section introduces *Tiny Webserver* as a small Bottle-based HTTP server that demonstrates how a Python project can use a Dev Container with Docker outside of Docker (DooD), `uv`, and a deployment container image published to Cloudsmith.

## Project Components

The table below lists the main files that support the Dev Container and container-image example project.

| Component | Description |
| --------- | ----------- |
| [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) | This file is the entry point for the Dev Container setup. It enables the `docker-outside-of-docker` Feature, passes Cloudsmith configuration into the container, and runs the dependency sync after creation. |
| [.devcontainer/Dockerfile](.devcontainer/Dockerfile) | This development image builds the environment that VS Code opens. It installs Python, `uv`, and the Cloudsmith CLI, while the Docker CLI itself is contributed by the Feature. |
| [Dockerfile](Dockerfile) | This deployment image builds the project wheel, installs it into a runtime virtual environment, exposes port 8080, and starts the `tiny-webserver` console script. |
| [pyproject.toml](pyproject.toml) | This file defines the project metadata, runtime dependency on Bottle, and development tools that `uv sync --group dev` installs inside the Dev Container. |

## End-User Guide

This section shows how an end user installs and runs `tiny-webserver` as a container image published to Cloudsmith.

### Requirements

- Docker or Podman.
- Access to the Cloudsmith repository that publishes the image.

### Installation

Set `CLOUDSMITH_REPOSITORY` to the Cloudsmith owner and repository path, such as `example-org/python-containers`. Do not include the registry host or image name in this value.

```bash
export CLOUDSMITH_REPOSITORY="<owner>/<repository>"
```

Download the `tiny-webserver` image from Cloudsmith:

```bash
docker pull "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/tiny-webserver:latest"
```

### Usage

Run the container detached and give it a name so you can manage it explicitly:

```bash
docker run -d --rm --name tiny-webserver -p 8080:8080 "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/tiny-webserver:latest"
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

The project workflow runs inside the Dev Container image because the container includes the Python tooling and the Cloudsmith CLI. Docker outside of Docker (DooD) keeps image builds on the host Docker daemon while the development commands still run inside the container.

DooD is provided by the official [`docker-outside-of-docker`](https://github.com/devcontainers/features/tree/main/src/docker-outside-of-docker) Dev Container Feature. The Feature installs the Docker CLI, mounts the host Docker socket, and aligns socket permissions when the container starts, so no manual group or socket configuration is needed on the host.

> **Security note:** Access to the host Docker socket is equivalent to root access on the host. Only use this Dev Container with sources you trust.

### Setup Environment

Install the Dev Container CLI on the host if you want to build and enter the same environment outside VS Code:

```bash
sudo apt-get update && sudo apt-get install -y nodejs npm
```

Next, install the Dev Container CLI via `npm`:

```bash
sudo npm install -g @devcontainers/cli
```

Set `CLOUDSMITH_REPOSITORY` to the Cloudsmith owner and repository path that will receive the published image:

```bash
export CLOUDSMITH_REPOSITORY="<owner>/<repository>"
```

From the project directory, start the Dev Container workspace:

```bash
devcontainer up --workspace-folder .
```

Open an interactive shell in that container:

```bash
devcontainer exec --workspace-folder . bash
```

Confirm that the container can reach the host Docker daemon:

```bash
docker version
```

### Sync Environment

The Dev Container runs `uv sync --group dev` automatically through `postCreateCommand`. If you change dependencies later, resync them manually inside the container:

```bash
uv sync --group dev
```

### Run Tests

Within the running container, you can run the test suite with Karva:

```bash
PYTHONPATH=src uv run karva test tests/
```

### Lint

Within the running container, you can run Ruff against the source tree:

```bash
uv run ruff check .
```

### Build Guide

Run the build commands below from a shell opened with `devcontainer exec --workspace-folder . bash`. Files written inside the project directory remain available on the host because the workspace is bind-mounted into the Dev Container.

Build the project wheel:

```bash
uv build --wheel
```

Build the final `tiny-webserver` container image through the host Docker daemon:

```bash
docker build --file Dockerfile --tag tiny-webserver:latest .
```

> Because the daemon runs on the host, any `-v` path you pass to `docker run` is resolved on the host rather than inside the container. Use the `LOCAL_WORKSPACE_FOLDER` variable, which the Dev Container sets to the host path of this project, when a container needs to mount workspace files.

Tag the local image for the configured Cloudsmith Docker registry path:

```bash
docker tag tiny-webserver:latest "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/tiny-webserver:latest"
```

Log in to Cloudsmith's Docker registry from the same shell:

```bash
docker login docker.cloudsmith.io
```

Upload the image to Cloudsmith:

```bash
docker push "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/tiny-webserver:latest"
```

List the package in Cloudsmith after the upload finishes:

```bash
cloudsmith list packages "${CLOUDSMITH_REPOSITORY}" -q "tiny-webserver"
```
