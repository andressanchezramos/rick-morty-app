from api.config import _configure_logging
from api.backend import RickAndMortyAPI
from api.db import PostgreManager
from api.db import RedisManager
from dotenv import load_dotenv


# Configure logging
logger = _configure_logging(__name__)
# Load env vars
load_dotenv()
# Set-up Postgre Connection
pg_db = PostgreManager()
# Set-up Regis Connection
redis_db = RedisManager()

if __name__ == "__main__":
    """
    Stand-alone module to query the API and store data in both DB and cache
    """
    api = RickAndMortyAPI()
    complete_results, characters = api.get_filtered_characters()
    for char in characters:
        logger.info(char)
    redis_db.store_results("characters", complete_results)
    pg_db.insert_characters(characters)
