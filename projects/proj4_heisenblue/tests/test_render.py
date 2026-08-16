from __future__ import annotations

from pathlib import Path

from PIL import Image

from heisenblue import analyze, render


def test_render_creates_valid_png(tmp_path: Path) -> None:
    result = analyze("CCO")
    output_path = tmp_path / "ethanol.png"

    render(result, output_path)

    assert output_path.exists()
    with Image.open(output_path) as image:
        assert image.format == "PNG"
        assert image.size[0] > 0
        assert image.size[1] > 0