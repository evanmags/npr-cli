from dataclasses import dataclass, asdict
import json
import pathlib
from typing import Any

import vlc

from npr.domain import Action, Stream

NPRRC = "~/.nprrc"


@dataclass
class AppState:
    favorites: list[Stream]
    now_playing: Stream | None
    last_played: Stream | None
    player: vlc.MediaPlayer | None = None

    _next_action: Action | None = None
    _next_args: tuple[Any, ...] = tuple()

    @classmethod
    def load(cls) -> "AppState":
        nprrc = pathlib.Path(NPRRC).expanduser()
        if not nprrc.exists():
            nprrc.touch()
            return cls(**default_app_state())

        with nprrc.open() as f:
            c = json.load(f)
            return cls(
                favorites=[Stream(**s) for s in c["favorites"]],
                now_playing=None,
                last_played=Stream(**c["last_played"]) if c["last_played"] else None,
            )

    def write(self):
        self.player = None
        nprrc = pathlib.Path(NPRRC).expanduser()
        with nprrc.open("w") as f:
            json.dump(asdict(self), f)

    def next(self):
        return self._next_action, *self._next_args

    def set_next(self, action: Action | None, *args: Stream | str | None):
        self._next_action = action
        self._next_args = args


def get_app_state() -> AppState:
    return AppState.load()


def default_app_state():
    return {
        "favorites": [],
        "now_playing": None,
        "last_played": None,
    }
