FROM ubuntu:24.04

ARG HOST_UID=1000
ARG HOST_GID=1000
ARG DEBIAN_FRONTEND=noninteractive

# Install operating-system tools.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        sudo \
        tree \
    && rm -rf /var/lib/apt/lists/*

# Install uv independently of the project environment.
COPY --from=ghcr.io/astral-sh/uv:0.13.3 /uv /uvx /usr/local/bin/

# Create the lab user with configurable host IDs.
RUN existing_user="$(getent passwd "${HOST_UID}" | cut -d: -f1)" \
    && if [ -n "${existing_user}" ]; then userdel "${existing_user}"; fi \
    && group_name="$(getent group "${HOST_GID}" | cut -d: -f1)" \
    && if [ -z "${group_name}" ]; then \
        groupadd --gid "${HOST_GID}" bob; \
        group_name=bob; \
    fi \
    && useradd --uid "${HOST_UID}" --gid "${group_name}" \
        --create-home --shell /bin/bash --groups sudo bob \
    && printf 'bob ALL=(ALL) NOPASSWD:ALL\n' > /etc/sudoers.d/bob \
    && chmod 0440 /etc/sudoers.d/bob \
    && mkdir -p /workspace /opt/uv-python /home/bob/scipy-demo \
    && chown -R bob:"${HOST_GID}" /workspace /opt/uv-python /home/bob/scipy-demo

# Install Jupyter on the system Python.
RUN python3 -m pip install --break-system-packages --no-cache-dir jupyterlab ipykernel \
    && python3 -m ipykernel install --sys-prefix \
        --name uv-cache-python3 --display-name "Python 3 - uv Cache Lab"

# Keep Python outside the disposable cache and use copy-mode installations.
ENV UV_CACHE_DIR=/home/bob/.cache/uv \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_LINK_MODE=copy \
    PATH=/home/bob/.local/bin:$PATH \
    HOME=/home/bob \
    USER=bob

# Use the prepared workspace and install the lab's Python as Bob.
USER bob
WORKDIR /workspace

RUN uv python install 3.12 --default

CMD ["/bin/bash"]
