# =============================================================================
# pipenv example: installs `pipenv` into the system Python 3.14, lets it
# create the venv from Pipfile.lock for a deterministic install, and drops
# into a bash dev shell with the pipenv-managed venv already activated.
#
# Build:  docker build -t pyenv-pipenv .
# Dev:    docker run --rm -it -v "$PWD":/app pyenv-pipenv
# =============================================================================
FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Install pipenv into the system Python.
RUN pip install --no-cache-dir pipenv==2024.4.0

# 2. Copy the dependency definitions. Pipfile.lock is committed to the
#    repository so the install is fully deterministic and hash-verified.
COPY Pipfile Pipfile.lock ./

# 3. Put the venv inside the project (./.venv) and install only the locked
#    versions. `--deploy` aborts if Pipfile.lock is out of sync with Pipfile.
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install --deploy --ignore-pipfile

# 4. "Activate" the pipenv-managed venv for non-interactive layers by
#    putting its bin/ directory at the front of PATH.
ENV VIRTUAL_ENV=/app/.venv
ENV PATH=/app/.venv/bin:$PATH

# 5. Copy the project sources. We expose `my_package` via PYTHONPATH so the
#    package stays importable even when /app is bind-mounted from the host
#    for live development.
COPY pyproject.toml ./
COPY src ./src
ENV PYTHONPATH=/app/src

# 6. Auto-activate the pipenv-managed venv in interactive bash shells.
RUN echo 'source /app/.venv/bin/activate' >> /root/.bashrc \
    && echo 'cd /app' >> /root/.bashrc

# 7. Default to an interactive dev shell. Use `docker run -it` to attach.
CMD ["/bin/bash"]
