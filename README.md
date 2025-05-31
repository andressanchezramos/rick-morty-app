# Rick & Morty Character Service

This project provides a REST API to collect, store, and query character data from the Rick and Morty API: https://rickandmortyapi.com/documentation/#rest

Note: The external API only supports filtering by "species" and "status".

---

## Project Structure
```
rick-morty-app/
├── api/                    # Application source code
│   ├── api.py              # API entrypoint
│   ├── backend.py          # Business logic
│   ├── collect_data.py     # Data collection module
│   ├── config.py           # Configuration utilities
│   ├── db.py               # Database interaction layer
│   └── ...
├── tests/                  # Unit tests
├── docker-compose.yaml     # Local environment setup
├── requirements.txt        # Python dependencies
├── start_server.sh         # Script to start the API & dependencies
├── shutdown_server.sh      # Script to stop the API & dependencies
└── README.md               # This file
```
---

## Development Setup

### Automated Setup

To spin up the environment quickly:

`./start_server.sh`

To shut it down:

`./shutdown_server.sh`

---

### Manual Setup

1. Create and activate a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```
2. Install dependencies:

`pip install -r requirements.txt`

3. Start Redis and PostgreSQL using Docker:

`docker-compose up -d`

---

## Running the Application

### Collect Data Manually

`python3 -m api.collect_data`

### Run Tests

`pytest`

### Start API Server Manually

`uvicorn api.api:app --reload`

---

## Using the API

Health check:

`curl http://localhost:8000/health`

Interactive API Docs:
Open http://localhost:8000/docs in your browser.

Query all characters:

`curl http://localhost:8000/characters`

Query with pagination:

`curl http://localhost:8000/characters?page=2&limit=10`

---

## Useful Commands

### Redis CLI Query
```
redis-cli
127.0.0.1:6379> GET characters
```
### PostgreSQL CLI Query
```
psql -h localhost -p 5432 -U user -d mydatabase
Password for user user:

mydatabase=# SELECT name, origin, status, species FROM characters;
```
---

## Cleanup

To stop the containers:

`docker compose down`

To stop and remove volumes (including database data):

`docker compose down -v`
