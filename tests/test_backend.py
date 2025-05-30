import pytest
import requests
from unittest.mock import patch, Mock
from api.backend import RickAndMortyAPI
from requests.exceptions import HTTPError


@pytest.fixture
def api():
    return RickAndMortyAPI()


def test_get_filtered_characters_success(api):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "name": "Rick Sanchez",
                "origin": {"name": "Earth (C-137)"},
                "status": "Alive",
                "species": "Human",
            }
        ],
        "info": {"next": None},
    }

    with patch("requests.get", return_value=mock_response):
        complete_results, characters = api.get_filtered_characters()
        assert len(complete_results) == 1
        assert characters[0]["name"] == "Rick Sanchez"


def test_get_filtered_characters_rate_limited(api):
    mock_429 = Mock(status_code=429, headers={"Retry-After": "1"})
    mock_200 = Mock(status_code=200)
    mock_200.json.return_value = {
        "results": [
            {
                "name": "Morty Smith",
                "origin": {"name": "Earth (Replacement Dimension)"},
                "status": "Alive",
                "species": "Human",
            }
        ],
        "info": {"next": None},
    }

    with patch("requests.get", side_effect=[mock_429, mock_200]):
        complete_results, characters = api.get_filtered_characters()
        assert len(complete_results) == 1
        assert characters[0]["name"] == "Morty Smith"


def test_get_filtered_characters_transient_error(api):
    mock_500 = Mock()
    mock_500.status_code = 500
    mock_500.raise_for_status.side_effect = HTTPError("500 Server Error")

    mock_200 = Mock()
    mock_200.status_code = 200
    mock_200.json.return_value = {
        "results": [
            {
                "name": "Summer Smith",
                "origin": {"name": "Earth (C-500A)"},
                "status": "Alive",
                "species": "Human",
            }
        ],
        "info": {"next": None},
    }
    mock_200.raise_for_status.return_value = None

    with patch("requests.get", side_effect=[mock_500, mock_200]):
        complete_results, characters = api.get_filtered_characters()
        assert len(complete_results) == 1
        assert characters[0]["name"] == "Summer Smith"


def test_get_filtered_characters_network_error(api):
    with patch("requests.get", side_effect=requests.exceptions.RequestException):
        complete_results, characters = api.get_filtered_characters()
        assert complete_results == []
        assert characters == []
