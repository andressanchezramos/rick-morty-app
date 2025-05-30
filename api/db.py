import os
import json
import psycopg2
import redis


class RedisManager:
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
        )
        self.ttl = int(os.getenv("REDIS_TTL", 3600))  # default 1 hour

    def store_results(self, key: str, results: list[dict]) -> None:
        """
        Store the full 'results' list in Redis under the given key, with TTL.
        """
        json_data = json.dumps(results)
        self.client.setex(name=key, time=self.ttl, value=json_data)

    def get_results(self, key: str) -> list[dict] | None:
        """
        Retrieve the stored results by key, if available.
        """
        data = self.client.get(key)
        return json.loads(data) if data else None

    def check_connection(self) -> bool:
        try:
            return self.client.ping()
        except redis.RedisError:
            return False


class PostgreManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", 5432),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
        )
        self.conn.autocommit = True
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS characters (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    origin TEXT,
                    status TEXT,
                    species TEXT
                );
            """
            )

    def insert_characters(self, results: list[dict]) -> None:
        """
        Insert simplified character info into PostgreSQL.
        """
        with self.conn.cursor() as cur:
            for character in results:
                cur.execute(
                    """
                    INSERT INTO characters (name, origin, status, species)
                    VALUES (%s, %s, %s, %s);
                """,
                    (
                        character.get("name"),
                        character.get("origin"),
                        character.get("status"),
                        character.get("species"),
                    ),
                )

    # def fetch_all_characters(self, sort: str = "asc") -> list[dict]:
    #    if sort.lower() not in ("asc", "desc"):
    #        sort = "asc"  # fallback to default
    #
    #    with self.conn.cursor() as cur:
    #        query = f"SELECT name, origin, status, species FROM characters ORDER BY name {sort.upper()};"
    #        cur.execute(query)
    #        rows = cur.fetchall()
    #        columns = [desc[0] for desc in cur.description]
    #        result = [dict(zip(columns, row)) for row in rows]
    #        return json.dumps(result)

    def fetch_all_characters(
        self, sort: str = "asc", page: int = 1, limit: int = 10
    ) -> dict:
        if sort.lower() not in ("asc", "desc"):
            sort = "asc"

        offset = (page - 1) * limit

        with self.conn.cursor() as cur:
            # Get total count
            cur.execute("SELECT COUNT(*) FROM characters;")
            total = cur.fetchone()[0]

            # Get paginated results
            query = f"""
                SELECT name, origin, status, species
                FROM characters
                ORDER BY name {sort.upper()}
                LIMIT %s OFFSET %s;
            """
            cur.execute(query, (limit, offset))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in rows]

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,  # ceiling division
            "results": results,
        }

    def check_connection(self) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return True
        except psycopg2.Error:
            return False
