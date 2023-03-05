import json
from dataclasses import asdict
from pathlib import Path

import pytest

from npr.api.state import AppState
from npr.domain import Stream


@pytest.fixture(scope="function")
def mock_stream():
    return Stream(False, "WRVO", "As It Happens", "https://npr.stream")


@pytest.fixture(scope="function")
def mock_state(mock_stream: Stream):
    stream = asdict(mock_stream)
    return dict(
        __version__="0.1.1",
        favorites=[stream],
        last_played=stream,
    )


def test_creates_state_when_none_exists(tmp_path: Path):
    nprrc = tmp_path / "nprrc"
    state = AppState.load(nprrc)

    assert nprrc.exists()
    assert state.favorites == []
    assert state.last_played is None


def test_loads_existing_state(tmp_path: Path, mock_state: dict, mock_stream: Stream):
    nprrc = tmp_path / "nprrc"
    nprrc.touch()
    nprrc.write_text(json.dumps(mock_state))

    state = AppState.load(nprrc)

    assert nprrc.exists()
    assert state.favorites == [mock_stream]
    assert state.last_played == mock_stream


def test_writes_state(tmp_path: Path, mock_state: dict, mock_stream: Stream):
    nprrc = tmp_path / "nprrc"

    state = AppState(
        favorites=[mock_stream],
        last_played=mock_stream,
    )
    state.write(nprrc)

    ser_state = json.loads(nprrc.read_text())
    assert ser_state == mock_state
