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
    PAIGUARD_MODEL_DIR=/opt/irislab/paiguard \
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
        irislab-tools=0.0.1 \
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

#
# Download the Falconsai NSFW classifier used by PaiGuard.
#
# The model is stored outside the Python source tree and inference runs
# locally inside the container.
#
RUN mkdir -p /opt/irislab/paiguard/falconsai-nsfw \
  && curl -fsSL \
    https://huggingface.co/Falconsai/nsfw_image_detection/resolve/96cb0d0342c7afb80cab76ecc58b265fa44da256/config.json \
    -o /opt/irislab/paiguard/falconsai-nsfw/config.json \
  && echo 'cd8c0a19566f199b5c64da402f1d6a9daf80d094fe6536befb060a2cc59449c2  /opt/irislab/paiguard/falconsai-nsfw/config.json' | sha256sum -c - \
  && curl -fsSL \
    https://huggingface.co/Falconsai/nsfw_image_detection/resolve/96cb0d0342c7afb80cab76ecc58b265fa44da256/preprocessor_config.json \
    -o /opt/irislab/paiguard/falconsai-nsfw/preprocessor_config.json \
  && echo 'a34861a24e781942424ad790b82bc99348404a2e64ea882de88c40905851698d  /opt/irislab/paiguard/falconsai-nsfw/preprocessor_config.json' | sha256sum -c - \
  && curl -fsSL \
    https://huggingface.co/Falconsai/nsfw_image_detection/resolve/96cb0d0342c7afb80cab76ecc58b265fa44da256/model.safetensors \
    -o /opt/irislab/paiguard/falconsai-nsfw/model.safetensors \
  && echo '97b2ce64ec146884b37f98ee7944ca4891aa72f6827dc0cb10684a1cbecd5830  /opt/irislab/paiguard/falconsai-nsfw/model.safetensors' | sha256sum -c -

#
# Download the SigLIP2 image encoder used by PaiGuard.
#
# The model is stored outside the Python source tree and inference runs
# locally inside the container.
#
RUN mkdir -p /opt/irislab/paiguard/siglip2-base \
  && curl -fsSL \
    https://huggingface.co/google/siglip2-base-patch16-256/resolve/3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab/config.json \
    -o /opt/irislab/paiguard/siglip2-base/config.json \
  && echo '7b5aedcb8893e31376e129c1ffd7a5392f1a806dbc793ce53eda220c2ec59edf  /opt/irislab/paiguard/siglip2-base/config.json' | sha256sum -c - \
  && curl -fsSL \
    https://huggingface.co/google/siglip2-base-patch16-256/resolve/3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab/preprocessor_config.json \
    -o /opt/irislab/paiguard/siglip2-base/preprocessor_config.json \
  && echo 'd14ba2ee3fd816f3de8abaddc31953565128eaf37c73ad4bed32101a98465aff  /opt/irislab/paiguard/siglip2-base/preprocessor_config.json' | sha256sum -c - \
  && curl -fsSL \
    https://huggingface.co/google/siglip2-base-patch16-256/resolve/3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab/model.safetensors \
    -o /opt/irislab/paiguard/siglip2-base/model.safetensors \
  && echo '6125cacc01fa93bdc98a0c5101cefcd69b2ed1f8ab4f38d86f4ad5984f5dc863  /opt/irislab/paiguard/siglip2-base/model.safetensors' | sha256sum -c -

#
# Download the SigLIP2 violence head used by PaiGuard.
#
# The model is stored outside the Python source tree and inference runs
# locally inside the container.
#
RUN mkdir -p /opt/irislab/paiguard/siglip2-heads \
  && curl -fsSL \
    https://huggingface.co/khasinski/siglip2-moderation-heads/resolve/b88fe03369e3dc6aa9887cd3b4cd3e9b7cf76ee5/violence_head.onnx \
    -o /opt/irislab/paiguard/siglip2-heads/violence_head.onnx \
  && echo '268b8702e8e373ab0fea4de55250f506650ff87be532d1809ba70513bd5fa5b4  /opt/irislab/paiguard/siglip2-heads/violence_head.onnx' | sha256sum -c - \
  && curl -fsSL \
    https://huggingface.co/khasinski/siglip2-moderation-heads/resolve/b88fe03369e3dc6aa9887cd3b4cd3e9b7cf76ee5/violence_head.onnx.data \
    -o /opt/irislab/paiguard/siglip2-heads/violence_head.onnx.data \
  && echo '433df42d2b884d598a65f41d1cb16e2c44b60000f0f46da6b7c380f3851ce2ef  /opt/irislab/paiguard/siglip2-heads/violence_head.onnx.data' | sha256sum -c -

# Rename the base image's development user while retaining its UID/GID.
# Its existing sudoers entry names vscode, so grant bob sudo access explicitly.
RUN usermod --login bob --home /home/bob --move-home vscode \
    && groupmod --new-name bob vscode \
    && echo 'bob:c3po' | chpasswd \
    && printf 'bob ALL=(root) NOPASSWD:ALL\n' > /etc/sudoers.d/bob \
    && chmod 0440 /etc/sudoers.d/bob
