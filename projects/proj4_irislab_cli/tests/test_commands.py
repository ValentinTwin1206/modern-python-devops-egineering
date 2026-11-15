import json
from pathlib import Path

from click.testing import CliRunner

from irislab_cli.cli import analyze, history, reference_colors


class FakeAPI:
    def analyze_image(self, image_path: Path) -> dict:
        return {"analysis": image_path.name}

    def get_analysis_history(self) -> list[dict]:
        return [{"id": "one"}]

    def get_reference_colors(self) -> list[dict]:
        return [{"name": "brown"}]


class FakeSession:
    api = FakeAPI()


def test_commands_print_json_or_save_output(tmp_path: Path) -> None:
    runner = CliRunner()
    session = FakeSession()
    image = tmp_path / "eye.jpg"
    image.write_bytes(b"image")

    result = runner.invoke(analyze, ["--image", str(image)], obj=session)
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {"analysis": "eye.jpg"}

    output = tmp_path / "history.json"
    result = runner.invoke(history, ["--output", str(output)], obj=session)
    assert result.exit_code == 0, result.output
    assert json.loads(output.read_text(encoding="utf-8")) == [{"id": "one"}]
    assert "test-access-token" not in result.output

    result = runner.invoke(reference_colors, [], obj=session)
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == [{"name": "brown"}]