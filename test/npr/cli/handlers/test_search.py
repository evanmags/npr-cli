from unittest.mock import patch

import pytest

from npr.cli.handlers.search import search, user_select_from_list
from npr.domain import Action, Station, Stream


@pytest.fixture(scope="function")
def mock_select_prompt():
    with patch("npr.cli.handlers.search.inquirer.select.execute") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_text_prompt():
    with patch("npr.cli.handlers.search.inquirer.text.execute") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_api_call():
    with patch("npr.cli.handlers.search.api.search_stations") as mock:
        yield mock


class TestSearch:
    def test_api_returns_no_stations(self, mock_api_call):
        mock_api_call.return_value = []
        assert search("wxxi") == (None, None)

    def test_no_query(self, mock_text_prompt, mock_api_call):
        mock_text_prompt.return_value = "wxxi"
        mock_api_call.return_value = []
        search()
        mock_text_prompt.assert_called_once()

    def test_search(self, mock_api_call):
        stream = Stream(
            False,
            "wxxi",
            "NprNews",
            "https://npr.stream",
        )
        mock_api_call.return_value = [
            Station("wxxi", "wxxi", [stream]),
        ]

        assert search("wxxi") == (Action.play, stream)


class TestUserSelectFromList:
    class NamedObject:
        def __init__(self, name: str):
            self.name = name

    def test_empty_list(self):
        assert user_select_from_list("", []) is None

    def test_len_one(self):
        no = self.NamedObject("no")
        assert user_select_from_list("", [no]) is no

    def test_prompt_returns_none(self, mock_select_prompt):
        no1 = self.NamedObject("no1")
        no2 = self.NamedObject("no2")
        mock_select_prompt.side_effect = lambda: None
        assert user_select_from_list("", [no1, no2]) is None

    def test_prompt_returns_item(self, mock_select_prompt):
        no1 = self.NamedObject("no1")
        no2 = self.NamedObject("no2")
        mock_select_prompt.side_effect = lambda: no1.name
        assert user_select_from_list("", [no1, no2]) is no1
