# IrisLab API

IrisLab API provides HTTP endpoints for iris-color analysis with IrisLab. It accepts PNG and JPEG images up to 10 MiB and 20 megapixels.

## Installation

### Configure Cloudsmith Repository

Replace `<CLOUDSMITH_REPOSITORY>` with your Cloudsmith repository slug:

```bash
export CLOUDSMITH_REPOSITORY="<CLOUDSMITH_REPOSITORY>"
```

### Install IrisLab API

Pull and run the published container image:

```bash
docker pull "docker.cloudsmith.io/${CLOUDSMITH_REPOSITORY}/irislab-api:1.0.0"
docker run --rm -p 8080:8080 \
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
  -F 'image=@portrait.png' \
  http://127.0.0.1:8080/api/v1/analyses
```

Interactive API documentation is available at [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs).
