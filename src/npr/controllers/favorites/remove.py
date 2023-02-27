from npr.app.state import AppState, Stream


def favorites_remove_controller(app_state: AppState, stream: Stream):
    app_state.favorites.remove(stream)
    return None, None
