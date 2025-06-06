# Rick & Morty Character Service

This project provides a REST API to collect, store, and query character data from the Rick and Morty API: https://rickandmortyapi.com/documentation/#rest

Note: The external API only supports filtering by "species" and "status".

## Features
- Python backend with modular architecture
- Dockerized for easy deployment
- Helm charts for Kubernetes deployment
- GitHub Actions for CI/CD
- Comprehensive test suite
- Metrics for app monitoring
- TLocal test monitoring to stack for viewing metrics and dashboards

## Diagrams
![Alt text](docs/architecture.svg)
![Alt text](docs/api-uml.svg)
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
├── docs/                  
├── helm/                   # Helm Charts
│   ├── templates/          # Chart Templates
│   ├── Chart.yaml          # Chart file
│   ├── values.yaml         # Values file
├── tests/                  # Unit tests
├── docker-compose.yaml     # Local environment setup
├── requirements.txt        # Python dependencies
├── start_server.sh         # Script to start the API & dependencies
├── shutdown_server.sh      # Script to stop the API & dependencies
└── README.md               # This file
```
---

## Development Setup

### Pre-requisites

The app is expecting a set of environment variables in order for it to work. Here is a sample .env file you can use to set the environment variables in your local set-up

```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=mydatabase
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=3600
```

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

## Running & Testing the Application

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

Query metrics
`curl http://localhost:8000/metrics`
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
### Get Helm Template
```
helm template ./helm 
```
### Deploy the chart in your test cluster
```
helm upgrade --install rick-morty-app ./helm/ --set image_tag="$IMAGE_TAG" --set secrets.POSTGRES_PASSWORD="$POSTGRES_PASSWORD"
```
Check pods status
```
kubectl get pods -n test -l app=rick-morty-api # Update namespace according to your setup
```
Delete the chart
```
helm uninstall rick-morty-app
```
Connect to Postgre
```
kubectl port-forward svc/postgres 5432:5432 -n test # Update namespace according to your setup
psql -h localhost -p 5432 -U user -d mydatabase
```
Connect to Redis
```
kubectl port-forward svc/redis 6379:6379 -n test # Update namespace according to your setup
redis-cli -h localhost
```
---

## Monitoring

### Metrics

The following metrics have been defined for the service:
- Total requests
- Request latency
- Errors
- Count of characters queried

### Testing the Metric Collection

The docker compose file includes a prometheus and grafana. You can access prometheus at http://localhost:9090/

Here are sample PromQL queries for checking their values:

- Query characters count
```
sum(app_characters_returned_total)
```
- Errors per endpoint
```
sum by (endpoint) (app_errors_total)
```
- Avg latency per endpoint
```
rate(app_request_latency_seconds_sum[5m]) / rate(app_request_latency_seconds_count[5m])
```
- Requests per endpoint
```
sum by (endpoint) (app_requests_total)
```

## Cleanup

To stop the containers:

`docker-compose down`

To stop and remove volumes (including database data):

`docker-compose down -v`

## CICD considerations

Workflows are defined in `.github/workflows/`.

This project uses GitHub Actions for:
- Running tests on PR creation
- Linting and formatting
- Static code analysis and docker image analysis
- Building Docker images
- Upload Images to dockerhub
- Deploy the service to minikub
- Validate correct deployment and service accessibility

The following variables were created in the project's repo for CICD integration

Docker credentials:
- DOCKERHUB_TOKEN
- DOCKERHUB_USERNAME

Postgres Password:
- POSTGRES_PASSWORD