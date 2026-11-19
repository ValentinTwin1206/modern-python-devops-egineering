# IrisLab API

IrisLab API provides HTTP endpoints for iris-color analysis with IrisLab. It accepts PNG and JPEG images up to 10 MiB and 20 megapixels. Every upload is moderated with [pAIguard](../proj1_paiguard/README.md) before IrisLab analyzes it.

## Installation

### Configure Cloudsmith Repository

Replace `<CLOUDSMITH_REPOSITORY>` with your Cloudsmith repository slug:

```bash
export CLOUDSMITH_REPOSITORY="<CLOUDSMITH_REPOSITORY>"
```

### Install IrisLab API

Configure the external MongoDB database and OIDC issuer before starting the API:

```bash
export MONGODB_URI="mongodb://..."
export MONGODB_DATABASE="irislab"
export OIDC_ISSUER_URL="https://..."
export OIDC_JWKS_URL="https://.../.well-known/jwks.json"
# Set OIDC_AUDIENCE and OIDC_REQUIRED_ROLE when required by your provider.
```

Pull and run the published container image:

```bash
docker pull "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/irislab-api:1.0.0"
docker run --rm -p 8080:8080 \
  -e MONGODB_URI -e MONGODB_DATABASE \
  -e OIDC_ISSUER_URL -e OIDC_JWKS_URL \
  -e OIDC_AUDIENCE -e OIDC_REQUIRED_ROLE \
  "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/irislab-api:1.0.0"
```

## Usage

### Check Service Health

```bash
curl -f http://127.0.0.1:8080/health/live
curl -f http://127.0.0.1:8080/health/ready
```

### List Reference Colors

```bash
curl -f http://127.0.0.1:8080/api/v1/reference-colors
```

### Analyze an Image

```bash
curl -f \
  -H "Authorization: Bearer <access-token>" \
  -F 'image=@portrait.png' \
  http://127.0.0.1:8080/api/v1/analyses
```

Interactive API documentation is available at [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs).

Images that pAIguard classifies as NSFW or violent are rejected with HTTP `422`. The thresholds can be changed with the environment variables `IRISLAB_API_NSFW_THRESHOLD` (default `0.80`) and `IRISLAB_API_VIOLENCE_THRESHOLD` (default `0.85`). The container reads the pAIguard models from `PAIGUARD_MODEL_DIR` (`/opt/irislab/paiguard`) and returns HTTP `503` when they are missing.
