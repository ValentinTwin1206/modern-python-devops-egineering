# =============================================================================
# venv example: uses the standard-library `venv` module to create an isolated
# Python 3.14 environment, installs the pinned dependencies from
# requirements.txt into it, and drops into a bash dev shell with the venv
# already activated.
#
# Build:  docker build -t pyenv-venv .
# Dev:    docker run --rm -it -v "$PWD":/app pyenv-venv
# =============================================================================
FROM python:3.14-slim

# Bash + a minimal toolchain for any source builds inside the dev shell.
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Create the virtual environment with the stdlib `venv` module.
RUN python -m venv /opt/venv

# 2. "Activate" the venv for every subsequent layer by putting its bin/
#    directory at the front of PATH. This is the Docker-friendly equivalent
#    of `source /opt/venv/bin/activate`.
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 3. Install the pinned dependencies into the venv.
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 4. Copy the project sources. We expose `my_package` via PYTHONPATH so the
#    package stays importable even when /app is bind-mounted from the host
#    for live development.
COPY pyproject.toml ./
COPY src ./src
ENV PYTHONPATH=/app/src

# 5. Auto-activate the venv whenever an interactive bash shell starts.
RUN echo 'source /opt/venv/bin/activate' >> /root/.bashrc \
    && echo 'cd /app' >> /root/.bashrc

# 6. Default to an interactive dev shell. Use `docker run -it` to attach.
#    Override with e.g. `docker run --rm pyenv-venv python -m my_package.main`.
CMD ["/bin/bash"]
