# =============================================================================
# Python 2.3 (Jul 2003) build environment
# -----------------------------------------------------------------------------
# Inspired by https://www.bitecode.dev/p/lets-compile-python-10
#
# Python 2.3 ships `distutils` in the stdlib (introduced in 1.6), so no
# extra distutils install step is needed.
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

# 2. Fetch Python 2.3 source from python.org's FTP archive.
WORKDIR /usr/src
RUN wget --no-check-certificate https://www.python.org/ftp/python/2.3/Python-2.3.tgz \
 && tar -xzf Python-2.3.tgz \
 && rm Python-2.3.tgz

WORKDIR /usr/src/Python-2.3

# 3. Patch around glibc-2.x changes that didn't exist in 2000:
#    `getline` is now a libc function, so Python's same-named static collides.
RUN sed -i 's/\bgetline\b/py_getline/g' Objects/fileobject.c

# 4. Build & install.
#    -w silences a wall of warnings; -fcommon restores pre-GCC10 tentative-
#    definition behaviour that several Python 2.3 modules rely on.
RUN set -eux; \
    CFLAGS="-w -fcommon" ./configure --prefix=/usr/local; \
    make; \
    make install

# 5. Copy the example project into the image.
#
#    Note: this image deliberately does NOT install Numeric, nor does it
#    run `python setup.py install` for the example package. The README
#    documents both as separate manual steps, mirroring how a user in
#    2003 would have done it.
#
#    jessie's glibc is too old to be supported by the devcontainers CLI's
#    Node.js runtime, so postCreateCommand.sh cannot execute reliably
#    in this image.
WORKDIR /opt/historic_calculator
COPY setup.py ./
COPY historic_calculator ./historic_calculator

CMD ["python", "-V"]
