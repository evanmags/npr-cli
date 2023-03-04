from unittest.mock import patch

import pytest

from npr.cli.controller import get_next_action, main_control_loop
from npr.domain import Action, Stream


@pytest.fixture(scope="function")
def mock_backend():
    with patch("npr.cli.controller.backend") as mock:
        mock.now_playing.return_value = None
        mock.get_favorites.return_value = []
        yield mock


@pytest.fixture(scope="function")
def mock_dispatcher():
    with patch("npr.cli.controller.dispatcher.execute") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_select_prompt():
    with patch("npr.cli.controller.inquirer.select.execute") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_get_next_action():
    with patch("npr.cli.controller.get_next_action") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_stream():
    return Stream(
        primary=False,
        station="wxxi",
        name="npr_news",
        href="https://npr.stream",
    )


class TestGetNextAction:
    def test_list_favorites_select(self, mock_backend, mock_stream, mock_select_prompt):
        mock_backend.get_favorites.return_value = [mock_stream]
        mock_select_prompt.return_value = Action.favorites_list
        next_action = get_next_action(mock_backend)

        assert next_action == (Action.favorites_list, [mock_stream])

    def test_add_favorites_select(self, mock_backend, mock_select_prompt):
        mock_backend.now_playing.return_value = mock_stream
        mock_select_prompt.return_value = Action.favorites_add
        next_action = get_next_action(mock_backend)

        assert next_action == (Action.favorites_add, mock_stream)

    def test_other_select(self, mock_backend, mock_select_prompt):
        mock_select_prompt.return_value = Action.search
        next_action = get_next_action(mock_backend)

        assert next_action == (Action.search, None)


class TestMainControlLoop:
    def test_action_exit(self, mock_dispatcher, mock_get_next_action):
        mock_get_next_action.return_value = Action.exit, None
        main_control_loop(action=None)
        mock_dispatcher.assert_not_called()

    def test_non_exit_action(self, mock_dispatcher):
        mock_dispatcher.return_value = None, None
        main_control_loop(action=Action.search, run_repl=False)
        mock_dispatcher.assert_called_once_with(Action.search, None)
