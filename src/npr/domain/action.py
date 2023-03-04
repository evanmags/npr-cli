from enum import Enum


class Action(Enum):
    up = "up"
    down = "down"
    search = "search"
    play = "play"
    stop = "stop"
    exit = "exit"
    favorites_list = "favorites_list"
    favorites_add = "favorites_add"
    favorites_remove = "favorites_remove"
