import time
from dataclasses import asdict
from functools import wraps
from typing import Any

import requests

from npr.domain import Stream
from npr.domain.constants import NPR_CLI_SERVER_URL
from npr.domain.exceptions import DaemonNotRunningException


def handle_request_errors_with(return_value: Any):
    def __decorator__(f):
        @wraps(f)
        def __wrapper__(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except requests.ConnectionError:
                raise DaemonNotRunningException()
            except requests.HTTPError:
                if isinstance(return_value, Exception):
                    raise return_value
                return return_value

        return __wrapper__

    return __decorator__


class Backend:
    def __init__(self, backend_url: str = NPR_CLI_SERVER_URL) -> None:
        self._url = backend_url

    @handle_request_errors_with(DaemonNotRunningException())
    def health(self):
        response = requests.get(self._url)
        response.raise_for_status()

        return True

    def poll_health(
        self,
        poll_for: bool = True,
        poll_count: int = 20,
        poll_interval: float = 0.5,
    ) -> bool:
        """
        Checks status of the daemon service.

        Arguments:
            poll_for: bool -> Sigil value to poll for
            poll_count: int -> Max number of polls
            poll_interval: float -> Time to wait between polls

        Returns:
            bool -> True if the service is up, False if not
        """

        _count = poll_count if poll_for in [True, False] else 1
        _status = False
        while _count:
            try:
                self.health()
                _status = True
            except DaemonNotRunningException:
                _status = False

            if _status == poll_for:
                return _status

            _count -= 1
            time.sleep(poll_interval)

        return _status

    @handle_request_errors_with(None)
    def play(self, stream: Stream | None):
        response = requests.post(
            self._url + "/play", json=asdict(stream) if stream else stream
        )
        response.raise_for_status()
        return Stream(**response.json())

    @handle_request_errors_with(None)
    def now_playing(self) -> Stream | None:
        response = requests.get(self._url + "/now_playing")
        if response.status_code == 200 and (data := response.json()):
            return Stream(**data)
        elif response.status_code == 404:
            return None

        response.raise_for_status()

    def stop(self) -> None:
        response = requests.post(self._url + "/stop")
        response.raise_for_status()

    @handle_request_errors_with([])
    def get_favorites(self) -> list[Stream]:
        response = requests.get(self._url + "/favorites")
        response.raise_for_status()
        return [Stream(**d) for d in response.json()]

    def add_favorite(self, stream: Stream) -> None:
        response = requests.post(self._url + "/favorites", json=asdict(stream))
        response.raise_for_status()

    def remove_favorite(self, stream: Stream) -> None:
        response = requests.delete(
            self._url + f"/favorites/{stream.station}/{stream.name}"
        )
        response.raise_for_status()


backend = Backend()
