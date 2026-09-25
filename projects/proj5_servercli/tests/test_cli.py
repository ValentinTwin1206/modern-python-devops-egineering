from click.testing import CliRunner

from server_cli.cli import cli


def test_help_lists_commands() -> None:
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0, result.output
    assert "login" in result.output
    assert "get-token" in result.output


def test_login_accepts_explicit_credentials() -> None:
    result = CliRunner().invoke(
        cli,
        ["login", "--username", "alice", "--password", "secret"],
    )
    assert result.exit_code == 0, result.output
    assert "login is not implemented yet for alice." in result.output
    assert "Username:" not in result.output
    assert "Password:" not in result.output


def test_login_prompts_for_missing_credentials() -> None:
    result = CliRunner().invoke(cli, ["login"], input="alice\nsecret\n")
    assert result.exit_code == 0, result.output
    assert "Username:" in result.output
    assert "Password:" in result.output
    assert "login is not implemented yet for alice." in result.output
    assert "secret" not in result.output


def test_get_token_is_a_placeholder() -> None:
    result = CliRunner().invoke(cli, ["get-token"])
    assert result.exit_code == 0, result.output
    assert result.output == "get-token is not implemented yet.\n"
