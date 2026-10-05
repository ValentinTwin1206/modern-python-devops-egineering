# =============================================================================
# Python 2.7 complete runtime image with pip-installed NumPy.
# -----------------------------------------------------------------------------
# Uses the official `python:2.7` image from Docker Hub, installs the pinned
# dependencies via `pip install -r requirements.txt`, and finally installs
# the sample calculator package.
# =============================================================================
FROM python:2.7

WORKDIR /opt/historic_calculator

# 1. Install pinned runtime dependencies via pip.
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 2. Install the sample package.
COPY setup.py ./
COPY src/historic_calculator ./src/historic_calculator
RUN python setup.py install

ENTRYPOINT ["/bin/bash"]

