from npr import __version__
from npr.api.migrations.migrator import migrator


@migrator.register("0.1.1")
def migration(obj: dict):
    favorites: list[dict] = obj.get("favorites", [])
    last_played: dict = obj.get("last_played", None)

    faves = []
    for f in favorites:
        f["name"] = f.get("title")
        del f["title"]
        faves.append(f)

    last_played["name"] = last_played.get("title")
    del last_played["title"]

    return {"__version__": __version__, "favorites": faves, "last_played": last_played}
