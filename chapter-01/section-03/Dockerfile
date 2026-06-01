# BUILD STAGE:
#   - uses python:3.12 to build the project wheel
#   - copies only metadata and source code needed for packaging
# # # # # # # # # # #
FROM python:3.12 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /build

COPY pyproject.toml ./
COPY src ./src

RUN uv build --wheel

# RUNTIME STAGE:
#   - uses continuumio/miniconda3 directly
#   - installs the wheel into a conda-managed Python 3.12 environment
# # # # # # # # # # #
FROM continuumio/miniconda3 AS runtime

ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

WORKDIR /app

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

COPY environment.yml ./

# Build the runtime conda environment from the same yml used in development.
RUN conda env create -f environment.yml \
    && conda clean --all --yes

ENV PATH=$CONDA_DIR/envs/image-processor/bin:$PATH
ENV CONDA_DEFAULT_ENV=image-processor

COPY --from=builder /build/dist /tmp/dist

# Install the project wheel into the conda environment.
RUN pip install --no-cache-dir /tmp/dist/image_processor-*.whl \
    && rm -rf /tmp/dist

ENTRYPOINT ["image-processor"]
