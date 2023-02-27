from npr.app.state import AppState, Stream


def favorites_add_controller(app_state: AppState, stream: Stream):
    app_state.favorites.append(stream)
    return None, None
