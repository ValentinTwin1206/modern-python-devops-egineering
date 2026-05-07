# =============================================================================
# Python 2.4 (Nov 2004) complete runtime image with setuptools.
# -----------------------------------------------------------------------------
# Builds Python 2.4 from source, installs setuptools 0.6c11, installs
# Numeric 24.0b2 (registered as a setuptools distribution so that
# `install_requires=["Numeric"]` is satisfied without contacting PyPI), and
# finally installs the sample calculator package.
# =============================================================================
FROM debian:jessie

ENV DEBIAN_FRONTEND=noninteractive

# 1. Jessie is EOL -- repos live on archive.debian.org and signatures expired.
RUN set -eux; \
    echo "deb http://archive.debian.org/debian jessie main"           >  /etc/apt/sources.list; \
    echo "deb http://archive.debian.org/debian-security jessie/updates main" >> /etc/apt/sources.list; \
    echo 'Acquire::Check-Valid-Until "false";' >  /etc/apt/apt.conf.d/99-archive; \
    echo 'Acquire::AllowInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99-archive; \
    apt-get -o Acquire::AllowInsecureRepositories=true update; \
    apt-get install -y --force-yes --no-install-recommends \
        ca-certificates \
        wget \
        build-essential \
        libreadline-dev \
        zlib1g-dev; \
    rm -rf /var/lib/apt/lists/*

# 2. Fetch Python 2.4 source.
WORKDIR /usr/src
RUN wget --no-check-certificate https://www.python.org/ftp/python/2.4/Python-2.4.tgz \
 && tar -xzf Python-2.4.tgz \
 && rm Python-2.4.tgz

WORKDIR /usr/src/Python-2.4

# 3. Patch around glibc-2.x changes that didn't exist in 2004.
RUN sed -i 's/\bgetline\b/py_getline/g' Objects/fileobject.c

# 3b. Python 2.4's setup.py doesn't search Debian's multiarch lib path,
#     so the zlib extension would silently fail to build. Force it on
#     via Modules/Setup.local instead of relying on autodetection.
RUN echo 'zlib zlibmodule.c -lz' > Modules/Setup.local

# 4. Build & install Python.
RUN set -eux; \
    CFLAGS="-w -fcommon" ./configure --prefix=/usr/local; \
    make; \
    make install

# 5. Install setuptools 0.6c11 (last release supporting Python 2.3).
WORKDIR /usr/src
RUN set -eux; \
    wget --no-check-certificate \
        https://files.pythonhosted.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz; \
    tar -xzf setuptools-0.6c11.tar.gz; \
    cd setuptools-0.6c11; \
    python setup.py install; \
    cd ..; \
    rm -rf setuptools-0.6c11 setuptools-0.6c11.tar.gz

# 6. Install Numeric 24.0. We patch its setup.py to use setuptools instead of
#    plain distutils so that an .egg-info is recorded -- otherwise pkg_resources
#    cannot see it and our own `install_requires=["Numeric"]` would try to
#    download from PyPI.
WORKDIR /usr/src
RUN set -eux; \
    wget --no-check-certificate \
        -O Numeric-24.0b2.tar.gz \
        "https://sourceforge.net/projects/numpy/files/OldFiles/Numeric-24.0b2.tar.gz/download"; \
    tar -xzf Numeric-24.0b2.tar.gz; \
    cd Numeric-24.0b2; \
    sed -i 's/from distutils.core import setup/from setuptools import setup/' setup.py; \
    CFLAGS="-w -fcommon" python setup.py install; \
    cd ..; \
    rm -rf Numeric-24.0b2 Numeric-24.0b2.tar.gz

# 7. Install the sample package. setuptools will see Numeric registered in
#    pkg_resources and consider `install_requires=["Numeric"]` satisfied.
WORKDIR /opt/historic_calculator
COPY setup.py ./
COPY src/historic_calculator ./src/historic_calculator
RUN python setup.py install

ENTRYPOINT ["/bin/bash"]

