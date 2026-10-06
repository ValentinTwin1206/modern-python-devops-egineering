# Start with the Jenkins controller used for this single-container demo.
FROM jenkins/jenkins:lts-jdk21

# Install a fixed uv version so builds use the same package manager.
COPY --from=ghcr.io/astral-sh/uv:0.11.1 /uv /uvx /usr/local/bin/

# Store downloaded packages in Jenkins home, which the run command mounts as a
# volume. Keep Python outside that volume and copy packages into each fresh .venv.
ENV UV_CACHE_DIR=/var/jenkins_home/.cache/uv \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_LINK_MODE=copy

# Create writable directories for the Python installation and demo project.
USER root
RUN mkdir -p /opt/uv-python /opt/uv-cache-demo \
    && chown -R jenkins:jenkins /opt/uv-python /opt/uv-cache-demo

# Copy the locked project and enable one controller executor for this demo.
COPY --chown=jenkins:jenkins pyproject.toml uv.lock /opt/uv-cache-demo/
COPY --chown=jenkins:jenkins init.groovy /usr/share/jenkins/ref/init.groovy.d/uv-cache-demo.groovy

# Install Python as the same user that runs the Jenkins pipeline.
USER jenkins
RUN uv python install 3.12
