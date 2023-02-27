from typing import Any

from npr.app.state import AppState


def stop_controller(app_state: AppState, *args: Any):
    if app_state.player:
        app_state.player.stop()

    app_state.now_playing = None

    return None, None
