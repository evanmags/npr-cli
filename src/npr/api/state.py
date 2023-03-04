import json
from dataclasses import asdict, dataclass
from pathlib import Path

import vlc

from npr import __version__
from npr.api.migrations import migrator
from npr.domain import Player, Stream
from npr.domain.constants import NPRRC


@dataclass
class AppState:
    favorites: list[Stream]
    last_played: Stream | None

    __version__: str = __version__
    player: Player = Player(vlc.MediaPlayer)

    @classmethod
    def load(cls, state_file: Path = NPRRC) -> "AppState":
        state_file.touch()

        with state_file.open() as f:
            try:
                c = migrator.migrate(json.load(f))
                return cls._load_dict(c)
            except json.JSONDecodeError:
                return cls([], None)

    @classmethod
    def _load_dict(cls, state: dict):
        return cls(
            favorites=[Stream(**s) for s in state["favorites"]],
            last_played=Stream(**state["last_played"])
            if state["last_played"]
            else None,
        )

    def write(self, state_file: Path = NPRRC):
        with state_file.open("w") as f:
            _serialized = {
                "__version__": __version__,
                "favorites": [asdict(s) for s in self.favorites],
                "last_played": asdict(self.last_played) if self.last_played else None,
            }

            json.dump(_serialized, f)
