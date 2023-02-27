from configparser import ConfigParser
import time

import requests
import vlc

from npr.app.state import AppState
from npr.domain import Stream


def play_controller(app_state: AppState, stream: Stream | None = None):
    if app_state.player:
        app_state.player.stop()

    if stream is None:
        stream = app_state.last_played

    assert stream is not None

    app_state.player = vlc.MediaPlayer(get_playable_from_stream(stream))
    app_state.player.play()

    app_state.now_playing = stream
    app_state.last_played = stream

    # there is a slight delay before the stream actually starts
    # at that point VLC writes an exception to the terminal
    # this can be removed when that exception is hidden.
    time.sleep(1.5)

    return None, None


def get_playable_from_stream(stream: Stream) -> str:
    if stream.is_playlist():
        return get_stream_url_from_playlist(stream.href)
    return stream.href


def get_stream_url_from_playlist(uri: str) -> str:
    response = requests.get(uri)
    config = ConfigParser()
    config.read_string(response.text)
    return config["playlist"]["file1"]
