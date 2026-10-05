# =============================================================================
# Python 1.6 (Sep 2000) complete runtime image
# -----------------------------------------------------------------------------
# Builds Python 1.6 from source, installs Numerical 15.3, and installs the
# sample calculator package so the CLI is ready to use immediately.
# =============================================================================
FROM debian:jessie

ENV DEBIAN_FRONTEND=noninteractive

# 1. Jessie is EOL — repos live on archive.debian.org and signatures expired.
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

# 2. Fetch Python 1.6 source from python.org's FTP archive.
WORKDIR /usr/src
RUN wget --no-check-certificate https://www.python.org/ftp/python/src/python-1.6.tar.gz \
 && tar -xzf python-1.6.tar.gz \
 && rm python-1.6.tar.gz

WORKDIR /usr/src/Python-1.6

# 3. Patch around glibc-2.x changes that didn't exist in 2000:
#    `getline` is now a libc function, so Python's same-named static collides.
RUN sed -i 's/\bgetline\b/py_getline/g' Objects/fileobject.c

# 4. Build & install.
#    -w silences a wall of warnings; -fcommon restores pre-GCC10 tentative-
#    definition behaviour that several Python 1.6 modules rely on.
RUN set -eux; \
    CFLAGS="-w -fcommon" ./configure --prefix=/usr/local; \
    make; \
    make install

# 5. Install Numerical 15.3.
WORKDIR /usr/src
RUN set -eux; \
    wget --no-check-certificate \
        -O Numerical-15.3.tgz \
        "https://sourceforge.net/projects/numpy/files/OldFiles/Numerical-15.3.tgz/download"; \
    tar -xzf Numerical-15.3.tgz; \
    cd Numerical-15.3; \
    CFLAGS="-w -fcommon" python setup.py install; \
    cd ..; \
    rm -rf Numerical-15.3 Numerical-15.3.tgz

# 6. Install the sample package.
WORKDIR /opt/historic_calculator
COPY setup.py ./
COPY bin/hist_calc ./bin/hist_calc
COPY src/historic_calculator ./src/historic_calculator
RUN python setup.py install

ENTRYPOINT ["/bin/bash"]
