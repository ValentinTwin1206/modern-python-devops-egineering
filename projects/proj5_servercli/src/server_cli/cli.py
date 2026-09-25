"""Command-line entry point for server-cli."""

from __future__ import annotations

import click

from server_cli import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="server-cli")
def cli() -> None:
    """Command-line client for the server API."""


@cli.command()
@click.option(
    "--username",
    help="Username to use for login; prompted when omitted.",
)
@click.option(
    "--password",
    help="Password to use for login; prompted securely when omitted.",
)
def login(username: str | None, password: str | None) -> None:
    """Collect login credentials for a future server authentication request."""
    if not username:
        username = click.prompt("Username")
    if not password:
        click.prompt("Password", hide_input=True)

    click.echo(f"login is not implemented yet for {username}.")


@cli.command()
def get_token() -> None:
    """Request a short-lived API token from the server in a future release."""
    click.echo("get-token is not implemented yet.")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
