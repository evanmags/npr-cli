from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from npr.api import NPRAPI
from npr.app.state import AppState
from npr.domain import Action, Station, Stream


api = NPRAPI()


def search_controller(
    app_state: AppState,
    query: str | None = None,  # type: ignore
):
    if query is None:
        query: str = inquirer.text(  # type: ignore
            "Station name, call, or zip code:",
            mandatory=True,
            validate=lambda x: bool(x),
        ).execute()

    stations = api.search_stations(query)

    if station := user_select_station(stations):
        if stream := user_select_stream(station):
            return Action.play, stream

    return None, None


def user_select_station(stations: list[Station]) -> Station | None:
    station_map = {s.name: s for s in stations}
    if not stations:
        return None
    elif len(stations) == 1:
        station_name = stations[0].name
    else:
        station_name = inquirer.select(  # type: ignore
            message="Select a station to continue",
            choices=[
                *station_map.keys(),
                Separator(),
                Choice(value=None, name="Main Menu"),
            ],
        ).execute()
    if station_name:
        return station_map[station_name]


def user_select_stream(station: Station) -> Stream | None:
    stream_map = {s.title: s for s in station.streams}

    stream_name = inquirer.select(  # type: ignore
        message=f"Select a stream from {station.name}",
        choices=[
            *stream_map.keys(),
            Separator(),
            Choice(value=None, name="Main Menu"),
        ],
    ).execute()

    if stream_name:
        return stream_map[stream_name]
