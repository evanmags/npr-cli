from dataclasses import dataclass


@dataclass
class Stream:
    primary: bool
    station: str
    title: str
    href: str

    def is_playlist(self) -> bool:
        return self.href.endswith(".pls")
