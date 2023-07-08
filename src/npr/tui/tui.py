from typing import cast

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Footer, Input, Static

from npr.domain import Action
from npr.services import backendapi
from npr.tui.components.buttons import NprButtonAction
from npr.tui.components.favorites import FavoritesList
from npr.tui.components.now_playing import NowPlaying
from npr.tui.components.search import Search

red = "#c93825"
black = "#010004"
blue = "#3a77bc"
gray = "#D8D4D5"


class Box(Widget):
    def __init__(
        self, title: str, child: Widget | Static, full_width: bool = False
    ) -> None:
        super().__init__(child, classes="full-width" if full_width else None)
        self.border_title = title


class MainContainer(Container):
    border_title = (
        f"[bold][white on {red}] n [/][white on {black}] p [/]"
        f"[white on {blue}] r [/][white]-cli[/]"
    )


class NPRTUI(App):
    TITLE = "npr-cli"

    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("p", "", "play/stop"),
        ("s", "focus_search", "Focus Search"),
        ("ctrl+s", "blur_search", "Blur Search"),
    ]

    CSS = """
    Screen {
        height: 100vh;
        width: 100vw;
        align: center middle;
    }

    .container {
        height: 32;
        width: 120;
        padding: 0;
        border: double #3a77bc;

        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 3fr;
    }

    .full-width {
        column-span: 2;
    }

    Box {
        margin: 1;
        border: solid darkgray;
        padding: 1;
        content-align: center middle;
    }

    NowPlaying {
        height: 1;
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
    }

    NowPlaying > Container {
        layout: horizontal;
    }

    NowPlaying > Container > Static {
        height: 100%;
        width: 1fr;
        content-align: center middle;
    }

    .favorites-list, #results {
        layout: vertical;
    }

    .favorite, .search-result {
        margin: 0 0;
        padding: 0;
        width: 100%;
        height: 3;
        layout: grid;
        grid-size: 4;
        grid-columns: 3fr 3fr 1fr 1fr;
    }

    .favorite > *, .search-result > *, .not-found{
        width: 100%;
        height: 100%;
        content-align: center middle;
        background: transparent;
    }

    Button {
        width: 1fr;
        background: transparent;
        border: none;
        content-align: center middle;
    }

    Button:focus {
        text-style: none;
    }

    Button:hover {
        background: lightgrey;
        border: none
    }
    """

    def compose(self) -> ComposeResult:
        favorites = backendapi.get_favorites()
        now_playing = backendapi.now_playing()
        yield MainContainer(
            Box(
                "Now Playing",
                NowPlaying(
                    now_playing,
                    is_favorite=now_playing in favorites,
                ),
                full_width=True,
            ),
            Box("Favorites", FavoritesList(favorites)),
            Box("Search", Search()),
            Footer(),
            classes="container",
        )

    def action_focus_search(self):
        si = cast(Input, self.query_one("#search-input"))
        si.focus()

    def action_blur_search(self):
        si = cast(Input, self.query_one("#search-input"))
        si.has_focus = False
        si.on_blur()  # type: ignore

    def on_npr_button_action(self, event: NprButtonAction):
        event.stop()
        match event.action:
            case Action.play:
                np = backendapi.play(event.stream)
                npe = self.query_one(NowPlaying)
                npe.stream = np
                npe.is_favorite = np in backendapi.get_favorites()
            case Action.stop:
                backendapi.stop()
                npe = self.query_one(NowPlaying)
                npe.stream = None
                npe.is_favorite = None
            case Action.favorites_add:
                if event.stream:
                    backendapi.add_favorite(event.stream)
                    self.query_one(FavoritesList).favorites = backendapi.get_favorites()
                    np = self.query_one(NowPlaying)
                    if event.stream == np.stream:
                        np.is_favorite = True
            case Action.favorites_remove:
                if event.stream:
                    backendapi.remove_favorite(event.stream)
                    self.query_one(FavoritesList).favorites = backendapi.get_favorites()
                    np = self.query_one(NowPlaying)
                    if event.stream == np.stream:
                        np.is_favorite = False
