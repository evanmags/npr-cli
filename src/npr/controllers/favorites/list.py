from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from npr.app.state import AppState
from npr.domain import Action


def favorites_list_controller(app_state: AppState, *args):
    stream = inquirer.select(  # type: ignore
        "Select a Stream",
        choices=[
            *[s.title for s in app_state.favorites],
            Separator(),
            Choice(value=None, name="Main Menu"),
        ],
    ).execute()

    if not stream:
        return None, None

    stream = next(s for s in app_state.favorites if s.title == stream)

    action = inquirer.select(  # type: ignore
        "Select Action",
        choices=[
            Choice(value=Action.play, name="Play"),
            Choice(value=Action.favorites_remove, name="Remove"),
            Separator(),
            Choice(value=None, name="Main Menu"),
        ],
    ).execute()

    return action, stream
