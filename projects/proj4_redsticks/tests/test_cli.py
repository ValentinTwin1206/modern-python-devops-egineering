"""Tests for the redsticks command-line interface."""

import pytest
from PIL import Image

from redsticks.cli import main


@pytest.fixture()
def eye_image(tmp_path):
    path = tmp_path / "eye.png"
    Image.new("RGB", (64, 64), (70, 110, 180)).save(path)
    return path


def test_cli_prints_hex_value(eye_image, capsys):
    exit_code = main(["--image", str(eye_image)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "#" in captured.out
    assert "Suggested shade:" in captured.out


def test_cli_writes_output_png(eye_image, tmp_path):
    output = tmp_path / "shade.png"

    exit_code = main(["--image", str(eye_image), "--output", str(output)])

    assert exit_code == 0
    assert output.is_file()
    with Image.open(output) as image:
        assert image.format == "PNG"


def test_cli_rejects_unsupported_image(tmp_path):
    exit_code = main(["--image", str(tmp_path / "missing.bmp")])

    assert exit_code == 2
