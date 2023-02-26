# npr-cli

A simple cli for streaming your favorite npr stations.

## Installation

```bash
pip install npr-cli
```

Installation requires VLC installed, homebrew instructions can be found [here](https://formulae.brew.sh/cask/vlc).

## Usage

```bash
npr
npr search # search stations by name, call or zip code.
npr search -q <your search> # search stations directly.
npr play # play your latest stream.
npr favorites # select a stream from your favorites.
```

## TODO:
- create a daemon to control vlc, it's not ideal to have to keep a terminal open at all times.
- allow over writing of last line in terminal, a giant stack of commands is ugly.
- create a "Now Playing" page to display known metadata about a stream

## Issues

Please report any bugs you encounter as issues to this repository.