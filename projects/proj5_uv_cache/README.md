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

## Run the Jenkins Demo in Docker

From the **repository root**, build a Jenkins controller with uv, Python 3.12,
and the committed dependency files. Docker is required:

```shell
docker build -t uv-cache-jenkins -f projects/proj5_uv_cache/Dockerfile projects/proj5_uv_cache
```

Start Jenkins at `http://localhost:8080`. The named volume retains Jenkins
settings and uv's package cache across container restarts or recreation:

```shell
docker run -d --name uv-cache-jenkins -p 127.0.0.1:8080:8080 -v uv-cache-jenkins-home:/var/jenkins_home uv-cache-jenkins
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
controller inside the container, which has uv and Python installed.

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
