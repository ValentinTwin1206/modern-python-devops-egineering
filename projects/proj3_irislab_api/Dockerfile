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

# Install IrisLab and MediaPipe:
#   - creates a Conda environment with the exact libirislab build
#   - includes libglib for MediaPipe's PyPI OpenCV wheel
#   - installs MediaPipe and resolves its Python dependencies with pip
RUN micromamba create \
    --yes \
    --prefix /opt/conda/envs/irislab-api \
        python=3.12 \
        irislab-tools=1.0.0 \
        libglib \
        pip \
    && /opt/conda/envs/irislab-api/bin/python -m pip install \
        mediapipe==0.10.35 \
    && micromamba clean --all --yes

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

#
# Download the Falconsai NSFW classifier used by PaiGuard.
#
# The model is stored outside the Python source tree and inference runs
# locally inside the container.
#
RUN mkdir -p /opt/irislab/paiguard/falconsai-nsfw \
  && /opt/conda/bin/curl -fsSL \
    https://huggingface.co/Falconsai/nsfw_image_detection/resolve/96cb0d0342c7afb80cab76ecc58b265fa44da256/config.json \
    -o /opt/irislab/paiguard/falconsai-nsfw/config.json \
  && echo 'cd8c0a19566f199b5c64da402f1d6a9daf80d094fe6536befb060a2cc59449c2  /opt/irislab/paiguard/falconsai-nsfw/config.json' | sha256sum -c - \
  && /opt/conda/bin/curl -fsSL \
    https://huggingface.co/Falconsai/nsfw_image_detection/resolve/96cb0d0342c7afb80cab76ecc58b265fa44da256/preprocessor_config.json \
    -o /opt/irislab/paiguard/falconsai-nsfw/preprocessor_config.json \
  && echo 'a34861a24e781942424ad790b82bc99348404a2e64ea882de88c40905851698d  /opt/irislab/paiguard/falconsai-nsfw/preprocessor_config.json' | sha256sum -c - \
  && /opt/conda/bin/curl -fsSL \
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
  && /opt/conda/bin/curl -fsSL \
    https://huggingface.co/google/siglip2-base-patch16-256/resolve/3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab/config.json \
    -o /opt/irislab/paiguard/siglip2-base/config.json \
  && echo '7b5aedcb8893e31376e129c1ffd7a5392f1a806dbc793ce53eda220c2ec59edf  /opt/irislab/paiguard/siglip2-base/config.json' | sha256sum -c - \
  && /opt/conda/bin/curl -fsSL \
    https://huggingface.co/google/siglip2-base-patch16-256/resolve/3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab/preprocessor_config.json \
    -o /opt/irislab/paiguard/siglip2-base/preprocessor_config.json \
  && echo 'd14ba2ee3fd816f3de8abaddc31953565128eaf37c73ad4bed32101a98465aff  /opt/irislab/paiguard/siglip2-base/preprocessor_config.json' | sha256sum -c - \
  && /opt/conda/bin/curl -fsSL \
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
  && /opt/conda/bin/curl -fsSL \
    https://huggingface.co/khasinski/siglip2-moderation-heads/resolve/b88fe03369e3dc6aa9887cd3b4cd3e9b7cf76ee5/violence_head.onnx \
    -o /opt/irislab/paiguard/siglip2-heads/violence_head.onnx \
  && echo '268b8702e8e373ab0fea4de55250f506650ff87be532d1809ba70513bd5fa5b4  /opt/irislab/paiguard/siglip2-heads/violence_head.onnx' | sha256sum -c - \
  && /opt/conda/bin/curl -fsSL \
    https://huggingface.co/khasinski/siglip2-moderation-heads/resolve/b88fe03369e3dc6aa9887cd3b4cd3e9b7cf76ee5/violence_head.onnx.data \
    -o /opt/irislab/paiguard/siglip2-heads/violence_head.onnx.data \
  && echo '433df42d2b884d598a65f41d1cb16e2c44b60000f0f46da6b7c380f3851ce2ef  /opt/irislab/paiguard/siglip2-heads/violence_head.onnx.data' | sha256sum -c -

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
    IRISLAB_MODEL_PATH=/opt/irislab/face_landmarker.task \
    PAIGUARD_MODEL_DIR=/opt/irislab/paiguard

# Copy the runtime components from the build stage:
#   - the Conda environment
#   - the uv environment containing the installed API
#   - the Face Landmarker model
#   - the PaiGuard moderation models
COPY --from=build /opt/conda/envs/irislab-api /opt/conda/envs/irislab-api
COPY --from=build /opt/irislab-api-venv /opt/irislab-api-venv
COPY --from=build /opt/irislab/face_landmarker.task /opt/irislab/face_landmarker.task
COPY --from=build /opt/irislab/paiguard /opt/irislab/paiguard

# Run the API as the unprivileged user provided by the base image.
USER $MAMBA_USER
WORKDIR /app
EXPOSE 8080
ENTRYPOINT []
CMD ["uvicorn", "irislab_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
