from typing import Any, Callable

from npr.domain import Action, Stream
from npr.domain.exceptions import FailedActionException, UnknownActionException


class ActionDispatcher:
    def __init__(self):
        self.handlers = {}

    def react_to(self, action: Action):
        def __decor__(
            f: Callable[..., tuple[Action | None, list[Stream] | Stream | None]]
        ):
            self.handlers[action] = f
            return f

        return __decor__

    def execute(self, action: Action, *args: Any, **kwargs: Any):
        if controller := self.handlers.get(action):
            try:
                return controller(*args, **kwargs)
            except Exception:
                raise FailedActionException(action)
        else:
            raise UnknownActionException(action)


dispatcher = ActionDispatcher()
