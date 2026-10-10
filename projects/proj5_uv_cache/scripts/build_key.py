"""Fingerprint all build inputs without depending on checkout timestamps."""

import hashlib
from pathlib import Path


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    sources = sorted(
        path
        for path in project.joinpath("src").rglob("*")
        if path.suffix in {".py", ".json", ".bin"}
    )
    if not (project / "src/uv_cache_demo/data/embeddings.bin").is_file():
        raise SystemExit("Run python scripts/generate_fixture.py before fingerprinting.")
    fingerprint = hashlib.sha256()
    for path in [project / "pyproject.toml", *sources]:
        # Include names as well as contents to detect additions and removals.
        fingerprint.update(path.relative_to(project).as_posix().encode())
        fingerprint.update(b"\0")
        fingerprint.update(path.read_bytes())
        fingerprint.update(b"\0")
    print(fingerprint.hexdigest())


if __name__ == "__main__":
    main()
