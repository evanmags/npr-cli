from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from npr.app.state import AppState
from npr.controllers import get_controllers, stop_controller
from npr.domain import Action


def main_control_loop(app_state: AppState):
    controllers = get_controllers()

    while (next_state := get_next_action(app_state)) and next_state[0] != Action.exit:
        action, args = next_state
        app_state.set_next(*controllers[action](app_state, *args))

    stop_controller(app_state)

    app_state.write()


def get_next_action(app_state: AppState) -> tuple:
    action, *args = app_state.next()
    if action:
        return action, args

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

    choice = inquirer.select(  # type: ignore
        message="Select an option",
        choices=[
            Choice(value=Action.search, name="Search Streams"),
            *choices,
            Separator(),
            Choice(value=Action.exit, name="Exit"),
        ],
    ).execute()

    if choice in [Action.favorites_add, Action.favorites_remove]:
        return choice, (app_state.now_playing,)

    return choice, (None,)
