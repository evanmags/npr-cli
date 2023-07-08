from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import LoadingIndicator, Static

from npr.domain import Stream
from npr.tui.components.buttons import PlayButton, RemoveFavoriteButton


class FavoritesListItem(Widget):
    def __init__(self, stream) -> None:
        super().__init__(classes="favorite")
        self.stream = stream

    def compose(self) -> ComposeResult:
        yield Static(self.stream.station)
        yield Static(self.stream.name)
        yield PlayButton(self.stream)
        yield RemoveFavoriteButton(self.stream)


class FavoritesList(Widget):
    favorites: reactive[list[Stream]] = reactive([])
    has_rendered = False

    def __init__(self, favorites: list):
        super().__init__(classes="favorites-list")
        self.favorites = favorites

    def watch_favorites(self, old_favorites: list[Stream], new_favorites: list[Stream]):
        if not self.has_rendered:
            return

        self.log(old_favorites, new_favorites)
        dif = []

        if len(old_favorites) > len(new_favorites):
            dif = [s for s in old_favorites if s not in new_favorites]
            for fli in self.query(FavoritesListItem):
                if fli.stream in dif:
                    fli.remove()

        elif len(old_favorites) < len(new_favorites):
            dif = [s for s in new_favorites if s not in old_favorites]
            container = self.query_one(Container)
            for s in dif:
                container.mount(FavoritesListItem(s))

        else:
            return

        self.refresh(layout=True)

    def compose(self):
        self.has_rendered = True
        if self.favorites:
            yield Container(*[FavoritesListItem(s) for s in self.favorites])
        else:
            yield LoadingIndicator()
