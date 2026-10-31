# 
# BUILD STAGE
# # # # # #
FROM mambaorg/micromamba:2.3.3 AS build

ARG IRISLAB_CHANNEL
USER root

# uv installs the API; pip supplies MediaPipe, which is not in the recipe.
COPY --from=ghcr.io/astral-sh/uv:0.11.1 /uv /usr/local/bin/uv

# Configure channel priority just as in the Chapter 02 consumer workflow.
# The channel URL is public and must not contain credentials.
RUN micromamba config prepend channels conda-forge \
    && micromamba config prepend channels "${IRISLAB_CHANNEL}" \
    && micromamba config set channel_priority strict

# Install IrisLab and its declared runtime dependencies, including the exact
# libirislab build. libglib is required by MediaPipe's PyPI OpenCV wheel.
RUN micromamba create \
    --yes \
    --prefix /opt/conda/envs/irislab-api \
        python=3.12 \
        irislab-tools=1.0.0 \
        libglib \
        pip \
    && micromamba clean --all --yes

# The Conda recipe does not depend on MediaPipe, which is distributed on PyPI.
# Let pip resolve its Python dependencies, as in the consumer workflow.
RUN /opt/conda/envs/irislab-api/bin/python -m pip install \
        mediapipe==0.10.35

# Install curl via conda:
#   - adds curl to the build stage's base Conda environment
#   - downloads and verifies the Face Landmarker model for the runtime image
RUN micromamba install \
    --yes \
    --name base \
    --channel conda-forge curl \
    && micromamba clean --all --yes

#
# Download the MediaPipe Face Landmarker model used by iris.py.
#
# The model is stored outside the Python source tree and inference runs
# locally inside the container.
#
RUN mkdir -p /opt/irislab \
    && /opt/conda/bin/curl -fsSL \
        https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task \
        -o /opt/irislab/face_landmarker.task \
    && echo '64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff  /opt/irislab/face_landmarker.task' | sha256sum -c -

# Use /app as the project directory so later relative paths, such as src, resolve
# from this location.
WORKDIR /app

# Configure uv:
#   - keeps uv-managed packages separate from Conda
#   - uses Conda's Python instead of downloading another interpreter
#   - copies packages into the environment
ENV UV_PROJECT_ENVIRONMENT=/opt/irislab-api-venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY src ./src

# Create the uv environment with Conda's Python:
#   - uses Conda's interpreter instead of downloading another Python
#   - exposes Conda-installed packages, including IrisLab and MediaPipe
RUN uv venv --python /opt/conda/envs/irislab-api/bin/python \
    --system-site-packages "${UV_PROJECT_ENVIRONMENT}"

# Install 'irislab-api':
#   - installs the production dependencies recorded in uv.lock
#   - leaves the lockfile unchanged and skips development dependencies
#   - checks that installed package requirements are compatible
RUN uv sync \
    --locked \
    --no-dev \
    --no-editable \
    && /opt/irislab-api-venv/bin/python -m pip check

#
# RUNTIME STAGE
# # # # # #
FROM mambaorg/micromamba:2.3.3 AS runtime

# Root is needed to copy the environment and model into system-owned paths.
USER root

# Use the prepared Conda environment and configure the application runtime.
ENV PATH="/opt/irislab-api-venv/bin:/opt/conda/envs/irislab-api/bin:${PATH}" \
    LD_LIBRARY_PATH=/opt/conda/envs/irislab-api/lib \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    IRISLAB_MODEL_PATH=/opt/irislab/face_landmarker.task

# Copy the runtime components from the build stage:
#   - the Conda environment
#   - the uv environment containing the installed API
#   - the Face Landmarker model
COPY --from=build /opt/conda/envs/irislab-api /opt/conda/envs/irislab-api
COPY --from=build /opt/irislab-api-venv /opt/irislab-api-venv
COPY --from=build /opt/irislab/face_landmarker.task /opt/irislab/face_landmarker.task

# Run the API as the unprivileged user provided by the base image.
USER $MAMBA_USER
WORKDIR /app
EXPOSE 8080
ENTRYPOINT []
CMD ["uvicorn", "irislab_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
