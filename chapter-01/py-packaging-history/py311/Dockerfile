# =============================================================================
# Python 3.11 base image (2022 era).
# -----------------------------------------------------------------------------
# Project sources are copied in but no dependencies are installed -- the
# README walks through `pip install .` or `pip install .[dev]`.
# =============================================================================
FROM python:3.11

WORKDIR /opt/my_package
COPY pyproject.toml ./
COPY my_package ./my_package
COPY tests ./tests

CMD ["python", "-V"]
