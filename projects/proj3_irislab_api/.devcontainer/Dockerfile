# DEVELOPMENT IMAGE:
#   - uses the Ubuntu 24.04 Dev Containers base image
#   - uses the same micromamba and uv versions as the production image
#   - installs IrisLab, MediaPipe, and the model used by the IrisLab API
#   - runs editor terminals and lifecycle commands as bob
# # # # # # # # # # #
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# The public channel URL contains no credentials.
ARG IRISLAB_CHANNEL

USER root

# Use the same micromamba and uv versions as the production image.
COPY --from=mambaorg/micromamba:2.3.3 /bin/micromamba /usr/local/bin/micromamba
COPY --from=ghcr.io/astral-sh/uv:0.11.1 /uv /uvx /usr/local/bin/

# Configure micromamba, uv, and the application runtime:
#   - use the same Conda prefix and native library path as production
#   - use Conda's Python instead of downloading another interpreter
#   - leave uv's project environment at the workspace's .venv
ENV CONDA_DIR=/opt/conda \
    MAMBA_ROOT_PREFIX=/opt/conda \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    LD_LIBRARY_PATH=/opt/conda/envs/irislab-api/lib \
    IRISLAB_MODEL_PATH=/opt/irislab/face_landmarker.task \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Put Conda and user-level tools installed by uv on PATH.
ENV PATH="/home/bob/.local/bin:${CONDA_DIR}/bin:${PATH}"

# Configure the same strict channel priority as the production build.
RUN if [ -z "${IRISLAB_CHANNEL}" ]; then \
        echo 'Set IRISLAB_CHANNEL to the public Conda channel containing irislab-tools and libirislab.' >&2; \
        exit 1; \
    fi \
    && micromamba config prepend channels conda-forge \
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

# The Conda recipe does not include MediaPipe; install it from PyPI.
RUN /opt/conda/envs/irislab-api/bin/python -m pip install \
        mediapipe==0.10.35

# Download and verify the Face Landmarker model used for local inference.
RUN mkdir -p /opt/irislab \
    && curl -fsSL \
        https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task \
        -o /opt/irislab/face_landmarker.task \
    && echo '64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff  /opt/irislab/face_landmarker.task' \
        | sha256sum -c -

# Rename the base image's development user while retaining its UID/GID.
# Its existing sudoers entry names vscode, so grant bob sudo access explicitly.
RUN usermod --login bob --home /home/bob --move-home vscode \
    && groupmod --new-name bob vscode \
    && echo 'bob:c3po' | chpasswd \
    && printf 'bob ALL=(root) NOPASSWD:ALL\n' > /etc/sudoers.d/bob \
    && chmod 0440 /etc/sudoers.d/bob
