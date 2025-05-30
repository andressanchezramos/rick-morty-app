import pytest
import json
from unittest.mock import patch, MagicMock
from api.db import RedisManager, PostgreManager


# === RedisManager Tests ===
@patch("api.db.redis.Redis")
def test_store_results_sets_data_with_ttl(mock_redis_class):
    mock_redis = MagicMock()
    mock_redis_class.return_value = mock_redis

    rm = RedisManager()
    test_key = "characters"
    test_data = [{"id": 1, "name": "Rick Sanchez"}]

    rm.store_results(test_key, test_data)

    mock_redis.setex.assert_called_once_with(
        name=test_key, time=rm.ttl, value=json.dumps(test_data)
    )


@patch("api.db.redis.Redis")
def test_get_results_returns_data(mock_redis_class):
    mock_redis = MagicMock()
    mock_redis.get.return_value = json.dumps([{"id": 1, "name": "Rick"}])
    mock_redis_class.return_value = mock_redis

    rm = RedisManager()
    result = rm.get_results("characters")

    assert result == [{"id": 1, "name": "Rick"}]


# === PostgreManager Tests ===
@patch("api.db.psycopg2.connect")
def test_postgre_manager_creates_table_and_inserts_data(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    pm = PostgreManager()
    characters = [
        {
            "name": "Rick Sanchez",
            "origin": "Earth (C-137)",
            "status": "Alive",
            "species": "Human",
        }
    ]

    pm.insert_characters(characters)

    # Check table creation was triggered
    assert (
        mock_cursor.execute.call_args_list[0][0][0]
        .strip()
        .startswith("CREATE TABLE IF NOT EXISTS")
    )

    # Check insert call
    mock_cursor.execute.assert_any_call(
        """
                    INSERT INTO characters (name, origin, status, species)
                    VALUES (%s, %s, %s, %s);
                """,
        ("Rick Sanchez", "Earth (C-137)", "Alive", "Human"),
    )
