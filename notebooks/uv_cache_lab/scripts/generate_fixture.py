"""Generate a deterministic synthetic embedding matrix for the wheel."""

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--size",
        type=int,
        default=16,
        metavar="MIB",
        help="Matrix size in whole MiB (default: 16)",
    )
    args = parser.parse_args()
    if args.size <= 0:
        parser.error("--size must be a positive integer in MiB")
    data = Path(__file__).resolve().parents[1] / "src/uv_cache_demo/data"
    spec = json.loads((data / "fixture.json").read_text())
    assert spec["dtype"] == "uint8"
    size = args.size * 1024 * 1024
    if spec["dimensions"] < 1 or size % spec["dimensions"]:
        parser.error("--size must contain a whole number of matrix rows")
    spec["rows"] = size // spec["dimensions"]
    # SHAKE produces reproducible, poorly compressible bytes without ML libraries.
    # These are synthetic quantized embeddings, not weights from a trained model.
    # Independent 1 MiB blocks bound memory and make the output size-independent.
    target = data / "embeddings.bin"
    with target.open("wb") as stream:
        for block in range(args.size):
            seed = spec["seed"].encode() + b"\0" + block.to_bytes(8, "little")
            stream.write(hashlib.shake_256(seed).digest(1024 * 1024))
    (data / "fixture.json").write_text(json.dumps(spec, indent=2) + "\n")
    print(f"Generated {target.name}: {size // (1024 * 1024)} MiB")


if __name__ == "__main__":
    main()
