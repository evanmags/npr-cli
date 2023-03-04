from functools import wraps

import click

from npr.cli.controller import main_control_loop
from npr.domain import Action
from npr.domain.exceptions import (
    DaemonNotRunningException,
    FailedActionException,
    UnknownActionException,
)
from npr.services.backend import backend


def domain_err_to_click_err(f):
    @wraps(f)
    def __inner__(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except DaemonNotRunningException:
            raise click.ClickException(
                click.style(
                    "The npr-cli daemon is not running. Run `npr up` to start.",
                    fg="red",
                )
            )
        except FailedActionException as fae:
            raise click.ClickException(
                click.style(
                    f"Failed to execute action `{fae.action.value}`.\n", fg="red"
                )
                + "If the problem persists please submit an issue:\n"
                + "\thttps://github.com/evanmags/npr-cli/issues"
            )
        except UnknownActionException as uae:
            raise click.ClickException(
                click.style(
                    f"Action `{uae.action.value}` is unknown to npr-cli.\n", fg="red"
                )
                + "If the problem persists please submit an issue:\n"
                + "\thttps://github.com/evanmags/npr-cli/issues"
            )

    return __inner__


@click.group(invoke_without_command=True)
@click.pass_context
@domain_err_to_click_err
def npr(ctx: click.Context):
    if ctx.invoked_subcommand != "up":
        backend.health()

    if ctx.invoked_subcommand is None:
        main_control_loop()


@npr.command()
@domain_err_to_click_err
def up():
    if not backend.poll_health(poll_for=False):
        click.echo(click.style("Starting npr-cli daemon.", fg="green"))
        main_control_loop(
            action=Action.up,
            run_repl=False,
        )
    else:
        click.echo(click.style("Daemon is already running.", fg="cyan"))


@npr.command()
@domain_err_to_click_err
def down():
    click.echo(click.style("Stopping npr-cli daemon.", fg="yellow"))
    main_control_loop(
        action=Action.down,
        run_repl=False,
    )


@npr.command()
@click.option("-q", "query", help="Station name, call, or zip code.")
@domain_err_to_click_err
def search(query: str | None):
    main_control_loop(
        action=Action.search,
        arg=query,
        run_repl=False,
    )


@npr.command()
@domain_err_to_click_err
def play():
    main_control_loop(
        action=Action.play,
        run_repl=False,
    )


@npr.command()
@domain_err_to_click_err
def stop():
    main_control_loop(
        action=Action.stop,
        run_repl=False,
    )


@npr.command()
@domain_err_to_click_err
def favorites():
    main_control_loop(
        action=Action.favorites_list,
        run_repl=False,
    )
