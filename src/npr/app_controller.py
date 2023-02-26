from configparser import ConfigParser
import time

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import requests
import vlc

from npr.api import NPRAPI
from npr.app_state import AppState
from npr.domain import Action, Station, Stream

api = NPRAPI()


def get_controllers():
    return {
        Action.search: search_controller,
        Action.play: play_controller,
        Action.stop: stop_controller,
        Action.favorites_list: favorites_list_controller,
        Action.favorites_add: favorites_add_controller,
        Action.favorites_remove: favorites_remove_controller,
    }


def main_control_loop(app_state: AppState):
    controllers = get_controllers()

    while (action := get_next_action(app_state)) != Action.exit:
        _, args = app_state.next()

        controllers[action](app_state, *args)

    stop_controller(app_state)

    app_state.write()


def get_next_action(app_state: AppState) -> Action:
    action, _ = app_state.next()
    if action:
        return action

    is_playing = app_state.player and app_state.player.is_playing()

    choices = []
    if app_state.last_played and not is_playing:
        choices.append(Choice(value=Action.play, name="Play Latest"))
    if app_state.favorites:
        choices.append(Choice(value=Action.favorites_list, name="Show Favorites"))
    if is_playing:
        choices.append(Choice(value=Action.stop, name="Stop Playing"))
        if app_state.now_playing in app_state.favorites:
            choices.append(
                Choice(value=Action.favorites_remove, name="Remove from Favorites")
            )
        else:
            choices.append(Choice(value=Action.favorites_add, name="Add to Favorites"))

    return inquirer.select(
        message="Select an option",
        choices=[
            Choice(value=Action.search, name="Search Streams"),
            *choices,
            Separator(),
            Choice(value=Action.exit, name="Exit"),
        ],
    ).execute()


def search_controller(app_state: AppState, query: str | None):
    if not query:
        query = inquirer.text(
            "Station name, call, or zip code:",
            mandatory=True,
            validate=lambda x: not not x,
        ).execute()

    stations = api.search_stations(query)

    if (station := user_select_station(stations)) is None:
        app_state.set_next(None, None)
        return

    if (stream := user_select_stream(station)) is None:
        app_state.set_next(None, None)
        return

    if stream:
        app_state.set_next(Action.play, stream)


def user_select_station(stations: list[Station]) -> Station | None:
    station_map = {s.name: s for s in stations}
    if not stations:
        return None
    elif len(stations) == 1:
        station_name = stations[0].name
    else:
        station_name = inquirer.select(
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

    stream_name = inquirer.select(
        message=f"Select a stream from {station.name}",
        choices=[
            *stream_map.keys(),
            Separator(),
            Choice(value=None, name="Main Menu"),
        ],
    ).execute()

    if stream_name:
        return stream_map[stream_name]


def play_controller(app_state: AppState, stream: Stream | None = None):
    if app_state.player:
        app_state.player.stop()

    if stream is None:
        stream = app_state.last_played

    app_state.player = vlc.MediaPlayer(get_playable_from_stream(stream))
    app_state.player.play()

    app_state.now_playing = stream
    app_state.last_played = stream

    # there is a slight delay before the stream actually starts
    # at that point VLC writes an exception to the terminal
    # this can be removed when that exception is hidden.
    time.sleep(1.5)

    app_state.set_next(None)


def get_playable_from_stream(stream: Stream) -> str:
    if stream.is_playlist():
        return get_stream_url_from_playlist(stream.href)
    return stream.href


def get_stream_url_from_playlist(uri: str) -> dict:
    response = requests.get(uri)
    config = ConfigParser()
    config.read_string(response.text)
    return config["playlist"]["file1"]


def stop_controller(app_state: AppState):
    if app_state.player:
        app_state.player.stop()

    app_state.now_playing = None

    app_state.set_next(None)


def favorites_list_controller(app_state: AppState):
    stream = inquirer.select(
        "Select a Stream",
        choices=[
            *[s.title for s in app_state.favorites],
            Separator(),
            Choice(value=None, name="Main Menu"),
        ],
    ).execute()
    if stream:
        stream = next(s for s in app_state.favorites if s.title == stream)

        action = inquirer.select(
            "Select Action",
            choices=[
                Choice(value=Action.play, name="Play"),
                Choice(value=Action.favorites_remove, name="Remove"),
                Separator(),
                Choice(value=None, name="Main Menu"),
            ],
        ).execute()
        print(action, stream)
        app_state.set_next(action, stream)
        return

    app_state.set_next(None, None)


def favorites_add_controller(app_state: AppState):
    app_state.favorites.append(app_state.now_playing)
    app_state.set_next(None)


def favorites_remove_controller(app_state: AppState, stream: Stream | None = None):
    app_state.favorites.remove(stream or app_state.now_playing)
    app_state.set_next(None)
