from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Static

from npr.services import backendapi, nprapi
from npr.tui.components.buttons import (
    AddFavoriteButton,
    PlayButton,
    RemoveFavoriteButton,
)


class Search(Widget):
    query: reactive[str] = reactive("")

    not_found_text = "No Streams Found 🤔"

    DEFAULT_CSS = """
    Search > Container {
        width: 100%;
        padding: 1;
    }

    Search Static {
        content-align: center middle;
    }

    #not_found {
        content-align: center middle;
        background: blue;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(self.query, "Station name, call, or zip code", id="search-input")
        yield Container(SearchResult(None), id="results")

    def on_input_changed(self, event: Input.Changed):
        favorites = backendapi.get_favorites()
        results_display = self.query_one("#results")
        results_display.query(SearchResult).remove()
        if not event.value or not (
            streams := nprapi.search_streams_by_station(event.value)
        ):
            results_display.mount(SearchResult(None))
        else:
            results_display.mount_all(SearchResult(s, s in favorites) for s in streams)

        self.mount(results_display)


class SearchResult(Widget):
    def __init__(self, stream, is_favorite=False) -> None:
        super().__init__(classes=("search-result" if stream else "not-found"))
        self.stream = stream
        self.is_favorite = is_favorite

    def compose(self) -> ComposeResult:
        if self.stream is None:
            yield Static("No Streams Found 🤔")
        else:
            yield Static(self.stream.station)
            yield Static(self.stream.name)
            yield PlayButton(self.stream)
            yield (
                RemoveFavoriteButton(self.stream)
                if self.is_favorite
                else AddFavoriteButton(self.stream)
            )
