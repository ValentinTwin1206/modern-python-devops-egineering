# The Ubuntu 24.04 server that Bob hands over to Alice.
#
# This image is deliberately "boring": it is the plain, freshly installed
# machine an administrator would provision, and nothing more.
#
#   * one shared system Python interpreter (python3, dev headers, pip, venv)
#   * Jupyter, so the story can be told from inside a notebook
#   * two real Linux users: bob (sudo) and alice (unprivileged)
#
# No application dependency is baked in. Every package that Bob or Alice
# needs for their projects is installed live in the notebook, because
# watching those installations collide is the whole point of the lesson.
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

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
# Create users
#
# Ubuntu 24.04 ships a placeholder "ubuntu" account on UID 1000.
# Remove it so bob and alice get the first human UIDs.
#
# Bob:
#   - administrator
#   - password: bar
#   - passwordless sudo for the demonstration
#
# Alice:
#   - unprivileged
#   - password: foo
# ----------------------------------------------------------------------
RUN if id ubuntu > /dev/null 2>&1; then userdel --remove ubuntu; fi \
    && useradd \
        --create-home \
        --shell /bin/bash \
        --groups sudo \
        bob \
    && echo 'bob:bar' | chpasswd \
    && echo 'bob ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/90-bob \
    && chmod 0440 /etc/sudoers.d/90-bob \
    && useradd \
        --create-home \
        --shell /bin/bash \
        alice \
    && echo 'alice:foo' | chpasswd

# ----------------------------------------------------------------------
# Jupyter on the shared system interpreter
#
# Ubuntu 24.04 marks its system Python as "externally managed" (PEP 668),
# so pip refuses to touch it unless --break-system-packages is given.
# The notebook keeps that flag visible on purpose; here it is needed once
# to make the machine able to run the notebook at all.
# ----------------------------------------------------------------------
RUN python3 -m pip install \
        --break-system-packages \
        --no-cache-dir \
        jupyterlab \
        notebook \
        ipykernel

# Register the system Python as a clearly named Jupyter kernel.
RUN python3 -m ipykernel install \
        --sys-prefix \
        --name system-python3 \
        --display-name "Python 3 — Ubuntu System"

# ----------------------------------------------------------------------
# Workspace
# ----------------------------------------------------------------------
RUN install -d -o bob -g bob /workspace

USER bob

WORKDIR /workspace

CMD ["/bin/bash"]
