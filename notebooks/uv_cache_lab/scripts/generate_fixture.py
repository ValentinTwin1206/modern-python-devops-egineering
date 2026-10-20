"""Generate a deterministic 16 MiB synthetic embedding matrix for the wheel."""

import hashlib
import json
from pathlib import Path


def main() -> None:
    data = Path(__file__).resolve().parents[1] / "src/uv_cache_demo/data"
    spec = json.loads((data / "fixture.json").read_text())
    assert spec["dtype"] == "uint8"
    size = spec["rows"] * spec["dimensions"]
    # SHAKE produces reproducible, poorly compressible bytes without ML libraries.
    # These are synthetic quantized embeddings, not weights from a trained model.
    payload = hashlib.shake_256(spec["seed"].encode()).digest(size)
    target = data / "embeddings.bin"
    target.write_bytes(payload)
    print(f"Generated {target.name}: {size // (1024 * 1024)} MiB")


if __name__ == "__main__":
    main()
