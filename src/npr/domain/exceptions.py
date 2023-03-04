from npr.domain import Action


class DaemonNotRunningException(Exception):
    pass


class FailedActionException(Exception):
    def __init__(self, action: Action) -> None:
        super().__init__(action.value)
        self.action = action


class UnknownActionException(Exception):
    def __init__(self, action: Action) -> None:
        super().__init__(action.value)
        self.action = action
