from dataclasses import dataclass

from npr.domain.stream import Stream


@dataclass
class Station:
    name: str
    call: str
    streams: list["Stream"]
