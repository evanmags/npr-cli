from dataclasses import asdict
from unittest.mock import patch

import pytest
from requests.exceptions import ConnectionError, HTTPError

from npr.domain import Stream
from npr.domain.exceptions import DaemonNotRunningException
from npr.services.backend import Backend, backend


@pytest.fixture(scope="function")
def mock_requests():
    with patch("npr.services.backend.requests") as mock:
        mock.ConnectionError = ConnectionError
        mock.HTTPError = HTTPError
        mock.get.return_value = mock
        mock.post.return_value = mock
        mock.delete.return_value = mock
        yield mock


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


def raise_connection_error(*args, **kwargs):
    raise ConnectionError()


def raise_http_error(*args, **kwargs):
    raise HTTPError()


def raise_daemon_not_running_exception(*args, **kwargs):
    raise DaemonNotRunningException()


def test_health(mock_requests):
    assert backend.health() is True


def test_health_raises_connection_error(mock_requests):
    mock_requests.get.side_effect = raise_connection_error
    with pytest.raises(DaemonNotRunningException):
        backend.health()


def test_health_raises_http_error(mock_requests):
    mock_requests.get.side_effect = raise_http_error
    with pytest.raises(DaemonNotRunningException):
        backend.health()


def test_poll_health_fails(mock_requests):
    with patch.object(backend, "health") as mock_backend:
        mock_backend.health.side_effect = raise_daemon_not_running_exception
        mock_backend.poll_health.side_effect = Backend.poll_health

        assert not mock_backend.poll_health(
            mock_backend, poll_for=True, poll_count=5, poll_interval=0.01
        )
        assert mock_backend.health.call_count == 5


def test_poll_health_succeeds(mock_requests):
    with patch.object(backend, "health") as mock_backend:
        mock_backend.poll_health.side_effect = Backend.poll_health

        assert mock_backend.poll_health(
            mock_backend, poll_for=True, poll_count=5, poll_interval=0.01
        )
        assert mock_backend.health.call_count == 1


def test_play(mock_requests, mock_stream, mock_stream_json):
    mock_requests.json.return_value = mock_stream_json

    assert backend.play(mock_stream) == mock_stream


def test_now_playing(mock_requests, mock_stream, mock_stream_json):
    mock_requests.json.return_value = mock_stream_json
    mock_requests.status_code = 200

    assert backend.now_playing() == mock_stream


def test_now_playing_404(mock_requests):
    mock_requests.status_code = 404

    assert backend.now_playing() is None


def test_now_playing_raises(mock_requests):
    mock_requests.raise_for_status.side_effect = raise_http_error

    assert backend.now_playing() is None


def test_stop(mock_requests):
    backend.stop()

    mock_requests.post.assert_called_with(
        backend._url + "/stop",
    )


def test_get_favorites(mock_requests, mock_stream_json, mock_stream):
    mock_requests.json.return_value = [mock_stream_json]

    assert backend.get_favorites() == [mock_stream]
    mock_requests.get.assert_called_with(
        backend._url + "/favorites",
    )


def test_add_favorite(mock_requests, mock_stream, mock_stream_json):
    backend.add_favorite(mock_stream)

    mock_requests.post.assert_called_with(
        backend._url + "/favorites",
        json=mock_stream_json,
    )


def test_remove_favorite(mock_requests, mock_stream):
    backend.remove_favorite(mock_stream)

    mock_requests.delete.assert_called_with(
        backend._url + f"/favorites/{mock_stream.station}/{mock_stream.name}",
    )
