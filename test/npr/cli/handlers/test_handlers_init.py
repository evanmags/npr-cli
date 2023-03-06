from unittest.mock import patch

import pytest

from npr.cli.handlers import (
    down,
    favorites_add,
    favorites_list,
    favorites_remove,
    play,
    stop,
    up,
)
from npr.domain import Action, Stream


@pytest.fixture(scope="function")
def mock_select_prompt():
    with patch("npr.cli.handlers.inquirer.select.execute") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_backend():
    with patch("npr.cli.handlers.backend") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_pidfile():
    with patch("npr.cli.handlers.NPR_PIDFILE") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_popen():
    with patch("npr.cli.handlers.Popen") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_stream():
    return Stream(
        primary=False,
        station="wxxi",
        name="NprNews",
        href="https://npr.stream",
    )


def test_up(mock_backend, mock_popen):
    mock_popen.return_value = mock_popen
    mock_backend.poll_health.return_value = True

    assert up() == (None, None)


def test_down(mock_backend, mock_popen, mock_pidfile):
    mock_pidfile.read_text.return_value = "1234"
    mock_popen.return_value = mock_popen
    mock_backend.poll_health.return_value = False

    assert down() == (None, None)


def test_play(mock_backend):
    assert play() == (None, None)
    mock_backend.play.assert_called_once_with(None)


def test_stop(mock_backend):
    assert stop() == (None, None)
    mock_backend.stop.assert_called_once()


class TestFavoritesList:
    def test_exit(self, mock_backend, mock_select_prompt):
        mock_backend.get_favorites.return_value = []
        mock_select_prompt.return_value = None
        assert favorites_list() == (None, None)

    def test_stream_selected(self, mock_backend, mock_stream, mock_select_prompt):
        mock_backend.get_favorites.return_value = [mock_stream]
        mock_select_prompt.side_effect = [mock_stream.name, Action.play]
        assert favorites_list() == (Action.play, mock_stream)


def test_favorites_add(mock_backend, mock_stream):
    assert favorites_add(mock_stream) == (None, None)
    mock_backend.add_favorite.assert_called_once_with(mock_stream)


def test_favorites_remove(mock_backend, mock_stream):
    assert favorites_remove(mock_stream) == (None, None)
    mock_backend.remove_favorite.assert_called_once_with(mock_stream)
