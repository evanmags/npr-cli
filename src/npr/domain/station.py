from dataclasses import dataclass

from domain.stream import Stream


@dataclass
class Station:
    name: str
    call: str
    streams: list["Stream"]
