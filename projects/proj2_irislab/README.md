# IrisLab

IrisLab analyzes iris color from portrait images using local MediaPipe inference, Python, and a native C++ color-distance library.

## Installation

### Configure Cloudsmith Repository

Replace `<CLOUDSMITH_REPOSITORY>` with your Cloudsmith repository slug:

```bash
export CLOUDSMITH_CHANNEL="https://conda.cloudsmith.io/<CLOUDSMITH_REPOSITORY>/"
conda config --add channels "$CLOUDSMITH_CHANNEL"
conda config --add channels conda-forge
conda config --set channel_priority strict
```

### Install IrisLab

Create an `environment.yml` file:

```yaml
name: irislab
channels:
  - https://conda.cloudsmith.io/<CLOUDSMITH_REPOSITORY>/
  - conda-forge
  - nodefaults
dependencies:
  - python=3.12
  - irislab-tools
  - pip
```

Create and activate the environment, then install MediaPipe:

```bash
conda env create --file environment.yml
conda activate irislab
python -m pip install mediapipe
```

## Usage

### Analyze an Image

```bash
irislab --image samples/blue-eyes.png
```

### Use the Python API

```python
from pathlib import Path
from irislab import analyze

result = analyze(Path("samples/blue-eyes.png"))
print(result.eye_color)
print(result.delta_e)
```

### Download the Face Landmarker Model

IrisLab requires a local MediaPipe Face Landmarker model. Download it and set its path:

```bash
mkdir -p models
curl -fL \
  https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task \
  -o models/face_landmarker.task
export IRISLAB_MODEL_PATH="$PWD/models/face_landmarker.task"
```
