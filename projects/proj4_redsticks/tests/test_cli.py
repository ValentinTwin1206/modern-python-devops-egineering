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
    assert "Suggested shade" in captured.out


def test_cli_rejects_unsupported_image(tmp_path):
    exit_code = main(["--image", str(tmp_path / "missing.bmp")])

    assert exit_code == 2


def test_cli_reports_eye_color_source(eye_image, capsys):
    exit_code = main(["--image", str(eye_image)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Color quantization" in captured.out


def test_cli_gpu_without_cuda_fails(eye_image, monkeypatch):
    monkeypatch.setattr("redsticks.cli.cuda_available", lambda: False)

    exit_code = main(["--image", str(eye_image), "--gpu"])

    assert exit_code == 2
