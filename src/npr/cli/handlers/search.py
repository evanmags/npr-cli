from typing import Protocol, TypeVar

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from npr.domain import Action, Station, Stream
from npr.services.npr import NPRAPI

api = NPRAPI()


def search(
    query: str | None = None,  # type: ignore
) -> tuple[Action, Stream] | tuple[None, None]:
    if query is None:
        query: str = inquirer.text(  # type: ignore
            "Station name, call, or zip code:",
            mandatory=True,
            validate=lambda x: bool(x),
        ).execute()

    stations = api.search_stations(query)

    if (station := user_select_station(stations)) and (
        stream := user_select_stream(station.streams)
    ):
        return Action.play, stream

    return None, None


class _T(Protocol):
    name: str


T = TypeVar("T", bound=_T)


def user_select_from_list(prompt: str, _list: list[T]) -> T | None:
    if not _list:
        return None
    elif len(_list) == 1:
        return _list[0]

    _map = {s.name: s for s in _list}
    _name = inquirer.select(  # type: ignore
        message=prompt,
        choices=[
            *_map.keys(),
            Separator(),
            Choice(value=None, name="Main Menu"),
        ],
    ).execute()

    if _name:
        return _map[_name]


def user_select_station(stations: list[Station]) -> Station | None:
    return user_select_from_list("Select a station", stations)


def user_select_stream(streams: list[Stream]) -> Stream | None:
    return user_select_from_list("Select a stream", streams)
