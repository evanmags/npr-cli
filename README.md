# npr-cli

A simple cli for streaming your favorite npr stations.

## Installation

```bash
pip install npr-cli
```

Installation requires VLC, homebrew instructions can be found [here](https://formulae.brew.sh/cask/vlc).

## Usage

```bash
npr

npr up # start the npr daemon
npr down  # stop the npr daemon

npr search # search stations by name, call or zip code.
npr search -q <your search> # search stations directly.

npr play # play your latest stream.
npr stop # stop streaming

npr favorites # select a stream from your favorites.
```

## TODO:
- Better handling of daemon, launchd/systemd
- Run daemon behind gunicorn/uvicorn
- Allow over writing of last line in terminal, a giant stack of commands is ugly.
- Create a "Now Playing" page to display known metadata about a stream
- `npr report` to report errors as issues in GH.
    - report streams that wont play
        - acceptance criteria:
            - should read `.npr/log/error.log` and send content as part of issue
            - should send stream object.
            - should not create issues for open issues with the same stream
    - report recent errors, this is long term

## Issues

Please report any bugs you encounter as issues to this repository.