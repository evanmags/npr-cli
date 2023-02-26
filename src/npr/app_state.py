from dataclasses import dataclass, asdict, field
import json
import pathlib

import vlc

from npr.domain import Action, Stream

NPRRC = "~/.nprrc"


@dataclass
class AppState:
    favorites: list[Stream]
    now_playing: Stream | None
    last_played: Stream | None
    player: vlc.MediaPlayer | None = None

    _next: tuple[Action | None, Stream | str | None] | None = None, (None,)

    @classmethod
    def load(cls) -> "AppState":
        nprrc = pathlib.Path(NPRRC).expanduser()
        if not nprrc.exists():
            nprrc.touch()
            with nprrc.open("w") as f:
                json.dump(default_app_state(), f)
            return cls(**default_app_state())

        with nprrc.open() as f:
            c = json.load(f)
            cl = cls(
                favorites=[Stream(**s) for s in c["favorites"]],
                now_playing=None,
                last_played=Stream(**c["last_played"]) if c["last_played"] else None,
            )
            return cl

    def write(self):
        self.player = None
        nprrc = pathlib.Path(NPRRC).expanduser()
        json.dump(asdict(self), nprrc.open("w"))

    def next(self):
        return self._next

    def set_next(self, action: Action | None, *args: Stream | str | None):
        self._next = action, args


def get_app_state() -> AppState:
    return AppState.load()


def default_app_state():
    return {
        "favorites": [],
        "now_playing": None,
        "last_played": None,
    }
