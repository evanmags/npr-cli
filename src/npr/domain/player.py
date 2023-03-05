from configparser import ConfigParser
from typing import Any, Protocol, Type

import requests

from npr.domain.stream import Stream


class MediaPlayer(Protocol):
    def __new__(cls, *args: Any) -> Any:
        ...

    def play(self):
        ...

    def stop(self):
        ...


class Player:
    player_class: Type[MediaPlayer]
    player: MediaPlayer | None = None
    now_playing: Stream | None = None

    def __init__(self, player_class: Type[MediaPlayer]):
        self.player_class = player_class

    def play(self, stream: Stream):
        self.stop()
        self.player = self.player_class(self._get_playable_from_stream(stream))
        self.player.play()
        self.now_playing = stream

    def stop(self):
        if self.player:
            self.player.stop()
        self.now_playing = None
        self.player = None

    def _get_playable_from_stream(self, stream: Stream) -> str:
        if stream.is_playlist():
            return self._get_stream_url_from_playlist(stream.href)
        return stream.href

    def _get_stream_url_from_playlist(self, uri: str) -> str:
        response = requests.get(uri)
        config = ConfigParser()
        config.read_string(response.text)
        return config["playlist"]["file1"]
