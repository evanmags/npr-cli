from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from npr.cli.handlers import dispatcher
from npr.domain import Action, Stream
from npr.services.backend import Backend, backend

ControllerInput = list[Stream] | Stream | str | None


def main_control_loop(
    *, action: Action | None = None, arg: ControllerInput = None, run_repl: bool = True
):
    # Allow None actions when repl is running
    # Exit on None actions when repl is not running
    # Always exit on Action.exit
    while run_repl or action is not None:
        if action is None:
            action, arg = get_next_action(backend)
            if action == Action.exit:
                return

        action, arg = dispatcher.execute(action, arg)


def get_next_action(api: Backend) -> tuple[Action, ControllerInput]:
    now_playing = api.now_playing()
    favorites = api.get_favorites()

    choices = [
        Choice(value=Action.play, name="Play Latest")
        if now_playing is None
        else Choice(value=Action.stop, name="Stop Playing"),
        Separator(),
    ]

    if favorites:
        choices.append(Choice(value=Action.favorites_list, name="Show Favorites"))
    if now_playing:
        choices.append(
            Choice(value=Action.favorites_remove, name="Remove from Favorites")
            if now_playing in favorites
            else Choice(value=Action.favorites_add, name="Add to Favorites")
        )

    if favorites or now_playing:
        choices.append(Separator())

    choice = inquirer.select(  # type: ignore
        message="Select an option",
        choices=[
            Choice(value=Action.search, name="Search Streams"),
            *choices,
            Choice(value=Action.exit, name="Exit"),
        ],
    ).execute()

    if choice in [Action.favorites_add, Action.favorites_remove]:
        return choice, now_playing

    if choice is Action.favorites_list:
        return choice, favorites

    return choice, None
