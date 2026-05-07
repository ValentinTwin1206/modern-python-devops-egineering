# BUILD STAGE:
#   - uses python:3.12 to build the project wheel
#   - copies only metadata and source code needed for packaging
# # # # # # # # # # #
FROM python:3.12 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /build

# Copy packaging inputs before building the wheel.
COPY pyproject.toml ./
COPY src ./src

RUN uv build --wheel

# RUNTIME STAGE:
#   - uses the Miniconda base image directly
#   - installs the wheel into a conda-managed Python 3.12 environment
# # # # # # # # # # #
FROM continuumio/miniconda3 AS runtime

ENV CONDA_DIR=/opt/conda
ENV PATH=/opt/conda/bin:$PATH

WORKDIR /app

# Create the runtime conda environment with pip for wheel installation.
RUN conda create -y -n tiny-webserver python=3.12 pip \
    && conda clean --all --yes

ENV PATH=/opt/conda/envs/tiny-webserver/bin:/opt/conda/bin:$PATH
ENV CONDA_DEFAULT_ENV=tiny-webserver

COPY --from=builder /build/dist /tmp/dist

# Install the project wheel into the conda environment.
RUN pip install --no-cache-dir /tmp/dist/tiny_webserver-*.whl \
    && rm -rf /tmp/dist

EXPOSE 8080

ENTRYPOINT ["tiny-webserver"]