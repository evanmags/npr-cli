from dataclasses import asdict
from unittest.mock import patch

import pytest
from flask.testing import FlaskClient

from npr.api.server import app
from npr.domain import Stream


@pytest.fixture(scope="function")
def mock_state():
    with patch("npr.api.server.state") as mock:
        mock.load.return_value = mock
        yield mock


@pytest.fixture(scope="function")
def client(mock_state):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def mock_stream():
    return Stream(
        station="wxxi",
        primary=False,
        name="NprNews",
        href="https://npr.stream",
    )


@pytest.fixture(scope="function")
def mock_stream_json(mock_stream):
    return asdict(mock_stream)


def test_health(client: FlaskClient):
    response = client.get("/")
    assert response.text == "live"


def test_play(client: FlaskClient, mock_state, mock_stream, mock_stream_json):
    response = client.post("/play", json=mock_stream_json)
    mock_state.player.play.assert_called_once_with(mock_stream)
    assert mock_state.last_played == mock_stream
    assert response.json == mock_stream_json


def test_play_failure(client: FlaskClient, mock_state):
    mock_state.last_played = None
    client.post("/play", json=None)
    mock_state.player.play.assert_not_called()


def test_now_playing(client: FlaskClient, mock_state, mock_stream, mock_stream_json):
    mock_state.player.now_playing = mock_stream
    response = client.get("/now_playing")
    assert response.json == mock_stream_json


def test_now_playing_404(
    client: FlaskClient, mock_state, mock_stream, mock_stream_json
):
    mock_state.player.now_playing = None
    response = client.get("/now_playing")
    assert response.status_code == 404


def test_stop(client: FlaskClient, mock_state):
    response = client.post("/stop")
    assert response.status_code == 202
    mock_state.player.stop.assert_called_once()


def test_get_favorites(client: FlaskClient, mock_state):
    mock_state.favorites = []
    response = client.get("/favorites")
    assert response.json == []


def test_add_favorite(client: FlaskClient, mock_state, mock_stream_json, mock_stream):
    mock_state.favorites = []
    response = client.post("/favorites", json=mock_stream_json)
    assert response.status_code == 201
    assert mock_state.favorites == [mock_stream]


def test_add_favorite_now_playing(client: FlaskClient, mock_state, mock_stream):
    mock_state.favorites = []
    mock_state.player.now_playing = mock_stream
    response = client.post("/favorites")
    assert response.status_code == 201
    assert mock_state.favorites == [mock_stream]


def test_add_favorite_failure(client: FlaskClient, mock_state, mock_stream):
    mock_state.favorites = []
    mock_state.player.now_playing = None
    response = client.post("/favorites")
    assert response.status_code == 400
    assert mock_state.favorites == []


def test_remove_favorite(client: FlaskClient, mock_state, mock_stream):
    mock_state.favorites = [mock_stream]
    response = client.delete(f"/favorites/{mock_stream.station}/{mock_stream.name}")
    assert response.status_code == 204
    assert mock_state.favorites == []


def test_remove_favorite_not_exits(client: FlaskClient, mock_state):
    mock_state.favorites = []
    response = client.delete("/favorites/wxxi/nprnews")
    assert response.status_code == 204
    assert mock_state.favorites == []
