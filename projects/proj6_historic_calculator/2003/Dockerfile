# Python 2.3 complete runtime image.
# Builds Python 2.3 from source, installs Numeric, and installs the sample
# package so the historical CLI is ready inside the container.
# # # # # # # # # # #
FROM debian:jessie

ENV DEBIAN_FRONTEND=noninteractive

# Configure archived Jessie repositories and install build dependencies.
RUN set -eux; \
    echo "deb http://archive.debian.org/debian jessie main" > /etc/apt/sources.list; \
    echo "deb http://archive.debian.org/debian-security jessie/updates main" >> /etc/apt/sources.list; \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99-archive; \
    echo 'Acquire::AllowInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99-archive; \
    apt-get -o Acquire::AllowInsecureRepositories=true update; \
    apt-get install -y --force-yes --no-install-recommends \
        ca-certificates \
        wget \
        build-essential \
        libreadline-dev \
        zlib1g-dev; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src

# Build Python 2.3 from the historical source archive.
RUN wget --no-check-certificate https://www.python.org/ftp/python/2.3/Python-2.3.tgz \
    && tar -xzf Python-2.3.tgz \
    && rm Python-2.3.tgz

WORKDIR /usr/src/Python-2.3

# Patch a modern libc name collision, then build and install Python.
RUN sed -i 's/\bgetline\b/py_getline/g' Objects/fileobject.c \
    && CFLAGS="-w -fcommon" ./configure --prefix=/usr/local \
    && make \
    && make install

WORKDIR /usr/src

# Install Numeric 24.0b2, the historical runtime dependency.
RUN set -eux; \
    wget --no-check-certificate \
        -O Numeric-24.0b2.tar.gz \
        "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"; \
    tar -xzf Numeric-24.0b2.tar.gz; \
    cd Numeric-24.0b2; \
    CFLAGS="-w -fcommon" python setup.py install; \
    cd ..; \
    rm -rf Numeric-24.0b2 Numeric-24.0b2.tar.gz

WORKDIR /opt/historic_calculator

# Install the sample package and its distutils script launcher.
COPY setup.py ./
COPY bin/hist_calc ./bin/hist_calc
COPY src/historic_calculator ./src/historic_calculator
RUN python setup.py install

ENTRYPOINT ["/bin/bash"]