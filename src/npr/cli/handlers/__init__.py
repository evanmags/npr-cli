import sys
from subprocess import Popen
from typing import Any

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from npr.cli.handlers import search
from npr.cli.handlers.dispatcher import dispatcher
from npr.domain import Action, Stream
from npr.domain.constants import NPR_CLI_SERVER_BIND, NPR_PIDFILE
from npr.services import backendapi

dispatcher.react_to(Action.search)(search.search)


@dispatcher.react_to(Action.up)
def up(*args: Any):
    p = Popen(
        [
            sys.executable,
            "-m",
            "gunicorn",
            "--bind",
            NPR_CLI_SERVER_BIND,
            "--name",
            "npr.cli.server",
            "--pid",
            NPR_PIDFILE,
            "--daemon",
            "npr.api.server:app",
        ],
    )
    p.wait()

    assert backendapi.poll_health(poll_for=True)

    return None, None


@dispatcher.react_to(Action.down)
def down(*args: Any):
    pid = NPR_PIDFILE.read_text().strip()

    p = Popen(["kill", pid])
    p.wait()

    assert not backendapi.poll_health(poll_for=False)

    return None, None


@dispatcher.react_to(Action.play)
def play(stream: Stream | None = None):
    backendapi.play(stream)
    return None, None


@dispatcher.react_to(Action.stop)
def stop(*args: Any):
    backendapi.stop()
    return None, None


@dispatcher.react_to(Action.favorites_list)
def favorites_list(*args: Any):
    favorites = backendapi.get_favorites()

    stream = inquirer.select(  # type: ignore
        "Select a Stream",
        choices=[
            *[s.name for s in favorites],
            Separator(),
            Choice(value=None, name="Exit"),
        ],
    ).execute()

    if not stream:
        return None, None

    stream = next(s for s in favorites if s.name == stream)

    action = inquirer.select(  # type: ignore
        "Select Action",
        choices=[
            Choice(value=Action.play, name="Play"),
            Choice(value=Action.favorites_remove, name="Remove"),
            Separator(),
            Choice(value=None, name="Exit"),
        ],
    ).execute()

    return action, stream


@dispatcher.react_to(Action.favorites_add)
def favorites_add(stream: Stream | None):
    if stream is None:
        stream = backendapi.now_playing_or_throw()

    backendapi.add_favorite(stream)
    return None, None


@dispatcher.react_to(Action.favorites_remove)
def favorites_remove(stream: Stream | None):
    if stream is None:
        stream = backendapi.now_playing_or_throw()

    backendapi.remove_favorite(stream)
    return None, None
