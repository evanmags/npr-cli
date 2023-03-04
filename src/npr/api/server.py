from dataclasses import asdict
from http import HTTPStatus

from flask import Flask, request

from npr.api.helpers import init_logging, init_npr_files, marshal_stream_from_request
from npr.api.state import AppState

app = Flask(__name__)
init_npr_files()
init_logging(app)

state = AppState.load()


@app.after_request
def after_request(response):
    state.write()
    return response


@app.get("/")
def index():
    return "live"


@app.post("/play")
def play():
    stream = marshal_stream_from_request(request) or state.last_played
    if stream:
        state.player.play(stream)
        state.last_played = stream
        return asdict(stream), HTTPStatus.ACCEPTED

    return "", HTTPStatus.BAD_REQUEST


@app.get("/now_playing")
def playing():
    if state.player.now_playing:
        return asdict(state.player.now_playing)

    return "", HTTPStatus.NOT_FOUND


@app.post("/stop")
def stop():
    state.player.stop()
    return "", HTTPStatus.ACCEPTED


@app.get("/favorites")
def favorites():
    return state.favorites


@app.post("/favorites")
def favorites_create():
    stream = marshal_stream_from_request(request) or state.player.now_playing
    if stream:
        if stream not in state.favorites:
            state.favorites.append(stream)

        return "", HTTPStatus.CREATED

    return "", HTTPStatus.BAD_REQUEST


@app.delete("/favorites/<station>/<stream>")
def favorites_delete(station: str, stream: str):
    state.favorites = [
        s for s in state.favorites if s.station != station and s.name != stream
    ]

    return "", HTTPStatus.NO_CONTENT
