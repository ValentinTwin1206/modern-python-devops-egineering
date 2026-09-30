# A small, reproducible Ubuntu environment for the uv dependency-resolution lab.
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# Copy uv from its published image so the lesson uses the real uv executable,
# without installing it into the notebook's project environment.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# ----------------------------------------------------------------------
# Base operating-system tooling
# ----------------------------------------------------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        passwd \
        procps \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        sudo \
        util-linux \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------------
# The notebook runs as "bob"
# ----------------------------------------------------------------------
RUN if id ubuntu > /dev/null 2>&1; then userdel --remove ubuntu; fi \
    && useradd \
        --create-home \
        --shell /bin/bash \
        --groups sudo \
        bob \
    && echo 'bob:bar' | chpasswd \
    && echo 'bob ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/90-bob \
    && chmod 0440 /etc/sudoers.d/90-bob

# ----------------------------------------------------------------------
# Jupyter on the system Python. The project dependencies are intentionally
# installed later by uv in the notebook, not baked into this image.
# ----------------------------------------------------------------------
RUN python3 -m pip install \
        --break-system-packages \
        --no-cache-dir \
        jupyterlab \
        notebook \
        ipykernel

RUN python3 -m ipykernel install \
        --sys-prefix \
        --name uv-resolution-python3 \
        --display-name "Python 3 - uv Dependency Resolution"

# ----------------------------------------------------------------------
# Workspace
# ----------------------------------------------------------------------
RUN install -d -o bob -g bob /workspace

USER bob

WORKDIR /workspace

CMD ["/bin/bash"]
