from typing import Callable, Any, ParamSpec, Concatenate

from npr.app.state import AppState
from npr.domain import Action

from npr.controllers.search import search_controller
from npr.controllers.play import play_controller
from npr.controllers.stop import stop_controller
from npr.controllers.favorites.list import favorites_list_controller
from npr.controllers.favorites.add import favorites_add_controller
from npr.controllers.favorites.remove import favorites_remove_controller

Params = ParamSpec("Params")
NextState = tuple

Controller = Callable[Concatenate[AppState, Params], NextState]


def get_controllers() -> dict[Action, Controller]:
    return {
        Action.search: search_controller,
        Action.play: play_controller,
        Action.stop: stop_controller,
        Action.favorites_list: favorites_list_controller,
        Action.favorites_add: favorites_add_controller,
        Action.favorites_remove: favorites_remove_controller,
    }
