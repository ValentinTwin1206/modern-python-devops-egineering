FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN if id ubuntu >/dev/null 2>&1; then userdel --remove ubuntu; fi \
    && useradd --create-home --shell /bin/bash bob

RUN python3 -m venv /opt/jupyter \
    && /opt/jupyter/bin/python -m pip install --no-cache-dir jupyterlab ipykernel \
    && /opt/jupyter/bin/python -m ipykernel install --prefix /usr/local --name venv-lab-python3 \
       --display-name "Python 3 - venv Lab"

RUN install -d -o bob -g bob /workspace
USER bob
WORKDIR /workspace
CMD ["/bin/bash"]
