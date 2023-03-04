import pytest

from npr.cli.handlers.dispatcher import ActionDispatcher
from npr.domain import Action
from npr.domain.exceptions import FailedActionException, UnknownActionException


def func(*args):
    return None, None


def func_raises(*args):
    raise Exception()


def test_react_to():
    d = ActionDispatcher()
    d.react_to(Action.exit)(func)

    assert d.handlers[Action.exit] is func


def test_dispatch():
    d = ActionDispatcher()
    d.react_to(Action.exit)(func)

    assert d.execute(Action.exit) == (None, None)


def test_dispatch_unknown_action():
    d = ActionDispatcher()

    with pytest.raises(UnknownActionException) as exc_info:
        d.execute(Action.exit)

    assert exc_info.value.action is Action.exit


def test_dispatch_failed_action():
    d = ActionDispatcher()
    d.react_to(Action.exit)(func_raises)

    with pytest.raises(FailedActionException) as exc_info:
        d.execute(Action.exit)

    assert exc_info.value.action is Action.exit
