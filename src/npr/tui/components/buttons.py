from textual.color import Color
from textual.message import Message
from textual.widgets import Button

from npr.domain import Action, Stream


class NprButtonAction(Message):
    def __init__(self, action: Action, stream: Stream | None = None) -> None:
        super().__init__()
        self.action = action
        self.stream = stream


class NPRButton(Button):
    def __init__(
        self,
        label: str,
        action: Action,
        stream: Stream | None = None,
        disabled: bool = False,
    ):
        super().__init__(f"[ {label} ]", disabled=disabled)
        self.action = action
        self.stream = stream

    def on_button_pressed(self, event: Button.Pressed):
        event.stop()
        self.styles.background = Color(0, 0, 0, 0)
        self.post_message(NprButtonAction(self.action, self.stream))


class PlayButton(NPRButton):
    def __init__(self, stream: Stream | None = None, disabled: bool = False) -> None:
        super().__init__("▶", Action.play, stream, disabled)


class StopButton(NPRButton):
    def __init__(self, stream: Stream | None = None, disabled: bool = False) -> None:
        super().__init__("◼", Action.stop, stream, disabled)


class AddFavoriteButton(NPRButton):
    def __init__(self, stream: Stream) -> None:
        super().__init__("+", Action.favorites_add, stream)


class RemoveFavoriteButton(NPRButton):
    def __init__(self, stream: Stream) -> None:
        super().__init__("-", Action.favorites_remove, stream)
