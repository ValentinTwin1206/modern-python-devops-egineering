# IrisLab

IrisLab analyzes iris color from portrait images using local MediaPipe inference, Python, and a native C++ color-distance library.

## Installation

### Configure Cloudsmith Repository

Add the public Cloudsmith broadcast to your Conda config:

```bash
conda config --add channels "https://conda.cloudsmith.io/pravi-brothers/modern-python-engineering/"
conda config --add channels conda-forge
conda config --set channel_priority strict
```

### Install IrisLab

#### From an `environment.yml` File

Create an `environment.yml` file:

```yaml
name: irislab
channels:
  - https://conda.cloudsmith.io/pravi-brothers/modern-python-engineering/
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

#### From Scratch

Install the Python package and CLI from Cloudsmith:

```bash
conda install irislab-tools=0.0.1 \
  -c https://conda.cloudsmith.io/pravi-brothers/modern-python-engineering/
```

> Conda installs `libirislab` automatically as a dependency.

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
