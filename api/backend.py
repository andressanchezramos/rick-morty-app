import requests
import json
import time
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)
from requests.exceptions import RequestException
from api.config import _configure_logging


class RickAndMortyAPI:
    def __init__(self):
        self.logger = _configure_logging(__name__)
        self.url = "https://rickandmortyapi.com/api/character/"
        self.params = {"species": "Human", "status": "Alive"}

    @retry(
        retry=(
            retry_if_exception_type(RequestException)
            | retry_if_result(lambda r: r is not None and r.status_code == 429)
        ),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(3),
    )
    def _robust_get(self, url, params=None) -> requests.Response:
        """
        Uses tenacity to perform a robust request and retry the request if:
            A RequestException occurs (e.g., network error)
            The response has status code 429 (rate limited)
        Implements exponential backoff and respects the Retry-After header if present.
        """
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                wait_time = int(retry_after)
                self.logger.warning(
                    f"Rate limited. Waiting {wait_time} seconds before retrying..."
                )
                time.sleep(wait_time)

        response.raise_for_status()
        return response

    def get_filtered_characters(self) -> tuple[list, list]:
        """
        Queries the Rick and Morty API and filters it based on the pre-defined params variable and on the "origin" parameter.
        """
        complete_results = []
        characters = []
        execution_params = self.params
        execution_url = self.url

        try:
            while execution_url:
                response = self._robust_get(execution_url, params=execution_params)
                data = response.json()
                complete_results.extend(data["results"])
                for character in data["results"]:
                    if character["origin"]["name"].startswith("Earth"):
                        characters.append(
                            {
                                "name": character["name"],
                                "origin": character["origin"]["name"],
                                "status": character["status"],
                                "species": character["species"],
                            }
                        )
                execution_url = data["info"]["next"]
                execution_params = {}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error: {e}")
        except ValueError:
            self.logger.error("Failed to parse JSON response.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
        else:
            self.logger.info(f"Data retrieved from {self.url} with success")

        return complete_results, characters
