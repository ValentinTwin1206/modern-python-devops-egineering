# uv Cache Demo (ML Dependencies)

This project declares `tensorflow-cpu`, `transformers`, and `scikit-learn` in
`pyproject.toml`. The committed `uv.lock` pins their resolved dependencies.
Both the [GitHub Actions workflow](../../.github/workflows/uv-cache.yml) and
the [Jenkins pipeline](./Jenkinsfile) install them with uv. Neither example
downloads models or needs a GPU.

## Run Locally

With Python 3.12 and uv installed, run this from the project directory to
install exactly the locked dependencies:

```shell
uv sync --locked --python 3.12
```

Check that the ML packages can be imported:

```shell
.venv/bin/python -c "import tensorflow, transformers, sklearn; print('ML packages imported successfully')"
```

## Start the Development Container

The [Dockerfile.devEnv](./Dockerfile.devEnv) uses the official Jenkins image,
which already includes Bash. It adds uv 0.11.1, Python 3.12, `tree`, and a
`bob` user with passwordless sudo for this teaching environment. The default
command opens Bash rather than starting Jenkins.

From the repository's `projects/` directory, build the image and open the shell
with [build.sh](../build.sh). The script matches bob's UID/GID to your host user
and bind-mounts this project at `/app`:

```bash
./build.sh build --path proj5_uv_cache/Dockerfile.devEnv --rm-container
```

If the image already exists, open it with the same project and build-artifact
mounts:

```bash
docker run --rm -it -v "$PWD/proj5_uv_cache:/app" -v "$PWD/proj5_uv_cache/.build:/opt/conda/conda-bld" -p 8080:8080 mpe/proj5_uv_cache /bin/bash
```

Both commands open Bash as `bob` in `/app`. The image sets `UV_CACHE_DIR` to
`/var/jenkins_home/.cache/uv` and keeps Python in `/opt/uv-python`. Packages
are copied into each environment, so cleaning the cache does not remove
installed packages. Changes under `/app`, including `.venv`, affect the
host project; the package cache is separate from your host's uv cache.

Follow [The Cache Workflow](../../docs/chapter-03/section-03.md#the-cache-workflow)
to inspect the cache, reinstall offline, and clear cached packages. The
development container does not use the persistent named Jenkins volume below.

## Run the Jenkins Demo in Docker

From the repository's `projects/` directory, build the same image without
opening the development shell:

```bash
./build.sh build --path proj5_uv_cache/Dockerfile.devEnv --build-only
```

Start Jenkins at `http://localhost:8080`. The named volume retains Jenkins
settings and uv's package cache across container restarts or recreation.
Passing `/usr/local/bin/jenkins.sh` overrides the default Bash command:

```bash
docker run -d --name uv-cache-jenkins -p 127.0.0.1:8080:8080 -v uv-cache-jenkins-home:/var/jenkins_home mpe/proj5_uv_cache /usr/local/bin/jenkins.sh
```

Read the initial admin password from the volume:

```shell
docker exec uv-cache-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open `http://localhost:8080`, unlock Jenkins, install the suggested plugins,
and create an admin account. Select **New Item → Pipeline**, give it a name,
and under **Pipeline → Definition** choose **Pipeline script**. Paste the
contents of [`Jenkinsfile`](./Jenkinsfile) into the editor and save. Click
**Build Now** twice; compare the console logs. The pipeline deletes `.venv`
before each build but reuses `UV_CACHE_DIR` at
`/var/jenkins_home/.cache/uv`. Large ML wheels can take time on the first run.
This is a single-node demonstration: the pipeline runs on the Jenkins
controller as `bob` inside the container, which has uv and Python installed.
The pipeline uses the locked project copied to `/opt/uv-cache-demo`, not the
development bind mount at `/app`.

Use a fresh named volume for this example. If you reuse a volume created by
an older image with a different UID/GID, adjust its ownership before starting
Jenkins; do not delete existing Jenkins data to fix permissions.

To stop the container without deleting its cache, run:

```shell
docker stop uv-cache-jenkins
```

To restart it with the same named volume, run:

```shell
docker start uv-cache-jenkins
```

For the GitHub Actions cache comparison and an explanation of both CI examples,
see [Dependency Caching with uv](../../docs/chapter-03/section-03.md#using-uv-cache-in-cicd-environments).
