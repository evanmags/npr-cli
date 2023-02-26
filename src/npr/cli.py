import click

from npr.app_state import get_app_state
from npr.domain import Action
from npr.app_controller import main_control_loop


@click.group(invoke_without_command=True)
@click.pass_context
def npr(ctx: click.Context):
    app_state = get_app_state()

    ctx.ensure_object(dict)
    ctx.obj["APP_STATE"] = app_state

    if ctx.invoked_subcommand is None:
        main_control_loop(app_state)


@npr.command()
@click.option("-q", "query", help="Station name, call, or zip code.")
@click.pass_context
def search(ctx: click.Context, query: str | None):
    state = ctx.obj["APP_STATE"]
    state.set_next(Action.search, query)

    main_control_loop(state)


@npr.command()
@click.pass_context
def play(ctx: click.Context):
    state = ctx.obj["APP_STATE"]
    state.set_next(Action.play)

    main_control_loop(state)


@npr.command()
@click.pass_context
def favorites(ctx):
    state = ctx.obj["APP_STATE"]
    state.set_next(Action.favorites_list)

    main_control_loop(state)
