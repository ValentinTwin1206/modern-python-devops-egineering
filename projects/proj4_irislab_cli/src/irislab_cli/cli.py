"""Interactive IrisLab CLI and its API commands."""

from __future__ import annotations

import shlex
from pathlib import Path

import click

from irislab_cli import __version__, auth
from irislab_cli.api import IrisAPIError, IrisSession, write_json


# ================================================================
# Command-line interface commands
# ================================================================
@click.command(help="Analyze an eye image and return the result as JSON.")
@click.option(
    "--image",
    "image_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="PNG or JPEG image to upload.",
)
@click.option("-o", "--output", type=click.Path(dir_okay=False, path_type=Path))
@click.pass_obj
def analyze(session: IrisSession, image_path: Path, output: Path | None) -> None:
    """Upload an image for IrisLab analysis."""
    try:
        result = session.api.analyze_image(image_path)
    except IrisAPIError as error:
        raise click.ClickException(str(error)) from error
    write_json(result, output)


@click.command(help="Return the authenticated user's analysis history as JSON.")
@click.option("-o", "--output", type=click.Path(dir_okay=False, path_type=Path))
@click.pass_obj
def history(session: IrisSession, output: Path | None) -> None:
    """Retrieve the authenticated user's analysis history."""
    try:
        result = session.api.get_analysis_history()
    except IrisAPIError as error:
        raise click.ClickException(str(error)) from error
    write_json(result, output)


@click.command(help="Return the IrisLab reference colors as JSON.")
@click.option("-o", "--output", type=click.Path(dir_okay=False, path_type=Path))
@click.pass_obj
def reference_colors(session: IrisSession, output: Path | None) -> None:
    """Retrieve IrisLab reference colors."""
    try:
        result = session.api.get_reference_colors()
    except IrisAPIError as error:
        raise click.ClickException(str(error)) from error
    write_json(result, output)


COMMANDS = {
    "analyze": analyze,
    "history": history,
    "reference-colors": reference_colors,
}


# ==============================================================
# Interactive CLI session
# ==============================================================

def run_shell(session: IrisSession) -> None:
    """Read and dispatch command lines until the user exits."""
    click.echo(
        "Authenticated. Commands: analyze, history, reference-colors, help, exit"
    )
    # Read lines from the user until EOF or exit command.
    while True:
        try:
            # "iris> " is the prompt for the interactive CLI.
            line = input("iris> ")
        except EOFError:
            click.echo()
            return
        except KeyboardInterrupt:
            click.echo("\nSession ended.")
            return

        # Split the line into command name and arguments, handling quotes and escapes.
        try:
            args = shlex.split(line)
        except ValueError as error:
            click.echo(f"Invalid command: {error}", err=True)
            continue
        if not args:
            continue
        name, *command_args = args
        if name in {"exit", "quit"}:
            return
        if name == "help":
            click.echo("Commands: analyze, history, reference-colors, help, exit")
            continue

        # Dispatch the command to the appropriate Click command function.
        command = COMMANDS.get(name)
        if command is None:
            message = f"Unknown command: {name}. Type help for available commands."
            click.echo(message, err=True)
            continue

        # Run the command with the provided arguments and the current session object.
        try:
            command.main(
                args=command_args,
                prog_name=name,
                obj=session,
                standalone_mode=False,
            )
        except click.ClickException as error:
            error.show()
        except IrisAPIError as error:
            click.echo(f"Error: {error}", err=True)
        except click.Abort:
            click.echo("Command cancelled.", err=True)


def run_session() -> None:
    """Authenticate and start an in-memory interactive CLI session."""
    try:
        session = IrisSession(auth.login())
    except auth.OIDCError as error:
        raise click.ClickException(str(error)) from error

    try:
        run_shell(session)
    finally:
        session.close()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="irislab-cli")
def cli() -> None:
    """Log in to IrisLab and open an interactive API session."""
    run_session()


def main() -> None:
    """Entry point of the console script and the compiled executable."""
    cli(prog_name="irislab-cli")


if __name__ == "__main__":
    main()