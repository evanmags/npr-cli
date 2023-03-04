from unittest.mock import patch

import pytest

from npr.domain import Player, Stream


class MockMediaPlayer:
    def __new__(cls, *args):
        return super().__new__(cls)

    def play(self):
        pass

    def stop(self):
        pass


@pytest.fixture(scope="function")
def mock_player() -> Player:
    return Player(MockMediaPlayer)


@pytest.fixture(scope="function")
def mock_stream() -> Stream:
    return Stream(
        primary=False,
        station="FakeNprStation",
        name="Npr News",
        # using a `pls` extention here to exercise the code path.
        href="http://npr.station/stream.pls",
    )


class MockResponse:
    text = """[playlist]
File1=https://24453.live.streamtheworld.com:443/WRVOFM_SC
File2=https://26353.live.streamtheworld.com:443/WRVOFM_SC
File3=https://18193.live.streamtheworld.com:443/WRVOFM_SC
Title1=WRVOFM_SC
Title2=WRVOFM_SC-Bak
Length1=-1
NumberOfEntries=3
Version=2
"""


@pytest.fixture(scope="module", autouse=True)
def mock_requests_get():
    with patch("npr.domain.player.requests.get") as mock:
        mock.side_effect = lambda *args, **kwargs: MockResponse()
        yield mock


def test_init(mock_player: Player):
    assert mock_player.player_class == MockMediaPlayer


def test_get_stream_url_from_pls(mock_player: Player, mock_stream: Stream):
    assert (
        mock_player._get_stream_url_from_playlist(mock_stream.href)
        == "https://24453.live.streamtheworld.com:443/WRVOFM_SC"
    )


def test_get_playable_from_stream_pls(mock_player: Player, mock_stream: Stream):
    assert (
        mock_player._get_playable_from_stream(mock_stream)
        == "https://24453.live.streamtheworld.com:443/WRVOFM_SC"
    )


def test_get_playable_from_stream(mock_player: Player, mock_stream: Stream):
    mock_stream.href = "https://24453.live.streamtheworld.com:443/WRVOFM_SC"
    assert (
        mock_player._get_playable_from_stream(mock_stream)
        == "https://24453.live.streamtheworld.com:443/WRVOFM_SC"
    )


def test_play(mock_player: Player, mock_stream: Stream):
    mock_player.play(mock_stream)
    assert mock_player.now_playing == mock_stream
    assert isinstance(mock_player.player, mock_player.player_class)


def test_stop_when_playing(mock_player: Player, mock_stream: Stream):
    mock_player.now_playing = mock_stream
    mock_player.player = mock_player.player_class(mock_stream.href)
    mock_player.stop()

    assert mock_player.now_playing is None
    assert mock_player.player is None


def test_stop_when_not_playing(mock_player: Player):
    mock_player.stop()

    assert mock_player.now_playing is None
    assert mock_player.player is None
