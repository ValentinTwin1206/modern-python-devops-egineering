# =============================================================================
# conda example: uses the official miniconda3 image and creates a Python 3.14
# environment from environment.yml. All dependencies come from the
# conda-forge channel -- no pip step is required. The default entry point is
# a bash dev shell with the conda env already activated.
#
# Build:  docker build -t pyenv-conda .
# Dev:    docker run --rm -it -v "$PWD":/app pyenv-conda
# =============================================================================
FROM continuumio/miniconda3

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copy the environment definition into the image.
COPY environment.yml ./

# 2. Create the conda environment named `my-package` and clean up the
#    package cache to keep the image small.
RUN conda env create -f environment.yml \
    && conda clean --all --yes

# 3. Make the conda environment the default for every subsequent non-
#    interactive layer by putting its bin/ directory at the front of PATH.
ENV PATH=/opt/conda/envs/my-package/bin:$PATH
ENV CONDA_DEFAULT_ENV=my-package

# 4. Copy the project sources. The constraint for this example is
#    "conda must not use pip unless necessary", so we do not run
#    `pip install .` -- instead we expose `my_package` via PYTHONPATH.
COPY pyproject.toml ./
COPY src ./src
ENV PYTHONPATH=/app/src

# 5. Auto-activate the conda environment whenever an interactive bash shell
#    starts. This gives a real `(my-package)` prompt with `conda` available.
RUN echo 'source /opt/conda/etc/profile.d/conda.sh' >> /root/.bashrc \
    && echo 'conda activate my-package' >> /root/.bashrc \
    && echo 'cd /app' >> /root/.bashrc

# 6. Default to an interactive dev shell. Use `docker run -it` to attach.
CMD ["/bin/bash"]
