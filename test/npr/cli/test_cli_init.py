from unittest.mock import patch

import pytest
from click import ClickException
from click.testing import CliRunner

from npr.cli import (
    domain_err_to_click_err,
    down,
    favorites,
    npr,
    play,
    search,
    stop,
    up,
)
from npr.domain import Action
from npr.domain.exceptions import (
    DaemonNotRunningException,
    FailedActionException,
    UnknownActionException,
)


@pytest.fixture(scope="function")
def mock_main_control_loop():
    with patch("npr.cli.main_control_loop") as mock:
        yield mock


@pytest.fixture(scope="function", autouse=True)
def mock_backend():
    with patch("npr.cli.backendapi") as mock:
        mock.health.return_value = True
        yield mock


class TestDomainErrToClickErr:
    @domain_err_to_click_err
    def func(self, exc: Exception):
        raise exc

    def test_raises_domain_not_running(self):
        with pytest.raises(ClickException) as exc:
            self.func(DaemonNotRunningException())

        assert (
            "The npr-cli daemon is not running. Run `npr up` to start."
            in exc.value.message
        )

    def test_raises_failed_action(self):
        with pytest.raises(ClickException) as exc:
            self.func(FailedActionException(Action.exit))

        assert f"Failed to execute action `{Action.exit.value}`." in exc.value.message

    def test_raises_unknown_action(self):
        with pytest.raises(ClickException) as exc:
            self.func(UnknownActionException(Action.exit))

        assert (
            f"Action `{Action.exit.value}` is unknown to npr-cli." in exc.value.message
        )


class TestNpr:
    def test_npr(self, mock_main_control_loop):
        runner = CliRunner()
        runner.invoke(npr)  # type: ignore
        mock_main_control_loop.assert_called_once_with()

    def _health_side_effect_raises(self):
        raise DaemonNotRunningException()

    def test_npr_no_daemon(self, mock_main_control_loop, mock_backend):
        mock_backend.health.side_effect = self._health_side_effect_raises
        runner = CliRunner()
        result = runner.invoke(npr)  # type: ignore
        mock_main_control_loop.assert_not_called()
        assert (
            "The npr-cli daemon is not running. Run `npr up` to start." in result.output
        )


class TestUp:
    def test_up(self, mock_main_control_loop):
        runner = CliRunner()
        result = runner.invoke(up)
        assert "Daemon is already running." in result.output
        mock_main_control_loop.assert_not_called()

    def test_up_no_daemon(self, mock_main_control_loop, mock_backend):
        mock_backend.poll_health.return_value = False
        runner = CliRunner()
        result = runner.invoke(up)
        assert "Starting npr-cli daemon." in result.output
        mock_main_control_loop.assert_called_once_with(
            action=Action.up,
            run_repl=False,
        )


class TestDown:
    def test_down(self, mock_main_control_loop, mock_backend):
        mock_backend.health.return_value = False
        runner = CliRunner()
        result = runner.invoke(down)
        assert "Stopping npr-cli daemon." in result.output
        mock_main_control_loop.assert_called_once_with(
            action=Action.down,
            run_repl=False,
        )

    def test_down_no_daemon(self, mock_main_control_loop, mock_backend):
        mock_backend.health.return_value = False
        runner = CliRunner()
        result = runner.invoke(down)
        assert "Stopping npr-cli daemon." in result.output
        mock_main_control_loop.assert_called_once_with(
            action=Action.down,
            run_repl=False,
        )


class TestSearch:
    def test_search_no_query(self, mock_main_control_loop):
        runner = CliRunner()
        runner.invoke(search)
        mock_main_control_loop.assert_called_once_with(
            action=Action.search,
            arg=None,
            run_repl=False,
        )

    def test_search_with_query(self, mock_main_control_loop):
        runner = CliRunner()
        runner.invoke(search, ["-q", "wxxi"])
        mock_main_control_loop.assert_called_once_with(
            action=Action.search,
            arg="wxxi",
            run_repl=False,
        )


def test_play(mock_main_control_loop):
    runner = CliRunner()
    runner.invoke(play)
    mock_main_control_loop.assert_called_once_with(
        action=Action.play,
        run_repl=False,
    )


def test_stop(mock_main_control_loop):
    runner = CliRunner()
    runner.invoke(stop)
    mock_main_control_loop.assert_called_once_with(
        action=Action.stop,
        run_repl=False,
    )


def test_favorites(mock_main_control_loop):
    runner = CliRunner()
    runner.invoke(favorites)
    mock_main_control_loop.assert_called_once_with(
        action=Action.favorites_list,
        run_repl=False,
    )
