from typing import cast

from textual.app import ComposeResult
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from npr.domain import Stream
from npr.tui.components.buttons import (
    AddFavoriteButton,
    PlayButton,
    RemoveFavoriteButton,
    StopButton,
)


class NowPlaying(Widget):
    stream: reactive[Stream | None] = reactive[Stream | None](None, always_update=True)
    is_favorite: reactive[bool | None] = reactive[bool | None](None)

    def __init__(self, playing: Stream | None, is_favorite: bool) -> None:
        super().__init__()
        self.stream = playing
        self.is_favorite = is_favorite

    def watch_is_favorite(self, old: bool, new: bool):
        try:
            self.query(RemoveFavoriteButton).remove()
        except NoMatches:
            pass
        try:
            self.query(AddFavoriteButton).remove()
        except NoMatches:
            pass

        if new is None or self.stream is None:
            return

        try:
            self.query_one("#np-buttons").mount(
                RemoveFavoriteButton(self.stream)
                if new
                else AddFavoriteButton(self.stream)
            )
        except NoMatches:
            self.log("here")

    def watch_stream(self):
        if self.stream is not None:
            try:
                cast(Static, self.query_one("#station")).update(
                    f"📡 {self.stream.station}"
                )
                cast(Static, self.query_one("#stream-name")).update(
                    f"🎵 {self.stream.name}"
                )
                self.query_one(PlayButton).disabled = True
                self.query_one(StopButton).disabled = False
            except NoMatches:
                pass

        else:
            try:
                cast(Static, self.query_one("#station")).update("Nothing Playing 🎧")
                cast(Static, self.query_one("#stream-name")).update("")
                self.query_one(PlayButton).disabled = False
                self.query_one(StopButton).disabled = True
            except NoMatches:
                pass

    def compose(self) -> ComposeResult:
        yield Container(
            Static(
                f"📡 {self.stream.station}" if self.stream else "Nothing Playing 🎧",
                id="station",
            ),
            Static(
                f"🎵 {self.stream.name}" if self.stream else "",
                id="stream-name",
            ),
        )
        yield Container(
            PlayButton(self.stream, disabled=self.stream is not None),
            StopButton(self.stream, disabled=self.stream is None),
            *[
                RemoveFavoriteButton(s) if self.is_favorite else AddFavoriteButton(s)
                for s in [self.stream]
                if s is not None
            ],
            id="np-buttons",
        )
