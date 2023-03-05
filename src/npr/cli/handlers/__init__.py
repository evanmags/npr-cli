import sys
from subprocess import DEVNULL, STDOUT, Popen
from typing import Any

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from npr.cli.handlers import search
from npr.cli.handlers.dispatcher import dispatcher
from npr.domain import Action, Stream
from npr.domain.constants import NPR_CLI_SERVER_PORT, NPR_PIDFILE
from npr.services.backend import backend

dispatcher.react_to(Action.search)(search.search)


@dispatcher.react_to(Action.up)
def up(*args: Any):
    p = Popen(
        [
            sys.executable,
            "-m",
            "flask",
            "--app",
            "npr.api.server:app",
            "run",
            "--port",
            f"{NPR_CLI_SERVER_PORT}",
        ],
        start_new_session=True,
        stdout=DEVNULL,
        stderr=STDOUT,
    )

    assert backend.poll_health(poll_for=True)

    NPR_PIDFILE.write_text(str(p.pid))

    return None, None


@dispatcher.react_to(Action.down)
def down(*args: Any):
    pid = NPR_PIDFILE.read_text()

    p = Popen(["kill", pid])
    p.wait()

    assert not backend.poll_health(poll_for=False)

    return None, None


@dispatcher.react_to(Action.play)
def play(stream: Stream | None = None):
    backend.play(stream)
    return None, None


@dispatcher.react_to(Action.stop)
def stop(*args: Any):
    backend.stop()
    return None, None


@dispatcher.react_to(Action.favorites_list)
def favorites_list(*args: Any):
    favorites = backend.get_favorites()

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
def favorites_add(stream: Stream):
    backend.add_favorite(stream)
    return None, None


@dispatcher.react_to(Action.favorites_remove)
def favorites_remove(stream: Stream):
    backend.remove_favorite(stream)
    return None, None
