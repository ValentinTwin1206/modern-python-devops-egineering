# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - installs CPython, uv, and the Cloudsmith CLI
#   - receives the Docker CLI and host socket access from the
#     docker-outside-of-docker Feature declared in devcontainer.json
#   - runs editor terminals and lifecycle commands as vscode
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Scoped to the build so the setting does not leak into the running container.
ARG DEBIAN_FRONTEND=noninteractive

# Put user-level tools installed by uv on PATH and keep the Cloudsmith target explicit.
ENV PATH="/home/vscode/.local/bin:${PATH}" \
    CLOUDSMITH_REPOSITORY=""

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install the Python runtime and source-build tools used by the project workflow.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Keep the final image user aligned with devcontainer.json.
USER vscode

# Install publication tooling as the same account VS Code uses.
RUN uv tool install cloudsmith-cli

WORKDIR /workspaces/proj3_tiny_webserver