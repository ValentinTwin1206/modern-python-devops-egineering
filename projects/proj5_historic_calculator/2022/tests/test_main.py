"""Pytest cases for historic_calculator (2022 era)."""
import pytest
from click.testing import CliRunner

from historic_calculator.main import cli, parse_vector, run_calculator


@pytest.mark.parametrize(
    "command,text,expected",
    [
        ("max", "1,-2,4", 4.0),
        ("min", "1,-2,4", -2.0),
        ("sum", "10,20,30,40", 100.0),
        ("mean", "1.5,2.5,3.5", 2.5),
    ],
)
def test_run_calculator(command: str, text: str, expected: float) -> None:
    assert run_calculator(command, text) == expected


def test_parse_vector_rejects_empty() -> None:
    with pytest.raises(ValueError):
        parse_vector("")


def test_run_calculator_rejects_unknown_command() -> None:
    with pytest.raises(ValueError):
        run_calculator("bogus", "1,2,3")


def test_cli_max_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["max", "1,-2,4"])
    assert result.exit_code == 0
    assert "max(1,-2,4) = 4.0" in result.output


def test_cli_invalid_vector_exits_non_zero() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["mean", "1,,3"])
    assert result.exit_code != 0
