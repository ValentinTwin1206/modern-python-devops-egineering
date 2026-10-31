# IrisLab API

A FastAPI service exposing [IrisLab](../proj3_irislab/README.md) iris-color
analysis. Inference runs locally on the CPU. The API accepts PNG or JPEG
portraits up to 10 MiB and 20 megapixels; uploads are removed after analysis.

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health/live` | Process liveness |
| GET | `/health/ready` | Check that the model file is present and nonempty |
| GET | `/api/v1/reference-colors` | Available reference profiles |
| POST | `/api/v1/analyses` | Analyze a multipart upload named `image` |

Interactive API documentation is available at `/docs`. Analysis returns 415
for unsupported or invalid images, 413 for an oversized upload, 422 if no iris
can be detected, and 503 if the model is missing. `confidence` is an extraction
quality indicator, not a calibrated probability.

## Build and run

First build and publish **both** `irislab-tools` and `libirislab` for Linux
and Python 3.12 as described in [Chapter 02, Section 03](../../docs/chapter-02/section-03.md).
Republish packages built from the current recipe: older builds may target a
different Python version or lack `IRISLAB_MODEL_PATH` support. Use a public
Cloudsmith Conda channel URL without credentials; private channels require
separate authentication setup.

From this directory, replace the example with your public channel URL:

```bash
docker build --build-arg IRISLAB_CHANNEL=https://conda.cloudsmith.io/OWNER/REPOSITORY/ -t irislab-api:1.0.0 .
docker run --rm -p 8080:8080 irislab-api:1.0.0
```

In another terminal, from this directory:

```bash
curl -f http://localhost:8080/health/ready
curl -f http://localhost:8080/api/v1/reference-colors
curl -f -F 'image=@../proj3_irislab/samples/blue-eyes.png' http://localhost:8080/api/v1/analyses
```

Micromamba installs `irislab-tools` and resolves its Conda dependencies,
including `libirislab`. It also installs `libglib`, needed by MediaPipe's
OpenCV wheel. The recipe does not include MediaPipe, so the build
installs it from PyPI using `python -m pip install mediapipe==0.10.35`, following
the chapter's consumer workflow. Pip resolves its dependencies and may update
packages previously installed by Conda. A second environment created with `--system-site-packages`
uses that Conda Python and sees its packages. `uv sync --locked --no-dev
--no-editable` installs the API and its Python dependencies into the second
environment. Both environments remain at their original paths in the runtime
image, which starts Uvicorn as an unprivileged user. API environment packages
take precedence over inherited Conda packages. The lockfile covers the API's
Python dependencies, not Conda's solve or MediaPipe's transitive dependencies.
The image downloads and verifies the MediaPipe model. Set `IRISLAB_MODEL_PATH`
to override its location.

## Development and tests

Create the Conda environment with the published IrisLab packages first, using
the [consumer workflow](../../docs/chapter-02/section-03.md#consumer-workflow).
Install MediaPipe and its dependencies in that environment, then from this
directory create the API environment using the Conda interpreter:

```bash
conda activate irislab-demo
python -m pip install mediapipe==0.10.35
uv venv --python "$CONDA_PREFIX/bin/python" --system-site-packages
uv sync --locked
uv run --no-sync pytest
IRISLAB_MODEL_PATH="$PWD/../proj3_irislab/models/face_landmarker.task" uv run --no-sync uvicorn irislab_api.main:app --host 127.0.0.1 --port 8080
```

The model is not tracked by Git. Supply the Face Landmarker model locally at
the path above or set `IRISLAB_MODEL_PATH` to an existing model file. The tests
mock inference; the container example exercises the real model. Because uv
cannot resolve Conda artifacts, IrisLab is an external environment dependency
rather than a `pyproject.toml` dependency of the API.
