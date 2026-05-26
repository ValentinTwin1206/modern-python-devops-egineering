from pathlib import Path

from click.testing import CliRunner
from PIL import Image

from pixelpack.cli import cli


def _make_image(path: Path, size: tuple[int, int] = (16, 16), color: str = "red") -> None:
    Image.new("RGB", size, color=color).save(path)


def test_resize_writes_target_dimensions(tmp_path: Path) -> None:
    source = tmp_path / "in.png"
    destination = tmp_path / "out.png"
    _make_image(source, size=(32, 32))

    result = CliRunner().invoke(
        cli,
        ["resize", str(source), str(destination), "--width", "8", "--height", "4"],
    )

    assert result.exit_code == 0, result.output
    with Image.open(destination) as image:
        assert image.size == (8, 4)


def test_convert_changes_format(tmp_path: Path) -> None:
    source = tmp_path / "in.png"
    destination = tmp_path / "out.jpg"
    _make_image(source)

    result = CliRunner().invoke(cli, ["convert", str(source), str(destination)])

    assert result.exit_code == 0, result.output
    with Image.open(destination) as image:
        assert image.format == "JPEG"


def test_grayscale_produces_single_channel(tmp_path: Path) -> None:
    source = tmp_path / "in.png"
    destination = tmp_path / "out.png"
    _make_image(source)

    result = CliRunner().invoke(cli, ["grayscale", str(source), str(destination)])

    assert result.exit_code == 0, result.output
    with Image.open(destination) as image:
        assert image.mode == "L"
