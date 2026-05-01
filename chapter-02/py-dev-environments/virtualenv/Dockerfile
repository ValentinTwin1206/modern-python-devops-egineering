# =============================================================================
# virtualenv example: installs the third-party `virtualenv` tool, uses it to
# create the isolated Python 3.14 environment, installs the pinned
# dependencies from requirements.txt, and drops into a bash dev shell with
# the venv already activated.
#
# Build:  docker build -t pyenv-virtualenv .
# Dev:    docker run --rm -it -v "$PWD":/app pyenv-virtualenv
# =============================================================================
FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Install the virtualenv tool itself into the system pip.
RUN pip install --no-cache-dir virtualenv==20.26.6

# 2. Create the virtual environment with virtualenv (note: NOT `python -m venv`).
RUN virtualenv /opt/venv

# 3. "Activate" the venv for every subsequent layer by putting its bin/
#    directory at the front of PATH.
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 4. Install the pinned dependencies into the venv.
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 5. Copy the project sources. We expose `my_package` via PYTHONPATH so the
#    package stays importable even when /app is bind-mounted from the host
#    for live development.
COPY pyproject.toml ./
COPY src ./src
ENV PYTHONPATH=/app/src

# 6. Auto-activate the venv whenever an interactive bash shell starts.
RUN echo 'source /opt/venv/bin/activate' >> /root/.bashrc \
    && echo 'cd /app' >> /root/.bashrc

# 7. Default to an interactive dev shell. Use `docker run -it` to attach.
CMD ["/bin/bash"]
