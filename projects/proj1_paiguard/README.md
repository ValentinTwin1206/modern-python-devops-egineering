# PaiGuard

**PaiGuard** is a lightweight, framework-independent Python library for inspecting images with local moderation models before an application accepts them.

It currently provides:

-   **NSFW detection** for explicit content
-   **Violence detection**

PaiGuard separates its moderation rules from framework integration and from upload handling. The application validates and decodes the upload, for example with Pillow, and passes the decoded image to PaiGuard. Inference runs locally; PaiGuard never downloads models and never sends images to another service.

## Installation

### Requirements

-   Python 3.11+
-   `uv` or `pip`
-   The model files listed under [Models](#models), about 1.8 GB on disk

### Install PaiGuard

With `uv`, first configure the PyTorch CPU index in your project's `pyproject.toml` so PyTorch resolves to the CPU-only build:

```toml
[tool.uv.sources]
torch = { index = "pytorch-cpu" }

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

Add PaiGuard to your project dependencies using `uv`. 

```bash
uv add "paiguard==0.1.0"
```

Its model weights are downloaded separately. Follow [Install Models](#install-models) to download them.

### Install Models

Set `PAIGUARD_MODEL_DIR` to the directory where PaiGuard should find its local
model files:

```bash
export PAIGUARD_MODEL_DIR="${PAIGUARD_MODEL_DIR:-$PWD/models}"
```

The SigLIP2 base model encodes images for violence moderation. To download the
model and its weights, use `curl`:

```bash
mkdir -p "$PAIGUARD_MODEL_DIR/siglip2-base"
BASE_URL="https://huggingface.co/google/siglip2-base-patch16-256/resolve/3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab"
curl -fsSL "$BASE_URL/config.json" -o "$PAIGUARD_MODEL_DIR/siglip2-base/config.json"
curl -fsSL "$BASE_URL/preprocessor_config.json" -o "$PAIGUARD_MODEL_DIR/siglip2-base/preprocessor_config.json"
curl -fsSL "$BASE_URL/model.safetensors" -o "$PAIGUARD_MODEL_DIR/siglip2-base/model.safetensors"
```

The SigLIP2 moderation head classifies image embeddings for violence. To
download the model and its weights, use `curl`:

```bash
mkdir -p "$PAIGUARD_MODEL_DIR/siglip2-heads"
BASE_URL="https://huggingface.co/khasinski/siglip2-moderation-heads/resolve/b88fe03369e3dc6aa9887cd3b4cd3e9b7cf76ee5"
curl -fsSL "$BASE_URL/violence_head.onnx" -o "$PAIGUARD_MODEL_DIR/siglip2-heads/violence_head.onnx"
curl -fsSL "$BASE_URL/violence_head.onnx.data" -o "$PAIGUARD_MODEL_DIR/siglip2-heads/violence_head.onnx.data"
```

The Falconsai classifier detects NSFW content. To download the model and its
weights, use `curl`:

```bash
mkdir -p "$PAIGUARD_MODEL_DIR/falconsai-nsfw"
BASE_URL="https://huggingface.co/Falconsai/nsfw_image_detection/resolve/96cb0d0342c7afb80cab76ecc58b265fa44da256"
curl -fsSL "$BASE_URL/config.json" -o "$PAIGUARD_MODEL_DIR/falconsai-nsfw/config.json"
curl -fsSL "$BASE_URL/preprocessor_config.json" -o "$PAIGUARD_MODEL_DIR/falconsai-nsfw/preprocessor_config.json"
curl -fsSL "$BASE_URL/model.safetensors" -o "$PAIGUARD_MODEL_DIR/falconsai-nsfw/model.safetensors"
```

## Usage

### Create a `PaiGuard` instance

Create a `PaiGuard` instance and pass the moderation rules you want to enable. `PaiGuard` runs all configured rules when an image is inspected:

``` python
from PIL import Image

from paiguard import PaiGuard
from paiguard.rules import PaiNsfwDetection, PaiViolenceDetection

guard = PaiGuard(
    rules=[
        PaiNsfwDetection(threshold=0.80),
        PaiViolenceDetection(threshold=0.85, review_threshold=0.50),
    ]
)

# PaiGuard expects an image that the application has already decoded:
image = Image.open("uploads/image.jpg").convert("RGB")

result = guard.inspect(image)

if result.is_safe:
    print("Image approved")
else:
    print(f"Image {result.decision}: {result.violations}")
```

`guard.inspect(image)` returns an `InspectionResult`:

| Attribute    | Description                                                              |
|--------------|--------------------------------------------------------------------------|
| `decision`   | `"allow"`, `"review"`, or `"block"`.                                     |
| `is_safe`    | `True` when the decision is `"allow"`.                                   |
| `violations` | Categories of the rules that asked for a block or a review.              |
| `results`    | One `RuleResult` per rule with `rule`, `category`, `score`, `detected`, `needs_review`, and `details`. |

The decision is `"block"` when any score reaches its `threshold`, `"review"` when any score reaches its `review_threshold`, and `"allow"` otherwise. It raises `ModelNotFoundError` when a model file is missing.

### Moderation Rules

Configure the thresholds of each rule:

``` python
from paiguard import PaiGuard
from paiguard.rules import PaiNsfwDetection

guard = PaiGuard(
    rules=[
        PaiNsfwDetection(
            threshold=0.80,
            review_threshold=0.50,
        )
    ]
)
```

Parameters:

| Parameter          | Description                                                             |
|--------------------|-------------------------------------------------------------------------|
| `threshold`        | Score from which the image is blocked. Default: `0.80` for `PaiNsfwDetection`, `0.85` for `PaiViolenceDetection`. |
| `review_threshold` | Optional lower score from which the image requires a review.            |
| `model`            | Optional object with a `score(image)` method that replaces the default model, for example in tests. |

> Note: Scores are raw model outputs between 0 and 1. They are not calibrated probabilities, so choose thresholds by testing with your own images.

To add your own rule, subclass `paiguard.rules.PaiRule` and return a `RuleResult` from `inspect(image)`.

### Models

PaiGuard reads its models from the directory named by `PAIGUARD_MODEL_DIR` (default: `/opt/paiguard/models`). A model is loaded when its rule inspects the first image and then stays in memory.

| Rule | Directory | Model and pinned revision | Files | License on model card |
|------|-----------|---------------------------|-------|-----------------------|
| `PaiNsfwDetection` | `falconsai-nsfw/` | [Falconsai/nsfw_image_detection](https://huggingface.co/Falconsai/nsfw_image_detection) @ `96cb0d0342c7afb80cab76ecc58b265fa44da256` | `config.json`, `preprocessor_config.json`, `model.safetensors` (343 MB) | Apache-2.0 |
| `PaiViolenceDetection` | `siglip2-base/` | [google/siglip2-base-patch16-256](https://huggingface.co/google/siglip2-base-patch16-256) @ `3f9f96cb90da5dbc758b01813f2f6f1aee24c1ab` | `config.json`, `preprocessor_config.json`, `model.safetensors` (1.5 GB) | Apache-2.0 |
| `PaiViolenceDetection` | `siglip2-heads/` | [khasinski/siglip2-moderation-heads](https://huggingface.co/khasinski/siglip2-moderation-heads) @ `b88fe03369e3dc6aa9887cd3b4cd3e9b7cf76ee5` | `violence_head.onnx`, `violence_head.onnx.data` (0.8 MB) | Apache-2.0 |

The development image built from `Dockerfile.devEnv` downloads these files with `curl` and verifies their SHA-256 checksums. The model files are not part of the PaiGuard wheel. The licenses above are the ones stated on the model cards; the cards do not fully document the licenses of the training data, so review them before commercial use.

## Drawbacks

- **Model accuracy:** `PaiNsfwDetection` uses a general NSFW classifier and does not report a dedicated nudity score. `PaiViolenceDetection` was trained on real-life violence and may miss illustrations. Both models can produce false positives and false negatives.

- **Weapon detection:** PaiGuard does not detect weapons yet, because neither model provides it. A `PaiWeaponDetection` rule is planned as a future feature.

- **Resource usage:** The models need about 1.8 GB on disk, and the first inspection is slow because the models are loaded then. Inference runs on the CPU. Each worker process loads its own copy of the models.

- **Image handling:** PaiGuard does not validate uploads, limit file sizes, or remove metadata. The application must do this before it calls `guard.inspect(image)`.
