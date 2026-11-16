# Verification TODO: pAIguard in IrisLab API

pAIguard is integrated into IrisLab API. Unit/API tests and real sample-image
moderation have been exercised, but the production image build and several
container runtime checks below remain outstanding. The API needs the
`irislab-tools` Conda package, which must be built locally from `../proj2_irislab`
and made available through a local channel for a fresh production build.

What was verified elsewhere: the pAIguard unit tests, the wheel build, the
model downloads with SHA-256 checks in `proj1_paiguard/Dockerfile.devEnv`,
real offline inference in that container, and the FastAPI reference project
`../tmp_proj`.

## What changed in this project

- `pyproject.toml`: new dependencies `pillow` and `paiguard==0.1.0`,
  a pinned Cloudsmith package index for pAIguard, and the PyTorch CPU index.
- `uv.lock`: regenerated with `uv lock` (no `nvidia-*` packages).
- `src/irislab_api/services/analysis.py`: a module-level `guard` and
  `AnalysisService.moderate()`, called after the upload validation and before
  `irislab.analyze`.
- `src/irislab_api/api/routes/analysis.py`: HTTP `422` for rejected content,
  HTTP `503` when the pAIguard models are missing.
- `Dockerfile` and `.devcontainer/Dockerfile`: download the pAIguard models to
  `/opt/irislab/paiguard` and set `PAIGUARD_MODEL_DIR`.
- `tests/test_api.py`: fake models in the `client` fixture and two new tests.

## Prerequisites

- [ ] Build the `irislab-tools` Conda package locally from `../proj2_irislab`
      and make it available as a local channel.
- [ ] Decide how the Dockerfiles receive that local channel. Both currently
      expect the build argument `IRISLAB_CHANNEL` to be a channel URL.

## Build

- [ ] Configure the actual Cloudsmith repository and authentication, then build
      the image from this directory:

      ```bash
      # Configure Cloudsmith in pyproject.toml and regenerate uv.lock first.
      docker build \
          --build-arg IRISLAB_CHANNEL="<local-channel>" \
          -t irislab-api:paiguard-check .
      ```

- [ ] Confirm in a fresh production image build that all eight model downloads
      pass their `sha256sum -c -` check. The checked-in model files were hashed
      separately and matched the expected values.
- [ ] Replace the Cloudsmith owner/repository URL placeholder in
      `pyproject.toml` using the chapter 03 `uv add --index` command and
      regenerate `uv.lock`, then confirm in a fresh
      production image build that `uv sync --locked --no-dev --no-editable`
      succeeds. The actual Cloudsmith owner/repository and credentials are
      required to resolve the package.
- [x] `pip check` passed in the dev-container environment (NumPy 2.5.4 and
      MediaPipe 0.10.35).
- [x] PyTorch CPU build verified (`2.15.0+cpu`).
- [ ] Note the final image size. The models add about 1.8 GB and the
      inference packages about 1 GB.

## Tests

- [ ] Rebuild the dev container and run `uv sync --locked` and `pytest`.
- [x] API tests passed in the available dev-container image (6 passed), using
      the fake models from the fixture.
- [x] `test_moderation_runs_before_analysis` passed (block and review give `422`).
- [x] `test_missing_paiguard_models` passed (`503`).

## Run

- [ ] Start the production container and check `/health/live` and `/health/ready`.
- [ ] Upload a harmless portrait to `/api/v1/analyses` and confirm HTTP `200`.
      The first request is slow because the models are loaded then.
- [ ] Run the production container with `--network none` and repeat the upload
      to confirm that no model download is attempted.
- [ ] Start the production container with `-e PAIGUARD_MODEL_DIR=/missing` and
      confirm HTTP `503` and the error in the container log.
- [ ] Set `IRISLAB_API_NSFW_THRESHOLD=0.0` and confirm that the same portrait
      is rejected with HTTP `422`.
- [x] All four `proj1_paiguard/samples/*.jpg` images were rejected by the API
      with HTTP `422` for violence using the real local pAIguard models.

## Follow-up

- [ ] Configure `CLOUDSMITH_REPOSITORY` and Cloudsmith credentials, then use
      the documented `uv add --index` command to set the actual Cloudsmith
      package source and regenerate the lockfile. uv does not interpolate
      shell variables in `pyproject.toml` URLs.
- [ ] Decide whether `/health/ready` should also check the pAIguard models.
- [ ] Check memory use with more than one uvicorn worker; each worker loads
      its own copy of the models.
